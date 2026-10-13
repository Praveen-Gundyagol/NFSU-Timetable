import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.resources import Room, Faculty, FacultyAvailability
from app.schemas.resources import (
    RoomCreate, RoomOut, FacultyCreate, FacultyOut,
    FacultyAvailabilityBatchUpdate, FacultyAvailabilityOut
)

router = APIRouter(prefix="/api/resources", tags=["Resources"])

# --- Rooms Endpoints ---
@router.get("/rooms", response_model=List[RoomOut])
def get_rooms(db: Session = Depends(get_db)):
    rooms = db.query(Room).all()
    results = []
    for r in rooms:
        results.append(RoomOut(
            id=r.id,
            code=r.code,
            name=r.name,
            room_type=r.room_type,
            capacity=r.capacity,
            is_active=r.is_active,
            unavailable_slots=json.loads(r.unavailable_slots_json) if r.unavailable_slots_json else []
        ))
    return results

@router.post("/rooms", response_model=RoomOut)
def create_room(payload: RoomCreate, db: Session = Depends(get_db)):
    existing = db.query(Room).filter(Room.code == payload.code).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Room with code '{payload.code}' already exists.")
    
    room = Room(
        code=payload.code,
        name=payload.name,
        room_type=payload.room_type,
        capacity=payload.capacity,
        is_active=payload.is_active,
        unavailable_slots_json=json.dumps(payload.unavailable_slots)
    )
    db.add(room)
    db.commit()
    db.refresh(room)
    return RoomOut(
        id=room.id,
        code=room.code,
        name=room.name,
        room_type=room.room_type,
        capacity=room.capacity,
        is_active=room.is_active,
        unavailable_slots=payload.unavailable_slots
    )

@router.delete("/rooms/{room_id}")
def delete_room(room_id: int, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found.")
    db.delete(room)
    db.commit()
    return {"message": f"Room {room.code} deleted successfully."}

# --- Faculty Endpoints ---
@router.get("/faculty", response_model=List[FacultyOut])
def get_faculty(db: Session = Depends(get_db)):
    faculty_list = db.query(Faculty).all()
    results = []
    for f in faculty_list:
        avails = [
            FacultyAvailabilityOut(
                id=a.id,
                faculty_id=a.faculty_id,
                day_index=a.day_index,
                period_index=a.period_index,
                status=a.status,
                note=a.note
            )
            for a in f.availabilities
        ]
        results.append(FacultyOut(
            id=f.id,
            employee_id=f.employee_id,
            name=f.name,
            email=f.email,
            department=f.department,
            max_weekly_periods=f.max_weekly_periods,
            max_daily_periods=f.max_daily_periods,
            is_active=f.is_active,
            availabilities=avails
        ))
    return results

@router.post("/faculty", response_model=FacultyOut)
def create_faculty(payload: FacultyCreate, db: Session = Depends(get_db)):
    existing = db.query(Faculty).filter(Faculty.employee_id == payload.employee_id).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Faculty with ID '{payload.employee_id}' already exists.")
    
    faculty = Faculty(
        employee_id=payload.employee_id,
        name=payload.name,
        email=payload.email,
        department=payload.department,
        max_weekly_periods=payload.max_weekly_periods,
        max_daily_periods=payload.max_daily_periods,
        is_active=payload.is_active
    )
    db.add(faculty)
    db.commit()
    db.refresh(faculty)
    return FacultyOut(
        id=faculty.id,
        employee_id=faculty.employee_id,
        name=faculty.name,
        email=faculty.email,
        department=faculty.department,
        max_weekly_periods=faculty.max_weekly_periods,
        max_daily_periods=faculty.max_daily_periods,
        is_active=faculty.is_active,
        availabilities=[]
    )

@router.post("/faculty/availability")
def update_faculty_availability(payload: FacultyAvailabilityBatchUpdate, db: Session = Depends(get_db)):
    faculty = db.query(Faculty).filter(Faculty.id == payload.faculty_id).first()
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty not found.")
    
    # Remove existing
    db.query(FacultyAvailability).filter(FacultyAvailability.faculty_id == payload.faculty_id).delete()
    
    new_avails = [
        FacultyAvailability(
            faculty_id=payload.faculty_id,
            day_index=a.day_index,
            period_index=a.period_index,
            status=a.status,
            note=a.note
        )
        for a in payload.availabilities
    ]
    db.add_all(new_avails)
    db.commit()
    return {"message": "Faculty availability updated successfully.", "count": len(new_avails)}
