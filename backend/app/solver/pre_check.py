from typing import List, Tuple
from app.solver.schemas import SolverInput

def run_pre_solver_checks(input_data: SolverInput) -> Tuple[bool, List[str]]:
    """Performs deterministic sanity checks before CP-SAT solver starts.
    Returns (is_viable, list_of_error_messages).
    """
    errors: List[str] = []
    
    total_teaching_slots_per_day = input_data.periods_per_day - len(input_data.break_periods)
    total_week_slots = len(input_data.working_days) * total_teaching_slots_per_day

    # 1. Check if university schedule has any teaching slots
    if total_week_slots <= 0:
        errors.append("No active teaching slots available in university schedule.")

    # 2. Check room capacity and room type sufficiency
    for task in input_data.tasks:
        required_strength = task.batch_strength if task.batch_id else task.section_strength
        matching_rooms = [
            r for r in input_data.rooms
            if r.is_active and r.capacity >= required_strength
            and (task.session_type != "PRACTICAL" or r.room_type == task.required_room_type)
        ]
        if not matching_rooms:
            target_desc = f"Batch {task.batch_name}" if task.batch_name else f"Section {task.section_name}"
            req_type_desc = f"with type '{task.required_room_type}'" if task.session_type == "PRACTICAL" else "classroom"
            errors.append(
                f"No suitable room available for {task.subject_name} ({target_desc}): "
                f"Needs {req_type_desc} with capacity >= {required_strength}."
            )

    # 3. Check faculty workload vs available slots
    faculty_dict = {f.id: f for f in input_data.faculty}
    faculty_required_hours: dict = {}
    for task in input_data.tasks:
        faculty_required_hours[task.faculty_id] = (
            faculty_required_hours.get(task.faculty_id, 0) + task.duration_periods
        )

    for fac_id, req_hours in faculty_required_hours.items():
        fac = faculty_dict.get(fac_id)
        if not fac:
            continue
        
        # Unavailable slots that fall on active teaching periods
        unavail_count = len([
            slot for slot in fac.unavailable_slots
            if slot[0] in input_data.working_days and slot[1] not in input_data.break_periods
        ])
        available_slots = total_week_slots - unavail_count

        if req_hours > available_slots:
            errors.append(
                f"Faculty '{fac.name}' is assigned {req_hours} teaching periods, but is only "
                f"available for {available_slots} periods across the week ({unavail_count} unavailable slots)."
            )

    # 4. Check for conflicting locked sessions / fixed commitments
    locked_room_slots = {}
    locked_fac_slots = {}
    locked_group_slots = {}

    for task in input_data.tasks:
        if task.is_locked and task.locked_day is not None and task.locked_period is not None:
            day = task.locked_day
            start_p = task.locked_period
            
            for p in range(start_p, start_p + task.duration_periods):
                # Check break clash
                if p in input_data.break_periods:
                    errors.append(
                        f"Locked session '{task.subject_name}' ({task.section_name}) spans break period {p} on Day {day}."
                    )
                
                # Check room clash
                if task.locked_room_id:
                    key = (task.locked_room_id, day, p)
                    if key in locked_room_slots:
                        errors.append(
                            f"Conflicting locked sessions for Room ID {task.locked_room_id} on Day {day}, Period {p}: "
                            f"'{task.subject_name}' clashes with '{locked_room_slots[key]}'."
                        )
                    else:
                        locked_room_slots[key] = task.subject_name

                # Check faculty clash
                fac_key = (task.faculty_id, day, p)
                if fac_key in locked_fac_slots:
                    errors.append(
                        f"Conflicting locked sessions for Faculty '{task.faculty_name}' on Day {day}, Period {p}: "
                        f"'{task.subject_name}' clashes with '{locked_fac_slots[fac_key]}'."
                    )
                else:
                    locked_fac_slots[fac_key] = task.subject_name

                # Check group clash (whole class vs batch or same batch)
                group_key = (task.section_id, task.batch_id, day, p)
                if group_key in locked_group_slots:
                    errors.append(
                        f"Conflicting locked sessions for Section '{task.section_name}' on Day {day}, Period {p}: "
                        f"'{task.subject_name}' clashes with '{locked_group_slots[group_key]}'."
                    )
                else:
                    locked_group_slots[group_key] = task.subject_name

    # Deduplicate errors
    unique_errors = list(dict.fromkeys(errors))
    return (len(unique_errors) == 0, unique_errors)
