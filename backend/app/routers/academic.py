import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.academic import Programme, Semester, Section, PracticalBatch
from app.models.curriculum import Subject, SubjectFacultyAssignment
from app.models.resources import Room, Faculty, FacultyAvailability
from app.models.university import InstitutionConfig
from app.schemas.academic import (
    ProgrammeCreate, ProgrammeOut, SectionCreate, SectionOut,
    PracticalBatchCreate, PracticalBatchOut
)
from app.schemas.curriculum import (
    SubjectCreate, SubjectOut, SubjectFacultyAssignmentCreate, SubjectFacultyAssignmentOut
)
from app.routers.config import regenerate_time_slots

router = APIRouter(prefix="/api/academic", tags=["Academic"])

# --- Programmes Endpoints ---
@router.get("/programmes", response_model=List[ProgrammeOut])
def get_programmes(db: Session = Depends(get_db)):
    return db.query(Programme).all()

@router.post("/programmes", response_model=ProgrammeOut)
def create_programme(payload: ProgrammeCreate, db: Session = Depends(get_db)):
    existing = db.query(Programme).filter(Programme.code == payload.code).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Programme with code '{payload.code}' already exists.")
    
    prog = Programme(code=payload.code, name=payload.name, department=payload.department)
    db.add(prog)
    db.commit()
    db.refresh(prog)
    return prog

@router.post("/semesters")
def add_semester(programme_id: int, semester_number: int, db: Session = Depends(get_db)):
    prog = db.query(Programme).filter(Programme.id == programme_id).first()
    if not prog:
        raise HTTPException(status_code=404, detail="Programme not found.")
    
    sem = Semester(programme_id=programme_id, semester_number=semester_number)
    db.add(sem)
    db.commit()
    db.refresh(sem)
    return {"id": sem.id, "programme_id": sem.programme_id, "semester_number": sem.semester_number}

@router.post("/sections", response_model=SectionOut)
def create_section(payload: SectionCreate, db: Session = Depends(get_db)):
    sem = db.query(Semester).filter(Semester.id == payload.semester_id).first()
    if not sem:
        raise HTTPException(status_code=404, detail="Semester not found.")
    
    sec = Section(semester_id=payload.semester_id, name=payload.name, total_strength=payload.total_strength)
    db.add(sec)
    db.commit()
    db.refresh(sec)
    return sec

@router.post("/batches", response_model=PracticalBatchOut)
def create_batch(payload: PracticalBatchCreate, db: Session = Depends(get_db)):
    sec = db.query(Section).filter(Section.id == payload.section_id).first()
    if not sec:
        raise HTTPException(status_code=404, detail="Section not found.")
    
    batch = PracticalBatch(section_id=payload.section_id, name=payload.name, batch_strength=payload.batch_strength)
    db.add(batch)
    db.commit()
    db.refresh(batch)
    return batch

# --- Subjects Endpoints ---
@router.get("/subjects", response_model=List[SubjectOut])
def get_subjects(db: Session = Depends(get_db)):
    subjects = db.query(Subject).all()
    results = []
    for s in subjects:
        assignments = [
            SubjectFacultyAssignmentOut(
                id=a.id,
                subject_id=a.subject_id,
                faculty_id=a.faculty_id,
                component=a.component,
                batch_id=a.batch_id,
                faculty_name=a.faculty.name if a.faculty else None
            )
            for a in s.faculty_assignments
        ]
        results.append(SubjectOut(
            id=s.id,
            semester_id=s.semester_id,
            code=s.code,
            name=s.name,
            subject_type=s.subject_type,
            weekly_theory_periods=s.weekly_theory_periods,
            weekly_practical_sessions=s.weekly_practical_sessions,
            practical_duration_periods=s.practical_duration_periods,
            required_room_type=s.required_room_type,
            preferred_room_id=s.preferred_room_id,
            faculty_assignments=assignments
        ))
    return results

