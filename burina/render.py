"""Bu Rina: render 1 video tips FB Pro (40 dtk) dari naskah.json berikutnya, lalu kabari Make untuk posting.

Dijalankan GitHub Actions 5x sehari. Suara: ElevenLabs (Riri, tegas), 8 potong per video.
Foto: acak dari burina/foto/ (kalau ada) + artis/. Hasil: burina/out/<id>.mp4, catatan di burina/sudah.json.
"""
import json, os, random, shutil, subprocess, sys, urllib.request
from pathlib import Path

ROOT = Path(__file__).parent
REPO = ROOT.parent
REMO = ROOT / "remo"
CFG = json.loads((ROOT / "config.json").read_text())
VOICE = CFG.get("voice_id", "tCKeP99grYL9wZRg6sQ9")
KEY = os.environ["ELEVENLABS_API_KEY"]
MULAI = [0.15, 5.2, 10.2, 15.2, 20.2, 25.2, 30.4, 35.3]  # detik tiap potongan suara
ANGKA = ["Satu", "Dua", "Tiga", "Empat", "Lima"]


def sh(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode:
        raise RuntimeError(" ".join(map(str, cmd[:3])) + ": " + (r.stderr or r.stdout)[-800:])
    return r.stdout


def durasi(p):
    return float(sh(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)]))


def tts(teks, out):
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}?output_format=mp3_44100_128",
        data=json.dumps({"text": teks, "model_id": CFG.get("model_id", "eleven_multilingual_v2"),
                         "voice_settings": {"stability": 0.45, "similarity_boost": 0.8, "style": 0.35, "use_speaker_boost": True}}).encode(),
        headers={"xi-api-key": KEY, "Content-Type": "application/json", "Accept": "audio/mpeg"})
    out.write_bytes(urllib.request.urlopen(req, timeout=120).read())


def musik(out):
    import numpy as np, wave
    sr, T = 44100, 40
    o = np.zeros(sr * T)
    def note(m, s, d, v):
        f = 440 * 2 ** ((m - 69) / 12); i0 = int(s * sr); n = int(d * sr); t = np.arange(n) / sr
        w = (np.sin(2 * np.pi * f * t) + .3 * np.sin(4 * np.pi * f * t)) * np.exp(-t * 2.2) * (1 - np.exp(-t * 80)) * v
        e = min(len(o), i0 + n); o[i0:e] += w[:e - i0]
    ch = [[60, 64, 67], [57, 60, 64], [53, 57, 60], [55, 59, 62]]
    beat = 60 / 96
    for b in range(int(T / beat)):
        c = ch[(b // 8) % 4]
        if b % 8 == 0:
            for m in c: note(m - 12, b * beat, beat * 8, .1)
        note([c[0], c[1], c[2], c[1] + 12][b % 4] + 12, b * beat, beat * 1.5, .16)
    o = o / np.abs(o).max() * .8
    d = (o * 32767).astype(np.int16)
    w = wave.open(str(out), "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(d.tobytes()); w.close()


def main():
    naskah = json.loads((ROOT / "naskah.json").read_text())
    sudah_p = ROOT / "sudah.json"
    sudah = json.loads(sudah_p.read_text()) if sudah_p.exists() else []
    sisa = [n for n in naskah if n["id"] not in sudah]
    if not sisa:
        print("Naskah habis, tidak ada yang dirender."); return
    n = sisa[0]
    kerja = ROOT / "kerja"; shutil.rmtree(kerja, ignore_errors=True); kerja.mkdir()

    teks = [n["hook"]] + [f"{ANGKA[i]}. {j}. {s}" for i, (j, s) in enumerate(n["tips"])] + \
           [f"Bonus. {n['bonus'][0]}. {n['bonus'][1]}", f"{n['cta']} Tulis di komentar, ya!"]
    fc, lab = "", ""
    for i, t in enumerate(teks):
        p = kerja / f"s{i}.mp3"; tts(t, p)
        d = durasi(p); batas = 4.75 if i < 7 else 4.5
        tempo = min(1.25, d / batas) if d > batas else 1.0
        ms = int(MULAI[i] * 1000)
        fc += f"[{i}:a]atempo={tempo:.3f},atrim=0:{batas},adelay={ms}|{ms}[s{i}];"; lab += f"[s{i}]"
    musik(kerja / "musik.wav")
    fc += (f"{lab}amix=inputs=8:normalize=0,apad=whole_dur=40,highpass=f=90,acompressor=threshold=-22dB:ratio=4,volume=2.2,asplit=2[n][sc];"
           "[8:a]volume=0.08,afade=t=out:st=37.5:d=2.5[m];[m][sc]sidechaincompress=threshold=0.03:ratio=8[md];"
           "[n][md]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1[a]")
    ins = sum([["-i", str(kerja / f"s{i}.mp3")] for i in range(8)], []) + ["-i", str(kerja / "musik.wav")]
    sh(["ffmpeg", "-loglevel", "error", "-y", *ins, "-filter_complex", fc, "-map", "[a]", "-t", "40", str(kerja / "audio.wav")])

    pool = [p for d in (ROOT / "foto", REPO / "artis") if d.exists() for p in d.iterdir()
            if p.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp")]
    pilih = random.sample(pool, 3)
    pub = REMO / "public" / "foto"; shutil.rmtree(pub, ignore_errors=True); pub.mkdir(parents=True)
    foto = []
    for k, p in enumerate(pilih):
        shutil.copy(p, pub / f"{k}{p.suffix.lower()}"); foto.append(f"foto/{k}{p.suffix.lower()}")
    urut = [0, 1, 2, 3]; random.shuffle(urut)
    props = {"foto": foto, "thumb": {k: n[k] for k in ("besar", "label", "kecil")}, "tips": n["tips"],
             "bonus": n["bonus"], "cta": n["cta"], "urut": urut}
    (kerja / "props.json").write_text(json.dumps(props))

    if not (REMO / "node_modules" / "remotion").exists():
        sh(["npm", "install", "--no-audit", "--no-fund", "--loglevel=error"], cwd=REMO, timeout=900)
    sh(["npx", "remotion", "render", "src/index.ts", "Film", str(kerja / "v.mp4"), f"--props={kerja / 'props.json'}",
        "--muted", "--concurrency=2", "--log=error"], cwd=REMO, timeout=2400)

    out = ROOT / "out"; out.mkdir(exist_ok=True)
    sh(["ffmpeg", "-loglevel", "error", "-y", "-i", str(kerja / "v.mp4"), "-i", str(kerja / "audio.wav"),
        "-vf", "scale=720:1280", "-c:v", "libx264", "-preset", "veryfast", "-crf", "26", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", "-t", "40", str(out / f"{n['id']}.mp4")])
    sudah.append(n["id"]); sudah_p.write_text(json.dumps(sudah))
    tag = "#facebookpro #tipsfacebook #kontenkreator #iburumahtangga #belajarbareng"
    caption = f"{n['hook']}\n\n{n['cta']} Tulis di komentar 👇\n\n(Bu Rina adalah karakter AI)\n{tag}"
    (ROOT / "terakhir.json").write_text(json.dumps({"id": n["id"], "caption": caption}, ensure_ascii=False))
    shutil.rmtree(kerja, ignore_errors=True)
    print(f"OK video {n['id']}")


if __name__ == "__main__":
    main()
