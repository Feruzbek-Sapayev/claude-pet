"""Claude desktop pet -- ekran bo'ylab yuradigan maskot.

Claude Code ishlayotganda yuradi va boshi tepasida nima qilayotganini aytadi,
bo'sh turganda tik turib ko'z qisadi, uzoq bo'sh qolsa uxlaydi,
javobingizni kutayotganda sakraydi.

Windows va macOS'da ishlaydi.

Ishga tushirish:  pythonw pet.py  (macOS: python3 pet.py)
Chiqish:          maskotga o'ng tugma -> Chiqish
Ko'chirish:       chap tugma bilan sudrang
"""
import json
import math
import os
import random
import socket
import subprocess
import sys
import time
import tkinter as tk

IS_MAC = sys.platform == "darwin"
IS_WIN = os.name == "nt"

if IS_WIN:
    import ctypes
    import ctypes.wintypes
    import winsound          # ovoz effektlari uchun
else:
    ctypes = winsound = None

_LOCK_PORT = 50573
_lock = None


def acquire_lock():
    """Bitta nusxadan ortiq ishga tushmasligi uchun portni band qiladi.

    Faqat dastur to'g'ridan-to'g'ri ishga tushganda chaqiriladi -- shunda
    modulni import qilib sinash mumkin bo'ladi.
    """
    global _lock
    _lock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        _lock.bind(("127.0.0.1", _LOCK_PORT))
        return True
    except OSError:
        return False


HERE = os.path.dirname(os.path.abspath(__file__))
SPRITES = os.path.join(HERE, "sprites")
SOUNDS = os.path.join(HERE, "sounds")

sys.path.insert(0, HERE)
from paths import STATE_DIR, STATE_FILE, PID_FILE   # noqa: E402

# Shaffoflik ikki xil ishlaydi. Windows'da oyna bitta "kalit rang"ni butunlay
# ko'rinmas qiladi, shuning uchun kadrlar shu rangga yopishtirilgan nusxadan
# (sprites/flat) o'qiladi. macOS'da oynaning o'zi shaffof bo'la oladi, u yerda
# alfa kanalli asl kadrlar ishlatiladi.
TRANS = "systemTransparent" if IS_MAC else "#ff00ff"
FRAME_DIR = SPRITES if IS_MAC else os.path.join(SPRITES, "flat")
UI_FONT = "Helvetica Neue" if IS_MAC else "Segoe UI"

# macOS'da ovozni tizimning o'z chalg'ichi chaladi (winsound o'rniga)
AFPLAY = "/usr/bin/afplay" if IS_MAC and os.path.exists("/usr/bin/afplay") else None

TICK_MS = 50
WALK_SPEED = 2.4        # ishlayotgandagi tezlik (piksel/tik)
IDLE_SPEED = 1.0
FRAME_TICKS = 3         # necha tikda kadr almashadi
STALE_SEC = 900         # bundan eski "working" holati eskirgan hisoblanadi
WAIT_SEC = 7            # "kutyapti" holatida shuncha sakraydi, keyin tinchiydi
VERB_SEC = 3.5          # gap pufagidagi so'z shuncha soniyada almashadi
SLEEP_AFTER = 240       # shuncha soniya bo'sh tursa uxlaydi
TALK_MIN, TALK_MAX = 25, 70   # bo'sh turganda shuncha oraliqda gapiradi
TALK_SEC = 4.5          # bitta gap ekranda shuncha turadi
BOB_PX = 2              # yurganda tebranish balandligi
GROUND_EASE = 6         # monitorlar balandligi farq qilsa, shuncha px/tik moslashadi

# fizika (uloqtirish va yiqilish)
GRAVITY = 1.5           # tik tezlanish (px/tik^2)
AIR_DRAG = 0.99         # havo qarshiligi
BOUNCE = 0.42           # yerdan qaytish koeffitsienti
WALL_BOUNCE = 0.55      # devordan qaytish koeffitsienti
STOP_V = 3.0            # shundan sekin sakrash to'xtaydi
THROW_MAX = 60.0        # uloqtirish tezligi chegarasi (px/tik)
SQUASH_TICKS = 5        # yerga urilgandan keyin necha tik siqilib turadi

# kursorga e'tibor
NOTICE_PX = 240         # kursor shu masofaga kirsa, pet unga qaraydi
POKE_SEC = 2.2          # ustiga bosilganda shuncha vaqt hayajonlanadi
CLICK_PX = 5            # shundan kam siljish "bosish" hisoblanadi

# kulgan holat -- ko'zi "^^" ga o'tadi
HAPPY_SEC = 2.6         # bosilgandan keyin shuncha vaqt kulib turadi
# kulgan nusxasi bor kadrlar
HAPPY_FRAMES = ("stand", "wave", "wave_l", "wave_r", "cheer")

# Qo'l silkitish uslublari: ikkala qo'l, faqat chapi, faqat o'ngi yoki
# navbat bilan. Ro'yxatdan tasodifiy tanlanadi.
WAVE_STYLES = ("wave", "wave_l", "wave_r", "alt")

# ovoz
SOUND_ON = True         # ovoz standart holatda yoniq
SOUND_GAP = 0.07        # ketma-ket tovushlar orasidagi eng kam oraliq (s)
IDLE_SOUND_MIN, IDLE_SOUND_MAX = 22, 50   # oddiy turganda chirp oralig'i

WALK_CYCLE = ["walk1", "walk2", "walk3", "walk2"]

# Ish paytidagi faoliyatlar. "walk" ro'yxatda ko'p marta -- u tez-tez tushadi.
ACTIVITIES = ["walk", "walk", "walk", "walk", "peck", "peck",
              "wave", "think", "think", "cheer"]
ACT_MIN, ACT_MAX = 3.0, 8.0     # bitta faoliyat shuncha soniya davom etadi

