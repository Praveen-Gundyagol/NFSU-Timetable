from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Programme(Base):
    __tablename__ = "programmes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True) # "BT-CS", "MS-DFS"
    name = Column(String(100)) # "B.Tech Cyber Security", "M.Sc Digital Forensics"
    department = Column(String(100)) # "School of Cyber Security & Digital Forensics"

    semesters = relationship("Semester", back_populates="programme", cascade="all, delete-orphan")

class Semester(Base):
    __tablename__ = "semesters"

    id = Column(Integer, primary_key=True, index=True)
    programme_id = Column(Integer, ForeignKey("programmes.id"), index=True)
    semester_number = Column(Integer) # e.g. 4 for 4th Semester

    programme = relationship("Programme", back_populates="semesters")
    sections = relationship("Section", back_populates="semester", cascade="all, delete-orphan")
    subjects = relationship("Subject", back_populates="semester", cascade="all, delete-orphan")

class Section(Base):
    __tablename__ = "sections"

    id = Column(Integer, primary_key=True, index=True)
    semester_id = Column(Integer, ForeignKey("semesters.id"), index=True)
    name = Column(String(20)) # "A", "B"
    total_strength = Column(Integer, default=60)

    semester = relationship("Semester", back_populates="sections")
    batches = relationship("PracticalBatch", back_populates="section", cascade="all, delete-orphan")

class PracticalBatch(Base):
    __tablename__ = "practical_batches"

    id = Column(Integer, primary_key=True, index=True)
    section_id = Column(Integer, ForeignKey("sections.id"), index=True)
    name = Column(String(20)) # "B1", "B2"
    batch_strength = Column(Integer, default=30)

    section = relationship("Section", back_populates="batches")
