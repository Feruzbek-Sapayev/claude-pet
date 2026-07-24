# Claude desktop pet

Ekran bo'ylab yuradigan Claude Code maskoti. Claude Code'ning holatiga qarab
o'zini tutadi: ishlayotganda harakatlanadi va nima qilayotganini aytadi,
bo'sh turganda gaplashadi, uzoq jim qolsa uxlaydi. Harakatlarida — sakrash,
uloqtirilish, bosilish — ovoz ham chiqaradi.

## O'rnatish

**Kerak bo'ladi:** Windows va Python 3.8+ ([python.org](https://python.org),
o'rnatishda «Add Python to PATH» katagini belgilang). Boshqa hech narsa kerak
emas — kadrlar va ovozlar tayyor holda keladi (ovoz Windows'ning o'z
`winsound` moduli bilan chalinadi, qo'shimcha kutubxona shart emas).

**GitHub'dan:**

```bash
git clone https://github.com/Feruzbek-Sapayev/claude-pet.git
cd claude-pet
```

so'ng **`install.bat`** ni ikki marta bosing va Claude Code'ni qayta ishga
tushiring.

**Yoki ZIP orqali:**

1. ZIP faylni istalgan papkaga yeching (masalan `C:\claude-pet`)
2. **`install.bat`** ni ikki marta bosing
3. Claude Code'ni qayta ishga tushiring

Tamom. O'rnatgich uch ishni qiladi: Claude Code hooklarini qo'shadi, pet'ni
Windows avtostartiga yozadi va uni ishga tushiradi.

> Papkani keyinchalik ko'chirsangiz, yangi joyida `install.bat` ni qaytadan
> ishga tushiring — yo'llar yangilanadi. Qayta o'rnatish xavfsiz: yozuvlar
> takrorlanmaydi, yangilanadi.

### Nimalarga tegadi

| Nima | Qayerda |
|---|---|
| Hooklar | `~/.claude/settings.json` — mavjud sozlamalaringiz va boshqa hooklaringiz saqlanadi, avval `settings.json.bak` zaxirasi olinadi |
| Avtostart | Startup papkasidagi `claude-pet.vbs` |
| Vaqtinchalik holat | `%TEMP%\claude-pet\` |

### O'chirish

**`uninstall.bat`** ni ishga tushiring — u faqat o'zi qo'shgan hooklarni va
avtostartni olib tashlaydi, boshqa sozlamalaringizga tegmaydi. So'ng papkani
o'chirsangiz bo'ladi.

## Do'stingizga berish

`package.bat` ni ishga tushiring — yonidagi papkada `claude-pet.zip` (~60 KB)
paydo bo'ladi. O'shani yuboring, ular yechib `install.bat` ni bossa bo'ldi.

## Holatlar

| Holat | Qachon | Nima qiladi |
|---|---|---|
| `working` | siz Claude'ga xabar yuborgandan keyin | 3–8 soniyada almashadigan turli faoliyatlar (pastga qarang), boshi tepasida «Pishiryapman...» kabi yozuv |
| `waiting` | Claude sizdan javob/ruxsat kutayotganda | `WAIT_SEC` soniya sakraydi va «Javobingizni kutyapman» deydi, keyin `idle` ga o'tadi |
| `idle` | Claude javobini tugatganda | tik turadi, ko'z qisadi, sekin sayr qiladi va o'zicha gapirib turadi |
| uyqu | `SLEEP_AFTER` soniya bo'sh tursa | ko'zini yumib «z z z» deb uxlaydi |

## Ish paytidagi faoliyatlar

Claude ishlayotganda pet faqat yuravermaydi — har 3–8 soniyada boshqa ishga
o'tadi. Tanlov `ACTIVITIES` ro'yxatidan tasodifiy olinadi; `walk` ro'yxatda
bir necha marta takrorlangani uchun tez-tez tushadi.

| Faoliyat | Taxminiy ulush | Nima qiladi |
|---|---|---|
| `walk` | ~34% | ekran bo'ylab yuradi, qadam bilan tebranadi |
| `peck` | ~27% | boshini egib-ko'tarib «cho'qiydi» — kod terayotgandek |
| `think` | ~17% | sekin u yon-bu yon chayqaladi |
| `wave` | ~14% | qo'llarini ko'tarib-tushiradi |
| `cheer` | ~10% | qo'lini ko'tarib joyida sakraydi |

Nisbatni o'zgartirish uchun `ACTIVITIES` ro'yxatidagi takrorlarni ko'paytiring
yoki kamaytiring. Masalan `peck` ni ikki barobar tez-tez chiqarish uchun uni
ro'yxatga yana ikki marta qo'shing.

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

## Gap pufagidagi yozuv

Fe'llar `~/.claude/settings.json` dagi **`spinnerVerbs.verbs`** ro'yxatidan olinadi —
terminalda ko'rinadigani bilan aynan bir xil ro'yxat (hozir 186 ta o'zbekcha fe'l).

Diqqat: Claude Code ayni damda qaysi fe'lni ko'rsatayotganini tashqariga bermaydi,
shuning uchun pet o'sha ro'yxatdan **mustaqil** tanlaydi va har `VERB_SEC`
soniyada almashtiradi. Ya'ni so'z terminaldagi bilan bir vaqtda mos tushmaydi,
lekin uslub va manba bitta.

## Bir nechta monitor

Pet barcha monitorlar bo'ylab yuradi — chekkaga yetganda to'xtamay, qo'shni
ekranga o'tib ketadi. Monitorlar `EnumDisplayMonitors` orqali aniqlanadi,
har birining **o'z vazifalar paneli** hisobga olinadi.

- Monitorlar balandligi har xil bo'lsa, pet polni `GROUND_EASE` px/tik tezlikda
  yumshoq moslashtiradi — zinapoyaga chiqqandek ko'rinadi
- Monitorlar orasida bo'shliq bo'lsa (masalan turli o'lchamdagi ekranlar),
  eng yaqin monitorning poli olinadi
- Monitor ulansa yoki uzilsa, ro'yxat har 10 soniyada yangilanadi — dasturni
  qayta ishga tushirish shart emas

## Boshqarish

- **Sudrash va uloqtirish** — chap tugma bilan tortib qo'yib yuboring: pet
  tezlikni saqlab uchadi, polga tushib bir-ikki sakraydi va tinchiydi.
  Devorlardan va shiftdan qaytadi, qo'shni monitorga uchib o'tishi mumkin
- **Bosish** — ustiga bir marta bosing, sapchib «Nima gap?» deydi
- **O'ng tugma** — «Yerga qaytar», «Ovoz» (yoqish/o'chirish) yoki «Chiqish»
- **Qayta ishga tushirish** — `start-pet.bat`

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
install.bat       o'rnatish (do'stingiz shuni bosadi)
uninstall.bat     o'chirish
package.bat       tarqatish uchun ZIP yasaydi
start-pet.bat     ishga tushirgich -- Python'ni o'zi topadi

pet.py            asosiy dastur (faqat standart kutubxona -- Pillow kerak emas)
set_state.py      Claude Code hooklari chaqiradi, holatni yozadi
install.py        o'rnatish mantiqi
uninstall.py      o'chirish mantiqi
make_sprites.py   sprayt kadrlarini yasaydi (faqat kadrlarni o'zgartirsangiz
                  kerak bo'ladi, Pillow talab qiladi)
make_sounds.py    ovoz fayllarini yasaydi (faqat ovozni o'zgartirsangiz kerak,
                  faqat standart kutubxona)
grid.json         maskotning asl piksellari
sprites/          12 ta kadr x 2 yo'nalish: stand, walk1-3, blink, fall,
                  squash, peck, wave, cheer, sway_l/r (alfali nusxa)
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

**Pet ko'rinmayapti** — `start-pet.bat` ni qo'lda ishga tushiring. Xato chiqsa
Python o'rnatilmagan yoki PATH da yo'q.

**Yuradi, lekin Claude'ning holatini bilmaydi** — Claude Code'ni qayta ishga
tushirdingizmi? Hooklar faqat yangi sessiyada yuklanadi. Tekshirish uchun
`%TEMP%\claude-pet\state.json` ga qarang: xabar yuborganingizda `working`
bo'lishi kerak.

**Papkani ko'chirdim, ishlamay qoldi** — yangi joyida `install.bat` ni
qaytadan ishga tushiring.

**Ikkita pet chiqdi** — chiqmaydi: 50573-port qulf sifatida ishlatiladi, ikkinchi
nusxa o'zi yopiladi.

**Butunlay o'chirish** — `uninstall.bat`, so'ng papkani o'chiring.
