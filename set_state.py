"""Claude Code hooklari uchun: pet holatini yozadi.

Ishlatilishi:  pythonw set_state.py working|idle|waiting
Hech qachon xato qaytarmaydi -- hookni to'xtatib qo'ymasligi kerak.
"""
import json
import os
import sys
import time

STATE_DIR = os.path.join(os.environ.get("TEMP", "/tmp"), "claude-pet")
STATE_FILE = os.path.join(STATE_DIR, "state.json")

try:
    state = sys.argv[1] if len(sys.argv) > 1 else "idle"
    os.makedirs(STATE_DIR, exist_ok=True)
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump({"state": state, "ts": time.time()}, fh)
    os.replace(tmp, STATE_FILE)
except Exception:
    pass
