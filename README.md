# Claude desktop pet

> **Windows** va **macOS**. O'rnatish: [Windows'da](#windowsda) ·
> [macOS'da](#macosda) · [macOS xususiyatlari](#macos-xususiyatlari)

Ekran bo'ylab yuradigan Claude Code maskoti. Claude Code'ning holatiga qarab
o'zini tutadi: ishlayotganda harakatlanadi va nima qilayotganini aytadi,
bo'sh turganda gaplashadi, uzoq jim qolsa uxlaydi. Harakatlarida — sakrash,
uloqtirilish, bosilish — ovoz ham chiqaradi.

## O'rnatish

Pet **Windows** va **macOS** da ishlaydi. Ikkalasida ham Python 3.8+ kerak,
boshqa hech narsa emas — kadrlar va ovozlar tayyor holda keladi.

Papkani olish (yoki ZIP faylni istalgan joyga yeching):

```bash
git clone https://github.com/Feruzbek-Sapayev/claude-pet.git
cd claude-pet
```

### Windows'da

1. Python 3.8+ o'rnating — [python.org](https://python.org). O'rnatishda
   **«Add Python to PATH»** katagini belgilang.
2. **`install.bat`** ni ikki marta bosing.
3. Claude Code'ni qayta ishga tushiring.

### macOS'da

1. Python 3.8+ o'rnating. **Tkinter bilan birga kelgan nusxa kerak** —
   [python.org](https://python.org) dan olingani eng ishonchli. Tekshirish:

   ```bash
   python3 -c "import tkinter; print(tkinter.TkVersion)"
   ```

   Raqam chiqsa (8.6 yoki undan yuqori) hammasi joyida. Xato chiqsa
   python.org dan Python o'rnating — Homebrew nusxasiga qo'shimcha
   `brew install python-tk` kerak bo'lishi mumkin.

2. O'rnatgichni ishga tushiring — Finder'da **`install.command`** ni ikki
   marta bosing, yoki terminalda:

   ```bash
   chmod +x install.command      # ZIP orqali olgan bo'lsangiz
   ./install.command
   ```

3. Claude Code'ni qayta ishga tushiring.

> **Gatekeeper.** Birinchi marta ochganda «tasdiqlanmagan dasturchi»
> ogohlantirishi chiqishi mumkin. Faylga o'ng tugma → **Open** → yana
> **Open**. Yoki umuman chetlab o'tib, terminalda `python3 install.py`.

**Ikkinchi monitor** kerak bo'lsa (ixtiyoriy):
`pip3 install pyobjc-framework-Cocoa`. Usiz pet faqat asosiy ekranda yuradi.

### O'rnatgich nima qiladi

Uch ish: Claude Code hooklarini qo'shadi, pet'ni tizim avtostartiga yozadi
va uni ishga tushiradi.

> Papkani keyinchalik ko'chirsangiz, yangi joyida o'rnatgichni qaytadan ishga
> tushiring — yo'llar yangilanadi. Qayta o'rnatish xavfsiz: yozuvlar
> takrorlanmaydi, yangilanadi.

### Nimalarga tegadi

| Nima | Windows | macOS |
|---|---|---|
| Hooklar | `~/.claude/settings.json` — mavjud sozlamalaringiz va boshqa hooklaringiz saqlanadi, avval `settings.json.bak` zaxirasi olinadi | shu yerda |
| Avtostart | Startup papkasidagi `claude-pet.vbs` | `~/Library/LaunchAgents/com.claude-pet.plist` |
| Vaqtinchalik holat | `%TEMP%\claude-pet\` | `~/Library/Caches/claude-pet/` |

### O'chirish

**`uninstall.bat`** (macOS'da **`uninstall.command`**) ni ishga tushiring — u
faqat o'zi qo'shgan hooklarni va avtostartni olib tashlaydi, boshqa
sozlamalaringizga tegmaydi. So'ng papkani o'chirsangiz bo'ladi.

## macOS xususiyatlari

O'rnatish yuqorida. Bu yerda — kundalik ishlatish va Windows'dan farqlari.

| Ish | Buyruq |
|---|---|
| Qo'lda ishga tushirish | `./start-pet.command` yoki `python3 pet.py` |
| Chiqish | pet'ga ikki barmoq bilan bosing → «Chiqish» |
| O'chirish | `./uninstall.command` |
| Avtostartni vaqtincha to'xtatish | `launchctl unload ~/Library/LaunchAgents/com.claude-pet.plist` |
| Avtostartni qaytarish | `launchctl load ~/Library/LaunchAgents/com.claude-pet.plist` |

O'ng tugma menyusi trackpad'da **ikki barmoq bilan bosish** yoki `Control` +
bosish orqali ochiladi.

### Windows'dan farqlari

| Nima | Windows | macOS |
|---|---|---|
| Shaffof fon | oynadagi kalit rang ko'rinmas qilinadi, kadrlar `sprites/flat/` dan | oynaning o'zi shaffof, kadrlar alfa kanali bilan `sprites/` dan |
| Ovoz | `winsound` | `afplay` |
| Ekranlar | `EnumDisplayMonitors` | `NSScreen` (pyobjc) yoki faqat asosiy ekran |
| Avtostart | Startup papkasidagi `.vbs` | `~/Library/LaunchAgents/com.claude-pet.plist` |
| Holat fayli | `%TEMP%\claude-pet\` | `~/Library/Caches/claude-pet/` |
| Shrift | Segoe UI | Helvetica Neue |

Holat fayli macOS'da `TMPDIR` da emas, `Caches` da turadi: `TMPDIR` sessiyaga
bog'langan bo'lishi mumkin va hook bilan pet uni har xil ko'rib qolardi.
Yo'l `paths.py` da bir marta hisoblanadi.

### macOS nosozliklari

**Pet ko'rinmayapti** — terminaldan `python3 pet.py` ni ishlating va xatoni
o'qing. Ko'p uchraydigani: Tkinter yo'q (o'rnatish bo'limidagi tekshiruvga
qarang).

**Pet fonida to'rtburchak qoladi** — oyna shaffofligi Tk versiyasiga bog'liq.
`python3 -c "import tkinter; print(tkinter.TkVersion)"` 8.6 dan past bo'lsa
python.org dan yangi Python o'rnating.

**Faqat bitta ekranda yuradi** — `pip3 install pyobjc-framework-Cocoa`,
so'ng pet'ni qayta ishga tushiring.

**Ovoz chiqmayapti** — `/usr/bin/afplay` borligini tekshiring; menyudagi
«Ovoz» belgisi yoqilganmi?

## Do'stingizga berish

`package.bat` ni ishga tushiring — yonidagi papkada `claude-pet.zip` (~60 KB)
paydo bo'ladi. O'shani yuboring, ular yechib `install.bat` ni bossa bo'ldi.

## Holatlar

| Holat | Qachon | Nima qiladi |
|---|---|---|
| `working` | siz Claude'ga xabar yuborgandan keyin | 3–8 soniyada almashadigan turli faoliyatlar (pastga qarang), boshi tepasida «Pishiryapman...» kabi yozuv |
| `waiting` | Claude sizdan javob/ruxsat kutayotganda | `WAIT_SEC` soniya sakraydi va «Javobingizni kutyapman» deydi, keyin `idle` ga o'tadi |
| `idle` | Claude javobini tugatganda | tik turadi, ko'z qisadi, sekin sayr qiladi va o'zicha gapirib turadi |
| uyqu | `SLEEP_AFTER` soniya bo'sh tursa | yonboshlab yotadi, tepasidan «Z» lar ko'tarilib turadi |

## Ish paytidagi faoliyatlar

Claude ishlayotganda pet faqat yuravermaydi — har 3–8 soniyada boshqa ishga
o'tadi. Tanlov `ACTIVITIES` ro'yxatidan tasodifiy olinadi; `walk` ro'yxatda
bir necha marta takrorlangani uchun tez-tez tushadi.

| Faoliyat | Taxminiy ulush | Nima qiladi |
|---|---|---|
| `walk` | ~34% | ekran bo'ylab yuradi, qadam bilan tebranadi |
| `peck` | ~27% | boshini egib-ko'tarib «cho'qiydi» — kod terayotgandek |
| `think` | ~17% | sekin u yon-bu yon chayqaladi |
| `wave` | ~14% | qo'l silkitadi (pastga qarang) |
| `cheer` | ~10% | qo'lini ko'tarib joyida sakraydi |

### Qo'l silkitish

`wave` faoliyati boshlanganda uslub `WAVE_STYLES` dan tasodifiy tanlanadi:

| Uslub | Nima qiladi |
|---|---|
| `wave` | ikkala qo'lini birga ko'taradi |
| `wave_l` | faqat chap qo'lini |
| `wave_r` | faqat o'ng qo'lini |
| `alt` | navbat bilan goh u, goh bu qo'lini |

Kadrlarni `make_sprites.py` dagi `shift_arm_tips(base, dy, side)` yasaydi —
`side` "l", "r" yoki "lr" bo'lishi mumkin. Yangi qo'l holati kerak bo'lsa
(masalan boshqa balandlikda) shu funksiyani chaqirib kadr qo'shing, so'ng
uni `pet.py` dagi kadrlar ro'yxatiga yozing.

Nisbatni o'zgartirish uchun `ACTIVITIES` ro'yxatidagi takrorlarni ko'paytiring
yoki kamaytiring. Masalan `peck` ni ikki barobar tez-tez chiqarish uchun uni
ro'yxatga yana ikki marta qo'shing.

## Uyqu

`SLEEP_AFTER` soniya bo'sh tursa pet yonboshlab yotadi: keng qo'l bo'lagi
polda, tana uning ustida, oyoqlari tepada yig'ilgan, ko'zi ikki qisqa chiziq.
Kadr `make_sprites.py` dagi `sleeping()` da yasaladi — gavdaning pastki yarmi
(`SLEEP_ROWS`) ag'dariladi, kalla ko'rinmaydi.

Tepasidan «Z» harflari ko'tarilib turadi: pastda kichik va yorug', yuqoriga
chiqqan sari kattalashib so'nadi, yon tomonga yoy chizib suriladi. Ular
maskotning o'z oynasiga sig'magani uchun alohida shaffof oynada chiziladi
(`Zzz` klassi).

Harf shrift bilan emas, `Z_GLYPH` piksel naqshidan chiziladi — Windows
shriftni silliqlaganda chekkalari shaffof kalit rangga aralashib, magenta
hoshiya qoldiradi. Har bosqich uchun rasm dastur ishga tushganda bir marta
tayyorlanadi.

Sozlash (`pet.py`): `ZZZ_COUNT`, `ZZZ_RISE`, `ZZZ_PERIOD`, `ZZZ_DRIFT`,
`ZZZ_SCALE`, `ZZZ_LIFT`, `ZZZ_NEAR`/`ZZZ_FAR`.

## Kulish

Xursand paytlarda pet ko'zini `^^` shakliga o'zgartiradi. Bu quyidagi
holatlarda chiqadi:

| Qachon | Qancha davom etadi |
|---|---|
| ustiga bosilganda (bir qo'lini ko'tarib) | `HAPPY_SEC` soniya |
| ish paytidagi `cheer` (sakrab quvonish) | faoliyat oxirigacha |
| ish paytidagi `wave` (qo'l silkitish, har uch uslubi ham) | faoliyat oxirigacha |
| bo'sh turganda gap aytayotganda | gap ekranda turgan vaqt |

Kulgan nusxasi bor kadrlar `pet.py` dagi **`HAPPY_FRAMES`** ro'yxatida
(`stand`, `wave`, `cheer`) — `make_sprites.py` shularning `happy_` prefiksli
juftini yasaydi. Boshqa kadrga ham kulgan nusxa kerak bo'lsa, ikkala joyga
qo'shing. Kulgan ko'zning kengligi `make_sprites.py` dagi `SMILE_WIDEN`
bilan boshqariladi.

## Bo'sh turgandagi gaplar

Claude ishlamayotganda pet har 25–70 soniyada o'zicha bir gap aytadi va
gapirayotganda qo'l silkitadi. Gap 4.5 soniya turadi.

Gaplar uch manbadan yig'iladi (`pet.py` boshida):

- **`IDLE_TALK`** — umumiy gaplar: «Zerikdim...», «Suv ichishni unutmang»,
  «Ko'zlaringizga bir dam bering», «Commit qilishni unutmang»
- **`TIME_TALK`** — kun vaqtiga qarab, uch barobar ko'proq tushadi:
  ertalab «Xayrli tong!», tushda «Tushlik vaqti bo'ldi»,
  kechqurun «Kech bo'ldi, charchamadingizmi?», tunda «Uxlash vaqti emasmi?»
- **`LONG_IDLE_TALK`** — 10 daqiqadan ortiq jimlikdan keyin qo'shiladi:
  «Ketib qoldingizmi?», «Kutib turibman»

Yangi gap qo'shish uchun shu ro'yxatlarga qator qo'shing, xolos.

## Gap buluti

Yozuv bulut shaklidagi ramkada chiqadi: chetlari to'lqinli, pastida esa
maskot tomon tushadigan ikkita kichrayuvchi doira.

Bulut o'zak to'rtburchak va uning to'rt chekkasi bo'ylab terilgan doiralardan
yig'iladi (`Bubble._parts`). Radiuslar `BUMPS` ro'yxati bo'yicha navbatlashadi
— shundan kontur to'lqinlanib chiqadi; har chekka navbatning turli joyidan
boshlanadi, shuning uchun naqsh takrorlanmaydi.

O'zak matndan `MARGIN` qadar kengroq. Buni kamaytirmang: qo'shni doiralar
tutashgan joyda kontur ichkariga botadi, o'sha bo'shliq bo'lmasa harflarning
dumi (`y`, `p`) chiziqqa tegib ketadi.

Ichki yoylarni yashirish uchun ikki qatlam chiziladi: avval hamma bo'lak
hoshiyasi bilan, so'ng har biri chiziq qalinligicha ichkariga siqib qayta
bo'yaladi. Shu sabab qo'shni doiralar bir-birini yaxshigina qoplashi kerak —
`STEP` ni kattalashtirsangiz `BUMPS` ni ham oshiring, aks holda kontur
uzilib qoladi.

Sozlash: `BUMPS`, `STEP`, `MARGIN`, `TAIL_R`, `LINE` — hammasi `Bubble`
klassining boshida (`PAD_X`/`PAD_Y` shulardan hisoblanadi). Ranglar:
`BUBBLE_BG`, `BUBBLE_LINE`, `BUBBLE_TEXT`.

## Gap pufagidagi yozuv

Fe'llar `~/.claude/settings.json` dagi **`spinnerVerbs.verbs`** ro'yxatidan olinadi —
terminalda ko'rinadigani bilan aynan bir xil ro'yxat (hozir 186 ta o'zbekcha fe'l).

Diqqat: Claude Code ayni damda qaysi fe'lni ko'rsatayotganini tashqariga bermaydi,
shuning uchun pet o'sha ro'yxatdan **mustaqil** tanlaydi va har `VERB_SEC`
soniyada almashtiradi. Ya'ni so'z terminaldagi bilan bir vaqtda mos tushmaydi,
lekin uslub va manba bitta.

## Bir nechta monitor

Pet barcha monitorlar bo'ylab yuradi — chekkaga yetganda to'xtamay, qo'shni
ekranga o'tib ketadi. Har bir monitorning **o'z paneli** (Windows'da vazifalar
paneli, macOS'da menyu paneli va Dock) hisobga olinadi.

- Monitorlar balandligi har xil bo'lsa, pet polni `GROUND_EASE` px/tik tezlikda
  yumshoq moslashtiradi — zinapoyaga chiqqandek ko'rinadi
- Monitorlar orasida bo'shliq bo'lsa (masalan turli o'lchamdagi ekranlar),
  eng yaqin monitorning poli olinadi
- Monitor ulansa yoki uzilsa, ro'yxat har 10 soniyada yangilanadi — dasturni
  qayta ishga tushirish shart emas

Ekranlar qanday aniqlanadi:

| Tizim | Usul |
|---|---|
| Windows | `EnumDisplayMonitors` — hamma ekran, qo'shimcha hech narsa kerak emas |
| macOS | `NSScreen.visibleFrame` — **pyobjc** o'rnatilgan bo'lsa hamma ekran |
| macOS (pyobjc'siz) | faqat asosiy ekran |

macOS'da ikkinchi monitor kerak bo'lsa:

```bash
pip3 install pyobjc-framework-Cocoa
```

so'ng pet'ni qayta ishga tushiring. Bu ixtiyoriy — usiz ham pet ishlaydi,
faqat asosiy ekrandan chiqmaydi.

## Boshqarish

- **Sudrash va uloqtirish** — chap tugma bilan tortib qo'yib yuboring: pet
  tezlikni saqlab uchadi, polga tushib bir-ikki sakraydi va tinchiydi.
  Devorlardan va shiftdan qaytadi, qo'shni monitorga uchib o'tishi mumkin
- **Bosish** — ustiga bir marta bosing, bir qo'lini ko'tarib (qaysi biri —
  tasodifiy) sapchiydi va «Nima gap?» deydi
- **O'ng tugma** — «Yerga qaytar», «Ovoz» (yoqish/o'chirish) yoki «Chiqish».
  macOS'da trackpad'da ikki barmoq bilan bosing yoki `Control` ushlab bosing
- **Qayta ishga tushirish** — `start-pet.bat` (macOS: `start-pet.command`)

## Ovozlar

Pet harakatlariga mos qisqa "retro" tovushlar chiqaradi. Ovoz asinxron
chalinadi — pet sekinlashmaydi — va o'ng tugma menyusidagi **«Ovoz»** belgisi
orqali istagancha o'chirib-yoqiladi (standart holatda yoniq).

| Harakat | Ovoz |
|---|---|
| Uchirib yuborilganda (kuchli uloqtirish) | `throw` — "vushsh" swoosh |
| Yerga urilganda | `land` — past "tuk" |
| Sakraganda (javob kutayotganda) | `hop` — "boing", har sakrashda |
| Ustiga bosilganda | `poke` — ko'tariluvchi "bloop" |
| Ish paytida quvonganda (`cheer`) | `cheer` — uch nota |
| Oddiy holatda turganda | `idle` — goh-goh yumshoq "chirp" (uxlaganda jim) |

Ovozlar `sounds/` papkasidagi tayyor WAV fayllar. Ularni **`make_sounds.py`**
protsedural yasaydi (faqat standart kutubxona — `wave` + `math`, Pillow kerak
emas). O'zgartirmoqchi bo'lsangiz — fayldagi chastota, uzunlik yoki balandlikni
(`vol=`) tahrirlab, `python make_sounds.py` ni qayta ishlating. Pet ovozni har
chalinganda fayldan o'qiydi, shuning uchun yangi WAV darrov kuchga kiradi.

## Kursorga e'tibor

Bo'sh turganda pet sichqoncha kursorini kuzatadi:

- Kursor `NOTICE_PX` masofaga kirsa — sayrni to'xtatib, o'sha tomonga o'giriladi
- Uxlayotgan bo'lsa — kursor yaqinlashganda uyg'onadi

Bir vaqtda faqat bitta nusxa ishlaydi (50573-port qulf sifatida band qilinadi).

## Fayllar

```
install.bat       o'rnatish (do'stingiz shuni bosadi)      -- Windows
uninstall.bat     o'chirish                                -- Windows
package.bat       tarqatish uchun ZIP yasaydi              -- Windows
start-pet.bat     ishga tushirgich -- Python'ni o'zi topadi -- Windows

install.command   o'rnatish                                -- macOS
uninstall.command o'chirish                                -- macOS
start-pet.command ishga tushirgich                         -- macOS

pet.py            asosiy dastur (faqat standart kutubxona -- Pillow kerak emas)
paths.py          holat fayli yo'li -- pet, hook va o'chirgich uchun umumiy
set_state.py      Claude Code hooklari chaqiradi, holatni yozadi
install.py        o'rnatish mantiqi
uninstall.py      o'chirish mantiqi
make_sprites.py   sprayt kadrlarini yasaydi (faqat kadrlarni o'zgartirsangiz
                  kerak bo'ladi, Pillow talab qiladi)
make_sounds.py    ovoz fayllarini yasaydi (faqat ovozni o'zgartirsangiz kerak,
                  faqat standart kutubxona)
grid.json         maskotning asl piksellari
sprites/          20 ta kadr x 2 yo'nalish: stand, walk1-3, blink, sleep,
                  fall, squash, peck, wave, wave_l, wave_r, cheer,
                  sway_l/r va kulgan nusxalari happy_* (alfali nusxa)
sprites/flat/     kadrlar (kalit rangga yopishtirilgan -- pet shularni o'qiydi)
sounds/           harakat tovushlari: hop, poke, cheer, throw, land, idle (WAV)
```

Holat fayli: `%TEMP%\claude-pet\state.json`

## Sozlash

`pet.py` boshidagi doimiylar:

```python
TICK_MS = 50        # yangilanish oralig'i
WALK_SPEED = 2.4    # ishlayotgandagi tezlik (piksel/tik)
IDLE_SPEED = 1.0    # sayr tezligi
FRAME_TICKS = 3     # kadr almashish tezligi
WAIT_SEC = 7        # "kutyapti" holatida shuncha sakraydi, keyin tinchiydi
VERB_SEC = 3.5      # pufakdagi so'z shuncha soniyada almashadi
SLEEP_AFTER = 240   # shuncha soniya bo'sh tursa uxlaydi
TALK_MIN, TALK_MAX = 25, 70   # bo'sh turganda gaplar orasidagi tanaffus
TALK_SEC = 4.5      # bitta gap ekranda shuncha turadi
BOB_PX = 2          # yurgandagi tebranish balandligi
GROUND_EASE = 6     # monitorlar balandligi farq qilsa, moslashish tezligi

GRAVITY = 1.5       # tortishish kuchi
BOUNCE = 0.42       # yerdan qaytish (0 = umuman sakramaydi)
WALL_BOUNCE = 0.55  # devordan qaytish
THROW_MAX = 60.0    # uloqtirish tezligi chegarasi

NOTICE_PX = 240     # kursorni shu masofadan sezadi
POKE_SEC = 2.2      # bosilganda shuncha vaqt hayajonlanadi
HAPPY_SEC = 2.6     # bosilganda shuncha vaqt kulib turadi

ACT_MIN, ACT_MAX = 3.0, 8.0   # bitta faoliyat shuncha soniya davom etadi
STALE_SEC = 900     # bundan eski "working" holati eskirgan hisoblanadi

SOUND_ON = True     # ovoz standart holatda yoniqmi
SOUND_GAP = 0.07    # ketma-ket tovushlar orasidagi eng kam oraliq (s)
IDLE_SOUND_MIN, IDLE_SOUND_MAX = 22, 50   # oddiy turgandagi "chirp" oralig'i
```

## O'lcham

`make_sprites.py` dagi **`SCALE`** — hozir `2` (oyna 142x94 px). O'zgartirgach
`python make_sprites.py` ni qayta ishlating va pet'ni qayta ishga tushiring.

Faqat **butun son** ishlating: 1, 2, 3... Kasrli masshtabda (masalan 2.5)
piksellar har xil kattalikda chiqib, maskotning uslubi buziladi.

Kattalikni o'zgartirsangiz sakrash balandliklarini ham mutanosib moslang
(`pet.py` dagi `_do_hop`, `_act_cheer`, `_do_poke` ichidagi sonlar) va
pufak shriftini (`Bubble.__init__` dagi `size`).

## Nosozliklar

macOS'ga xoslari yuqorida — [macOS nosozliklari](#macos-nosozliklari).

**Pet ko'rinmayapti** — `start-pet.bat` ni qo'lda ishga tushiring. Xato chiqsa
Python o'rnatilmagan yoki PATH da yo'q.

**Yuradi, lekin Claude'ning holatini bilmaydi** — Claude Code'ni qayta ishga
tushirdingizmi? Hooklar faqat yangi sessiyada yuklanadi. Tekshirish uchun
holat fayliga qarang — xabar yuborganingizda `working` bo'lishi kerak:

```
Windows:  %TEMP%\claude-pet\state.json
macOS:    ~/Library/Caches/claude-pet/state.json
```

**Papkani ko'chirdim, ishlamay qoldi** — yangi joyida `install.bat`
(macOS: `install.command`) ni qaytadan ishga tushiring.

**Ikkita pet chiqdi** — chiqmaydi: 50573-port qulf sifatida ishlatiladi, ikkinchi
nusxa o'zi yopiladi.

**Butunlay o'chirish** — `uninstall.bat` (macOS: `uninstall.command`), so'ng
papkani o'chiring.
