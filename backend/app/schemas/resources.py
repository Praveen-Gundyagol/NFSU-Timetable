from typing import List, Optional
from pydantic import BaseModel, ConfigDict

class RoomBase(BaseModel):
    code: str
    name: str
    room_type: str = "CLASSROOM"
    capacity: int = 60
    is_active: bool = True
    unavailable_slots: List[List[int]] = [] # list of [day_index, period_index]

class RoomCreate(RoomBase):
    pass

class RoomOut(RoomBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class FacultyAvailabilityBase(BaseModel):
    day_index: int
    period_index: int
    status: str = "AVAILABLE" # AVAILABLE, UNAVAILABLE, FIXED_COMMITMENT
    note: Optional[str] = None

class FacultyAvailabilityOut(FacultyAvailabilityBase):
    id: int
    faculty_id: int
    model_config = ConfigDict(from_attributes=True)

class FacultyBase(BaseModel):
    employee_id: str
    name: str
    email: str
    department: str
    max_weekly_periods: int = 16
    max_daily_periods: int = 4
    is_active: bool = True

class FacultyCreate(FacultyBase):
    pass

class FacultyOut(FacultyBase):
    id: int
    availabilities: List[FacultyAvailabilityOut] = []
    model_config = ConfigDict(from_attributes=True)

class FacultyAvailabilityBatchUpdate(BaseModel):
    faculty_id: int
    availabilities: List[FacultyAvailabilityBase]
