"""Claude desktop pet o'rnatgichi.

Qiladigan ishlari:
  1. Claude Code hooklarini ~/.claude/settings.json ga qo'shadi
     (mavjud sozlamalar va boshqa hooklar saqlanadi, zaxira nusxa olinadi)
  2. Tizim avtostartiga qo'shadi (Windows: Startup papkasi, macOS: LaunchAgent)
  3. Pet'ni ishga tushiradi

Qayta ishga tushirilsa hech narsa takrorlanmaydi -- eski yozuvlar yangilanadi.
"""
import json
import os
import shutil
import subprocess
import sys

IS_MAC = sys.platform == "darwin"
IS_WIN = os.name == "nt"

HERE = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser("~")
CLAUDE_DIR = os.path.join(HOME, ".claude")
SETTINGS = os.path.join(CLAUDE_DIR, "settings.json")

LAUNCH_LABEL = "com.claude-pet"
if IS_MAC:
    STARTUP = os.path.join(HOME, "Library", "LaunchAgents")
    STARTUP_FILE = os.path.join(STARTUP, LAUNCH_LABEL + ".plist")
    LAUNCHER = "start-pet.command"
else:
    STARTUP = os.path.join(os.environ.get("APPDATA", ""), "Microsoft", "Windows",
                           "Start Menu", "Programs", "Startup")
    STARTUP_FILE = os.path.join(STARTUP, "claude-pet.vbs")
    LAUNCHER = "start-pet.bat"

# Qaysi hodisada pet qaysi holatga o'tadi
HOOK_EVENTS = {
    "UserPromptSubmit": "working",
    "Stop": "idle",
    "Notification": "waiting",
    "SessionStart": "idle",
    "SessionEnd": "idle",
}


def say(msg):
    print(msg)


def python_path():
    """Hooklar chaqiradigan Python yo'li.

    Virtual muhitdan qochamiz: venv o'chirilsa yoki ko'chirilsa hook ishlamay
    qolardi. Shuning uchun asosiy (base) Python qidiriladi. Windows'da
    konsolsiz nusxasi (pythonw) afzal -- hook ishlaganda oyna chaqnamasin.
    """
    roots = []
    base = getattr(sys, "base_prefix", sys.prefix)
    if base != sys.prefix:
        roots.append(base)               # venv ichidamiz -- asosiysini olamiz
    roots.append(os.path.dirname(sys.executable))
    roots.append(sys.prefix)

    names = ("pythonw.exe", "pyw.exe") if IS_WIN else ("python3", "python")
    subdir = "Scripts" if IS_WIN else "bin"
    for root in roots:
        for name in names:
            for cand in (os.path.join(root, name),
                         os.path.join(root, subdir, name)):
                if os.path.exists(cand):
                    return cand
    return sys.executable  # topilmasa shu ham bo'ladi


def hook_entry(py, state):
    cmd = '"{}" "{}" {}'.format(py, os.path.join(HERE, "set_state.py"), state)
    return {"hooks": [{"type": "command", "command": cmd}]}


def is_ours(entry):
    """Shu yozuv bizniki (set_state.py ni chaqiradi)mi?"""
    try:
        return any("set_state.py" in h.get("command", "")
                   for h in entry.get("hooks", []))
    except Exception:
        return False


def install_hooks(py):
    os.makedirs(CLAUDE_DIR, exist_ok=True)

    settings = {}
    if os.path.exists(SETTINGS):
        try:
            with open(SETTINGS, encoding="utf-8") as fh:
                settings = json.load(fh)
        except Exception as exc:
            say("  ! settings.json o'qilmadi ({}), yangisi yaratiladi".format(exc))
            settings = {}
        backup = SETTINGS + ".bak"
        shutil.copy2(SETTINGS, backup)
        say("  zaxira nusxa: {}".format(backup))

    hooks = settings.get("hooks") or {}
    for event, state in HOOK_EVENTS.items():
        # o'zimizning eski yozuvlarimizni olib tashlaymiz, boshqalarni tegmaymiz
        existing = [e for e in (hooks.get(event) or []) if not is_ours(e)]
        hooks[event] = existing + [hook_entry(py, state)]
    settings["hooks"] = hooks

    with open(SETTINGS, "w", encoding="utf-8") as fh:
        json.dump(settings, fh, indent=2, ensure_ascii=False)
    say("  hooklar qo'shildi: {}".format(", ".join(HOOK_EVENTS)))


PLIST = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" \
"http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>{label}</string>
  <key>ProgramArguments</key>
  <array>
    <string>{py}</string>
    <string>{pet}</string>
  </array>
  <key>RunAtLoad</key><true/>
  <key>ProcessType</key><string>Interactive</string>
</dict>
</plist>
"""


def install_startup(py):
    if not IS_MAC:
        return install_startup_windows()

    os.makedirs(STARTUP, exist_ok=True)
    with open(STARTUP_FILE, "w", encoding="utf-8") as fh:
        fh.write(PLIST.format(label=LAUNCH_LABEL, py=py,
                              pet=os.path.join(HERE, "pet.py")))
    # eskisi yuklangan bo'lsa avval tushiramiz, keyin yangisini yuklaymiz
    for args in (["unload", STARTUP_FILE], ["load", STARTUP_FILE]):
        subprocess.run(["launchctl"] + args, capture_output=True)
    say("  avtostart: {}".format(STARTUP_FILE))
    return True


def install_startup_windows():
    if not os.path.isdir(STARTUP):
        say("  ! avtostart papkasi topilmadi, bu qadam o'tkazib yuborildi")
        return False
    vbs = (
        "' Claude desktop pet -- kompyuter yoqilganda ko'rinmas ishga tushadi\n"
        'CreateObject("WScript.Shell").Run """{}""", 0, False\n'
    ).format(os.path.join(HERE, LAUNCHER))
    with open(STARTUP_FILE, "w", encoding="utf-8") as fh:
        fh.write(vbs)
    say("  avtostart: {}".format(STARTUP_FILE))
    return True


def launch(py):
    try:
        if IS_MAC:
            # LaunchAgent RunAtLoad bilan allaqachon ko'tarilgan bo'lishi mumkin;
            # pet o'zi port qulfi orqali ikkinchi nusxani yopadi
            subprocess.Popen([py, os.path.join(HERE, "pet.py")],
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
        else:
            subprocess.Popen([os.path.join(HERE, LAUNCHER)], shell=True,
                             creationflags=getattr(subprocess,
                                                   "CREATE_NO_WINDOW", 0))
        say("  pet ishga tushdi")
    except Exception as exc:
        say("  ! ishga tushmadi: {} -- {} ni qo'lda oching".format(exc, LAUNCHER))


def main():
    say("Claude desktop pet o'rnatilyapti")
    say("  papka: {}".format(HERE))

    missing = [f for f in ("pet.py", "paths.py", "set_state.py", LAUNCHER)
               if not os.path.exists(os.path.join(HERE, f))]
    sprites = os.path.join(HERE, "sprites" if IS_MAC else "sprites/flat")
    if missing or not os.path.isdir(sprites):
        say("  ! fayllar to'liq emas: {}".format(missing or sprites))
        return 1

    py = python_path()
    say("  Python: {}".format(py))
    if IS_MAC:
        os.chmod(os.path.join(HERE, LAUNCHER), 0o755)

    install_hooks(py)
    install_startup(py)
    launch(py)

    say("")
    say("Tayyor. Claude Code'ni qayta ishga tushiring -- pet uning holatini")
    say("shundan keyin o'zi biladi.")
    say("O'chirish uchun: {}".format("uninstall.command" if IS_MAC
                                     else "uninstall.bat"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
