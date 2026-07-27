"""Claude maskotidan desktop-pet uchun sprayt kadrlarini yasaydi.

grid.json ichida asl rasmning piksellari bor (PNG dekodlangan holda).
Bu skript bir marta ishlatiladi -- natija sprites/ papkasiga tushadi.
"""
import json
import os
from collections import deque

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "sprites")

SCALE = 2
BBOX = (24, 9, 81, 49)          # asl rasmda maskotning chegarasi

# Kadr atrofidagi bo'shliq: egilish/aylanishda burchaklar qirqilmasligi uchun.
# Pastda bo'shliq yo'q -- oyoqlar kadr tubida turadi, shunda pol hisobi o'zgarmaydi.
PAD_X, PAD_TOP = 7, 7

HEAD_ROWS = (0, 16)             # bosh qatorlari (kesilgan rasmda)
HEAD_X = (7, 50)                # bosh/tana kengligi -- bundan tashqarisi qo'l uchi
ARM_ROWS = (16, 24)             # qo'llar qatorlari
LEG_ROWS = (32, 40)             # kesilgan rasmda oyoq qatorlari
LEG_L = (10, 22)                # chap oyoq ustunlari
LEG_R = (35, 46)                # o'ng oyoq ustunlari
HEAD_INNER = (1, 15)            # kalla ichi: tepa konturi bilan tag chizig'i orasi
EYE_LIFT = 3                    # ko'zni tag chizig'idan shuncha piksel uzadi
SMILE_WIDEN = 1                 # kulgan ko'z ("^") ochiq ko'zdan shuncha keng
SMILE_THICK = 2                 # "^" chizig'ining qalinligi
SLEEP_ROWS = (16, 40)           # yotgan gavda shu qatorlardan yig'iladi
SHUT_EYE_WIDEN = 2              # yumuq ko'z ochiq ko'zdan shuncha keng
SHUT_EYE_H = 3                  # yumuq ko'z chizig'ining qalinligi

BG = (25, 26, 28)
BG_TOL = 14

# Asl rasm terminal skrinshotidan olingan, shuning uchun tanada har belgi-katak
# chegarasida tikka chiziq qolgan. Ranglarni ikkiga ajratib tekislaymiz:
# yorug'lari -- tana, qorong'ilari -- kontur va ko'z. Ikki guruh orasidagi
# eng katta bo'shliq 96 va 109 yorqinliklari orasida, chegarani o'shanga qo'yamiz.
BODY = (215, 119, 87, 255)
INK = (0, 0, 0, 255)
INK_MAX_LUM = 102


def load_source(grid_path):
    with open(grid_path, encoding="utf-8") as fh:
        data = json.load(fh)
    w, h, grid = data["w"], data["h"], data["grid"]
    img = Image.new("RGBA", (w, h))
    img.putdata([tuple(p) for row in grid for p in row])
    return img


def strip_background(img):
    """Chetdan boshlab fon rangini shaffofga aylantiradi (ko'zlarga tegmaydi)."""
    w, h = img.size
    px = img.load()

    def is_bg(x, y):
        r, g, b, _ = px[x, y]
        return (abs(r - BG[0]) <= BG_TOL
                and abs(g - BG[1]) <= BG_TOL
                and abs(b - BG[2]) <= BG_TOL)

    seen = [[False] * w for _ in range(h)]
    q = deque()
    for x in range(w):
        for y in (0, h - 1):
            if is_bg(x, y) and not seen[y][x]:
                seen[y][x] = True
                q.append((x, y))
    for y in range(h):
        for x in (0, w - 1):
            if is_bg(x, y) and not seen[y][x]:
                seen[y][x] = True
                q.append((x, y))

    while q:
        x, y = q.popleft()
        px[x, y] = (0, 0, 0, 0)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and not seen[ny][nx] and is_bg(nx, ny):
                seen[ny][nx] = True
                q.append((nx, ny))
    return img


def flatten(img):
    """Katak chiziqlarini yo'qotadi -- tana bir tekis, chekkalari toza kontur."""
    w, h = img.size
    px = img.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if not a:
                continue
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            px[x, y] = INK if lum <= INK_MAX_LUM else BODY
    return img


def find_eyes(img):
    """Kalla ichidagi qora dog'larni -- ko'zlarni -- topadi.

    Chegaralar qo'lda yozilmaydi, shuning uchun ko'z ko'chsa `blink` ham
    o'z-o'zidan ergashadi. Kalla ichida ko'zdan boshqa qora narsa yo'q.
    """
    px = img.load()
    xs = range(HEAD_X[0] + 1, HEAD_X[1] - 1)
    pts = [(x, y) for x in xs for y in range(*HEAD_INNER) if px[x, y] == INK]
    if not pts:
        return []

    runs, run = [], []
    for x in sorted({x for x, _ in pts}):
        if run and x > run[-1] + 1:
            runs.append(run)
            run = []
        run.append(x)
    runs.append(run)

    boxes = []
    for cols in runs:
        ys = [y for x, y in pts if cols[0] <= x <= cols[-1]]
        boxes.append((cols[0], cols[-1] + 1, min(ys), max(ys) + 1))
    return boxes