# Bo'sh turganda o'zicha aytadigan gaplari.
IDLE_TALK = [
    "Bugun ish qanday ketyapti?",
    "Yana biror vazifa bormi?",
    "Men shu yerdaman",
    "Zerikdim...",
    "Kod o'zi yozilmaydi-da",
    "Nima o'ylayapsiz?",
    "Commit qilishni unutmang",
    "Bir piyola choy ichsangiz bo'lardi",
    "Ko'zlaringizga bir dam bering",
    "Suv ichishni unutmang",
    "Yelkangizni rostlang",
    "Biroz cho'zilib oling",
    "Tanaffus ham kerak",
]

# Kun vaqtiga qarab aytiladiganlari: (boshlanish, tugash, gaplar)
TIME_TALK = [
    (5, 10, ["Xayrli tong!", "Qahva vaqti", "Ertalabki kod eng shirin bo'ladi"]),
    (12, 14, ["Tushlik vaqti bo'ldi", "Ovqatlanib oldingizmi?"]),
    (18, 22, ["Kech bo'ldi, charchamadingizmi?", "Bugunga yetar-ov"]),
    (22, 24, ["Kech bo'ldi, dam oling", "Ertaga davom etsak bo'ladi"]),
    (0, 5, ["Yarim tundan oshdi", "Uxlash vaqti emasmi?", "Sog'liq ham muhim"]),
]

LONG_IDLE_TALK = ["Uzoq jim turibsiz", "Ketib qoldingizmi?", "Kutib turibman"]

SETTINGS = os.path.join(os.path.expanduser("~"), ".claude", "settings.json")
# settings.json da spinnerVerbs bo'lmasa shular ishlatiladi
FALLBACK_VERBS = [
    "Ishlayapman", "O'ylayapman", "Pishiryapman", "Yasayapman",
    "Hisoblayapman", "Qidiryapman", "Yozyapman", "Tahrirlayapman",
    "Fikr yuritayapman", "Bosh qotiryapman", "Yaratyapman", "Yig'ishtiryapman",
    "Ko'rib chiqyapman", "Aniqlayapman", "Amalga oshiryapman", "Damlayapman",
    "Mulohaza qilyapman", "Shakllantiryapman", "Tekshiryapman", "Ulayapman",
]

# pufak ranglari
BUBBLE_BG = "#1e1f22"
BUBBLE_LINE = "#d77757"
BUBBLE_TEXT = "#ece4dc"

# uxlayotganda tepaga ko'tariladigan "Z" harflari
ZZZ_COUNT = 3           # bir vaqtda nechta Z ko'rinadi
ZZZ_RISE = 56           # bitta Z shuncha piksel ko'tarilib so'nadi
ZZZ_PERIOD = 3.2        # shu yo'lni bosib o'tishga ketadigan vaqt (s)
ZZZ_DRIFT = 12          # ko'tarilgan sari yon tomonga eng ko'p siljish
ZZZ_SCALE = (2, 4)      # harf piksellarining kattaligi: pastda kichik, tepada katta
ZZZ_STEPS = 12          # yo'l shuncha bosqichga bo'linadi (har biriga tayyor rasm)
ZZZ_LIFT = 44           # yotgan maskot tepasidan shuncha px balandda boshlanadi
ZZZ_NEAR = "#ded7cf"    # yangi chiqqan Z
ZZZ_FAR = "#4c4d54"     # so'nib borayotgani

# "Z" harfi -- shrift emas, piksel naqsh. Shrift bo'lsa Windows uni silliqlab
# chekkalarini shaffof kalit rangga aralashtirib yuboradi (magenta hoshiya).
Z_GLYPH = ("#####",
           "...##",
           "..##.",
           ".##..",
           "#####")


def pick_phrase(idle_sec):
    """Bo'sh turgandagi gapni tanlaydi -- kun vaqti va jimlik uzunligiga qarab."""
    pool = list(IDLE_TALK)
    hour = time.localtime().tm_hour
    for start, end, phrases in TIME_TALK:
        if start <= hour < end:
            pool += phrases * 3        # kun vaqtiga mosi ko'proq tushsin
    if idle_sec > 600:
        pool += LONG_IDLE_TALK * 3
    return random.choice(pool)


def load_verbs():
    """Terminaldagi spinner fe'llarining aynan o'sha ro'yxatini o'qiydi."""
    try:
        with open(SETTINGS, encoding="utf-8") as fh:
            verbs = json.load(fh).get("spinnerVerbs", {}).get("verbs", [])
        if verbs:
            return verbs
    except Exception:
        pass
    return FALLBACK_VERBS


if IS_WIN:
    class RECT(ctypes.Structure):
        _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long),
                    ("right", ctypes.c_long), ("bottom", ctypes.c_long)]

    class MONITORINFO(ctypes.Structure):
        _fields_ = [("cbSize", ctypes.c_ulong), ("rcMonitor", RECT),
                    ("rcWork", RECT), ("dwFlags", ctypes.c_ulong)]


def make_dpi_aware():
    """Har monitor uchun alohida DPI -- koordinatalar haqiqiy piksellarda bo'ladi.

    Faqat Windows'da kerak: macOS'da Tk allaqachon nuqta koordinatalarida
    ishlaydi va Retina masshtabini o'zi hal qiladi.
    """
    if not IS_WIN:
        return
    for fn in (lambda: ctypes.windll.shcore.SetProcessDpiAwareness(2),
               lambda: ctypes.windll.shcore.SetProcessDpiAwareness(1),
               lambda: ctypes.windll.user32.SetProcessDPIAware()):
        try:
            fn()
            return
        except Exception:
            continue


