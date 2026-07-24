"""Claude desktop pet o'rnatgichi.

Qiladigan ishlari:
  1. Claude Code hooklarini ~/.claude/settings.json ga qo'shadi
     (mavjud sozlamalar va boshqa hooklar saqlanadi, zaxira nusxa olinadi)
  2. Windows avtostartiga qo'shadi
  3. Pet'ni ishga tushiradi

Qayta ishga tushirilsa hech narsa takrorlanmaydi -- eski yozuvlar yangilanadi.
"""
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CLAUDE_DIR = os.path.join(os.path.expanduser("~"), ".claude")
SETTINGS = os.path.join(CLAUDE_DIR, "settings.json")
STARTUP = os.path.join(os.environ.get("APPDATA", ""), "Microsoft", "Windows",
                       "Start Menu", "Programs", "Startup")
STARTUP_FILE = os.path.join(STARTUP, "claude-pet.vbs")

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


def pythonw_path():
    """Konsolsiz Python yo'li -- hooklar shuni chaqiradi.

    Virtual muhitdan qochamiz: venv o'chirilsa yoki ko'chirilsa hook ishlamay
    qolardi. Shuning uchun asosiy (base) Python qidiriladi.
    """
    roots = []
    base = getattr(sys, "base_prefix", sys.prefix)
    if base != sys.prefix:
        roots.append(base)               # venv ichidamiz -- asosiysini olamiz
    roots.append(os.path.dirname(sys.executable))
    roots.append(sys.prefix)

    for root in roots:
        for name in ("pythonw.exe", "pyw.exe"):
            for cand in (os.path.join(root, name),
                         os.path.join(root, "Scripts", name)):
                if os.path.exists(cand):
                    return cand
    return sys.executable  # topilmasa oddiysi ham bo'ladi


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


def install_startup():
    if not os.path.isdir(STARTUP):
        say("  ! avtostart papkasi topilmadi, bu qadam o'tkazib yuborildi")
        return False
    vbs = (
        "' Claude desktop pet -- kompyuter yoqilganda ko'rinmas ishga tushadi\n"
        'CreateObject("WScript.Shell").Run """{}""", 0, False\n'
    ).format(os.path.join(HERE, "start-pet.bat"))
    with open(STARTUP_FILE, "w", encoding="utf-8") as fh:
        fh.write(vbs)
    say("  avtostart: {}".format(STARTUP_FILE))
    return True


def launch():
    bat = os.path.join(HERE, "start-pet.bat")
    try:
        subprocess.Popen([bat], shell=True,
                         creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        say("  pet ishga tushdi")
    except Exception as exc:
        say("  ! ishga tushmadi: {} -- start-pet.bat ni qo'lda oching".format(exc))


def main():
    say("Claude desktop pet o'rnatilyapti")
    say("  papka: {}".format(HERE))

    missing = [f for f in ("pet.py", "set_state.py", "start-pet.bat")
               if not os.path.exists(os.path.join(HERE, f))]
    if missing or not os.path.isdir(os.path.join(HERE, "sprites", "flat")):
        say("  ! fayllar to'liq emas: {}".format(missing or "sprites/flat"))
        return 1

    py = pythonw_path()
    say("  Python: {}".format(py))

    install_hooks(py)
    install_startup()
    launch()

    say("")
    say("Tayyor. Claude Code'ni qayta ishga tushiring -- pet uning holatini")
    say("shundan keyin o'zi biladi.")
    say("O'chirish uchun: uninstall.bat")
    return 0


if __name__ == "__main__":
    sys.exit(main())
