from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True) # e.g. "CR-101", "LAB-DFS"
    name = Column(String(100)) # e.g. "Lecture Hall 101", "Digital Forensics Lab"
    room_type = Column(String(50), default="CLASSROOM") # "CLASSROOM", "LAB_COMPUTER", "LAB_FORENSIC", "LAB_CYBER"
    capacity = Column(Integer, default=60)
    is_active = Column(Boolean, default=True)
    unavailable_slots_json = Column(Text, default="[]") # JSON list of [day_index, period_index]

class Faculty(Base):
    __tablename__ = "faculty"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(50), unique=True, index=True)
    name = Column(String(100))
    email = Column(String(100))
    department = Column(String(100))
    max_weekly_periods = Column(Integer, default=16)
    max_daily_periods = Column(Integer, default=4)
    is_active = Column(Boolean, default=True)

    availabilities = relationship("FacultyAvailability", back_populates="faculty", cascade="all, delete-orphan")

class FacultyAvailability(Base):
    __tablename__ = "faculty_availabilities"

    id = Column(Integer, primary_key=True, index=True)
    faculty_id = Column(Integer, ForeignKey("faculty.id"), index=True)
    day_index = Column(Integer, index=True)
    period_index = Column(Integer, index=True)
    status = Column(String(30), default="AVAILABLE") # "AVAILABLE", "UNAVAILABLE", "FIXED_COMMITMENT"
    note = Column(String(200), nullable=True)

    faculty = relationship("Faculty", back_populates="availabilities")
