"""Mesin animasi stickman: adegan (JSON) -> klip MP4 bergerak.

Latar   : taman, hujan, malam, kota, pantai, gurun, senja, kafe, kamar
Aksi    : diam, jalan, jalan_masuk, pergi, melambai, tertawa, sedih, menangis, malu,
          kaget, cinta, memberi, berlutut, pegangan, memayungi, haus, main_hp, panik, lompat
Chat    : "chat": [{"dari": "kiri"|"kanan", "teks": "..."}]
Posisi  : kiri, tengah, kanan
Bawa    : produk, bunga, cincin, hadiah, payung, gelas, surat, hp
Efek    : hati, hujan, bintang, panah
Tata    : penuh | atas_produk | goyang
Wajah   : senyum, tawa, sedih, nangis, malu, kaget, cinta, haus, datar
"""
import math, random, subprocess
from PIL import Image, ImageDraw, ImageFont
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

W, H, FPS = 1080, 1920, 30
K = (20, 20, 20)
G = 1450
HY = G - 700
POS = {"kiri": 330, "tengah": 540, "kanan": 750}
WARNA = {"hijau": (110, 170, 70), "biru": (50, 100, 220), "merah": (215, 60, 60),
         "merah muda": (245, 130, 170), "pink": (245, 130, 170), "ungu": (140, 90, 200),
         "kuning": (240, 200, 50), "oranye": (240, 140, 50), "hitam": (50, 50, 55),
         "putih": (240, 240, 240), "abu": (150, 150, 155), "coklat": (140, 90, 50), "toska": (40, 180, 170)}


def _gradasi(d, atas, bawah, y1=H):
    for y in range(y1):
        t = y / y1
        d.line([(0, y), (W, y)], fill=tuple(int(a * (1 - t) + b * t) for a, b in zip(atas, bawah)))


def _pohon(d, x, s=1.0):
    d.rectangle([x - 18 * s, G - 330 * s, x + 18 * s, G - 40], fill=(120, 80, 45))
    for dx, dy, r in [(0, -420, 120), (-80, -350, 95), (80, -350, 95)]:
        d.ellipse([x + dx * s - r * s, G + dy * s - r * s, x + dx * s + r * s, G + dy * s + r * s], fill=(70, 150, 70))


