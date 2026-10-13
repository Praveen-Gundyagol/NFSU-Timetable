import json
import io
import csv
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.university import InstitutionConfig, TimeSlot
from app.models.resources import Room, Faculty, FacultyAvailability
from app.models.academic import Programme, Semester, Section, PracticalBatch
from app.models.curriculum import Subject, SubjectFacultyAssignment
from app.models.timetable import Timetable, TimetableSession
from app.schemas.timetable import (
    GenerateRequest, TimetableOut, SessionOut,
    ManualMoveValidateRequest, ManualMoveValidateResponse, ConflictDetail,
    SessionLockRequest
)
from app.solver.schemas import SolverInput, RoomData, FacultyData, SessionTask
from app.solver.engine import solve_timetable

router = APIRouter(prefix="/api/timetable", tags=["Timetable"])

def build_solver_input_from_db(db: Session, preserve_locks_timetable_id: Optional[int] = None) -> SolverInput:
    config = db.query(InstitutionConfig).first()
    if not config:
        raise HTTPException(status_code=400, detail="University configuration not found.")

    working_days = json.loads(config.working_days_json)
    break_periods = json.loads(config.break_periods_json)

    # 1. Rooms
    rooms_db = db.query(Room).filter(Room.is_active == True).all()
    room_data_list = [
        RoomData(
            id=r.id,
            code=r.code,
            name=r.name,
            room_type=r.room_type,
            capacity=r.capacity,
            is_active=r.is_active,
            unavailable_slots=json.loads(r.unavailable_slots_json) if r.unavailable_slots_json else []
        )
        for r in rooms_db
    ]

    # 2. Faculty
    faculty_db = db.query(Faculty).filter(Faculty.is_active == True).all()
    faculty_data_list = []
    for f in faculty_db:
        unavail = [
            [a.day_index, a.period_index]
            for a in f.availabilities
            if a.status in ("UNAVAILABLE", "FIXED_COMMITMENT")
        ]
        faculty_data_list.append(FacultyData(
            id=f.id,
            name=f.name,
            max_weekly_periods=f.max_weekly_periods,
            max_daily_periods=f.max_daily_periods,
            unavailable_slots=unavail
        ))

    # Existing locked sessions map: (subject_id, section_id, batch_id, component, instance_idx) -> session
    locked_sessions_map = {}
    if preserve_locks_timetable_id:
        existing_tt = db.query(Timetable).filter(Timetable.id == preserve_locks_timetable_id).first()
        if existing_tt:
            for s in existing_tt.sessions:
                if s.is_locked:
                    key = (s.subject_id, s.section_id, s.batch_id, s.session_type)
                    if key not in locked_sessions_map:
                        locked_sessions_map[key] = []
                    locked_sessions_map[key].append(s)

    # 3. Build Tasks to Schedule
    tasks: List[SessionTask] = []
    subjects = db.query(Subject).all()
    
    for sub in subjects:
        sem = sub.semester
        if not sem:
            continue
        for sec in sem.sections:
            # A. Theory sessions (whole-class)
            theory_assignments = [
                a for a in sub.faculty_assignments
                if a.component == "THEORY"
            ]
            primary_theory_faculty = theory_assignments[0].faculty if theory_assignments else None
            if not primary_theory_faculty and faculty_db:
                primary_theory_faculty = faculty_db[0] # fallback

            if primary_theory_faculty and sub.weekly_theory_periods > 0:
                locked_list = locked_sessions_map.get((sub.id, sec.id, None, "THEORY"), [])
                for i in range(sub.weekly_theory_periods):
                    task_id = f"T_{sub.id}_SEC_{sec.id}_{i+1}"
                    locked_sess = locked_list[i] if i < len(locked_list) else None
                    tasks.append(SessionTask(
                        id=task_id,
                        subject_id=sub.id,
                        subject_code=sub.code,
                        subject_name=sub.name,
                        section_id=sec.id,
                        section_name=sec.name,
                        section_strength=sec.total_strength,
                        batch_id=None,
                        batch_name=None,
                        batch_strength=None,
                        faculty_id=primary_theory_faculty.id,
                        faculty_name=primary_theory_faculty.name,
                        duration_periods=1,
                        required_room_type="CLASSROOM",
                        session_type="THEORY",
                        locked_day=locked_sess.day_index if locked_sess else None,
                        locked_period=locked_sess.period_index if locked_sess else None,
                        locked_room_id=locked_sess.room_id if locked_sess else None,
                        is_locked=bool(locked_sess)
                    ))

            # B. Practical sessions (per batch)
            if sub.weekly_practical_sessions > 0 and sub.practical_duration_periods > 0:
                batches = sec.batches if sec.batches else []
                for batch in batches:
                    # Look for specific batch faculty assignment, or default practical faculty
                    batch_assignment = next(
                        (a for a in sub.faculty_assignments if a.component == "PRACTICAL" and a.batch_id == batch.id),
                        None
                    )
                    if not batch_assignment:
                        batch_assignment = next(
                            (a for a in sub.faculty_assignments if a.component == "PRACTICAL"),
                            None
                        )
                    lab_faculty = batch_assignment.faculty if batch_assignment else (primary_theory_faculty or faculty_db[0])

                    locked_list = locked_sessions_map.get((sub.id, sec.id, batch.id, "PRACTICAL"), [])
                    for i in range(sub.weekly_practical_sessions):
                        task_id = f"P_{sub.id}_SEC_{sec.id}_B_{batch.id}_{i+1}"
                        locked_sess = locked_list[i] if i < len(locked_list) else None
                        tasks.append(SessionTask(
                            id=task_id,
                            subject_id=sub.id,
                            subject_code=sub.code,
                            subject_name=sub.name,
                            section_id=sec.id,
                            section_name=sec.name,
                            section_strength=sec.total_strength,
                            batch_id=batch.id,
                            batch_name=batch.name,
                            batch_strength=batch.batch_strength,
                            faculty_id=lab_faculty.id,
                            faculty_name=lab_faculty.name,
                            duration_periods=sub.practical_duration_periods,
                            required_room_type=sub.required_room_type,
                            session_type="PRACTICAL",
                            locked_day=locked_sess.day_index if locked_sess else None,
                            locked_period=locked_sess.period_index if locked_sess else None,
                            locked_room_id=locked_sess.room_id if locked_sess else None,
                            is_locked=bool(locked_sess)
                        ))

    return SolverInput(
        working_days=working_days,
        periods_per_day=config.periods_per_day,
        break_periods=break_periods,
        rooms=room_data_list,
        faculty=faculty_data_list,
        tasks=tasks,
        time_limit_seconds=15
    )

