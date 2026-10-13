# NFSU Automated Academic Timetable Generation System

Automated Academic Timetable Generation System engineered for the NFSU Coder's Event project.

## Architecture & Technology Stack
- **Frontend**: React + TypeScript + Vite + Tailwind CSS v4
- **Backend**: Python + FastAPI
- **Solver**: Google OR-Tools CP-SAT (Constraint Programming - Satisfiability)
- **Database**: SQLite (SQLAlchemy ORM)
- **Version Control**: Git

---

## Implemented Mandatory Requirements

| # | Requirement | Implementation Status |
| :--- | :--- | :--- |
| **1** | Working days, timings, duration, breaks config | Fully configurable via UI & API (`/api/config`); auto-calculates time slot matrix. |
| **2** | Rooms, labs, capacities, availability | Complete CRUD with room specialty and capacity matching (`/api/resources/rooms`). |
| **3** | Programmes, semesters, sections, batches | Full hierarchy support: Programme $\rightarrow$ Semester $\rightarrow$ Section $\rightarrow$ Practical Batches (`/api/academic`). |
| **4** | Subjects, faculty, theory & practical rules | Configurable theory periods and consecutive multi-period lab sessions (`/api/academic/subjects`). |
| **5** | Faculty availability & fixed commitments | Individual faculty availability matrix and max workload limits (`/api/resources/faculty/availability`). |
| **6** | Mandatory constraint enforcement | CP-SAT engine enforces zero faculty clashes, zero room clashes, and capacity limits. |
| **7** | Whole-class vs Practical batch non-overlap | Mathematical constraint guarantees whole-class lectures never overlap with batch practicals, while distinct batches can run parallel practicals in different labs. |
| **8** | Consecutive lab sessions in matching labs | Practicals scheduled for $N$ consecutive periods; strictly prohibited from crossing lunch breaks. |
| **9** | Weekly teaching hours & fixed commitments | Exact weekly period delivery satisfied; locked and fixed sessions pinned. |
| **10** | Mandatory vs Preference distinction | Hard constraints strictly enforced; soft preferences optimized (subject day spread, compact student schedules). |
| **11** | Infeasibility detection & diagnostic explainer | Multi-layer diagnosis: Pre-checks, Slack-variable relaxation, and plain-language bottleneck explanations. |
| **12** | Multi-perspective timetable views | **Programme/Section view**, **Faculty view**, and **Room/Lab view** available in UI. |
| **13** | Manual edits with live conflict validation | Instant validation endpoint (`/api/timetable/validate-move`) tests hard constraints in milliseconds before confirming moves. |
| **14** | Session locking & selective regeneration | Toggle lock button on session cards preserves slots during solver regeneration. |
| **15** | Drafts, publishing, print & CSV export | Draft vs Published workflow; CSV export and print-friendly view supported. |

---

## How to Run the Application

### 1. Start the Backend API
Double-click `run_backend.bat` or run in terminal:
```powershell
cd c:\git\Timetable\backend
.\.venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
API Documentation will be accessible at: `http://localhost:8000/docs`

### 2. Start the Frontend Web UI
Double-click `run_frontend.bat` or run in terminal:
```powershell
cd c:\git\Timetable\frontend
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## How to Run Automated Tests

To run the complete test suite (11 comprehensive unit & solver tests):
```powershell
cd c:\git\Timetable\backend
.\.venv\Scripts\pytest.exe -v tests/
```
All tests verify:
- API health and Google OR-Tools CP-SAT execution
- University configuration and slot generation
- Room and Faculty CRUD with availability matrices
- Seed data population for realistic NFSU department scenario
- CP-SAT 100% clash-free schedule generation
- Practical batch vs whole-class non-overlap enforcement
- Session locking and slot preservation during regeneration
- Manual move live conflict validation
- Infeasibility diagnostic reporting on impossible availability
- CSV export functionality
