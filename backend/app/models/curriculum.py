from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    semester_id = Column(Integer, ForeignKey("semesters.id"), index=True)
    code = Column(String(50), index=True) # "CS401", "DFS202"
    name = Column(String(100))
    subject_type = Column(String(30), default="INTEGRATED") # "THEORY_ONLY", "PRACTICAL_ONLY", "INTEGRATED"
    weekly_theory_periods = Column(Integer, default=3)
    weekly_practical_sessions = Column(Integer, default=1) # number of practical blocks per batch per week
    practical_duration_periods = Column(Integer, default=2) # consecutive periods (e.g. 2 periods)
    required_room_type = Column(String(50), default="CLASSROOM") # "CLASSROOM", "LAB_COMPUTER", "LAB_FORENSIC"
    preferred_room_id = Column(Integer, ForeignKey("rooms.id"), nullable=True)

    semester = relationship("Semester", back_populates="subjects")
    faculty_assignments = relationship("SubjectFacultyAssignment", back_populates="subject", cascade="all, delete-orphan")

class SubjectFacultyAssignment(Base):
    __tablename__ = "subject_faculty_assignments"

    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), index=True)
    faculty_id = Column(Integer, ForeignKey("faculty.id"), index=True)
    component = Column(String(20), default="THEORY") # "THEORY", "PRACTICAL"
    batch_id = Column(Integer, ForeignKey("practical_batches.id"), nullable=True) # if assigned to specific batch

    subject = relationship("Subject", back_populates="faculty_assignments")
    faculty = relationship("Faculty")
    batch = relationship("PracticalBatch")