def format_timetable_response(tt: Timetable) -> TimetableOut:
    session_outs = []
    for s in tt.sessions:
        session_outs.append(SessionOut(
            id=s.id,
            timetable_id=s.timetable_id,
            subject_id=s.subject_id,
            subject_code=s.subject.code if s.subject else "N/A",
            subject_name=s.subject.name if s.subject else "N/A",
            faculty_id=s.faculty_id,
            faculty_name=s.faculty.name if s.faculty else "N/A",
            room_id=s.room_id,
            room_code=s.room.code if s.room else "N/A",
            room_name=s.room.name if s.room else "N/A",
            section_id=s.section_id,
            section_name=s.section.name if s.section else "N/A",
            batch_id=s.batch_id,
            batch_name=s.batch.name if s.batch else None,
            day_index=s.day_index,
            period_index=s.period_index,
            duration_periods=s.duration_periods,
            session_type=s.session_type,
            is_locked=s.is_locked,
            is_fixed_commitment=s.is_fixed_commitment
        ))

    infeasibility_data = None
    if tt.infeasibility_report_json:
        try:
            infeasibility_data = json.loads(tt.infeasibility_report_json)
        except Exception:
            infeasibility_data = {"raw": tt.infeasibility_report_json}

    return TimetableOut(
        id=tt.id,
        title=tt.title,
        academic_year=tt.academic_year,
        semester_type=tt.semester_type,
        status=tt.status,
        solver_status=tt.solver_status,
        infeasibility_report=infeasibility_data,
        sessions=session_outs
    )

