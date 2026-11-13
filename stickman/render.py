"""Render video stickman 9:16 dari cerita/*.json.
Suara: ElevenLabs (secret ELEVENLABS_API_KEY) atau edge-tts gratis | Musik: musik.py | Animasi: mesin.py
"""
import asyncio, json, math, os, subprocess, sys, time, urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ELEVEN_DEFAULT = "W98P5TTtcHAH6zHkf7ul"   # Raya Fie: perempuan Indonesia, cocok affiliate


def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def durasi(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", str(path)], capture_output=True, text=True).stdout
    return float(out.strip())


def unduh_foto(url, path):
    png = path.with_suffix(".png")
    if png.exists():
        return str(png)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as r:
            path.write_bytes(r.read())
        Image.open(path).convert("RGBA").save(png)
        return str(png)
    except Exception as e:
        print(f"  gagal unduh foto produk ({e})")
        return url


async def _tts(teks, suara, path):
    import edge_tts
    await edge_tts.Communicate(teks, suara, rate="+5%").save(str(path))


def suara_eleven(teks, voice_id, path):
    key = os.environ.get("ELEVENLABS_API_KEY")
    if not key:
        return False
    body = json.dumps({"text": teks, "model_id": "eleven_multilingual_v2",
                       "voice_settings": {"stability": 0.45, "similarity_boost": 0.8, "style": 0.35,
                                          "use_speaker_boost": True}}).encode()
    req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}?output_format=mp3_44100_128",
                                 data=body, headers={"xi-api-key": key, "Content-Type": "application/json"})
    for i in range(3):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                path.write_bytes(r.read())
            return True
        except Exception as e:
            print(f"  ElevenLabs gagal ({e})")
            time.sleep(5)
    return False


def buat_suara(teks, suara, path, eleven=None):
    if eleven and suara_eleven(teks, eleven, path):
        return
    for _ in range(3):
        try:
            asyncio.run(_tts(teks, suara, path))
            return
        except Exception as e:
            print(f"  TTS gagal ({e}), coba lagi")
            time.sleep(5)
    print("  pakai hening")
    dur = max(2.5, len(teks.split()) / 2.6)
    run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-t", f"{dur:.2f}", str(path)])


def bungkus(teks, lebar):
    baris, kini = [], ""
    for k in teks.split():
        if len(kini) + len(k) + 1 > lebar and kini:
            baris.append(kini)
            kini = k
        else:
            kini = (kini + " " + k).strip()
    if kini:
        baris.append(kini)
    return "\n".join(baris)


def potong_subtitle(teks, maks_kata=6):
    kata = teks.split()
    n = math.ceil(len(kata) / maks_kata)
    per = math.ceil(len(kata) / n)
    return [" ".join(kata[i:i + per]) for i in range(0, len(kata), per)]


def png_subtitle(teks, path):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(FONT, 64)
    d.multiline_text((W / 2, H * 0.80), bungkus(teks.upper(), 20), font=f, fill=(255, 230, 0),
                     anchor="mm", align="center", stroke_width=7, stroke_fill="black", spacing=10)
    img.save(path)


def png_judul(teks, path):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(FONT, 58)
    tb = d.multiline_textbbox((W / 2, 120), bungkus(teks, 24), font=f, anchor="ma", align="center", spacing=8)
    d.rounded_rectangle([tb[0] - 30, tb[1] - 22, tb[2] + 30, tb[3] + 26], 24, fill=(0, 0, 0, 170))
    d.multiline_text((W / 2, 120), bungkus(teks, 24), font=f, fill="white", anchor="ma", align="center", spacing=8)
    img.save(path)


