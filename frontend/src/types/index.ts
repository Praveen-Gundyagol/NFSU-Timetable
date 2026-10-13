export interface InstitutionConfig {
  id: number;
  name: string;
  working_days: number[];
  periods_per_day: number;
  period_duration_minutes: number;
  start_time: string;
  break_periods: number[];
}

export interface TimeSlot {
  id: number;
  day_index: number;
  period_index: number;
  start_time: string;
  end_time: string;
  is_break: boolean;
}

export interface Room {
  id: number;
  code: string;
  name: string;
  room_type: string;
  capacity: number;
  is_active: boolean;
  unavailable_slots: number[][];
}

export interface FacultyAvailability {
  id: number;
  faculty_id: number;
  day_index: number;
  period_index: number;
  status: string;
  note?: string;
}

export interface Faculty {
  id: number;
  employee_id: string;
  name: string;
  email: string;
  department: string;
  max_weekly_periods: number;
  max_daily_periods: number;
  is_active: boolean;
  availabilities: FacultyAvailability[];
}

export interface PracticalBatch {
  id: number;
  section_id: number;
  name: string;
  batch_strength: number;
}

export interface Section {
  id: number;
  semester_id: number;
  name: string;
  total_strength: number;
  batches: PracticalBatch[];
}

export interface Semester {
  id: number;
  programme_id: number;
  semester_number: number;
  sections: Section[];
}

export interface Programme {
  id: number;
  code: string;
  name: string;
  department: string;
  semesters: Semester[];
}

export interface SubjectFacultyAssignment {
  id: number;
  subject_id: number;
  faculty_id: number;
  component: string;
  batch_id?: number;
  faculty_name?: string;
}

export interface Subject {
  id: number;
  semester_id: number;
  code: string;
  name: string;
  subject_type: string;
  weekly_theory_periods: number;
  weekly_practical_sessions: number;
  practical_duration_periods: number;
  required_room_type: string;
  preferred_room_id?: number;
  faculty_assignments: SubjectFacultyAssignment[];
}

export interface Session {
  id: number;
  timetable_id: number;
  subject_id: number;
  subject_code: string;
  subject_name: string;
  faculty_id: number;
  faculty_name: string;
  room_id: number;
  room_code: string;
  room_name: string;
  section_id: number;
  section_name: string;
  batch_id?: number;
  batch_name?: string;
  day_index: number;
  period_index: number;
  duration_periods: number;
  session_type: string;
  is_locked: boolean;
  is_fixed_commitment: boolean;
}

export interface InfeasibilityReport {
  status: string;
  unscheduled_count: number;
  conflict_explanations: string[];
  solver_time_seconds: number;
}

export interface Timetable {
  id: number;
  title: string;
  academic_year: string;
  semester_type: string;
  status: string;
  solver_status?: string;
  infeasibility_report?: InfeasibilityReport;
  sessions: Session[];
}

export interface ConflictDetail {
  conflict_type: string;
  message: string;
}

export interface ValidateMoveResponse {
  valid: boolean;
  conflicts: ConflictDetail[];
}
