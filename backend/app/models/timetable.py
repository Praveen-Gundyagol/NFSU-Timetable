from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class Timetable(Base):
    __tablename__ = "timetables"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), default="NFSU Academic Timetable")
    academic_year = Column(String(20), default="2026-2027")
    semester_type = Column(String(10), default="EVEN") # "ODD", "EVEN"
    status = Column(String(20), default="DRAFT") # "DRAFT", "PUBLISHED", "ARCHIVED"
    solver_status = Column(String(30), nullable=True) # "OPTIMAL", "FEASIBLE", "INFEASIBLE"
    infeasibility_report_json = Column(Text, nullable=True) # diagnostic breakdown
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    sessions = relationship("TimetableSession", back_populates="timetable", cascade="all, delete-orphan")

class TimetableSession(Base):
    __tablename__ = "timetable_sessions"

    id = Column(Integer, primary_key=True, index=True)
    timetable_id = Column(Integer, ForeignKey("timetables.id"), index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), index=True)
    faculty_id = Column(Integer, ForeignKey("faculty.id"), index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), index=True)
    section_id = Column(Integer, ForeignKey("sections.id"), index=True)
    batch_id = Column(Integer, ForeignKey("practical_batches.id"), nullable=True, index=True) # None for whole-class
    
    day_index = Column(Integer, index=True) # 0=Monday
    period_index = Column(Integer, index=True) # starting period index
    duration_periods = Column(Integer, default=1) # 1 for theory, 2+ for lab
    session_type = Column(String(20), default="THEORY") # "THEORY", "PRACTICAL"
    
    is_locked = Column(Boolean, default=False) # if True, solver must not move this session
    is_fixed_commitment = Column(Boolean, default=False)

    timetable = relationship("Timetable", back_populates="sessions")
    subject = relationship("Subject")
    faculty = relationship("Faculty")
    room = relationship("Room")
    section = relationship("Section")
    batch = relationship("PracticalBatch")
