import json
from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.university import InstitutionConfig, TimeSlot
from app.schemas.university import InstitutionConfigCreate, InstitutionConfigOut, TimeSlotOut

router = APIRouter(prefix="/api/config", tags=["Configuration"])

def regenerate_time_slots(db: Session, config: InstitutionConfig):
    """Regenerates the complete TimeSlot matrix based on working days and periods."""
    db.query(TimeSlot).delete()
    
    working_days = json.loads(config.working_days_json)
    break_periods = json.loads(config.break_periods_json)
    
    # Calculate start times
    start_dt = datetime.strptime(config.start_time, "%H:%M")
    duration = timedelta(minutes=config.period_duration_minutes)
    
    slots = []
    for day in working_days:
        current_time = start_dt
        for p in range(config.periods_per_day):
            end_time = current_time + duration
            is_break = (p in break_periods)
            slot = TimeSlot(
                day_index=day,
                period_index=p,
                start_time=current_time.strftime("%H:%M"),
                end_time=end_time.strftime("%H:%M"),
                is_break=is_break
            )
            slots.append(slot)
            current_time = end_time
            
    db.add_all(slots)
    db.commit()

@router.get("", response_model=InstitutionConfigOut)
def get_config(db: Session = Depends(get_db)):
    config = db.query(InstitutionConfig).first()
    if not config:
        config = InstitutionConfig()
        db.add(config)
        db.commit()
        db.refresh(config)
        regenerate_time_slots(db, config)
    
    return InstitutionConfigOut(
        id=config.id,
        name=config.name,
        working_days=json.loads(config.working_days_json),
        periods_per_day=config.periods_per_day,
        period_duration_minutes=config.period_duration_minutes,
        start_time=config.start_time,
        break_periods=json.loads(config.break_periods_json)
    )

@router.put("", response_model=InstitutionConfigOut)
def update_config(payload: InstitutionConfigCreate, db: Session = Depends(get_db)):
    config = db.query(InstitutionConfig).first()
    if not config:
        config = InstitutionConfig()
        db.add(config)

    config.name = payload.name
    config.working_days_json = json.dumps(payload.working_days)
    config.periods_per_day = payload.periods_per_day
    config.period_duration_minutes = payload.period_duration_minutes
    config.start_time = payload.start_time
    config.break_periods_json = json.dumps(payload.break_periods)
    
    db.commit()
    db.refresh(config)
    regenerate_time_slots(db, config)

    return InstitutionConfigOut(
        id=config.id,
        name=config.name,
        working_days=json.loads(config.working_days_json),
        periods_per_day=config.periods_per_day,
        period_duration_minutes=config.period_duration_minutes,
        start_time=config.start_time,
        break_periods=json.loads(config.break_periods_json)
    )

@router.get("/slots", response_model=List[TimeSlotOut])
def get_slots(db: Session = Depends(get_db)):
    return db.query(TimeSlot).order_by(TimeSlot.day_index, TimeSlot.period_index).all()
