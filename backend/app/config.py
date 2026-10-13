import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/timetable.db")

APP_TITLE = "NFSU Automated Academic Timetable Generation System"
APP_VERSION = "1.0.0"