@router.post("/generate", response_model=TimetableOut)
def generate_timetable(payload: GenerateRequest, db: Session = Depends(get_db)):
    """Triggers Google OR-Tools CP-SAT solver and saves generated schedule."""
    # Check if there is an existing draft to preserve locked sessions
    existing_draft = db.query(Timetable).filter(Timetable.status == "DRAFT").first()
    preserve_id = existing_draft.id if existing_draft else None

    solver_input = build_solver_input_from_db(db, preserve_locks_timetable_id=preserve_id)
    if payload.time_limit_seconds:
        solver_input.time_limit_seconds = payload.time_limit_seconds

    # Run solver
    solver_output = solve_timetable(solver_input)

    # Create new timetable record
    new_tt = Timetable(
        title=payload.title or "NFSU Academic Timetable",
        academic_year=payload.academic_year or "2026-2027",
        semester_type=payload.semester_type or "EVEN",
        status="DRAFT",
        solver_status=solver_output.status,
        infeasibility_report_json=json.dumps({
            "status": solver_output.status,
            "unscheduled_count": len(solver_output.unscheduled_sessions),
            "conflict_explanations": solver_output.conflict_explanations,
            "solver_time_seconds": round(solver_output.solver_time_seconds, 2)
        }) if solver_output.conflict_explanations else None
    )
    db.add(new_tt)
    db.commit()
    db.refresh(new_tt)

    # Save scheduled sessions
    sessions_to_add = []
    for s in solver_output.scheduled_sessions:
        sessions_to_add.append(TimetableSession(
            timetable_id=new_tt.id,
            subject_id=s.subject_id,
            faculty_id=s.faculty_id,
            room_id=s.room_id,
            section_id=s.section_id,
            batch_id=s.batch_id,
            day_index=s.day_index,
            period_index=s.period_index,
            duration_periods=s.duration_periods,
            session_type=s.session_type,
            is_locked=s.is_locked,
            is_fixed_commitment=s.is_fixed_commitment
        ))
    db.add_all(sessions_to_add)
    db.commit()
    db.refresh(new_tt)

    return format_timetable_response(new_tt)

@router.get("/latest", response_model=TimetableOut)
def get_latest_timetable(db: Session = Depends(get_db)):
    tt = db.query(Timetable).order_by(Timetable.id.desc()).first()
    if not tt:
        raise HTTPException(status_code=404, detail="No timetable generated yet.")
    return format_timetable_response(tt)

