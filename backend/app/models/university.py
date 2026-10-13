from sqlalchemy import Column, Integer, String, Boolean, Text
from app.database import Base

class InstitutionConfig(Base):
    __tablename__ = "institution_configs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), default="National Forensic Sciences University")
    # JSON list of days: 0=Mon, 1=Tue, 2=Wed, 3=Thu, 4=Fri, 5=Sat
    working_days_json = Column(Text, default="[0, 1, 2, 3, 4]")
    periods_per_day = Column(Integer, default=7)
    period_duration_minutes = Column(Integer, default=60)
    start_time = Column(String(10), default="09:00")
    # JSON list of period indices that are breaks, e.g. [4] for lunch break
    break_periods_json = Column(Text, default="[4]")

class TimeSlot(Base):
    __tablename__ = "time_slots"

    id = Column(Integer, primary_key=True, index=True)
    day_index = Column(Integer, index=True) # 0=Monday
    period_index = Column(Integer, index=True) # 0=first period
    start_time = Column(String(10)) # "09:00"
    end_time = Column(String(10)) # "10:00"
    is_break = Column(Boolean, default=False)
