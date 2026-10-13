# NFSU Automated Academic Timetable Generation System

Automated Academic Timetable Generation System for the NFSU Coder's Event.

## Architecture
- **Frontend**: React + TypeScript + Vite + Tailwind CSS
- **Backend**: Python + FastAPI
- **Solver**: Google OR-Tools CP-SAT (Constraint Programming)
- **Database**: SQLite (SQLAlchemy ORM)

## Features
- Configurable university working days, timings, duration, and breaks.
- Department, programme, semester, section, and practical batch management.
- Room and laboratory capacity and specialty matching.
- Faculty availability matrix, max loads, and fixed commitments.
- Constraint satisfaction solver with 100% hard constraint enforcement.
- Plain-language infeasibility and conflict diagnostic explainer.
- Multi-perspective timetable views (Programme-wise, Faculty-wise, Room-wise).
- Instant conflict feedback on manual adjustments.
- Session locking and selective regeneration.
- Draft saving, publishing, and PDF/CSV export.
