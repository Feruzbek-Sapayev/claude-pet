"""Claude maskoti uchun oddiy ovoz effektlarini yasaydi (WAV).

Tashqi kutubxonasiz -- faqat stdlib (wave + math). Bir marta ishlatiladi,
natija sounds/ papkasiga tushadi. pet.py ularni winsound bilan chaladi:
har harakat uchun bittadan qisqa "retro" tovush.
"""
import math
import os
import random
import struct
import wave

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "sounds")
RATE = 22050


def envelope(i, n, attack=0.012, release=0.3):
    """Boshi/oxiridagi shiqillashni yo'qotuvchi amplituda konverti (0..1)."""
    t = i / n if n else 0
    rise = min(1.0, t / attack) if attack else 1.0
    fall = min(1.0, (1 - t) / release) if release else 1.0
    return min(rise, fall)


def sweep(f0, f1, dur, vol=0.32, kind="sine", release=0.3):
    """f0 dan f1 gacha chastota surilishi -- bir marta chalinadigan tovush."""
    n = int(RATE * dur)
    out = []
    phase = 0.0
    for i in range(n):
        freq = f0 + (f1 - f0) * (i / n)
        phase += 2 * math.pi * freq / RATE
        if kind == "square":
            sample = 1.0 if math.sin(phase) >= 0 else -1.0
        else:
            sample = math.sin(phase)
        out.append(sample * vol * envelope(i, n, release=release))
    return out


def noise(dur, vol=0.2, release=0.5):
    n = int(RATE * dur)
    return [random.uniform(-1, 1) * vol * envelope(i, n, release=release)
            for i in range(n)]


def bell(i, n):
    """Silliq 0->1->0 amplituda konverti (yarim sinus)."""
    return math.sin(math.pi * (i / n if n else 0))


def tone(freq_fn, dur, vol=0.3, harmonics=(1.0,), vibrato=0.0, vib_rate=0.0,
         env=bell):
    """Boyroq ohang: vaqtga bog'liq chastota, garmonikalar va vibrato.

    freq_fn(t) -- 0..1 oralig'ida chastota beradi; harmonics -- ohang tembri
    uchun ohangdoshlar amplitudalari; vibrato -- yengil "multfilm" tebranishi.
    """
    n = int(RATE * dur)
    out = []
    phase = 0.0
    for i in range(n):
        t = i / n if n else 0
        freq = freq_fn(t)
        if vibrato:
            freq *= 1.0 + vibrato * math.sin(2 * math.pi * vib_rate * (i / RATE))
        phase += 2 * math.pi * freq / RATE
        sample = sum(amp * math.sin(k * phase)
                     for k, amp in enumerate(harmonics, start=1))
        out.append(sample * vol * env(i, n))
    return out


def whoosh(dur, vol=1.4):
    """Sweep qilinuvchi bandpass-shovqin -- "vush" (uchirib yuborilgandek).

    Ikki bir-qutbli past-o'tkazgich ayirmasi orqali havodor filtr, yorqinligi
    o'rtada eng baland. numpy'siz -- oddiy holat o'zgaruvchisi bilan.
    """
    n = int(RATE * dur)
    out = []
    lp1 = lp2 = 0.0
    for i in range(n):
        t = i / n if n else 0
        bright = math.sin(math.pi * t)          # 0..1..0
        alpha = 0.03 + 0.45 * bright
        white = random.uniform(-1, 1)
        lp1 += alpha * (white - lp1)
        lp2 += alpha * (lp1 - lp2)
        band = lp1 - lp2                         # taxminiy bandpass
        out.append(band * vol * bright ** 1.5)
    return out


def mix(*tracks):
    """Bir necha tovushni ustma-ust qo'shadi (eng uzuniga tenglashtiriladi)."""
    n = max(len(track) for track in tracks)
    out = [0.0] * n
    for track in tracks:
        for i, sample in enumerate(track):
            out[i] += sample
    return out


def throw_freq(t):
    """"viiiiiii" -- avval tez ko'tariladi, so'ng balandda cho'ziladi."""
    if t < 0.5:
        return 480 + (1150 - 480) * (t / 0.5)
    return 1150 + 90 * ((t - 0.5) / 0.5)


def save(name, samples):
    frames = bytearray()
    for sample in samples:
        clamped = max(-1.0, min(1.0, sample))
        frames += struct.pack("<h", int(clamped * 32767))
    with wave.open(os.path.join(OUT, name + ".wav"), "w") as writer:
        writer.setnchannels(1)
        writer.setsampwidth(2)
        writer.setframerate(RATE)
        writer.writeframes(bytes(frames))


def main():
    os.makedirs(OUT, exist_ok=True)

    sounds = {
        # sakraganda -- pastdan tepaga "boing"
        "hop": sweep(520, 960, 0.10, vol=0.30),
        # ustiga bosilganda -- aniq "bloop" (ko'tariluvchi, vibratoli)
        "poke": tone(lambda t: 480 + 520 * min(1.0, t / 0.35), 0.22,
                     vol=0.34, harmonics=(1.0, 0.35, 0.12),
                     vibrato=0.03, vib_rate=18),
        # ish tugaganda / quvonganda -- uch nota ko'tarilib
        "cheer": (sweep(660, 660, 0.075, vol=0.26)
                  + sweep(880, 880, 0.075, vol=0.26)
                  + sweep(1170, 1170, 0.11, vol=0.26)),
        # uchirib yuborilganda -- cho'zilgan "viiiiiii" (yuqoriga ko'tariluvchi ohang)
        "throw": tone(throw_freq, 0.55, vol=0.28,
                      harmonics=(1.0, 0.45, 0.2, 0.1),
                      vibrato=0.015, vib_rate=13,
                      env=lambda i, n: envelope(i, n, attack=0.02, release=0.22)),
        # yerga urilganda -- past "tuk"
        "land": mix(sweep(180, 70, 0.12, vol=0.42, release=0.6),
                    noise(0.05, vol=0.18)),
        # oddiy holatda turganda -- past ovozli yumshoq "chirp"
        "idle": sweep(560, 640, 0.10, vol=0.16),
    }

    for name, samples in sounds.items():
        save(name, samples)
    print(f"{len(sounds)} ta oviz yozildi -> {OUT}")


if __name__ == "__main__":
    main()
