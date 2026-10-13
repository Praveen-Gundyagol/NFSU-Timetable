import time
from typing import Dict, List, Tuple
from ortools.sat.python import cp_model
from app.solver.schemas import (
    SolverInput, SolverOutput, SessionTask, ScheduledSlot, RoomData, FacultyData
)
from app.solver.pre_check import run_pre_solver_checks

def solve_timetable(input_data: SolverInput, allow_slack: bool = False) -> SolverOutput:
    """Builds and executes the CP-SAT model for university timetable scheduling."""
    start_time = time.time()
    
    # Run pre-solver sanity checks
    is_viable, pre_errors = run_pre_solver_checks(input_data)
    if not is_viable and not allow_slack:
        return SolverOutput(
            status="INFEASIBLE",
            unscheduled_sessions=input_data.tasks,
            conflict_explanations=pre_errors,
            solver_time_seconds=time.time() - start_time
        )

    model = cp_model.CpModel()
    
    # Lookup dictionaries
    room_dict: Dict[int, RoomData] = {r.id: r for r in input_data.rooms if r.is_active}
    faculty_dict: Dict[int, FacultyData] = {f.id: f for f in input_data.faculty}
    
    # Precompute unavailable slot sets for fast lookup
    fac_unavail_set = {
        (f.id, slot[0], slot[1])
        for f in input_data.faculty
        for slot in f.unavailable_slots
    }
    room_unavail_set = {
        (r.id, slot[0], slot[1])
        for r in input_data.rooms
        for slot in r.unavailable_slots
    }
    break_set = set(input_data.break_periods)

    # Decision variables: task_vars[task.id][(d, p, r)] = BoolVar
    task_vars: Dict[str, Dict[Tuple[int, int, int], cp_model.IntVar]] = {}
    slack_vars: Dict[str, cp_model.IntVar] = {}

    for task in input_data.tasks:
        task_vars[task.id] = {}
        required_strength = task.batch_strength if task.batch_id else task.section_strength

        # Determine valid rooms
        if task.is_locked and task.locked_room_id is not None:
            valid_rooms = [room_dict[task.locked_room_id]] if task.locked_room_id in room_dict else []
        else:
            valid_rooms = [
                r for r in room_dict.values()
                if r.capacity >= required_strength
                and (task.session_type != "PRACTICAL" or r.room_type == task.required_room_type)
            ]

        # Determine valid start slots
        for day in input_data.working_days:
            # If locked, only allow locked day
            if task.is_locked and task.locked_day is not None and task.locked_day != day:
                continue

            for start_p in range(input_data.periods_per_day):
                # If locked, only allow locked period
                if task.is_locked and task.locked_period is not None and task.locked_period != start_p:
                    continue

                end_p = start_p + task.duration_periods
                if end_p > input_data.periods_per_day:
                    continue # Exceeds end of working day

                # Check if any period in [start_p, end_p - 1] intersects break periods
                spans_break = any(p in break_set for p in range(start_p, end_p))
                if spans_break:
                    continue

                # Check faculty availability across [start_p, end_p - 1]
                fac_busy = any((task.faculty_id, day, p) in fac_unavail_set for p in range(start_p, end_p))
                if fac_busy:
                    continue

                # Generate variable for each valid room
                for r in valid_rooms:
                    room_busy = any((r.id, day, p) in room_unavail_set for p in range(start_p, end_p))
                    if room_busy:
                        continue

                    var_name = f"x_{task.id}_{day}_{start_p}_{r.id}"
                    var = model.NewBoolVar(var_name)
                    task_vars[task.id][(day, start_p, r.id)] = var

        # Assignment constraint
        candidate_vars = list(task_vars[task.id].values())
        if allow_slack:
            slack_var = model.NewBoolVar(f"unscheduled_{task.id}")
            slack_vars[task.id] = slack_var
            model.Add(sum(candidate_vars) + slack_var == 1)
        else:
            if not candidate_vars:
                # No valid slots mathematically exist for this session
                return SolverOutput(
                    status="INFEASIBLE",
                    unscheduled_sessions=[task],
                    conflict_explanations=[
                        f"Session {task.subject_name} ({task.section_name}) has 0 mathematically valid candidate slots."
                    ],
                    solver_time_seconds=time.time() - start_time
                )
            model.Add(sum(candidate_vars) == 1)

    # --- 1. HARD CONSTRAINT: Room No-Overlap ---
    for r_id in room_dict.keys():
        for day in input_data.working_days:
            for p in range(input_data.periods_per_day):
                if p in break_set:
                    continue
                occupying_vars = []
                for task in input_data.tasks:
                    dur = task.duration_periods
                    for start_p in range(max(0, p - dur + 1), p + 1):
                        if (day, start_p, r_id) in task_vars[task.id]:
                            occupying_vars.append(task_vars[task.id][(day, start_p, r_id)])
                if occupying_vars:
                    model.Add(sum(occupying_vars) <= 1)

    # --- 2. HARD CONSTRAINT: Faculty No-Overlap ---
    for fac_id in faculty_dict.keys():
        for day in input_data.working_days:
            for p in range(input_data.periods_per_day):
                if p in break_set:
                    continue
                fac_vars = []
                for task in input_data.tasks:
                    if task.faculty_id != fac_id:
                        continue
                    dur = task.duration_periods
                    for start_p in range(max(0, p - dur + 1), p + 1):
                        for r_id in room_dict.keys():
                            if (day, start_p, r_id) in task_vars[task.id]:
                                fac_vars.append(task_vars[task.id][(day, start_p, r_id)])
                if fac_vars:
                    model.Add(sum(fac_vars) <= 1)

    # --- 3. HARD CONSTRAINT: Section & Practical Batch Non-Overlap ---
    # Requirements 6 & 7: Whole-class sessions cannot overlap with practicals
    # of students from that class; practicals for different batches CAN run simultaneously.
    sections_set = {task.section_id for task in input_data.tasks}
    for sec_id in sections_set:
        sec_tasks = [t for t in input_data.tasks if t.section_id == sec_id]
        whole_class_tasks = [t for t in sec_tasks if t.batch_id is None]
        batch_tasks = [t for t in sec_tasks if t.batch_id is not None]
        batch_ids = {t.batch_id for t in batch_tasks}

        for day in input_data.working_days:
            for p in range(input_data.periods_per_day):
                if p in break_set:
                    continue
                
                # Active whole-class variables at (day, p)
                whole_vars = []
                for t in whole_class_tasks:
                    dur = t.duration_periods
                    for start_p in range(max(0, p - dur + 1), p + 1):
                        for r_id in room_dict.keys():
                            if (day, start_p, r_id) in task_vars[t.id]:
                                whole_vars.append(task_vars[t.id][(day, start_p, r_id)])

                # At most 1 whole class session at (day, p)
                if whole_vars:
                    model.Add(sum(whole_vars) <= 1)

                # For each batch, at most 1 session for that batch at (day, p)
                # AND whole class cannot overlap with that batch
                for b_id in batch_ids:
                    b_vars = []
                    for t in batch_tasks:
                        if t.batch_id != b_id:
                            continue
                        dur = t.duration_periods
                        for start_p in range(max(0, p - dur + 1), p + 1):
                            for r_id in room_dict.keys():
                                if (day, start_p, r_id) in task_vars[t.id]:
                                    b_vars.append(task_vars[t.id][(day, start_p, r_id)])

                    # Single batch can only have 1 active session
                    if b_vars:
                        model.Add(sum(b_vars) <= 1)

                    # Whole class cannot overlap with batch session!
                    if whole_vars and b_vars:
                        model.Add(sum(whole_vars) + sum(b_vars) <= 1)

    # --- 4. OBJECTIVE FUNCTION: Preferences & Optimization ---
    penalties = []
    
    # Slack penalty: 1,000,000 per unscheduled session if slack allowed
    if allow_slack:
        for slack_var in slack_vars.values():
            penalties.append(slack_var * 1000000)

    # Preference 1: Spread theory sessions of the same subject across different days
    # Section x Subject x Day theory count penalty if > 1
    sec_subj_pairs = {(t.section_id, t.subject_id) for t in input_data.tasks if t.session_type == "THEORY"}
    for (sec_id, subj_id) in sec_subj_pairs:
        matching_theory = [t for t in input_data.tasks if t.section_id == sec_id and t.subject_id == subj_id and t.session_type == "THEORY"]
        if len(matching_theory) > 1:
            for day in input_data.working_days:
                day_theory_vars = []
                for t in matching_theory:
                    for start_p in range(input_data.periods_per_day):
                        for r_id in room_dict.keys():
                            if (day, start_p, r_id) in task_vars[t.id]:
                                day_theory_vars.append(task_vars[t.id][(day, start_p, r_id)])
                if len(day_theory_vars) > 1:
                    excess_var = model.NewIntVar(0, len(matching_theory), f"excess_{sec_id}_{subj_id}_{day}")
                    model.Add(excess_var >= sum(day_theory_vars) - 1)
                    penalties.append(excess_var * 100) # 100 penalty per extra lecture on same day

    # Preference 2: Prefer earlier periods (compact schedules, avoid late-day dispersion)
    for task in input_data.tasks:
        for (day, start_p, r_id), var in task_vars[task.id].items():
            penalties.append(var * (start_p * 2))

    if penalties:
        model.Minimize(sum(penalties))

    # --- 5. SOLVE ---
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = float(input_data.time_limit_seconds)
    solver.parameters.num_workers = 4 # Multi-core parallelism

    solver_status = solver.Solve(model)
    elapsed = time.time() - start_time

    if solver_status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        scheduled: List[ScheduledSlot] = []
        unscheduled: List[SessionTask] = []
        task_map = {t.id: t for t in input_data.tasks}

        for task in input_data.tasks:
            assigned = False
            for (day, start_p, r_id), var in task_vars[task.id].items():
                if solver.Value(var) == 1:
                    room = room_dict[r_id]
                    scheduled.append(ScheduledSlot(
                        session_id=task.id,
                        subject_id=task.subject_id,
                        subject_code=task.subject_code,
                        subject_name=task.subject_name,
                        section_id=task.section_id,
                        section_name=task.section_name,
                        batch_id=task.batch_id,
                        batch_name=task.batch_name,
                        faculty_id=task.faculty_id,
                        faculty_name=task.faculty_name,
                        room_id=room.id,
                        room_code=room.code,
                        room_name=room.name,
                        day_index=day,
                        period_index=start_p,
                        duration_periods=task.duration_periods,
                        session_type=task.session_type,
                        is_locked=task.is_locked,
                        is_fixed_commitment=task.is_fixed_commitment
                    ))
                    assigned = True
                    break
            if not assigned:
                unscheduled.append(task)

        if unscheduled:
            # We used slack relaxation
            from app.solver.infeasibility import generate_conflict_explanations
            explanations = generate_conflict_explanations(input_data, scheduled, unscheduled)
            return SolverOutput(
                status="INFEASIBLE",
                scheduled_sessions=scheduled,
                unscheduled_sessions=unscheduled,
                conflict_explanations=explanations,
                solver_time_seconds=elapsed
            )

        return SolverOutput(
            status="OPTIMAL" if solver_status == cp_model.OPTIMAL else "FEASIBLE",
            scheduled_sessions=scheduled,
            unscheduled_sessions=[],
            conflict_explanations=[],
            solver_time_seconds=elapsed
        )
    else:
        # If strict solve was infeasible, run relaxation with slack to explain why
        if not allow_slack:
            return solve_timetable(input_data, allow_slack=True)

        return SolverOutput(
            status="INFEASIBLE",
            unscheduled_sessions=input_data.tasks,
            conflict_explanations=["Solver could not find a feasible schedule even with relaxation."],
            solver_time_seconds=elapsed
        )