def raise_eyes(img, dy=EYE_LIFT):
    """Ko'zni yuqoriga suradi -- kalla tubidagi chiziqqa tegib turmasin."""
    for x0, x1, y0, y1 in find_eyes(img):
        eye = img.crop((x0, y0, x1, y1))
        img.paste(BODY, (x0, y0, x1, y1))
        img.paste(eye, (x0, y0 - dy))
    return img


def smile(base):
    """Kuladigan kayfiyat -- ochiq ko'z o'rniga "^" belgisi qoladi.

    "^" ochiq ko'zning o'rniga markazlashadi, balandligi kengligidan kelib
    chiqadi -- shunda SMILE_WIDEN o'zgarsa ham burchak bir xil qiya bo'ladi.
    """
    img = base.copy()
    px = img.load()
    for x0, x1, y0, y1 in find_eyes(img):
        img.paste(BODY, (x0, y0, x1, y1))
        x0 = max(0, x0 - SMILE_WIDEN)
        x1 = min(img.width, x1 + SMILE_WIDEN)
        w = x1 - x0
        rows = (w + 1) // 2 + SMILE_THICK - 1
        top = y0 + ((y1 - y0) - rows) // 2
        mid = (w - 1) / 2.0
        for i in range(w):
            y = top + int(abs(i - mid))
            for t in range(SMILE_THICK):
                px[x0 + i, y + t] = INK
    return img


def shut_eye(img, x0, x1, top):
    """Yumuq ko'z chizig'i -- ochiq ko'z o'rniga, undan kengroq va qalinroq."""
    img.paste(INK, (max(0, x0 - SHUT_EYE_WIDEN), top,
                    min(img.width, x1 + SHUT_EYE_WIDEN), top + SHUT_EYE_H))


def sleeping(base):
    """Yotgan holat -- gavdaning pastki yarmi ag'dariladi.

    Kalla ko'rinmaydi: keng qo'l bo'lagi polga yotadi, tana uning ustida,
    oyoqlar tepada yig'ilib qoladi. Ko'z -- tana tubidagi ikki qisqa chiziq.
    """
    y0, y1 = SLEEP_ROWS
    lying = base.crop((0, y0, base.width, y1)).transpose(Image.FLIP_TOP_BOTTOM)
    img = Image.new("RGBA", base.size, (0, 0, 0, 0))
    top = base.height - lying.height
    img.paste(lying, (0, top))

    # ag'darilgach oyoq uchlari ochiq qolgan -- ustiga kontur qo'yamiz
    px = img.load()
    for x in range(img.width):
        if px[x, top][3]:
            px[x, top] = INK

    # qo'l bo'lagi eng pastda, ko'z esa tananing tubida -- undan bir qator tepada
    eye_y1 = img.height - (ARM_ROWS[1] - ARM_ROWS[0]) - 1
    for x0, x1, _, _ in find_eyes(base):
        shut_eye(img, x0, x1, eye_y1 - SHUT_EYE_H)
    return img


def lift_leg(base, cols, dy=2):
    """Bitta oyoqni dy piksel yuqoriga ko'taradi."""
    img = base.copy()
    y0, y1 = LEG_ROWS
    x0, x1 = cols
    leg = img.crop((x0, y0, x1, y1))
    # eski joyini tozalaymiz
    img.paste((0, 0, 0, 0), (x0, y0, x1, y1))
    img.paste(leg, (x0, y0 - dy), leg)
    # ko'tarilgan oyoqning pastini kesamiz
    img.paste((0, 0, 0, 0), (x0, y1 - dy, x1, y1))
    return img


def pad(img):
    """Kadr atrofiga shaffof bo'shliq qo'shadi (pastdan tashqari)."""
    out = Image.new("RGBA", (img.width + PAD_X * 2, img.height + PAD_TOP),
                    (0, 0, 0, 0))
    out.paste(img, (PAD_X, PAD_TOP), img)
    return out


def shift_band(base, rows, dy):
    """Gorizontal bo'lakni (masalan bosh yoki qo'llarni) tikka siljitadi."""
    img = base.copy()
    y0, y1 = rows
    band = img.crop((0, y0, img.width, y1))
    img.paste((0, 0, 0, 0), (0, y0, img.width, y1))
    img.paste(band, (0, y0 + dy), band)
    return img