def _win_monitors():
    """Windows: EnumDisplayMonitors orqali har ekranning ish maydoni."""
    mons = []
    proc_t = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p,
                                ctypes.POINTER(RECT), ctypes.c_void_p)

    def cb(hmon, _hdc, _lprc, _lparam):
        mi = MONITORINFO()
        mi.cbSize = ctypes.sizeof(MONITORINFO)
        if ctypes.windll.user32.GetMonitorInfoW(hmon, ctypes.byref(mi)):
            w = mi.rcWork
            mons.append((w.left, w.top, w.right, w.bottom))
        return 1

    try:
        user32 = ctypes.windll.user32
        user32.GetMonitorInfoW.argtypes = [ctypes.c_void_p,
                                           ctypes.POINTER(MONITORINFO)]
        user32.EnumDisplayMonitors(None, None, proc_t(cb), 0)
    except Exception:
        pass

    if not mons:  # zaxira: faqat asosiy monitor
        try:
            r = RECT()
            ctypes.windll.user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(r), 0)
            mons.append((r.left, r.top, r.right, r.bottom))
        except Exception:
            pass
    return mons


def _mac_monitors():
    """macOS: NSScreen orqali har ekranning ish maydoni (pyobjc bo'lsa).

    `visibleFrame` menyu paneli va Dock'ni hisobga oladi. NSScreen'ning y o'qi
    pastdan yuqoriga, Tk'niki esa yuqoridan pastga -- shuning uchun eng baland
    ekranga nisbatan ag'dariladi.
    """
    try:
        from AppKit import NSScreen
    except Exception:
        return []

    screens = list(NSScreen.screens())
    if not screens:
        return []
    # global koordinata boshi: eng tepadagi ekranning yuqori chekkasi
    top = max(s.frame().origin.y + s.frame().size.height for s in screens)

    mons = []
    for s in screens:
        v = s.visibleFrame()
        left = int(v.origin.x)
        bottom = int(top - v.origin.y)          # ag'darilgach pastki chekka
        mons.append((left, bottom - int(v.size.height),
                     left + int(v.size.width), bottom))
    return mons


def _tk_monitor(root):
    """Zaxira: faqat asosiy ekran, Tk'ning o'z ma'lumotidan.

    `wm maxsize` -- oyna egallashi mumkin bo'lgan eng katta o'lcham, ya'ni
    macOS'da menyu paneli va Dock chegirilgani. Panel balandligini bilish
    uchun ko'rinmas oyna 0,0 ga qo'yiladi: tizim uni panel ostiga suradi.
    """
    top = 0
    if IS_MAC:
        try:
            probe = tk.Toplevel(root)
            probe.attributes("-alpha", 0.0)
            probe.geometry("40x40+0+0")
            probe.update_idletasks()
            top = max(0, probe.winfo_y())
            probe.destroy()
        except Exception:
            top = 25          # odatdagi menyu paneli balandligi
    _, max_h = root.wm_maxsize()
    return [(0, top, root.winfo_screenwidth(), top + max_h)]


def list_monitors(root=None):
    """Barcha monitorlarning ish maydonlari, chapdan o'ngga tartiblangan.

    Har biri (left, top, right, bottom) -- vazifalar paneli / Dock chegirilgan.
    """
    mons = _win_monitors() if IS_WIN else _mac_monitors() if IS_MAC else []
    if not mons and root is not None:
        mons = _tk_monitor(root)
    return sorted(mons)


def cursor_pos(root):
    """Sichqoncha kursorining global koordinatasi, topilmasa None."""
    if IS_WIN:
        try:
            pt = ctypes.wintypes.POINT()
            ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
            return pt.x, pt.y
        except Exception:
            return None
    try:
        return root.winfo_pointerxy()
    except Exception:
        return None


def read_state():
    """Claude Code hooklari yozgan holatni o'qiydi."""
    try:
        with open(STATE_FILE, encoding="utf-8") as fh:
            data = json.load(fh)
        state = data.get("state", "idle")
        ts = float(data.get("ts", 0))
        age = time.time() - ts
        # "kutyapti" -- diqqatni tortish uchun qisqa signal, cheksiz sakramaydi
        if state == "waiting" and age > WAIT_SEC:
            return "idle"
        if state == "working" and age > STALE_SEC:
            return "idle"
        return state
    except Exception:
        return "idle"


def float_window(win):
    """Ramkasiz, hamma narsa ustida turadigan, foni ko'rinmas oyna.

    Windows: bitta kalit rang butunlay ko'rinmas qilinadi.
    macOS: oynaning o'zi shaffof bo'ladi, kadrlar alfa kanali bilan chiziladi.
    """
    win.overrideredirect(True)
    win.attributes("-topmost", True)
    try:
        win.attributes("-transparent" if IS_MAC else "-transparentcolor",
                       True if IS_MAC else TRANS)
    except tk.TclError:
        pass
    win.configure(bg=TRANS)


def mix(c1, c2, t):
    """Ikki "#rrggbb" rangni aralashtiradi: t=0 -> c1, t=1 -> c2."""
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(int(v + (w - v) * t) for v, w in zip(a, b))


