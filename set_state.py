"""Claude Code hooklari uchun: pet holatini yozadi.

Ishlatilishi:  python set_state.py working|idle|waiting
Hech qachon xato qaytarmaydi -- hookni to'xtatib qo'ymasligi kerak.
"""
import json
import os
import sys
import time

try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from paths import STATE_DIR, STATE_FILE

    state = sys.argv[1] if len(sys.argv) > 1 else "idle"
    os.makedirs(STATE_DIR, exist_ok=True)
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump({"state": state, "ts": time.time()}, fh)
    os.replace(tmp, STATE_FILE)
except Exception:
    pass