def shift_arm_tips(base, dy, side="lr"):
    """Tanadan chiqib turgan qo'l uchlarini ko'taradi.

    `side` -- qaysi qo'l: "l" (chap), "r" (o'ng) yoki "lr" (ikkalasi).
    Butun qo'l qatorini siljitsak tana ikkiga bo'linib ketadi -- shuning uchun
    bosh kengligidan tashqaridagi ustunlargagina tegamiz.
    """
    img = base.copy()
    y0, y1 = ARM_ROWS
    spans = {"l": (0, HEAD_X[0]), "r": (HEAD_X[1], base.width)}
    for s in side:
        x0, x1 = spans[s]
        tip = img.crop((x0, y0, x1, y1))
        img.paste((0, 0, 0, 0), (x0, y0, x1, y1))
        img.paste(tip, (x0, y0 + dy), tip)
    return img


def sway(base, dx):
    """Butun gavdani yon tomonga siljitadi -- o'ylanib turgandek.

    Aylantirish piksel uslubini buzadi, shuning uchun oddiy siljitish.
    """
    img = Image.new("RGBA", base.size, (0, 0, 0, 0))
    img.paste(base, (dx, 0), base)
    return img


def squash(base, factor=0.82):
    """Yerga urilganda siqilish -- bo'yi pasayadi, pastki chekkasi joyida qoladi."""
    img = Image.new("RGBA", base.size, (0, 0, 0, 0))
    small = base.resize((base.width, max(1, int(base.height * factor))),
                        Image.NEAREST)
    img.paste(small, (0, base.height - small.height), small)
    return img


def blink(base):
    """Ko'zlarni yumadi -- o'rnida yumuq ko'z chizig'i qoladi."""
    img = base.copy()
    for x0, x1, y0, y1 in find_eyes(img):
        img.paste(BODY, (x0, y0, x1, y1))
        shut_eye(img, x0, x1, (y0 + y1 - SHUT_EYE_H) // 2)
    return img


TRANS = (255, 0, 255)  # pet oynasida shaffof qilinadigan kalit rang


def save(img, name):
    """Ikki nusxa: alfali (zaxira) va kalit rangga yopishtirilgani (pet uchun).

    Yopishtirilgani tufayli pet.py ga Pillow kerak bo'lmaydi -- uni
    tkinter'ning o'zi PNG sifatida o'qiy oladi.
    """
    big = img.resize((img.width * SCALE, img.height * SCALE), Image.NEAREST)

    big.save(os.path.join(OUT, name + ".png"))

    flat_dir = os.path.join(OUT, "flat")
    os.makedirs(flat_dir, exist_ok=True)
    bg = Image.new("RGBA", big.size, TRANS + (255,))
    Image.alpha_composite(bg, big).convert("RGB").save(
        os.path.join(flat_dir, name + ".png"))


def main():
    os.makedirs(OUT, exist_ok=True)
    grid_path = os.environ.get("MASCOT_GRID", os.path.join(HERE, "grid.json"))
    src = flatten(strip_background(load_source(grid_path)))
    stand = raise_eyes(src.crop(BBOX))

    # havoda uchayotganda ikkala oyoq ham yig'ilgan bo'ladi
    fall = lift_leg(lift_leg(stand, LEG_L, dy=4), LEG_R, dy=4)
    # qo'l silkitish: ikkalasi, faqat chapi yoki faqat o'ngi
    waves = {"wave" + s: shift_arm_tips(stand, -6, side)
             for s, side in (("", "lr"), ("_l", "l"), ("_r", "r"))}
    cheer = shift_arm_tips(                             # sakrab quvonadi
        lift_leg(lift_leg(stand, LEG_L, dy=3), LEG_R, dy=3), -7)

    frames = {
        "stand": stand,
        "walk1": lift_leg(stand, LEG_L),
        "walk2": stand,
        "walk3": lift_leg(stand, LEG_R),
        "blink": blink(stand),
        "sleep": sleeping(stand),
        "fall": fall,
        "squash": squash(stand),
        # ish paytidagi qo'shimcha faoliyatlar
        "peck": shift_band(stand, HEAD_ROWS, 3),        # boshini egib "cho'qiydi"
        "cheer": cheer,
        # kulgan holat -- pet.py xursand paytda shu kadrlarga o'tadi
        "happy_stand": smile(stand),
        "happy_cheer": smile(cheer),
    }
    frames.update(waves)
    frames.update(("happy_" + n, smile(img)) for n, img in waves.items())

    frames = {name: pad(img) for name, img in frames.items()}
    # o'ylanib chayqalish -- bo'shliq qo'shilgandan keyin siljitiladi
    frames["sway_l"] = sway(frames["stand"], -4)
    frames["sway_r"] = sway(frames["stand"], 4)

    for name, img in frames.items():
        save(img, name)
        save(img.transpose(Image.FLIP_LEFT_RIGHT), name + "_flip")

    ref = frames["stand"]
    print(f"{len(frames) * 2} ta kadr yozildi -> {OUT}")
    print(f"o'lcham: {ref.width * SCALE}x{ref.height * SCALE}")


if __name__ == "__main__":
    main()