def buat_latar(nama):
    img = Image.new("RGB", (W, H)); d = ImageDraw.Draw(img)
    if nama in ("taman", "hujan"):
        _gradasi(d, (120, 180, 235) if nama == "taman" else (95, 105, 125), (200, 225, 245) if nama == "taman" else (140, 150, 165), G)
        d.rectangle([0, G - 80, W, H], fill=(100, 165, 80) if nama == "taman" else (85, 130, 75))
        _pohon(d, 90, .9); _pohon(d, 1000, 1.0)
    elif nama == "malam":
        _gradasi(d, (15, 20, 55), (60, 50, 110), G)
        d.ellipse([780, 200, 940, 360], fill=(250, 245, 210)); d.ellipse([820, 185, 970, 335], fill=(25, 30, 70))
        d.rectangle([0, G - 80, W, H], fill=(40, 70, 50))
    elif nama == "kota":
        _gradasi(d, (150, 200, 240), (230, 235, 245), G)
        random.seed(5)
        x = -20
        while x < W:
            w, h = random.randint(140, 220), random.randint(450, 900)
            c = random.choice([(170, 180, 200), (200, 190, 180), (160, 170, 185), (190, 200, 210)])
            d.rectangle([x, G - 80 - h, x + w, G - 80], fill=c, outline=(120, 120, 130), width=4)
            for wy in range(G - 50 - h, G - 120, 70):
                for wx in range(x + 20, x + w - 30, 50):
                    d.rectangle([wx, wy, wx + 25, wy + 35], fill=(240, 240, 200))
            x += w + 10
        d.rectangle([0, G - 80, W, H], fill=(170, 170, 175))
    elif nama == "pantai":
        _gradasi(d, (110, 190, 240), (210, 235, 250), G - 300)
        d.rectangle([0, G - 300, W, G - 80], fill=(40, 130, 200))
        d.rectangle([0, G - 80, W, H], fill=(240, 215, 160))
    elif nama == "senja":
        _gradasi(d, (250, 140, 90), (255, 210, 140), G)
        d.ellipse([400, G - 330, 680, G - 50], fill=(255, 190, 80))
        d.rectangle([0, G - 80, W, H], fill=(190, 140, 95))
    elif nama == "kafe":
        d.rectangle([0, 0, W, G - 80], fill=(235, 205, 165))
        for x in range(0, W, 120): d.line([(x, 0), (x, G - 80)], fill=(225, 190, 150), width=6)
        d.rounded_rectangle([90, 250, 470, 650], 20, fill=(150, 200, 235), outline=(110, 75, 45), width=14)
        d.rounded_rectangle([610, 250, 990, 650], 20, fill=(150, 200, 235), outline=(110, 75, 45), width=14)
        d.rectangle([0, G - 80, W, H], fill=(140, 95, 60))
    elif nama == "kamar":
        d.rectangle([0, 0, W, G - 80], fill=(70, 75, 120))
        d.rounded_rectangle([650, 230, 960, 600], 15, fill=(25, 30, 70), outline=(200, 190, 170), width=14)
        d.ellipse([820, 300, 900, 380], fill=(250, 245, 210))
        d.rectangle([0, G - 80, W, H], fill=(120, 90, 80))
    else:
        _gradasi(d, (110, 170, 230), (190, 220, 245), G)
        d.rectangle([0, G - 80, W, H], fill=(225, 180, 115))
    return img


def hati(d, x, y, s, warna=(235, 60, 90)):
    d.ellipse([x - s, y - s * .6, x, y + s * .4], fill=warna); d.ellipse([x, y - s * .6, x + s, y + s * .4], fill=warna)
    d.polygon([(x - s * .97, y), (x + s * .97, y), (x, y + s * 1.1)], fill=warna)


def efek(d, nama, t):
    if nama == "hujan":
        random.seed(1)
        for _ in range(170):
            x, y0 = random.randint(0, W + 60), random.randint(0, 1400)
            y = (y0 + t * 900) % 1500; x -= (t * 225) % 60
            d.line([(x, y), (x - 10, y + 40)], fill=(200, 220, 255), width=4)
    elif nama == "hati":
        random.seed(2)
        for k in range(9):
            fase = (t * .35 + k / 9) % 1
            x = 540 + math.sin(t * 2 + k) * 40 + random.randint(-110, 110)
            hati(d, x, HY - 60 - fase * 600, 20 + 16 * math.sin(fase * math.pi))
    elif nama == "bintang":
        random.seed(4)
        for k in range(40):
            x, y = random.randint(0, W), random.randint(0, 700)
            r = 3 + 3 * abs(math.sin(t * 2 + k))
            d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 220))


def chat(d, daftar, t, dur):
    if not daftar: return
    f = ImageFont.truetype(FONT, 46)
    jeda = max(.8, (dur - .5) / len(daftar))
    y = 320
    for k, c in enumerate(daftar):
        muncul = .3 + k * jeda
        if t < muncul: break
        skala = min(1, (t - muncul) / .25)
        teks = c["teks"]
        bx0, by0, bx1, by1 = d.textbbox((0, 0), teks, font=f)
        lw, lh = bx1 - bx0 + 60, by1 - by0 + 44
        kanan = c.get("dari", "kanan") == "kanan"
        x0 = W - 60 - lw if kanan else 60
        warna = (220, 248, 198) if kanan else (255, 255, 255)
        dy = (1 - skala) * 30
        d.rounded_rectangle([x0, y + dy, x0 + lw, y + lh + dy], 28, fill=warna, outline=(60, 60, 60), width=3)
        d.text((x0 + 30, y + 22 + dy - by0), teks, font=f, fill=(25, 25, 25))
        if c.get("centang", kanan):
            d.text((x0 + lw - 50, y + lh - 30 + dy), "✓✓", font=ImageFont.truetype(FONT, 20), fill=(60, 150, 230))
        y += lh + 25


