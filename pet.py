"""Claude desktop pet -- ekran bo'ylab yuradigan maskot.

Claude Code ishlayotganda yuradi va boshi tepasida nima qilayotganini aytadi,
bo'sh turganda tik turib ko'z qisadi, uzoq bo'sh qolsa uxlaydi,
javobingizni kutayotganda sakraydi.

Ishga tushirish:  pythonw pet.py
Chiqish:          maskotga o'ng tugma -> Chiqish
Ko'chirish:       chap tugma bilan sudrang
"""
import ctypes
import ctypes.wintypes
import json
import math
import os
import random
import socket
import sys
import time
import tkinter as tk

try:
    import winsound          # faqat Windows -- ovoz effektlari uchun
except Exception:
    winsound = None

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
STATE_DIR = os.path.join(os.environ.get("TEMP", "/tmp"), "claude-pet")
STATE_FILE = os.path.join(STATE_DIR, "state.json")
PID_FILE = os.path.join(STATE_DIR, "pet.pid")

TRANS = "#ff00ff"       # shaffof qilinadigan rang
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


class RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long),
                ("right", ctypes.c_long), ("bottom", ctypes.c_long)]


class MONITORINFO(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_ulong), ("rcMonitor", RECT),
                ("rcWork", RECT), ("dwFlags", ctypes.c_ulong)]


def make_dpi_aware():
    """Har monitor uchun alohida DPI -- koordinatalar haqiqiy piksellarda bo'ladi."""
    for fn in (lambda: ctypes.windll.shcore.SetProcessDpiAwareness(2),
               lambda: ctypes.windll.shcore.SetProcessDpiAwareness(1),
               lambda: ctypes.windll.user32.SetProcessDPIAware()):
        try:
            fn()
            return
        except Exception:
            continue


def list_monitors():
    """Barcha monitorlarning ish maydonlari, chapdan o'ngga tartiblangan.

    Har biri (left, top, right, bottom) -- vazifalar paneli hisobga olingan.
    """
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
    return sorted(mons)


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