class Zzz:
    """Uxlayotgan maskot tepasida ko'tarilib so'nadigan "Z" harflari.

    Pet oynasi sprayt bo'yiga teng, tepasida joy yo'q -- shuning uchun
    pufak kabi alohida shaffof oynada chiziladi.
    """

    W = 62

    def __init__(self, root):
        self.win = tk.Toplevel(root)
        float_window(self.win)

        self.base_y = len(Z_GLYPH) * ZZZ_SCALE[1] / 2 + 2
        self.h = int(ZZZ_RISE + self.base_y * 2)
        self.canvas = tk.Canvas(self.win, width=self.W, height=self.h,
                                bg=TRANS, highlightthickness=0, bd=0)
        self.canvas.pack()

        # yo'lning har bosqichi uchun tayyor rasm -- har tikda qayta chizilmaydi
        self.imgs = [self._render(t / (ZZZ_STEPS - 1)) for t in range(ZZZ_STEPS)]
        self.items = [self.canvas.create_image(0, 0, anchor="c")
                      for _ in range(ZZZ_COUNT)]
        self.win.withdraw()
        self.visible = False

    def _render(self, t):
        """Yo'lning t nuqtasidagi Z: o'lchami kattalashib, rangi so'nib boradi."""
        k = round(ZZZ_SCALE[0] + (ZZZ_SCALE[1] - ZZZ_SCALE[0]) * t)
        color = mix(ZZZ_NEAR, ZZZ_FAR, t)
        img = tk.PhotoImage(width=len(Z_GLYPH[0]) * k, height=len(Z_GLYPH) * k)
        if not IS_MAC:      # kalit rang: fon aynan shu rangda bo'lishi kerak
            img.put(TRANS, to=(0, 0, img.width(), img.height()))
        for y, row in enumerate(Z_GLYPH):
            for x, ch in enumerate(row):
                if ch == "#":
                    img.put(color, to=(x * k, y * k, (x + 1) * k, (y + 1) * k))
        return img

    def show(self, cx, bottom_y, now):
        """cx -- markaz, bottom_y -- eng pastki Z turadigan y."""
        self.win.geometry(f"{self.W}x{self.h}"
                          f"+{int(cx - self.W / 2)}+{int(bottom_y - self.h)}")
        for i, item in enumerate(self.items):
            # har bir Z bir xil yo'lni bosadi, faqat fazasi surilgan
            p = (now / ZZZ_PERIOD + i / ZZZ_COUNT) % 1.0
            self.canvas.coords(
                item,
                self.W / 2 + math.sin(p * math.pi) * ZZZ_DRIFT,
                self.h - self.base_y - p * ZZZ_RISE)
            self.canvas.itemconfig(
                item, image=self.imgs[int(p * ZZZ_STEPS) % ZZZ_STEPS])
        if not self.visible:
            self.win.deiconify()
            self.win.attributes("-topmost", True)
            self.visible = True

    def hide(self):
        if self.visible:
            self.win.withdraw()
            self.visible = False


class Bubble:
    """Maskot boshi tepasidagi bulut -- alohida shaffof oyna."""

    BUMPS = (12, 8.5, 11, 9)    # bulut chetidagi doiralar radiusi, navbatlashadi
    STEP = 17               # ular markazlari orasidagi masofa
    MARGIN = 7              # matn bilan bulut ichki chegarasi orasidagi bo'shliq
    TAIL_R = (5, 3)         # pastga tushadigan dumcha doiralari
    TAIL_GAP = 3
    LINE = 2                # hoshiya qalinligi

    # Doiralar markazi matn to'rtburchagining MARGIN qadar kengaytirilgan
    # chekkasida turadi, shuning uchun matndan tashqi chekkagacha:
    # MARGIN + eng katta radius + hoshiya.
    PAD_X = PAD_Y = int(MARGIN + max(BUMPS) + LINE)

    def __init__(self, root):
        self.win = tk.Toplevel(root)
        float_window(self.win)
        self.canvas = tk.Canvas(self.win, bg=TRANS, highlightthickness=0, bd=0)
        self.canvas.pack()

        import tkinter.font as tkfont
        self.font = tkfont.Font(family=UI_FONT, size=9)
        self.text = None
        self.w = self.h = 0
        self.win.withdraw()
        self.visible = False

    def _parts(self, x0, y0, x1, y1):
        """Bulutni tashkil qiladigan bo'laklar: o'zak to'rtburchak + doiralar.

        Doiralar o'zakning to'rt chekkasi bo'ylab teriladi, radiusi navbat
        bilan o'zgaradi -- shundan kontur to'lqinlanib chiqadi. Qo'shni
        doiralar bir-birini yaxshigina qoplaydi, aks holda ichki yoylar
        ko'milmay qoladi.
        """
        yield self.canvas.create_rectangle, x0, y0, x1, y1

        def along(ax, ay, bx, by, phase):
            n = max(1, round(math.hypot(bx - ax, by - ay) / self.STEP))
            for i in range(n + 1):
                t = i / n
                r = self.BUMPS[(phase + i) % len(self.BUMPS)]
                cx, cy = ax + (bx - ax) * t, ay + (by - ay) * t
                yield self.canvas.create_oval, cx - r, cy - r, cx + r, cy + r

        # har chekka navbatning boshqa joyidan boshlanadi -- naqsh takrorlanmasin
        yield from along(x0, y0, x1, y0, 0)     # tepa
        yield from along(x0, y1, x1, y1, 2)     # tag
        yield from along(x0, y0, x0, y1, 1)     # chap
        yield from along(x1, y0, x1, y1, 3)     # o'ng

    def _cloud(self, x0, y0, x1, y1):
        """Bulutni chizadi.

        Avval hamma bo'lak hoshiyasi bilan chiziladi, so'ng har biri chiziq
        qalinligicha ichkariga siqib qayta bo'yaladi -- shunda bo'laklarning
        ichkarida qolgan yoylari ko'milib, faqat tashqi hoshiya ko'rinadi.
        """
        parts = list(self._parts(x0, y0, x1, y1))
        for fn, a, b, c, d in parts:
            fn(a, b, c, d, fill=BUBBLE_BG, outline=BUBBLE_LINE, width=self.LINE)
        g = self.LINE
        for fn, a, b, c, d in parts:
            fn(a + g, b + g, c - g, d - g, fill=BUBBLE_BG, outline="")

    def show(self, text, cx, bottom_y):
        """cx -- markaz, bottom_y -- dumcha uchi turadigan y."""
        if text != self.text:
            self.text = text
            tw = self.font.measure(text)
            th = self.font.metrics("linespace")
            self.w = tw + self.PAD_X * 2
            cloud_h = th + self.PAD_Y * 2
            tail = sum(2 * r + self.TAIL_GAP for r in self.TAIL_R)
            self.h = int(cloud_h + tail)
            self.canvas.config(width=self.w, height=self.h)
            self.canvas.delete("all")

            # dumcha -- bulutdan maskot tomon tushadigan kichrayuvchi doiralar
            y = cloud_h
            for i, r in enumerate(self.TAIL_R):
                x = self.w / 2 - i * 5
                self.canvas.create_oval(x - r, y, x + r, y + 2 * r,
                                        fill=BUBBLE_BG, outline=BUBBLE_LINE,
                                        width=self.LINE)
                y += 2 * r + self.TAIL_GAP

            # o'zak matndan MARGIN qadar keng: bulutning ichkariga botgan
            # joylari ham matnga tegib ketmasin
            m = self.MARGIN
            self._cloud(self.PAD_X - m, self.PAD_Y - m,
                        self.w - self.PAD_X + m, self.PAD_Y + th + m)
            self.canvas.create_text(self.w / 2, self.PAD_Y + th / 2, text=text,
                                    fill=BUBBLE_TEXT, font=self.font)
        x = int(cx - self.w / 2)
        self.win.geometry(f"{self.w}x{self.h}+{x}+{int(bottom_y - self.h)}")
        if not self.visible:
            self.win.deiconify()
            self.win.attributes("-topmost", True)
            self.visible = True

    def hide(self):
        if self.visible:
            self.win.withdraw()
            self.visible = False


