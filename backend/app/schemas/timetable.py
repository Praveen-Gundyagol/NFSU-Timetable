from typing import List, Optional, Any, Dict
from pydantic import BaseModel, ConfigDict

class SessionOut(BaseModel):
    id: int
    timetable_id: int
    subject_id: int
    subject_code: str
    subject_name: str
    faculty_id: int
    faculty_name: str
    room_id: int
    room_code: str
    room_name: str
    section_id: int
    section_name: str
    batch_id: Optional[int] = None
    batch_name: Optional[str] = None
    day_index: int
    period_index: int
    duration_periods: int
    session_type: str
    is_locked: bool
    is_fixed_commitment: bool
    model_config = ConfigDict(from_attributes=True)

class TimetableOut(BaseModel):
    id: int
    title: str
    academic_year: str
    semester_type: str
    status: str
    solver_status: Optional[str] = None
    infeasibility_report: Optional[Dict[str, Any]] = None
    sessions: List[SessionOut] = []
    model_config = ConfigDict(from_attributes=True)

class GenerateRequest(BaseModel):
    title: Optional[str] = "NFSU Academic Timetable"
    academic_year: Optional[str] = "2026-2027"
    semester_type: Optional[str] = "EVEN"
    time_limit_seconds: Optional[int] = 15

class ManualMoveValidateRequest(BaseModel):
    timetable_id: int
    session_id: int
    target_day: int
    target_period: int
    target_room_id: Optional[int] = None

class ConflictDetail(BaseModel):
    conflict_type: str # "FACULTY_CLASH", "ROOM_CLASH", "SECTION_CLASH", "BATCH_CLASH", "CAPACITY_EXCEEDED", "ROOM_TYPE_MISMATCH", "BREAK_OVERLAP"
    message: str

class ManualMoveValidateResponse(BaseModel):
    valid: bool
    conflicts: List[ConflictDetail] = []

class SessionLockRequest(BaseModel):
    session_id: int
    is_locked: bool
