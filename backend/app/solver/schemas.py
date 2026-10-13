from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field

@dataclass
class SessionTask:
    # Mandatory non-default fields first
    id: str
    subject_id: int
    subject_code: str
    subject_name: str
    section_id: int
    section_name: str
    section_strength: int
    faculty_id: int
    faculty_name: str
    
    # Optional / default fields after
    batch_id: Optional[int] = None # None for whole-class
    batch_name: Optional[str] = None
    batch_strength: Optional[int] = None
    duration_periods: int = 1 # 1 for theory, 2+ for lab
    required_room_type: str = "CLASSROOM"
    session_type: str = "THEORY" # "THEORY" or "PRACTICAL"
    locked_day: Optional[int] = None
    locked_period: Optional[int] = None
    locked_room_id: Optional[int] = None
    is_locked: bool = False
    is_fixed_commitment: bool = False

@dataclass
class RoomData:
    id: int
    code: str
    name: str
    room_type: str
    capacity: int
    is_active: bool = True
    unavailable_slots: List[List[int]] = field(default_factory=list) # [[day, period]]

@dataclass
class FacultyData:
    id: int
    name: str
    max_weekly_periods: int = 16
    max_daily_periods: int = 4
    unavailable_slots: List[List[int]] = field(default_factory=list) # [[day, period]]

@dataclass
class ScheduledSlot:
    session_id: str
    subject_id: int
    subject_code: str
    subject_name: str
    section_id: int
    section_name: str
    batch_id: Optional[int]
    batch_name: Optional[str]
    faculty_id: int
    faculty_name: str
    room_id: int
    room_code: str
    room_name: str
    day_index: int
    period_index: int
    duration_periods: int
    session_type: str
    is_locked: bool = False
    is_fixed_commitment: bool = False

@dataclass
class SolverInput:
    working_days: List[int]
    periods_per_day: int
    break_periods: List[int]
    rooms: List[RoomData]
    faculty: List[FacultyData]
    tasks: List[SessionTask]
    time_limit_seconds: int = 15

@dataclass
class SolverOutput:
    status: str # "OPTIMAL", "FEASIBLE", "INFEASIBLE"
    scheduled_sessions: List[ScheduledSlot] = field(default_factory=list)
    unscheduled_sessions: List[SessionTask] = field(default_factory=list)
    conflict_explanations: List[str] = field(default_factory=list)
    solver_time_seconds: float = 0.0
