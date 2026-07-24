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
EYE_L = (15, 18, 8, 15)         # x0, x1, y0, y1
EYE_R = (39, 42, 8, 15)

BG = (25, 26, 28)
BG_TOL = 14


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


def shift_arm_tips(base, dy):
    """Faqat tanadan chiqib turgan qo'l uchlarini ko'taradi.

    Butun qo'l qatorini siljitsak tana ikkiga bo'linib ketadi -- shuning uchun
    bosh kengligidan tashqaridagi ustunlargagina tegamiz.
    """
    img = base.copy()
    y0, y1 = ARM_ROWS
    for x0, x1 in ((0, HEAD_X[0]), (HEAD_X[1], base.width)):
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
    """Ko'zlarni yumadi -- ko'z to'rtburchagini tepasidagi tana rangi bilan to'ldiradi."""
    img = base.copy()
    px = img.load()
    for x0, x1, y0, y1 in (EYE_L, EYE_R):
        for x in range(x0, x1):
            fill = px[x, y0 - 1]
            for y in range(y0, y1):
                px[x, y] = fill
        # ingichka yumuq ko'z chizig'i
        mid = (y0 + y1) // 2
        for x in range(x0, x1):
            px[x, mid] = (60, 24, 12, 255)
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
    src = strip_background(load_source(grid_path))
    stand = src.crop(BBOX)

    # havoda uchayotganda ikkala oyoq ham yig'ilgan bo'ladi
    fall = lift_leg(lift_leg(stand, LEG_L, dy=4), LEG_R, dy=4)

    frames = {
        "stand": stand,
        "walk1": lift_leg(stand, LEG_L),
        "walk2": stand,
        "walk3": lift_leg(stand, LEG_R),
        "blink": blink(stand),
        "fall": fall,
        "squash": squash(stand),
        # ish paytidagi qo'shimcha faoliyatlar
        "peck": shift_band(stand, HEAD_ROWS, 3),        # boshini egib "cho'qiydi"
        "wave": shift_arm_tips(stand, -6),              # qo'llarini ko'taradi
        "cheer": shift_arm_tips(                        # sakrab quvonadi
            lift_leg(lift_leg(stand, LEG_L, dy=3), LEG_R, dy=3), -7),
    }

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
