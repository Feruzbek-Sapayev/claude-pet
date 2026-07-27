"""Claude desktop pet'ni o'chiradi.

Faqat o'zi qo'shgan narsalarni olib tashlaydi: hooklar, avtostart, ishlab
turgan jarayon. settings.json dagi boshqa sozlamalaringizga tegmaydi.
Papkaning o'zini keyin qo'lda o'chirasiz.
"""
import json
import os
import shutil
import signal
import subprocess
import sys

IS_MAC = sys.platform == "darwin"

HERE = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser("~")
CLAUDE_DIR = os.path.join(HOME, ".claude")
SETTINGS = os.path.join(CLAUDE_DIR, "settings.json")

LAUNCH_LABEL = "com.claude-pet"
if IS_MAC:
    STARTUP_FILE = os.path.join(HOME, "Library", "LaunchAgents",
                                LAUNCH_LABEL + ".plist")
else:
    STARTUP_FILE = os.path.join(os.environ.get("APPDATA", ""), "Microsoft",
                                "Windows", "Start Menu", "Programs", "Startup",
                                "claude-pet.vbs")

sys.path.insert(0, HERE)
from paths import PID_FILE   # noqa: E402


def say(msg):
    print(msg)


def is_ours(entry):
    try:
        return any("set_state.py" in h.get("command", "")
                   for h in entry.get("hooks", []))
    except Exception:
        return False


def remove_hooks():
    if not os.path.exists(SETTINGS):
        say("  settings.json yo'q -- hooklar allaqachon yo'q")
        return
    try:
        with open(SETTINGS, encoding="utf-8") as fh:
            settings = json.load(fh)
    except Exception as exc:
        say("  ! settings.json o'qilmadi: {}".format(exc))
        return

    shutil.copy2(SETTINGS, SETTINGS + ".bak")
    hooks = settings.get("hooks") or {}
    removed = 0
    for event in list(hooks):
        kept = [e for e in (hooks[event] or []) if not is_ours(e)]
        removed += len(hooks[event] or []) - len(kept)
        if kept:
            hooks[event] = kept
        else:
            del hooks[event]      # bo'sh qolsa hodisani ham olib tashlaymiz
    if hooks:
        settings["hooks"] = hooks
    else:
        settings.pop("hooks", None)

    with open(SETTINGS, "w", encoding="utf-8") as fh:
        json.dump(settings, fh, indent=2, ensure_ascii=False)
    say("  {} ta hook olib tashlandi (zaxira: settings.json.bak)".format(removed))


def remove_startup():
    if not os.path.exists(STARTUP_FILE):
        say("  avtostartda yo'q edi")
        return
    if IS_MAC:
        # avval launchd ro'yxatidan tushiramiz, so'ng faylni olib tashlaymiz
        subprocess.run(["launchctl", "unload", STARTUP_FILE], capture_output=True)
    os.remove(STARTUP_FILE)
    say("  avtostartdan olib tashlandi")


def stop_pet():
    try:
        with open(PID_FILE, encoding="utf-8") as fh:
            pid = int(fh.read().strip())
        os.kill(pid, signal.SIGTERM)
        say("  pet to'xtatildi (PID {})".format(pid))
    except Exception:
        say("  pet ishlamayotgan edi (yoki uni o'ng tugma -> Chiqish bilan yoping)")
    try:
        os.remove(PID_FILE)
    except Exception:
        pass


def main():
    say("Claude desktop pet o'chirilyapti")
    remove_hooks()
    remove_startup()
    stop_pet()
    say("")
    say("Tayyor. Endi shu papkani ({}) o'chirsangiz bo'ladi.".format(HERE))
    say("Claude Code'ni qayta ishga tushiring.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
