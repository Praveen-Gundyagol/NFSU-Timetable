from typing import List
from pydantic import BaseModel, ConfigDict

class InstitutionConfigBase(BaseModel):
    name: str = "National Forensic Sciences University"
    working_days: List[int] = [0, 1, 2, 3, 4] # 0=Mon ... 4=Fri
    periods_per_day: int = 7
    period_duration_minutes: int = 60
    start_time: str = "09:00"
    break_periods: List[int] = [4] # Period index 4 is Lunch

class InstitutionConfigCreate(InstitutionConfigBase):
    pass

class InstitutionConfigOut(InstitutionConfigBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class TimeSlotOut(BaseModel):
    id: int
    day_index: int
    period_index: int
    start_time: str
    end_time: str
    is_break: bool
    model_config = ConfigDict(from_attributes=True)
