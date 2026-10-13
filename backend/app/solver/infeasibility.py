from typing import List
from app.solver.schemas import SolverInput, ScheduledSlot, SessionTask

def generate_conflict_explanations(
    input_data: SolverInput,
    scheduled: List[ScheduledSlot],
    unscheduled: List[SessionTask]
) -> List[str]:
    """Generates human-readable explanations of why sessions could not be scheduled."""
    explanations: List[str] = []

    # Build occupation maps from the scheduled sessions
    fac_occupied = set() # (faculty_id, day, p)
    room_occupied = set() # (room_id, day, p)
    sec_occupied = set() # (section_id, day, p)
    batch_occupied = set() # (batch_id, day, p)

    for s in scheduled:
        for p in range(s.period_index, s.period_index + s.duration_periods):
            fac_occupied.add((s.faculty_id, s.day_index, p))
            room_occupied.add((s.room_id, s.day_index, p))
            sec_occupied.add((s.section_id, s.day_index, p))
            if s.batch_id:
                batch_occupied.add((s.batch_id, s.day_index, p))

    fac_unavail = {
        (f.id, slot[0], slot[1])
        for f in input_data.faculty
        for slot in f.unavailable_slots
    }
    break_set = set(input_data.break_periods)
    room_dict = {r.id: r for r in input_data.rooms if r.is_active}

    for task in unscheduled:
        target_name = f"Batch {task.batch_name}" if task.batch_id else f"Section {task.section_name}"
        reasons = []

        # Find matching rooms
        req_strength = task.batch_strength if task.batch_id else task.section_strength
        valid_rooms = [
            r for r in room_dict.values()
            if r.capacity >= req_strength
            and (task.session_type != "PRACTICAL" or r.room_type == task.required_room_type)
        ]

        if not valid_rooms:
            reasons.append(
                f"No active room with type '{task.required_room_type}' and capacity >= {req_strength} exists."
            )
        else:
            # Check slot availability across the week
            possible_slots_count = 0
            faculty_blocked_count = 0
            room_blocked_count = 0
            class_blocked_count = 0

            for day in input_data.working_days:
                for start_p in range(input_data.periods_per_day):
                    end_p = start_p + task.duration_periods
                    if end_p > input_data.periods_per_day:
                        continue
                    if any(p in break_set for p in range(start_p, end_p)):
                        continue

                    possible_slots_count += 1

                    # Check faculty
                    fac_busy = any(
                        (task.faculty_id, day, p) in fac_occupied or (task.faculty_id, day, p) in fac_unavail
                        for p in range(start_p, end_p)
                    )
                    if fac_busy:
                        faculty_blocked_count += 1
                        continue

                    # Check section / batch
                    class_busy = False
                    for p in range(start_p, end_p):
                        if (task.section_id, day, p) in sec_occupied:
                            class_busy = True
                            break
                        if task.batch_id and (task.batch_id, day, p) in batch_occupied:
                            class_busy = True
                            break
                    if class_busy:
                        class_blocked_count += 1
                        continue

                    # Check room
                    any_room_free = False
                    for r in valid_rooms:
                        if not any((r.id, day, p) in room_occupied for p in range(start_p, end_p)):
                            any_room_free = True
                            break
                    if not any_room_free:
                        room_blocked_count += 1

            if faculty_blocked_count >= (possible_slots_count * 0.7):
                reasons.append(
                    f"Faculty '{task.faculty_name}' was unavailable or teaching other classes during {faculty_blocked_count}/{possible_slots_count} candidate slots."
                )
            if class_blocked_count >= (possible_slots_count * 0.7):
                reasons.append(
                    f"Students of {target_name} already had conflicting lectures or practicals during {class_blocked_count}/{possible_slots_count} candidate slots."
                )
            if room_blocked_count >= (possible_slots_count * 0.7):
                reasons.append(
                    f"Required rooms were occupied during {room_blocked_count}/{possible_slots_count} candidate slots."
                )

        reason_str = "; ".join(reasons) if reasons else "Severe schedule resource contention across faculty, rooms, and batches."
        explanations.append(
            f"Unscheduled: {task.subject_name} ({task.session_type}, {task.duration_periods} periods) for {target_name} with {task.faculty_name}. Conflict reason: {reason_str}"
        )

    return explanations