_PRODUK = {}
IMG_AKTIF = [None]


def foto_produk(path, ukuran):
    kunci = (path, ukuran)
    if kunci not in _PRODUK:
        try:
            im = Image.open(path).convert("RGBA")
        except Exception:
            im = Image.new("RGBA", (ukuran, ukuran), (230, 230, 230, 255))
        im.thumbnail((ukuran, ukuran))
        _PRODUK[kunci] = im
    return _PRODUK[kunci]


def produk_goyang(img, foto, t):
    im = foto_produk(foto, 250)
    sudut = math.sin(t * 5) * 7
    r = im.rotate(sudut, expand=True, resample=Image.BICUBIC)
    naik = abs(math.sin(t * 5)) * 18
    kartu = Image.new("RGBA", (r.width + 30, r.height + 30), (0, 0, 0, 0))
    ImageDraw.Draw(kartu).rounded_rectangle([0, 0, kartu.width - 1, kartu.height - 1], 24, fill=(255, 255, 255, 235), outline=(20, 20, 20, 255), width=5)
    kartu.paste(r, (15, 15), r)
    img.paste(kartu, (W // 2 - kartu.width // 2, int(1420 - kartu.height - naik)), kartu)


def tata_atas_produk(img, foto, t, harga=None, coret=None):
    kanvas = Image.new("RGB", (W, H), (255, 244, 230))
    d = ImageDraw.Draw(kanvas)
    for k in range(0, W + H, 90):
        d.line([(k, 0), (k - 920, 920)], fill=(255, 232, 205), width=30)
    uk = int(640 * (1 + 0.04 * math.sin(t * 3)))
    im = foto_produk(foto, 640).copy()
    im = im.resize((max(1, int(im.width * uk / 640)), max(1, int(im.height * uk / 640))))
    kanvas.paste(im, (W // 2 - im.width // 2, 520 - im.height // 2), im)
    if harga:
        f = ImageFont.truetype(FONT, 70); fk = ImageFont.truetype(FONT, 44)
        bx, by = W - 230, 760 + math.sin(t * 6) * 6
        lw = d.textbbox((0, 0), harga, font=f)[2] + 60
        d.rounded_rectangle([bx - lw // 2, by, bx + lw // 2, by + 100], 26, fill=(230, 40, 40), outline=K, width=6)
        d.text((bx, by + 50), harga, font=f, fill="white", anchor="mm")
        if coret:
            d.text((bx, by - 35), coret, font=fk, fill=(90, 90, 90), anchor="mm")
            cw = d.textbbox((0, 0), coret, font=fk)[2]
            d.line([(bx - cw / 2, by - 35), (bx + cw / 2, by - 35)], fill=(220, 30, 30), width=6)
    bawah = img.crop((0, 560, W, 1560)).resize((W, 1000))
    kanvas.paste(bawah, (0, 920))
    d.line([(0, 920), (W, 920)], fill=K, width=8)
    return kanvas


def panah(d, t):
    y = 1700 + abs(math.sin(t * 5)) * 40
    for dx in (-300, 300):
        x = W // 2 + dx
        d.polygon([(x - 50, y), (x + 50, y), (x + 50, y + 60), (x + 85, y + 60), (x, y + 140), (x - 85, y + 60), (x - 50, y + 60)],
                  fill=(255, 140, 0), outline=K)


def barang(d, nama, x, y, arah, t):
    if nama == "bunga":
        d.line([(x, y), (x + arah * 20, y - 120)], fill=(60, 140, 60), width=8)
        for dx, dy, c in [(0, -150, (235, 60, 90)), (-30, -125, (245, 130, 170)), (30, -125, (240, 200, 50))]:
            d.ellipse([x + arah * 20 + dx - 26, y + dy - 26, x + arah * 20 + dx + 26, y + dy + 26], fill=c, outline=K, width=3)
    elif nama == "cincin":
        d.rectangle([x - 35, y - 60, x + 35, y - 10], fill=(200, 40, 60), outline=K, width=4)
        d.ellipse([x - 18, y - 95, x + 18, y - 60], outline=(250, 210, 60), width=7)
    elif nama == "hadiah":
        d.rectangle([x - 50, y - 100, x + 50, y], fill=(80, 160, 230), outline=K, width=4)
        d.rectangle([x - 8, y - 100, x + 8, y], fill=(240, 60, 80)); hati(d, x, y - 115, 16, (240, 60, 80))
    elif nama == "surat":
        d.rectangle([x - 55, y - 80, x + 55, y - 5], fill=(250, 250, 245), outline=K, width=4)
        d.line([(x - 55, y - 80), (x, y - 40), (x + 55, y - 80)], fill=K, width=4); hati(d, x, y - 40, 12)
    elif nama == "produk" and _PRODUK.get("_aktif"):
        im = foto_produk(_PRODUK["_aktif"], 200)
        IMG_AKTIF[0].paste(im, (int(x - im.width / 2), int(y - im.height + 20)), im)
    elif nama == "hp":
        d.rounded_rectangle([x - 32, y - 120, x + 32, y], 10, fill=(30, 30, 35), outline=K, width=3)
        d.rounded_rectangle([x - 25, y - 112, x + 25, y - 10], 6, fill=(120, 220, 255) if int(t * 2) % 2 else (150, 235, 255))
    elif nama == "gelas":
        d.polygon([(x - 45, y - 110), (x + 45, y - 110), (x + 36, y), (x - 36, y)], fill=(180, 185, 190), outline=K)
        d.rectangle([x - 40, y - 105, x + 40, y - 80], fill=(110, 180, 250))


def payung(d, x, y_tangan, warna=(60, 120, 230)):
    top = HY - 200
    d.line([(x, y_tangan), (x, top)], fill=(110, 110, 110), width=12)
    d.chord([x - 290, top - 150, x + 290, top + 150], 180, 360, fill=warna, outline=K, width=7)


def wajah(d, x, y, e, t):
    mata = lambda: (d.ellipse([x - 42, y - 30, x - 22, y], fill=K), d.ellipse([x + 22, y - 30, x + 42, y], fill=K))
    if e == "senyum":
        mata(); d.arc([x - 50, y - 15, x + 50, y + 55], 20, 160, fill=K, width=8)
    elif e == "datar":
        mata(); d.line([(x - 30, y + 35), (x + 30, y + 35)], fill=K, width=7)
    elif e == "tawa":
        d.arc([x - 50, y - 40, x - 15, y - 10], 200, 340, fill=K, width=8); d.arc([x + 15, y - 40, x + 50, y - 10], 200, 340, fill=K, width=8)
        d.chord([x - 55, y - 5, x + 55, y + 75], 0, 180, fill=(120, 30, 30), outline=K, width=6)
        d.ellipse([x - 22, y + 42, x + 22, y + 68], fill=(240, 110, 120))
    elif e in ("sedih", "nangis"):
        d.line([(x - 50, y - 40), (x - 18, y - 30)], fill=K, width=6); d.line([(x + 18, y - 30), (x + 50, y - 40)], fill=K, width=6)
        mata(); d.arc([x - 35, y + 35, x + 35, y + 75], 200, 340, fill=K, width=7)
        if e == "nangis":
            for sx in (-32, 32):
                f = (t * 1.5 + (sx > 0) * .5) % 1
                d.ellipse([x + sx - 9, y + 5 + f * 90, x + sx + 9, y + 30 + f * 90], fill=(110, 180, 250))
    elif e == "malu":
        d.arc([x - 50, y - 25, x - 15, y], 20, 160, fill=K, width=7); d.arc([x + 15, y - 25, x + 50, y], 20, 160, fill=K, width=7)
        d.ellipse([x - 78, y + 5, x - 40, y + 32], fill=(250, 150, 160)); d.ellipse([x + 40, y + 5, x + 78, y + 32], fill=(250, 150, 160))
        d.arc([x - 22, y + 30, x + 22, y + 55], 20, 160, fill=K, width=6)
    elif e == "kaget":
        d.ellipse([x - 48, y - 40, x - 16, y - 2], fill=(255, 255, 255), outline=K, width=6)
        d.ellipse([x + 16, y - 40, x + 48, y - 2], fill=(255, 255, 255), outline=K, width=6)
        d.ellipse([x - 38, y - 28, x - 26, y - 14], fill=K); d.ellipse([x + 26, y - 28, x + 38, y - 14], fill=K)
        d.ellipse([x - 20, y + 25, x + 20, y + 70], fill=(120, 30, 30), outline=K, width=5)
    elif e == "cinta":
        s = 20 + 3 * math.sin(t * 8)
        hati(d, x - 33, y - 22, s); hati(d, x + 33, y - 22, s)
        d.arc([x - 45, y + 5, x + 45, y + 60], 20, 160, fill=K, width=8)
    elif e == "haus":
        d.ellipse([x - 45, y - 15, x - 25, y + 5], fill=K); d.ellipse([x + 25, y - 15, x + 45, y + 5], fill=K)
        d.ellipse([x - 30, y + 25, x + 30, y + 60], fill=(120, 30, 30))


def gambar_tokoh(d, x, spec, pose, t):
    baju = WARNA.get(spec.get("baju", "biru"), (50, 100, 220))
    cewek = spec.get("jenis", "laki").startswith("p")
    y = HY - pose.get("naik", 0)
    pinggul = y + (380 if cewek else 330)
    if pose["kaki"] == "lutut":
        d.line([(x - 30, pinggul), (x - 70, G - 120), (x - 130, G - 110)], fill=K, width=22, joint="curve")
        d.line([(x + 30, pinggul), (x + 80, G - 5), (x + 20, G - 5)], fill=K, width=22, joint="curve")
    else:
        if pose["kaki"] == "jalan":
            s = math.sin(pose["fase"]) * 100
            kaki = [(x - s, G - max(0, -math.cos(pose["fase"])) * 30), (x + s, G - max(0, math.cos(pose["fase"])) * 30)]
        else:
            kaki = [(x - 65, G), (x + 65, G)]
        kaki = [(fx, fy - pose.get("naik", 0)) for fx, fy in kaki]
        for (fx, fy), hx in zip(kaki, (x - 28, x + 28)):
            d.line([(hx, pinggul), (fx, fy)], fill=K, width=22)
            d.ellipse([fx - 35, fy - 18, fx + 35, fy + 17], fill=K)
    if cewek:
        rambut = WARNA.get(spec.get("rambut", "hitam"), (50, 50, 55))
        d.rounded_rectangle([x - 140, y - 115, x + 140, y + 190], 90, fill=rambut)
        d.polygon([(x - 60, y + 115), (x + 60, y + 115), (x + 120, pinggul), (x - 120, pinggul)], fill=baju)
        d.line([(x - 60, y + 115), (x - 120, pinggul), (x + 120, pinggul), (x + 60, y + 115)], fill=K, width=6)
    else:
        d.polygon([(x - 75, y + 115), (x + 75, y + 115), (x + 88, pinggul), (x - 88, pinggul)], fill=baju)
        d.line([(x - 75, y + 115), (x - 88, pinggul), (x + 88, pinggul), (x + 75, y + 115)], fill=K, width=6)
    for i, (tx, ty) in enumerate(pose["tangan"]):
        bx = x - 65 if i == 0 else x + 65
        d.line([(bx, y + 150), (tx, ty)], fill=K, width=20)
        d.ellipse([tx - 22, ty - 22, tx + 22, ty + 22], fill=K)
    d.ellipse([x - 115, y - 115, x + 115, y + 115], fill=(250, 250, 250), outline=K, width=9)
    if cewek:
        d.chord([x - 118, y - 118, x + 118, y + 60], 180, 360, fill=rambut)
        hati(d, x + 85, y - 95, 26, (235, 60, 90))
    else:
        d.chord([x - 117, y - 117, x + 117, y + 40], 195, 345, fill=WARNA.get(spec.get("rambut", "hitam"), (50, 50, 55)))
    wajah(d, x, y + 10, pose["wajah"], t)
    if pose.get("bawa") and pose["bawa"] != "payung":
        tx, ty = pose["tangan"][1 if pose.get("arah", 1) > 0 else 0]
        barang(d, pose["bawa"], tx, ty, pose.get("arah", 1), t)


WAJAH_AKSI = {"tertawa": "tawa", "sedih": "sedih", "menangis": "nangis", "malu": "malu", "kaget": "kaget",
              "cinta": "cinta", "pergi": "sedih", "haus": "haus", "panik": "kaget", "lompat": "tawa"}


def pose_tokoh(tk, spec, t, dur, jumlah=2):
    aksi = tk.get("aksi", "diam")
    pos = {"kiri": 190, "tengah": 540, "kanan": 890} if jumlah >= 3 else POS
    x0 = pos.get(tk.get("posisi", "tengah"), 540)
    arah = 1 if x0 < 540 else -1
    if tk.get("posisi") == "tengah":
        arah = tk.get("hadap", 1)
    x, kaki, fase, naik = x0, "diri", 0, 0
    y = HY
    napas = math.sin(t * 2.5) * 6
    tangan = [(x - 150, y + 340 + napas), (x + 150, y + 340 + napas)]
    jalan_dur = min(2.5, dur * .5)
    if aksi == "jalan_masuk" and t < jalan_dur:
        mulai = -250 if x0 <= 540 else W + 250
        x = mulai + (x0 - mulai) * (t / jalan_dur); kaki = "jalan"; fase = t * 7
    elif aksi == "pergi" and t > .8:
        tujuan = -300 if x0 <= 540 else W + 300
        x = x0 + (tujuan - x0) * min(1, (t - .8) / 2.5); kaki = "jalan"; fase = t * 7
    elif aksi == "jalan":
        kaki = "jalan"; fase = t * 7
    if kaki == "jalan":
        naik = abs(math.sin(fase)) * 12
        a = math.sin(fase) * 60
        tangan = [(x - 150 + a, y + 330 - naik), (x + 150 - a, y + 330 - naik)]
    depan = 1 if arah > 0 else 0
    ulur = min(1, t / 1.2)
    if aksi == "melambai":
        tangan[depan] = (x + arah * (170 + 40 * math.sin(t * 9)), y - 60)
    elif aksi == "tertawa":
        naik = abs(math.sin(t * 20)) * 14
        tangan = [(x - 140, y + 280 - naik), (x + 140, y + 280 - naik)]
    elif aksi in ("sedih", "menangis", "pergi"):
        naik = -12
        tangan = [(x - 110, y + 370), (x + 110, y + 370)] if kaki != "jalan" else tangan
    elif aksi == "malu":
        tangan = [(x - 25, y + 300), (x + 25, y + 300)]; x += math.sin(t * 3) * 10
    elif aksi == "kaget":
        naik = max(0, math.sin(min(t, .5) / .5 * math.pi)) * 80
        tangan = [(x - 190, y - 20 - naik), (x + 190, y - 20 - naik)]
    elif aksi == "cinta":
        x += math.sin(t * 2.5) * 15
        tangan = [(x - 40, y + 260), (x + 40, y + 260)]
    elif aksi in ("memberi", "pegangan"):
        tangan[depan] = (x + arah * (150 + 120 * ulur), y + 300 - 60 * ulur)
    elif aksi == "berlutut":
        kaki = "lutut"; naik = -110
        tangan[depan] = (x + arah * (150 + 110 * ulur), y + 200 - 30 * ulur)
    elif aksi == "memayungi":
        tangan[depan] = (x + arah * 200, y + 190)
    elif aksi == "main_hp":
        tangan[depan] = (x + arah * 70, y + 230); tangan[1 - depan] = (x - arah * 30, y + 270)
    elif aksi == "panik":
        x += math.sin(t * 25) * 10
        tangan = [(x - 90, y - 60 + math.sin(t * 12) * 20), (x + 90, y - 60 - math.sin(t * 12) * 20)]
    elif aksi == "lompat":
        naik = abs(math.sin(t * 5)) * 120
        tangan = [(x - 180, y - 80 - naik), (x + 180, y - 80 - naik)]
    elif aksi == "haus":
        kaki = "lutut"; naik = -110 + math.sin(t * 3) * 12
        tangan = [(x - 140, G - 30), (x + 140, G - 30)]
    if naik < 0 and kaki != "jalan":
        tangan = [(tx, ty - naik) for tx, ty in tangan] if aksi not in ("berlutut", "haus") else tangan
    bawa = tk.get("bawa")
    if bawa == "payung" and aksi not in ("memayungi",):
        tangan[depan] = (x + arah * 90, y + 200 - naik)
    return x, {"kaki": kaki, "fase": fase, "naik": naik, "tangan": tangan, "arah": arah,
               "wajah": tk.get("wajah") or WAJAH_AKSI.get(aksi, "senyum"), "bawa": bawa}


def buat_klip(adegan, tokoh_def, dur, path):
    latar = buat_latar(adegan.get("latar", "taman"))
    produk = adegan.get("produk") or {}
    _PRODUK["_aktif"] = produk.get("foto")
    efek_list = adegan.get("efek", [])
    if isinstance(efek_list, str): efek_list = [efek_list]
    if adegan.get("latar") == "hujan" and "hujan" not in efek_list: efek_list.append("hujan")
    if adegan.get("latar") == "malam" and "bintang" not in efek_list: efek_list.append("bintang")
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
                          "-pix_fmt", "yuv420p", str(path)], stdin=subprocess.PIPE)
    for f in range(int(dur * FPS) + 2):
        t = f / FPS
        img = latar.copy(); d = ImageDraw.Draw(img); IMG_AKTIF[0] = img
        for e in efek_list:
            if e == "bintang": efek(d, e, t)
        for tk in adegan.get("tokoh", []):
            spec = tokoh_def.get(tk["nama"], {})
            x, pose = pose_tokoh(tk, spec, t, dur, len(adegan.get("tokoh", [])))
            if pose["bawa"] == "payung":
                tx, ty = pose["tangan"][1 if pose["arah"] > 0 else 0]
                payung(d, tx, ty)
            gambar_tokoh(d, x, spec, pose, t)
        for e in efek_list:
            if e == "panah": panah(d, t)
            elif e != "bintang": efek(d, e, t)
        chat(d, adegan.get("chat"), t, dur)
        tata = adegan.get("tata", "penuh")
        if tata == "goyang" and produk.get("foto"):
            produk_goyang(img, produk["foto"], t)
        elif tata == "atas_produk" and produk.get("foto"):
            img = tata_atas_produk(img, produk["foto"], t, adegan.get("harga"), adegan.get("coret"))
        p.stdin.write(img.tobytes())
    p.stdin.close(); p.wait()
