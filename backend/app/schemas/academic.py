from typing import List
from pydantic import BaseModel, ConfigDict

class PracticalBatchBase(BaseModel):
    name: str
    batch_strength: int = 30

class PracticalBatchCreate(PracticalBatchBase):
    section_id: int

class PracticalBatchOut(PracticalBatchBase):
    id: int
    section_id: int
    model_config = ConfigDict(from_attributes=True)

class SectionBase(BaseModel):
    name: str
    total_strength: int = 60

class SectionCreate(SectionBase):
    semester_id: int

class SectionOut(SectionBase):
    id: int
    semester_id: int
    batches: List[PracticalBatchOut] = []
    model_config = ConfigDict(from_attributes=True)

class SemesterBase(BaseModel):
    semester_number: int

class SemesterCreate(SemesterBase):
    programme_id: int

class SemesterOut(SemesterBase):
    id: int
    programme_id: int
    sections: List[SectionOut] = []
    model_config = ConfigDict(from_attributes=True)

class ProgrammeBase(BaseModel):
    code: str
    name: str
    department: str

class ProgrammeCreate(ProgrammeBase):
    pass

class ProgrammeOut(ProgrammeBase):
    id: int
    semesters: List[SemesterOut] = []
    model_config = ConfigDict(from_attributes=True)
