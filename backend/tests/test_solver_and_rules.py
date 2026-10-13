import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def setup_module():
    """Seed the sample database before running solver tests."""
    client.post("/api/academic/seed-sample-data")

def test_full_timetable_generation_and_hard_constraints():
    """Verify that OR-Tools CP-SAT generates a 100% valid, clash-free schedule."""
    gen_res = client.post("/api/timetable/generate", json={"time_limit_seconds": 15})
    assert gen_res.status_code == 200
    tt = gen_res.json()
    assert tt["solver_status"] in ("OPTIMAL", "FEASIBLE")
    sessions = tt["sessions"]
    assert len(sessions) > 0

    # 1. Verify NO session spans lunch break (period 4)
    for s in sessions:
        dur = s["duration_periods"]
        start_p = s["period_index"]
        for p in range(start_p, start_p + dur):
            assert p != 4, f"Session {s['subject_name']} spans break period 4!"

    # 2. Verify NO faculty clashes
    fac_slots = {}
    for s in sessions:
        dur = s["duration_periods"]
        for p in range(s["period_index"], s["period_index"] + dur):
            key = (s["faculty_id"], s["day_index"], p)
            assert key not in fac_slots, f"Faculty clash for faculty {s['faculty_name']} at Day {s['day_index']}, Period {p}!"
            fac_slots[key] = s["id"]

    # 3. Verify NO room clashes
    room_slots = {}
    for s in sessions:
        dur = s["duration_periods"]
        for p in range(s["period_index"], s["period_index"] + dur):
            key = (s["room_id"], s["day_index"], p)
            assert key not in room_slots, f"Room clash for room {s['room_name']} at Day {s['day_index']}, Period {p}!"
            room_slots[key] = s["id"]

    # 4. Verify Requirements 6 & 7: Whole-class theory does not overlap with batch practicals
    # And batch practicals for the same batch do not overlap
    for day in range(5):
        for p in range(7):
            active_sessions = [
                s for s in sessions
                if s["day_index"] == day and s["period_index"] <= p < s["period_index"] + s["duration_periods"]
            ]
            by_sec = {}
            for s in active_sessions:
                sec_id = s["section_id"]
                if sec_id not in by_sec:
                    by_sec[sec_id] = []
                by_sec[sec_id].append(s)

            for sec_id, sec_active in by_sec.items():
                whole = [s for s in sec_active if s["batch_id"] is None]
                batches = [s for s in sec_active if s["batch_id"] is not None]
                if whole:
                    assert len(whole) == 1, "Multiple whole-class sessions for same section at same slot!"
                    assert len(batches) == 0, "Whole-class session overlapped with batch session!"
                
                # Check that no batch has 2 sessions
                batch_ids = [s["batch_id"] for s in batches]
                assert len(batch_ids) == len(set(batch_ids)), "Batch has multiple sessions at same slot!"

def test_session_locking_and_regeneration():
    """Verify that locking a session preserves its exact slot upon timetable regeneration."""
    latest_tt = client.get("/api/timetable/latest").json()
    assert len(latest_tt["sessions"]) > 0
    target_session = latest_tt["sessions"][0]
    
    # Lock the session
    lock_res = client.post("/api/timetable/sessions/lock", json={
        "session_id": target_session["id"],
        "is_locked": True
    })
    assert lock_res.status_code == 200

    # Regenerate timetable
    regen_res = client.post("/api/timetable/generate", json={"time_limit_seconds": 15})
    assert regen_res.status_code == 200
    regen_tt = regen_res.json()

    # Find the session corresponding to the same subject, section, and batch
    matching = [
        s for s in regen_tt["sessions"]
        if s["subject_id"] == target_session["subject_id"]
        and s["section_id"] == target_session["section_id"]
        and s["batch_id"] == target_session["batch_id"]
        and s["session_type"] == target_session["session_type"]
        and s["is_locked"] == True
    ]
    assert len(matching) >= 1
    locked_instance = matching[0]
    assert locked_instance["day_index"] == target_session["day_index"]
    assert locked_instance["period_index"] == target_session["period_index"]
    assert locked_instance["room_id"] == target_session["room_id"]

def test_manual_move_validation():
    """Verify that manual move validator catches hard constraint conflicts."""
    latest_tt = client.get("/api/timetable/latest").json()
    session = latest_tt["sessions"][0]

    # Test 1: Moving into Lunch Break (Period 4)
    val_break = client.post("/api/timetable/validate-move", json={
        "timetable_id": latest_tt["id"],
        "session_id": session["id"],
        "target_day": session["day_index"],
        "target_period": 4, # Lunch Break
        "target_room_id": session["room_id"]
    }).json()
    assert val_break["valid"] is False
    assert any(c["conflict_type"] == "BREAK_OVERLAP" for c in val_break["conflicts"])

    # Test 2: Moving into a slot that creates a faculty clash
    # Find another session taught by a different faculty
    other = next(s for s in latest_tt["sessions"] if s["faculty_id"] != session["faculty_id"])
    # Move session into other session's slot
    val_fac = client.post("/api/timetable/validate-move", json={
        "timetable_id": latest_tt["id"],
        "session_id": session["id"],
        "target_day": other["day_index"],
        "target_period": other["period_index"],
        "target_room_id": other["room_id"]
    }).json()
    # It should detect room clash (since same room) or group clash
    assert val_fac["valid"] is False

def test_infeasibility_reporting_on_impossible_schedule():
    """Verify that an impossible faculty availability returns INFEASIBLE with plain explanation."""
    # Temporarily make a faculty member unavailable for all 35 slots
    fac_list = client.get("/api/resources/faculty").json()
    target_fac = fac_list[0]
    
    all_slots = []
    for d in range(5):
        for p in range(7):
            all_slots.append({"day_index": d, "period_index": p, "status": "UNAVAILABLE", "note": "Blocked"})

    client.post("/api/resources/faculty/availability", json={
        "faculty_id": target_fac["id"],
        "availabilities": all_slots
    })

    # Try generating timetable
    res = client.post("/api/timetable/generate", json={"time_limit_seconds": 5})
    assert res.status_code == 200
    tt = res.json()
    assert tt["solver_status"] == "INFEASIBLE"
    assert tt["infeasibility_report"] is not None
    assert len(tt["infeasibility_report"]["conflict_explanations"]) > 0
    # Explanation must mention the faculty
    explanations_text = " ".join(tt["infeasibility_report"]["conflict_explanations"])
    assert target_fac["name"] in explanations_text or "available" in explanations_text

    # Verify that trying to publish an infeasible timetable is rejected with 400
    pub_res = client.post(f"/api/timetable/publish?timetable_id={tt['id']}")
    assert pub_res.status_code == 400

    # Reset sample data
    client.post("/api/academic/seed-sample-data")

def test_csv_export():
    """Verify that timetable can be exported to CSV format."""
    # Generate fresh valid timetable
    gen_res = client.post("/api/timetable/generate", json={"time_limit_seconds": 15})
    tt_id = gen_res.json()["id"]

    csv_res = client.get(f"/api/timetable/export/csv?timetable_id={tt_id}")
    assert csv_res.status_code == 200
    assert "text/csv" in csv_res.headers["content-type"]
    csv_text = csv_res.text
    assert "Subject Code" in csv_text
    assert "Faculty" in csv_text
