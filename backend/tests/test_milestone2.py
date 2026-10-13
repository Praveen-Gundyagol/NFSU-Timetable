import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_config_and_time_slots():
    """Verify university configuration and automatic time slot generation."""
    response = client.get("/api/config")
    assert response.status_code == 200
    config_data = response.json()
    assert config_data["periods_per_day"] == 7
    assert len(config_data["working_days"]) == 5 # Mon-Fri
    assert 4 in config_data["break_periods"] # Lunch break

    # Verify generated slots
    slots_res = client.get("/api/config/slots")
    assert slots_res.status_code == 200
    slots = slots_res.json()
    # 5 days * 7 periods = 35 slots
    assert len(slots) == 35
    # Period 4 on each day must be flagged as break
    break_slots = [s for s in slots if s["is_break"]]
    assert len(break_slots) == 5

def test_room_crud():
    """Verify Room creation and duplicate rejection."""
    # Create room
    res = client.post("/api/resources/rooms", json={
        "code": "TEST-LAB-01",
        "name": "Test Forensic Lab",
        "room_type": "LAB_FORENSIC",
        "capacity": 40,
        "is_active": True,
        "unavailable_slots": [[0, 0]]
    })
    assert res.status_code == 200
    data = res.json()
    assert data["code"] == "TEST-LAB-01"
    assert data["capacity"] == 40
    assert data["unavailable_slots"] == [[0, 0]]

    # Duplicate code rejection
    dup = client.post("/api/resources/rooms", json={
        "code": "TEST-LAB-01",
        "name": "Another Room",
        "room_type": "CLASSROOM",
        "capacity": 50,
        "is_active": True,
        "unavailable_slots": []
    })
    assert dup.status_code == 400

def test_faculty_and_availability():
    """Verify Faculty creation and availability matrix updates."""
    fac_res = client.post("/api/resources/faculty", json={
        "employee_id": "TEST-FAC-99",
        "name": "Dr. Testing",
        "email": "test@nfsu.ac.in",
        "department": "Cyber Security",
        "max_weekly_periods": 14,
        "max_daily_periods": 3,
        "is_active": True
    })
    assert fac_res.status_code == 200
    faculty_id = fac_res.json()["id"]

    # Update availability
    avail_res = client.post("/api/resources/faculty/availability", json={
        "faculty_id": faculty_id,
        "availabilities": [
            {"day_index": 0, "period_index": 1, "status": "UNAVAILABLE", "note": "HOD Meeting"},
            {"day_index": 1, "period_index": 2, "status": "FIXED_COMMITMENT", "note": "Research Advisory"}
        ]
    })
    assert avail_res.status_code == 200

def test_seed_sample_data():
    """Verify that the realistic NFSU department sample data seeds cleanly."""
    res = client.post("/api/academic/seed-sample-data")
    assert res.status_code == 200
    assert res.json()["status"] == "success"

    # Verify rooms seeded
    rooms = client.get("/api/resources/rooms").json()
    assert len(rooms) >= 5

    # Verify faculty seeded
    faculty = client.get("/api/resources/faculty").json()
    assert len(faculty) >= 5

    # Verify programmes and subjects seeded
    programmes = client.get("/api/academic/programmes").json()
    assert len(programmes) >= 2

    subjects = client.get("/api/academic/subjects").json()
    assert len(subjects) >= 7