@router.post("/validate-move", response_model=ManualMoveValidateResponse)
def validate_manual_move(payload: ManualMoveValidateRequest, db: Session = Depends(get_db)):
    """Validates if moving a session to (day, period, room) creates hard constraint violations."""
    session = db.query(TimetableSession).filter(TimetableSession.id == payload.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    config = db.query(InstitutionConfig).first()
    break_periods = json.loads(config.break_periods_json) if config else [4]
    periods_per_day = config.periods_per_day if config else 7

    target_day = payload.target_day
    target_period = payload.target_period
    target_room_id = payload.target_room_id or session.room_id
    target_room = db.query(Room).filter(Room.id == target_room_id).first()
    dur = session.duration_periods

    conflicts: List[ConflictDetail] = []

    # 1. Bounds & Break check
    if target_period + dur > periods_per_day:
        conflicts.append(ConflictDetail(
            conflict_type="OUT_OF_BOUNDS",
            message=f"Session of {dur} periods exceeds the last period of the day."
        ))
    if any(p in break_periods for p in range(target_period, target_period + dur)):
        conflicts.append(ConflictDetail(
            conflict_type="BREAK_OVERLAP",
            message="Session spans across scheduled university lunch/break period."
        ))

    # 2. Room Capacity & Room Type
    req_strength = session.batch.batch_strength if session.batch else session.section.total_strength
    if target_room:
        if target_room.capacity < req_strength:
            conflicts.append(ConflictDetail(
                conflict_type="CAPACITY_EXCEEDED",
                message=f"Room '{target_room.name}' capacity ({target_room.capacity}) is smaller than required student strength ({req_strength})."
            ))
        if session.session_type == "PRACTICAL" and target_room.room_type != session.subject.required_room_type:
            conflicts.append(ConflictDetail(
                conflict_type="ROOM_TYPE_MISMATCH",
                message=f"Room '{target_room.name}' ({target_room.room_type}) does not match required lab type '{session.subject.required_room_type}'."
            ))

    # 3. Faculty Clash
    other_sessions = db.query(TimetableSession).filter(
        TimetableSession.timetable_id == session.timetable_id,
        TimetableSession.id != session.id,
        TimetableSession.day_index == target_day
    ).all()

    for other in other_sessions:
        # Check time overlap
        o_start = other.period_index
        o_end = other.period_index + other.duration_periods
        overlap = max(target_period, o_start) < min(target_period + dur, o_end)
        if not overlap:
            continue

        # Faculty clash
        if other.faculty_id == session.faculty_id:
            conflicts.append(ConflictDetail(
                conflict_type="FACULTY_CLASH",
                message=f"Faculty '{session.faculty.name}' is already teaching '{other.subject.name}' ({other.section.name}) at this slot."
            ))

        # Room clash
        if other.room_id == target_room_id:
            conflicts.append(ConflictDetail(
                conflict_type="ROOM_CLASH",
                message=f"Room '{target_room.name}' is already occupied by '{other.subject.name}' at this slot."
            ))

        # Group / Batch clash
        if other.section_id == session.section_id:
            if session.batch_id is None or other.batch_id is None or session.batch_id == other.batch_id:
                conflicts.append(ConflictDetail(
                    conflict_type="GROUP_CLASH",
                    message=f"Section/Batch students are already occupied with '{other.subject.name}' at this slot."
                ))

    return ManualMoveValidateResponse(
        valid=len(conflicts) == 0,
        conflicts=conflicts
    )

@router.post("/sessions/move")
def execute_manual_move(payload: ManualMoveValidateRequest, db: Session = Depends(get_db)):
    """Executes a manual move and validates constraints."""
    val_res = validate_manual_move(payload, db)
    if not val_res.valid:
        error_msgs = "; ".join([c.message for c in val_res.conflicts])
        raise HTTPException(status_code=400, detail=f"Cannot move session due to conflicts: {error_msgs}")

    session = db.query(TimetableSession).filter(TimetableSession.id == payload.session_id).first()
    session.day_index = payload.target_day
    session.period_index = payload.target_period
    if payload.target_room_id:
        session.room_id = payload.target_room_id
    db.commit()
    return {"message": "Session moved successfully."}

@router.post("/sessions/lock")
def toggle_session_lock(payload: SessionLockRequest, db: Session = Depends(get_db)):
    session = db.query(TimetableSession).filter(TimetableSession.id == payload.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    session.is_locked = payload.is_locked
    db.commit()
    return {"message": f"Session lock set to {payload.is_locked}."}

@router.post("/publish")
def publish_timetable(timetable_id: int, db: Session = Depends(get_db)):
    tt = db.query(Timetable).filter(Timetable.id == timetable_id).first()
    if not tt:
        raise HTTPException(status_code=404, detail="Timetable not found.")
    if tt.solver_status == "INFEASIBLE":
        raise HTTPException(status_code=400, detail="Cannot publish an infeasible timetable with unscheduled sessions.")
    tt.status = "PUBLISHED"
    db.commit()
    return {"message": "Timetable published successfully."}

@router.get("/export/csv")
def export_csv(timetable_id: int, db: Session = Depends(get_db)):
    tt = db.query(Timetable).filter(Timetable.id == timetable_id).first()
    if not tt:
        raise HTTPException(status_code=404, detail="Timetable not found.")

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Day Index", "Period Index", "Duration", "Subject Code", "Subject Name",
        "Faculty", "Room", "Section", "Batch", "Type", "Locked"
    ])

    for s in tt.sessions:
        writer.writerow([
            s.day_index,
            s.period_index,
            s.duration_periods,
            s.subject.code if s.subject else "",
            s.subject.name if s.subject else "",
            s.faculty.name if s.faculty else "",
            s.room.name if s.room else "",
            s.section.name if s.section else "",
            s.batch.name if s.batch else "Whole Class",
            s.session_type,
            "Yes" if s.is_locked else "No"
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=timetable_{timetable_id}.csv"}
    )
