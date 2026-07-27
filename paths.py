"""Pet, hook va o'chirgich uchun umumiy yo'llar.

Uch dastur ham holat faylini bir xil joyda topishi shart, shuning uchun
yo'l shu yerda bir marta hisoblanadi.
"""
import os
import sys
import tempfile


def state_dir():
    """Holat fayli turadigan papka -- har platformada o'z odatiy joyi.

    macOS'da TMPDIR sessiyaga bog'langan bo'lishi mumkin, shuning uchun
    barqaror joy -- Caches.
    """
    if sys.platform == "darwin":
        return os.path.join(os.path.expanduser("~"), "Library", "Caches",
                            "claude-pet")
    base = os.environ.get("TEMP") if os.name == "nt" else None
    return os.path.join(base or tempfile.gettempdir(), "claude-pet")


STATE_DIR = state_dir()
STATE_FILE = os.path.join(STATE_DIR, "state.json")
PID_FILE = os.path.join(STATE_DIR, "pet.pid")
