"""Make the apps under test importable.

In YOUR repo the app lives at the repo root, so you would not need this file
(or you would add the repo root instead of these two folders).
"""
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parents[3]
APP_DIR = KIT / "session1" / "activity2_solution"
ASSISTANT_DIR = KIT / "session4" / "activity8_assistant"

for p in (APP_DIR, ASSISTANT_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