def render_adegan(i, adegan, cfg, kerja):
    import mesin
    teks = adegan["teks"]
    mp3 = kerja / f"a{i}.mp3"
    buat_suara(teks, cfg["suara"], mp3, cfg.get("eleven"))
    dur = durasi(mp3) + 0.4
    if cfg.get("produk_foto"):
        adegan.setdefault("produk", {}).setdefault("foto", cfg["produk_foto"])
    anim = kerja / f"anim{i}.mp4"
    mesin.buat_klip(adegan, cfg["tokoh"], dur, anim)
    potongan = potong_subtitle(teks)
    bobot = [len(p) for p in potongan]
    total = sum(bobot)
    inputs, filt, t0 = [], [], 0.0
    filt.append(f"[0:v]scale={W}:{H},fps={FPS},setpts=PTS-STARTPTS[v0]")
    for j, p in enumerate(potongan):
        sp = kerja / f"s{i}_{j}.png"
        png_subtitle(p, sp)
        inputs += ["-i", str(sp)]
        t1 = t0 + (dur - 0.4) * bobot[j] / total
        akhir = dur if j == len(potongan) - 1 else t1
        filt.append(f"[v{j}][{j + 1}:v]overlay=0:0:enable='between(t,{t0:.2f},{akhir:.2f})'[v{j + 1}]")
        t0 = t1
    n = len(potongan)
    if cfg.get("judul_png"):
        inputs += ["-i", str(cfg["judul_png"])]
        filt.append(f"[v{n}][{n + 1}:v]overlay=0:0[v{n + 1}]")
        n += 1
    filt.append(f"[v{n}]fade=t=in:st=0:d=0.3,format=yuv420p[vout]")
    out = kerja / f"c{i}.mp4"
    run(["ffmpeg", "-y", "-stream_loop", "-1", "-i", str(anim), *inputs,
         "-i", str(mp3), "-filter_complex", ";".join(filt),
         "-map", "[vout]", "-map", f"{n + 1}:a", "-af", "apad",
         "-t", f"{dur:.2f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
         "-c:a", "aac", "-ar", "44100", "-ac", "2", "-r", str(FPS), str(out)])
    return out


def render_cerita(json_path, folder_out):
    nama = json_path.stem
    hasil = folder_out / f"{nama}.mp4"
    if hasil.exists():
        print(f"Lewati {nama} (video sudah ada)")
        return
    data = json.loads(json_path.read_text(encoding="utf-8"))
    kerja = Path("kerja") / nama
    kerja.mkdir(parents=True, exist_ok=True)
    foto = data.get("produk_foto")
    if foto and foto.startswith("http"):
        foto = unduh_foto(foto, kerja / "produk_asli")
    cfg = {
        "suara": data.get("suara", "id-ID-GadisNeural"),
        "tokoh": data.get("tokoh", {}),
        "eleven": data.get("suara_eleven", ELEVEN_DEFAULT),
        "produk_foto": foto,
    }
    if data.get("judul_layar"):
        cfg["judul_png"] = kerja / "judul.png"
        png_judul(data["judul_layar"], cfg["judul_png"])
    print(f"Render {nama}: {len(data['adegan'])} adegan")
    klip = [render_adegan(i, a, cfg, kerja) for i, a in enumerate(data["adegan"])]
    daftar = kerja / "daftar.txt"
    daftar.write_text("".join(f"file '{c.resolve()}'\n" for c in klip))
    folder_out.mkdir(exist_ok=True)
    gabung = kerja / "gabung.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(daftar), "-c", "copy", str(gabung)])
    if data.get("musik", "ceria") != "tanpa":
        import musik
        wav = kerja / "musik.wav"
        musik.buat_musik(durasi(gabung), wav, data.get("musik", "ceria"))
        run(["ffmpeg", "-y", "-i", str(gabung), "-i", str(wav), "-filter_complex",
             "[1:a]volume=0.10[m];[0:a][m]amix=inputs=2:duration=first:normalize=0[a]",
             "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
             "-movflags", "+faststart", str(hasil)])
    else:
        run(["ffmpeg", "-y", "-i", str(gabung), "-c", "copy", "-movflags", "+faststart", str(hasil)])
    print(f"Selesai: {hasil} ({durasi(hasil):.1f} detik)")


if __name__ == "__main__":
    folder_out = Path("video")
    target = sys.argv[1:] or sorted(str(p) for p in Path("cerita").glob("*.json"))
    for t in target:
        try:
            render_cerita(Path(t), folder_out)
        except Exception as e:
            print(f"GAGAL render {t}: {e}")