@router.post("/subjects", response_model=SubjectOut)
def create_subject(payload: SubjectCreate, db: Session = Depends(get_db)):
    sem = db.query(Semester).filter(Semester.id == payload.semester_id).first()
    if not sem:
        raise HTTPException(status_code=404, detail="Semester not found.")
    
    sub = Subject(
        semester_id=payload.semester_id,
        code=payload.code,
        name=payload.name,
        subject_type=payload.subject_type,
        weekly_theory_periods=payload.weekly_theory_periods,
        weekly_practical_sessions=payload.weekly_practical_sessions,
        practical_duration_periods=payload.practical_duration_periods,
        required_room_type=payload.required_room_type,
        preferred_room_id=payload.preferred_room_id
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return SubjectOut(
        id=sub.id,
        semester_id=sub.semester_id,
        code=sub.code,
        name=sub.name,
        subject_type=sub.subject_type,
        weekly_theory_periods=sub.weekly_theory_periods,
        weekly_practical_sessions=sub.weekly_practical_sessions,
        practical_duration_periods=sub.practical_duration_periods,
        required_room_type=sub.required_room_type,
        preferred_room_id=sub.preferred_room_id,
        faculty_assignments=[]
    )

@router.post("/subjects/assign-faculty", response_model=SubjectFacultyAssignmentOut)
def assign_faculty(payload: SubjectFacultyAssignmentCreate, db: Session = Depends(get_db)):
    sub = db.query(Subject).filter(Subject.id == payload.subject_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subject not found.")
    fac = db.query(Faculty).filter(Faculty.id == payload.faculty_id).first()
    if not fac:
        raise HTTPException(status_code=404, detail="Faculty not found.")
    
    assignment = SubjectFacultyAssignment(
        subject_id=payload.subject_id,
        faculty_id=payload.faculty_id,
        component=payload.component,
        batch_id=payload.batch_id
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return SubjectFacultyAssignmentOut(
        id=assignment.id,
        subject_id=assignment.subject_id,
        faculty_id=assignment.faculty_id,
        component=assignment.component,
        batch_id=assignment.batch_id,
        faculty_name=fac.name
    )

# --- Sample Dataset Seeder ---
@router.post("/seed-sample-data")
def seed_sample_data(db: Session = Depends(get_db)):
    """Populates realistic NFSU academic department data for instant testing."""
    # Reset existing records
    db.query(SubjectFacultyAssignment).delete()
    db.query(Subject).delete()
    db.query(PracticalBatch).delete()
    db.query(Section).delete()
    db.query(Semester).delete()
    db.query(Programme).delete()
    db.query(FacultyAvailability).delete()
    db.query(Faculty).delete()
    db.query(Room).delete()

    # 1. Config
    config = db.query(InstitutionConfig).first()
    if not config:
        config = InstitutionConfig()
        db.add(config)
    config.name = "National Forensic Sciences University"
    config.working_days_json = "[0, 1, 2, 3, 4]" # Mon-Fri
    config.periods_per_day = 7
    config.period_duration_minutes = 60
    config.start_time = "09:00"
    config.break_periods_json = "[4]" # Lunch is Period index 4 (13:00-14:00)
    db.commit()
    regenerate_time_slots(db, config)

    # 2. Rooms
    rooms = [
        Room(code="CR-101", name="Lecture Hall 101", room_type="CLASSROOM", capacity=65, is_active=True),
        Room(code="CR-102", name="Lecture Hall 102", room_type="CLASSROOM", capacity=65, is_active=True),
        Room(code="LAB-CYBER-1", name="Cyber Defense Lab", room_type="LAB_CYBER", capacity=35, is_active=True),
        Room(code="LAB-COMP-1", name="Advanced Computing Lab", room_type="LAB_COMPUTER", capacity=35, is_active=True),
        Room(code="LAB-FOR-1", name="Digital Forensics Lab", room_type="LAB_FORENSIC", capacity=35, is_active=True),
    ]
    db.add_all(rooms)
    db.commit()

    # 3. Faculty
    faculty_members = [
        Faculty(employee_id="NFSU-FAC-01", name="Dr. Naveen Patel", email="npatel@nfsu.ac.in", department="Cyber Security", max_weekly_periods=16, max_daily_periods=4),
        Faculty(employee_id="NFSU-FAC-02", name="Dr. Sneha Rao", email="srao@nfsu.ac.in", department="Digital Forensics", max_weekly_periods=16, max_daily_periods=4),
        Faculty(employee_id="NFSU-FAC-03", name="Dr. Kunal Sharma", email="ksharma@nfsu.ac.in", department="Cyber Security", max_weekly_periods=16, max_daily_periods=4),
        Faculty(employee_id="NFSU-FAC-04", name="Dr. Ananya Verma", email="averma@nfsu.ac.in", department="Digital Forensics", max_weekly_periods=16, max_daily_periods=4),
        Faculty(employee_id="NFSU-FAC-05", name="Prof. Manish Joshi", email="mjoshi@nfsu.ac.in", department="Computer Science", max_weekly_periods=16, max_daily_periods=4),
    ]
    db.add_all(faculty_members)
    db.commit()

    # Faculty 1 (Dr. Patel) unavailable on Monday first period (e.g. Dean briefing)
    db.add(FacultyAvailability(faculty_id=faculty_members[0].id, day_index=0, period_index=0, status="UNAVAILABLE", note="Dean Briefing"))
    db.commit()

    # 4. Programme 1: B.Tech Cyber Security
    p1 = Programme(code="BT-CS", name="B.Tech Cyber Security", department="School of Cyber Security & Digital Forensics")
    db.add(p1)
    db.commit()

    s1 = Semester(programme_id=p1.id, semester_number=4)
    db.add(s1)
    db.commit()

    sec1 = Section(semester_id=s1.id, name="A", total_strength=60)
    db.add(sec1)
    db.commit()

    batch_a1 = PracticalBatch(section_id=sec1.id, name="B1", batch_strength=30)
    batch_a2 = PracticalBatch(section_id=sec1.id, name="B2", batch_strength=30)
    db.add_all([batch_a1, batch_a2])
    db.commit()

    # Subjects for B.Tech Sem 4
    sub1 = Subject(semester_id=s1.id, code="CS401", name="Cryptography & Network Security", subject_type="INTEGRATED", weekly_theory_periods=3, weekly_practical_sessions=1, practical_duration_periods=2, required_room_type="LAB_CYBER")
    sub2 = Subject(semester_id=s1.id, code="CS402", name="Database Security & Administration", subject_type="INTEGRATED", weekly_theory_periods=3, weekly_practical_sessions=1, practical_duration_periods=2, required_room_type="LAB_COMPUTER")
    sub3 = Subject(semester_id=s1.id, code="CS403", name="Operating Systems Security", subject_type="INTEGRATED", weekly_theory_periods=3, weekly_practical_sessions=1, practical_duration_periods=2, required_room_type="LAB_COMPUTER")
    sub4 = Subject(semester_id=s1.id, code="CS404", name="Cyber Laws & Ethics", subject_type="THEORY_ONLY", weekly_theory_periods=3, weekly_practical_sessions=0, practical_duration_periods=0, required_room_type="CLASSROOM")
    db.add_all([sub1, sub2, sub3, sub4])
    db.commit()

    # Assign Faculty
    db.add_all([
        SubjectFacultyAssignment(subject_id=sub1.id, faculty_id=faculty_members[0].id, component="THEORY"),
        SubjectFacultyAssignment(subject_id=sub1.id, faculty_id=faculty_members[0].id, component="PRACTICAL", batch_id=batch_a1.id),
        SubjectFacultyAssignment(subject_id=sub1.id, faculty_id=faculty_members[2].id, component="PRACTICAL", batch_id=batch_a2.id),
        SubjectFacultyAssignment(subject_id=sub2.id, faculty_id=faculty_members[3].id, component="THEORY"),
        SubjectFacultyAssignment(subject_id=sub2.id, faculty_id=faculty_members[3].id, component="PRACTICAL", batch_id=batch_a1.id),
        SubjectFacultyAssignment(subject_id=sub2.id, faculty_id=faculty_members[3].id, component="PRACTICAL", batch_id=batch_a2.id),
        SubjectFacultyAssignment(subject_id=sub3.id, faculty_id=faculty_members[4].id, component="THEORY"),
        SubjectFacultyAssignment(subject_id=sub3.id, faculty_id=faculty_members[4].id, component="PRACTICAL", batch_id=batch_a1.id),
        SubjectFacultyAssignment(subject_id=sub3.id, faculty_id=faculty_members[4].id, component="PRACTICAL", batch_id=batch_a2.id),
        SubjectFacultyAssignment(subject_id=sub4.id, faculty_id=faculty_members[2].id, component="THEORY"),
    ])
    db.commit()

    # 5. Programme 2: M.Sc Digital Forensics
    p2 = Programme(code="MS-DFS", name="M.Sc Digital Forensics", department="School of Cyber Security & Digital Forensics")
    db.add(p2)
    db.commit()

    s2 = Semester(programme_id=p2.id, semester_number=2)
    db.add(s2)
    db.commit()

    sec2 = Section(semester_id=s2.id, name="A", total_strength=30)
    db.add(sec2)
    db.commit()

    batch_m1 = PracticalBatch(section_id=sec2.id, name="B1", batch_strength=15)
    batch_m2 = PracticalBatch(section_id=sec2.id, name="B2", batch_strength=15)
    db.add_all([batch_m1, batch_m2])
    db.commit()

    # Subjects for M.Sc Sem 2
    sub5 = Subject(semester_id=s2.id, code="DF201", name="Digital Evidence & Malware Analysis", subject_type="INTEGRATED", weekly_theory_periods=3, weekly_practical_sessions=1, practical_duration_periods=2, required_room_type="LAB_FORENSIC")
    sub6 = Subject(semester_id=s2.id, code="DF202", name="Mobile & IoT Device Forensics", subject_type="INTEGRATED", weekly_theory_periods=3, weekly_practical_sessions=1, practical_duration_periods=2, required_room_type="LAB_FORENSIC")
    sub7 = Subject(semester_id=s2.id, code="DF203", name="Incident Response & Threat Hunting", subject_type="INTEGRATED", weekly_theory_periods=3, weekly_practical_sessions=1, practical_duration_periods=2, required_room_type="LAB_CYBER")
    db.add_all([sub5, sub6, sub7])
    db.commit()

    db.add_all([
        SubjectFacultyAssignment(subject_id=sub5.id, faculty_id=faculty_members[1].id, component="THEORY"),
        SubjectFacultyAssignment(subject_id=sub5.id, faculty_id=faculty_members[1].id, component="PRACTICAL", batch_id=batch_m1.id),
        SubjectFacultyAssignment(subject_id=sub5.id, faculty_id=faculty_members[1].id, component="PRACTICAL", batch_id=batch_m2.id),
        SubjectFacultyAssignment(subject_id=sub6.id, faculty_id=faculty_members[1].id, component="THEORY"),
        SubjectFacultyAssignment(subject_id=sub6.id, faculty_id=faculty_members[3].id, component="PRACTICAL", batch_id=batch_m1.id),
        SubjectFacultyAssignment(subject_id=sub6.id, faculty_id=faculty_members[3].id, component="PRACTICAL", batch_id=batch_m2.id),
        SubjectFacultyAssignment(subject_id=sub7.id, faculty_id=faculty_members[0].id, component="THEORY"),
        SubjectFacultyAssignment(subject_id=sub7.id, faculty_id=faculty_members[2].id, component="PRACTICAL", batch_id=batch_m1.id),
        SubjectFacultyAssignment(subject_id=sub7.id, faculty_id=faculty_members[2].id, component="PRACTICAL", batch_id=batch_m2.id),
    ])
    db.commit()

    return {
        "status": "success",
        "message": "Sample NFSU dataset successfully loaded with 2 programmes, 7 subjects, 5 labs/rooms, and 5 faculty members."
    }