class Bubble:
    """Maskot boshi tepasidagi gap pufagi -- alohida shaffof oyna."""

    PAD_X, PAD_Y, TAIL = 11, 6, 7

    def __init__(self, root):
        self.win = tk.Toplevel(root)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.attributes("-transparentcolor", TRANS)
        self.win.configure(bg=TRANS)
        self.canvas = tk.Canvas(self.win, bg=TRANS, highlightthickness=0, bd=0)
        self.canvas.pack()

        import tkinter.font as tkfont
        self.font = tkfont.Font(family="Segoe UI", size=9)
        self.text = None
        self.w = self.h = 0
        self.win.withdraw()
        self.visible = False

    def _rounded(self, x0, y0, x1, y1, r):
        pts = [x0 + r, y0, x1 - r, y0, x1, y0, x1, y0 + r, x1, y1 - r, x1, y1,
               x1 - r, y1, x0 + r, y1, x0, y1, x0, y1 - r, x0, y0 + r, x0, y0]
        self.canvas.create_polygon(pts, smooth=True, splinesteps=12,
                                   fill=BUBBLE_BG, outline=BUBBLE_LINE, width=2)

    def show(self, text, cx, bottom_y):
        """cx -- markaz, bottom_y -- pufak pastki chekkasi turadigan y."""
        if text != self.text:
            self.text = text
            tw = self.font.measure(text)
            th = self.font.metrics("linespace")
            self.w = tw + self.PAD_X * 2
            self.h = th + self.PAD_Y * 2 + self.TAIL
            self.canvas.config(width=self.w, height=self.h)
            self.canvas.delete("all")
            body_b = self.h - self.TAIL
            self._rounded(1, 1, self.w - 1, body_b, 9)
            # pastga qaragan uchburchak dumcha
            mid = self.w / 2
            self.canvas.create_polygon(
                mid - 6, body_b - 1, mid + 6, body_b - 1, mid, self.h - 1,
                fill=BUBBLE_BG, outline=BUBBLE_LINE, width=2)
            self.canvas.create_polygon(
                mid - 4, body_b - 2, mid + 4, body_b - 2, mid, self.h - 4,
                fill=BUBBLE_BG, outline=BUBBLE_BG)
            self.canvas.create_text(self.w / 2, body_b / 2 + 1, text=text,
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

        self.mons = list_monitors()
        self._span()

        self.win = tk.Toplevel(self.root)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.attributes("-transparentcolor", TRANS)
        self.win.configure(bg=TRANS)

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

        self.verbs = load_verbs()
        self.bubble = Bubble(self.root)
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
        """Kadrlar tayyor holda -- kalit rang fonga yopishtirilgan (flat/)."""
        frames = {}
        for name in ("stand", "blink", "walk1", "walk2", "walk3",
                     "fall", "squash", "peck", "wave", "cheer",
                     "sway_l", "sway_r"):
            for suffix in ("", "_flip"):
                key = name + suffix
                frames[key] = tk.PhotoImage(
                    file=os.path.join(SPRITES, "flat", key + ".png"))
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
        mons = list_monitors()
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
        self.canvas.bind("<Button-3>", self._menu)

        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="Yerga qaytar", command=self._reset_pos)
        self.menu.add_checkbutton(label="Ovoz", variable=self.sound_var)
        self.menu.add_separator()
        self.menu.add_command(label="Chiqish", command=self.root.destroy)

    def _drag_start(self, e):
        self.dragging = True
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
        """Ustiga bosilganda sapchib tushadi."""
        self.poke_until = time.time() + POKE_SEC
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

        Ovoz o'chirilgan yoki winsound yo'q bo'lsa jim o'tadi; ketma-ket
        tovushlar SOUND_GAP orqali chegaralanadi (bir-birini kesmasin).
        """
        if winsound is None or not self.sound_var.get():
            return
        now = time.time()
        if now < self._sound_block:
            return
        path = os.path.join(SOUNDS, name + ".wav")
        if not os.path.exists(path):
            return
        try:
            winsound.PlaySound(
                path,
                winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT)
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
            self._say("z z z")
        elif now < self.talk_until:
            self._say(self.talk_text)
        elif now >= self.next_talk:
            self.talk_text = pick_phrase(now - self.idle_since)
            self.talk_until = now + TALK_SEC
            self.next_talk = self.talk_until + random.uniform(TALK_MIN, TALK_MAX)
            self._say(self.talk_text)
        else:
            self.bubble.hide()
            self.next_verb = 0.0

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
            elif self.act == "cheer":
                self._play("cheer")
        getattr(self, "_act_" + self.act)()

    def _act_walk(self):
        self._do_walk(WALK_SPEED, bob=True)

    def _act_peck(self):
        """Boshini egib-ko'tarib "cho'qiydi" -- kod terayotgandek."""
        self.y_off = 0
        self._show("peck" if (self.tick // 4) % 2 else "stand")

    def _act_wave(self):
        """Qo'llarini ko'tarib-tushiradi."""
        self.y_off = 0
        self._show("wave" if (self.tick // 6) % 2 else "stand")

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
        """Bosilganidan keyingi hayajon -- joyida sapchiydi."""
        self.hop_phase += 0.32
        self.y_off = -abs(math.sin(self.hop_phase)) * 11
        self._show("stand")

    def _face_cursor(self):
        """Kursor yaqin bo'lsa, o'sha tomonga o'giriladi."""
        try:
            pt = ctypes.wintypes.POINT()
            ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
        except Exception:
            return False
        cx = self.x + self.w / 2
        if abs(pt.x - cx) > NOTICE_PX or abs(pt.y - (self.ground + self.h / 2)) > NOTICE_PX:
            return False
        self.dir = 1 if pt.x >= cx else -1
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

        # uzoq bo'sh tursa uxlaydi -- lekin kursor yaqinlashsa uyg'onadi
        if now - self.idle_since > SLEEP_AFTER:
            if not near:
                self._show("blink")
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
