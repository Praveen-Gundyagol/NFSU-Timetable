from typing import List, Optional
from pydantic import BaseModel, ConfigDict

class SubjectFacultyAssignmentBase(BaseModel):
    faculty_id: int
    component: str = "THEORY" # "THEORY", "PRACTICAL"
    batch_id: Optional[int] = None

class SubjectFacultyAssignmentCreate(SubjectFacultyAssignmentBase):
    subject_id: int

class SubjectFacultyAssignmentOut(SubjectFacultyAssignmentBase):
    id: int
    subject_id: int
    faculty_name: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class SubjectBase(BaseModel):
    code: str
    name: str
    subject_type: str = "INTEGRATED" # "THEORY_ONLY", "PRACTICAL_ONLY", "INTEGRATED"
    weekly_theory_periods: int = 3
    weekly_practical_sessions: int = 1
    practical_duration_periods: int = 2
    required_room_type: str = "CLASSROOM"
    preferred_room_id: Optional[int] = None

class SubjectCreate(SubjectBase):
    semester_id: int

class SubjectOut(SubjectBase):
    id: int
    semester_id: int
    faculty_assignments: List[SubjectFacultyAssignmentOut] = []
    model_config = ConfigDict(from_attributes=True)