class Pet:
    def __init__(self):
        make_dpi_aware()
        self.root = tk.Tk()
        self.root.withdraw()

        self.frames = self._load_frames()
        self.w, self.h = self.frames["stand"].width(), self.frames["stand"].height()

        self.mons = list_monitors(self.root)
        self._span()

        self.win = tk.Toplevel(self.root)
        float_window(self.win)

        self.canvas = tk.Canvas(self.win, width=self.w, height=self.h,
                                bg=TRANS, highlightthickness=0, bd=0)
        self.canvas.pack()
        self.item = self.canvas.create_image(0, 0, anchor="nw",
                                             image=self.frames["stand"])

        self.x = float(self.left + self.right) / 2 - self.w / 2
        self.ground = self._floor_at(self.x + self.w / 2)
        self.target_ground = self.ground
        self.y_off = 0.0
        self.dir = 1
        self.tick = 0
        self.frame_i = 0
        self.state = "idle"
        self.dragging = False
        self.blink_until = 0.0
        self.next_blink = time.time() + random.uniform(3, 7)
        self.idle_walk_until = 0.0
        self.next_idle_walk = time.time() + random.uniform(6, 14)
        self.hop_phase = 0.0

        # fizika holati
        self.vx = self.vy = 0.0
        self.flying = False
        self.squash_left = 0
        self.drag_trail = []

        # kursor
        self.poke_until = 0.0
        self.happy_until = 0.0
        self.poke_arm = "wave_r"

        # ovoz
        self.sound_var = tk.BooleanVar(master=self.root, value=SOUND_ON)
        self._sound_block = 0.0
        self._hop_n = -1
        self.next_idle_sound = time.time() + random.uniform(
            IDLE_SOUND_MIN, IDLE_SOUND_MAX)

        # ish paytidagi faoliyat
        self.act = "walk"
        self.act_until = 0.0
        self.act_phase = 0.0
        self.wave_style = "wave"

        self.verbs = load_verbs()
        self.bubble = Bubble(self.root)
        self.zzz = Zzz(self.root)
        self.verb = random.choice(self.verbs)
        self.next_verb = 0.0
        self.idle_since = time.time()

        # bo'sh turgandagi gaplar
        self.talk_text = ""
        self.talk_until = 0.0
        self.next_talk = time.time() + random.uniform(TALK_MIN, TALK_MAX)

        self._bind()
        self._place()
        self._reassert_topmost()
        self._refresh_monitors()
        self._loop()

    # ── yuklash ──────────────────────────────────────────────────────────
    def _load_frames(self):
        """Kadrlar tayyor holda: Windows'da kalit rangli, macOS'da alfali."""
        frames = {}
        names = ("stand", "blink", "sleep", "walk1", "walk2", "walk3",
                 "fall", "squash", "peck", "cheer",
                 "wave", "wave_l", "wave_r", "sway_l", "sway_r")
        for name in names + tuple("happy_" + n for n in HAPPY_FRAMES):
            for suffix in ("", "_flip"):
                key = name + suffix
                frames[key] = tk.PhotoImage(
                    file=os.path.join(FRAME_DIR, key + ".png"))
        return frames

    # ── monitorlar ───────────────────────────────────────────────────────
    def _span(self):
        """Barcha monitorlarni qamrab oluvchi umumiy gorizontal chegara."""
        if not self.mons:
            self.mons = [(0, 0, self.root.winfo_screenwidth(),
                          self.root.winfo_screenheight())]
        self.left = min(m[0] for m in self.mons)
        self.right = max(m[2] for m in self.mons)
        self.bottom = max(m[3] for m in self.mons)

    def _floor_at(self, cx):
        """Berilgan nuqtadagi monitorning poli (pet oynasining y koordinatasi)."""
        for m in self.mons:
            if m[0] <= cx < m[2]:
                return m[3] - self.h
        # monitorlar orasidagi bo'shliq -- eng yaqinining polini olamiz
        nearest = min(self.mons, key=lambda m: min(abs(cx - m[0]), abs(cx - m[2])))
        return nearest[3] - self.h

    def _refresh_monitors(self):
        """Monitor ulansa/uzilsa chegaralarni yangilaydi."""
        mons = list_monitors(self.root)
        if mons and mons != self.mons:
            self.mons = mons
            self._span()
            self.x = max(self.left, min(self.right - self.w, self.x))
        self.root.after(10000, self._refresh_monitors)

    def _settle_ground(self):
        """Polni joriy monitornikiga yumshoq moslashtiradi (zinapoya effekti)."""
        self.target_ground = self._floor_at(self.x + self.w / 2)
        d = self.target_ground - self.ground
        if abs(d) <= GROUND_EASE:
            self.ground = self.target_ground
        else:
            self.ground += GROUND_EASE if d > 0 else -GROUND_EASE

    # ── hodisalar ────────────────────────────────────────────────────────
    def _bind(self):
        self.canvas.bind("<ButtonPress-1>", self._drag_start)
        self.canvas.bind("<B1-Motion>", self._drag_move)
        self.canvas.bind("<ButtonRelease-1>", self._drag_end)
        # o'ng tugma: Windows'da 3-tugma, macOS'da Tk uni 2-tugma deb beradi
        for seq in ("<Button-3>",) + (("<Button-2>",) if IS_MAC else ()):
            self.canvas.bind(seq, self._menu)

        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="Yerga qaytar", command=self._reset_pos)
        self.menu.add_checkbutton(label="Ovoz", variable=self.sound_var)
        self.menu.add_separator()
        self.menu.add_command(label="Chiqish", command=self.root.destroy)

    def _drag_start(self, e):
        self.dragging = True
        self.idle_since = time.time()   # ushlansa uyg'onadi
        self.flying = False
        self.vx = self.vy = 0.0
        self._grab = (e.x, e.y)
        self._press = (self.win.winfo_pointerx(), self.win.winfo_pointery(),
                       time.time())
        self.drag_trail = [(time.time(), self.x, self.ground)]

    def _drag_move(self, e):
        gx = self.win.winfo_pointerx() - self._grab[0]
        gy = self.win.winfo_pointery() - self._grab[1]
        self.x = float(gx)
        self.ground = float(gy)
        self.y_off = 0
        self._show("fall")
        # tezlikni hisoblash uchun oxirgi izlarni saqlaymiz
        self.drag_trail.append((time.time(), self.x, self.ground))
        if len(self.drag_trail) > 12:
            self.drag_trail.pop(0)
        self._place()

    def _drag_end(self, _e):
        self.dragging = False
        px, py, pt = self._press
        moved = abs(self.win.winfo_pointerx() - px) + abs(
            self.win.winfo_pointery() - py)

        if moved < CLICK_PX and time.time() - pt < 0.5:
            self._poke()          # sudralmadi -- oddiy bosish
            return

        self.vx, self.vy = self._trail_velocity()
        self.flying = True
        if abs(self.vx) + abs(self.vy) > 6:
            self._play("throw")       # sezilarli kuch bilan uloqtirildi

    def _trail_velocity(self):
        """Sudrash izidan uloqtirish tezligini hisoblaydi (px/tik)."""
        now = time.time()
        recent = [s for s in self.drag_trail if now - s[0] < 0.14]
        if len(recent) < 2:
            return 0.0, 0.0
        t0, x0, y0 = recent[0]
        t1, x1, y1 = recent[-1]
        dt = t1 - t0
        if dt <= 0:
            return 0.0, 0.0
        scale = TICK_MS / 1000.0
        vx = (x1 - x0) / dt * scale
        vy = (y1 - y0) / dt * scale
        clamp = lambda v: max(-THROW_MAX, min(THROW_MAX, v))
        return clamp(vx), clamp(vy)

    def _poke(self):
        """Ustiga bosilganda bir qo'lini ko'tarib "Nima gap?" deb sapchiydi."""
        self.poke_until = time.time() + POKE_SEC
        self.happy_until = time.time() + HAPPY_SEC
        self.poke_arm = random.choice(("wave_l", "wave_r"))
        self.hop_phase = 0.0
        self._hop_n = -1
        self.idle_since = time.time()
        self._play("poke")

    def _reset_pos(self):
        """Asosiy monitorning o'rtasiga, poliga qaytaradi."""
        primary = next((m for m in self.mons if m[0] <= 0 < m[2]), self.mons[0])
        self.x = float(primary[0] + primary[2]) / 2 - self.w / 2
        self.ground = self.target_ground = primary[3] - self.h
        self._place()

    def _menu(self, e):
        try:
            self.menu.tk_popup(e.x_root, e.y_root)
        finally:
            self.menu.grab_release()

    # ── chizish ──────────────────────────────────────────────────────────
    def _place(self):
        y = self.ground + self.y_off
        self.win.geometry(f"+{int(self.x)}+{int(y)}")
        if self.bubble.visible:
            self._place_bubble(y)

    def _place_bubble(self, y, text=None):
        text = text or self.bubble.text
        if not text:
            return
        cx = self.x + self.w / 2
        half = max(self.bubble.w, self.font_guess(text)) / 2
        # ekran chetidan chiqib ketmasin
        cx = max(self.left + half, min(self.right - half, cx))
        self.bubble.show(text, cx, y + 6)

    def font_guess(self, text):
        """Matn hali chizilmagan bo'lsa ham taxminiy kenglik."""
        return self.bubble.font.measure(text) + Bubble.PAD_X * 2

    def _say(self, text):
        self._place_bubble(self.ground + self.y_off, text)

    def _show(self, name):
        # xursand paytda kadrning kulgan nusxasi bo'lsa -- o'shani ko'rsatamiz
        if time.time() < self.happy_until and name in HAPPY_FRAMES:
            name = "happy_" + name
        key = name + ("" if self.dir > 0 else "_flip")
        self.canvas.itemconfig(self.item, image=self.frames[key])

    def _reassert_topmost(self):
        try:
            self.win.attributes("-topmost", True)
        except Exception:
            pass
        self.root.after(5000, self._reassert_topmost)

    # ── ovoz ─────────────────────────────────────────────────────────────
    def _play(self, name):
        """Harakatga mos qisqa tovush -- asinxron, hech qachon bloklamaydi.

        Windows'da winsound, macOS'da `afplay` -- ikkalasi ham WAV faylni
        o'qiydi va fonda chaladi. Ovoz o'chirilgan yoki chaladigan narsa
        topilmasa jim o'tadi; ketma-ket tovushlar SOUND_GAP orqali
        chegaralanadi (bir-birini kesmasin).
        """
        if not self.sound_var.get():
            return
        now = time.time()
        if now < self._sound_block:
            return
        path = os.path.join(SOUNDS, name + ".wav")
        if not os.path.exists(path):
            return
        try:
            if winsound is not None:
                winsound.PlaySound(
                    path, winsound.SND_FILENAME | winsound.SND_ASYNC
                    | winsound.SND_NODEFAULT)
            elif AFPLAY:
                # chalib bo'lgach o'zi tugaydi; kutmaymiz, zombi ham qolmaydi
                # kutmaymiz; tugaganini Python keyingi Popen'da o'zi yig'ishtiradi
                subprocess.Popen([AFPLAY, path], stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL)
            else:
                return
            self._sound_block = now + SOUND_GAP
        except Exception:
            pass

    def _hop_started(self):
        """Sakrashning yangi bosqichi boshlandimi (har "boing" uchun bir marta)."""
        n = int(self.hop_phase / math.pi)
        started = n != self._hop_n
        self._hop_n = n
        return started

    # ── asosiy sikl ──────────────────────────────────────────────────────
    def _loop(self):
        self.tick += 1
        if self.tick % 10 == 0:
            self.state = read_state()

        if self.squash_left > 0:
            self.squash_left -= 1

        if not self.dragging:
            if self.flying:
                self._do_physics()          # uloqtirildi -- fizika boshqaradi
            else:
                if self.squash_left > 0:
                    self._show("squash")    # yerga urilgandan keyingi siqilish
                elif time.time() < self.poke_until:
                    self._do_poke()
                elif self.state == "working":
                    self.idle_since = time.time()
                    # ishdan qaytgach darrov gapirib yubormasin
                    self.talk_until = 0.0
                    self.next_talk = self.idle_since + random.uniform(
                        TALK_MIN, TALK_MAX)
                    self._do_working()
                elif self.state == "waiting":
                    self.idle_since = time.time()
                    self._do_hop()
                else:
                    self._do_idle()
                self._settle_ground()
            self._place()

        self._update_bubble()
        self.root.after(TICK_MS, self._loop)

    def _update_bubble(self):
        """Boshi tepasidagi yozuvni holatga qarab yangilaydi."""
        now = time.time()
        asleep = False
        if self.flying:
            self.bubble.hide()
        elif now < self.poke_until:
            self._say("Nima gap?")
        elif self.state == "working":
            if now >= self.next_verb:
                self.verb = random.choice(self.verbs)
                self.next_verb = now + VERB_SEC
            self._say(self.verb + "...")
        elif self.state == "waiting":
            self._say("Javobingizni kutyapman")
        elif now - self.idle_since > SLEEP_AFTER:
            asleep = True          # gap pufagi emas -- tepasida "Z" uchadi
            self.bubble.hide()
        elif now < self.talk_until:
            self._say(self.talk_text)
        elif now >= self.next_talk:
            self.talk_text = pick_phrase(now - self.idle_since)
            self.talk_until = now + TALK_SEC
            self.happy_until = self.talk_until   # gapirayotganda kulib turadi
            self.next_talk = self.talk_until + random.uniform(TALK_MIN, TALK_MAX)
            self._say(self.talk_text)
        else:
            self.bubble.hide()
            self.next_verb = 0.0

        if asleep:
            self._place_zzz(now)
        else:
            self.zzz.hide()

    def _place_zzz(self, now):
        """Z harflarini yotgan maskotning tepasiga qo'yadi."""
        half = self.zzz.W / 2
        cx = self.x + self.w / 2
        cx = max(self.left + half, min(self.right - half, cx))
        self.zzz.show(cx, self.ground + self.y_off + self.h - ZZZ_LIFT, now)

    def _step_frame(self):
        if self.tick % FRAME_TICKS == 0:
            self.frame_i = (self.frame_i + 1) % len(WALK_CYCLE)
        self._show(WALK_CYCLE[self.frame_i])

    def _move(self, speed):
        self.x += self.dir * speed
        if self.x <= self.left:
            self.x = self.left
            self.dir = 1
        elif self.x >= self.right - self.w:
            self.x = self.right - self.w
            self.dir = -1

    def _do_walk(self, speed, bob=False):
        self._move(speed)
        self._step_frame()
        # yurganda yengil tebranish -- qadam bilan bir maromda
        self.y_off = -BOB_PX if (bob and self.frame_i % 2 == 1) else 0

    # ── ish paytidagi faoliyatlar ────────────────────────────────────────
    def _do_working(self):
        """Har necha soniyada boshqa ishga o'tadi -- faqat yuravermaydi."""
        now = time.time()
        if now >= self.act_until:
            self.act = random.choice(ACTIVITIES)
            self.act_until = now + random.uniform(ACT_MIN, ACT_MAX)
            self.act_phase = 0.0
            if self.act == "walk":
                self.dir = random.choice((-1, 1))
            elif self.act == "wave":
                self.wave_style = random.choice(WAVE_STYLES)
            elif self.act == "cheer":
                self._play("cheer")
            # quvonch va salomlashish -- faoliyat oxirigacha kulib turadi
            if self.act in ("cheer", "wave"):
                self.happy_until = self.act_until
        getattr(self, "_act_" + self.act)()

    def _act_walk(self):
        self._do_walk(WALK_SPEED, bob=True)

    def _act_peck(self):
        """Boshini egib-ko'tarib "cho'qiydi" -- kod terayotgandek."""
        self.y_off = 0
        self._show("peck" if (self.tick // 4) % 2 else "stand")

    def _act_wave(self):
        """Qo'l silkitadi -- ikkalasini, bittasini yoki navbat bilan."""
        self.y_off = 0
        n = self.tick // 6
        if self.wave_style == "alt":
            up = "wave_l" if (n // 2) % 2 else "wave_r"
        else:
            up = self.wave_style
        self._show(up if n % 2 else "stand")

    def _act_think(self):
        """Sekin u yon-bu yon chayqaladi."""
        self.y_off = 0
        self._show("sway_l" if (self.tick // 14) % 2 else "sway_r")

    def _act_cheer(self):
        """Qo'lini ko'tarib joyida sakraydi."""
        self.act_phase += 0.26
        lift = abs(math.sin(self.act_phase))
        self.y_off = -lift * 14
        self._show("cheer" if lift > 0.25 else "stand")

    def _do_physics(self):
        """Uloqtirilgandan keyin: tortishish, havo qarshiligi, sakrash."""
        self.y_off = 0
        self.vy += GRAVITY
        self.vx *= AIR_DRAG
        self.x += self.vx
        self.ground += self.vy

        # yon devorlar (barcha monitorlarning umumiy chegarasi)
        if self.x <= self.left:
            self.x = self.left
            self.vx = abs(self.vx) * WALL_BOUNCE
        elif self.x >= self.right - self.w:
            self.x = self.right - self.w
            self.vx = -abs(self.vx) * WALL_BOUNCE

        # shift -- boshi bilan urilib qaytadi
        top = min(m[1] for m in self.mons)
        if self.ground < top:
            self.ground = top
            self.vy = abs(self.vy) * BOUNCE

        floor = self._floor_at(self.x + self.w / 2)
        if self.ground >= floor:
            impact = self.vy                # urilishdan oldingi pastga tezlik
            self.ground = floor
            if abs(self.vy) < STOP_V:
                self.flying = False        # tinchidi
                self.vx = self.vy = 0.0
                self.squash_left = SQUASH_TICKS
                self.target_ground = floor
            else:
                self.vy = -abs(self.vy) * BOUNCE
                self.vx *= 0.8
                self.squash_left = SQUASH_TICKS
            if impact > 2.0:
                self._play("land")         # sezilarli kuch bilan yerga urildi

        if self.vx:
            self.dir = 1 if self.vx > 0 else -1
        self._show("squash" if self.squash_left > 0 else "fall")

    def _do_poke(self):
        """Bosilganidan keyingi hayajon -- bir qo'li ko'tarilgan ko'yi sapchiydi."""
        self.hop_phase += 0.32
        self.y_off = -abs(math.sin(self.hop_phase)) * 11
        self._show(self.poke_arm)

    def _face_cursor(self):
        """Kursor yaqin bo'lsa, o'sha tomonga o'giriladi."""
        pos = cursor_pos(self.root)
        if pos is None:
            return False
        px, py = pos
        cx = self.x + self.w / 2
        if abs(px - cx) > NOTICE_PX or abs(py - (self.ground + self.h / 2)) > NOTICE_PX:
            return False
        self.dir = 1 if px >= cx else -1
        return True

    def _do_hop(self):
        self.hop_phase += 0.22
        self.y_off = -abs(math.sin(self.hop_phase)) * 15
        self._show("stand")
        if self._hop_started():
            self._play("hop")

    def _do_idle(self):
        now = time.time()
        self.y_off = 0

        # oddiy holatda turganda goh-goh yumshoq "chirp" (uxlayotganda jim)
        if now >= self.next_idle_sound:
            self.next_idle_sound = now + random.uniform(
                IDLE_SOUND_MIN, IDLE_SOUND_MAX)
            if now - self.idle_since <= SLEEP_AFTER:
                self._play("idle")

        near = self._face_cursor()

        # uzoq bo'sh tursa yotib uxlaydi -- lekin kursor yaqinlashsa uyg'onadi
        if now - self.idle_since > SLEEP_AFTER:
            if not near:
                self._show("sleep")
                return
            self.idle_since = now

        # gapirayotganda joyida turib qo'l silkitadi
        if now < self.talk_until:
            self.idle_walk_until = 0.0
            self._show("wave" if (self.tick // 8) % 2 else "stand")
            return

        # kursor yaqin bo'lsa sayrni to'xtatib, unga qarab turadi
        if near:
            self.idle_walk_until = 0.0
            self._show("blink" if now < self.blink_until else "stand")
            if now >= self.next_blink:
                self.blink_until = now + 0.14
                self.next_blink = now + random.uniform(3, 8)
            return

        if now < self.idle_walk_until:
            self._do_walk(IDLE_SPEED)
            return
        if now >= self.next_idle_walk:
            self.idle_walk_until = now + random.uniform(1.5, 4.0)
            self.next_idle_walk = self.idle_walk_until + random.uniform(8, 20)
            self.dir = random.choice((-1, 1))
            return

        if now < self.blink_until:
            self._show("blink")
            return
        if now >= self.next_blink:
            self.blink_until = now + 0.14
            self.next_blink = now + random.uniform(3, 8)
            return
        self._show("stand")

    def run(self):
        self.root.mainloop()


def write_pid():
    """O'chirgich pet'ni topib to'xtata olishi uchun PID yozib qo'yamiz."""
    try:
        os.makedirs(STATE_DIR, exist_ok=True)
        with open(PID_FILE, "w", encoding="utf-8") as fh:
            fh.write(str(os.getpid()))
    except Exception:
        pass


if __name__ == "__main__":
    if not acquire_lock():
        sys.exit(0)  # pet allaqachon ishlayapti
    write_pid()
    Pet().run()
