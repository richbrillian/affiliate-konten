"""Musik latar lo-fi gratis (dibuat dengan kode, bebas hak cipta).
Suasana: romantis, ceria, sedih, tegang
"""
import wave
import numpy as np

SR = 44100
NADA = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
SUASANA = {
    "romantis": (78, [("F", [0, 4, 7, 11]), ("E", [0, 3, 7, 10]), ("D", [0, 3, 7, 10]), ("C", [0, 4, 7, 11])]),
    "ceria":    (100, [("C", [0, 4, 7, 11]), ("A", [0, 3, 7, 10]), ("F", [0, 4, 7, 11]), ("G", [0, 4, 7, 10])]),
    "sedih":    (66, [("A", [0, 3, 7, 10]), ("F", [0, 4, 7, 11]), ("C", [0, 4, 7, 11]), ("G", [0, 4, 7, 10])]),
    "tegang":   (90, [("D", [0, 3, 7]), ("D", [0, 3, 8]), ("A", [0, 3, 7]), ("A", [0, 4, 7])]),
}


def _frek(akar, semi, oktaf=3):
    return 440 * 2 ** ((NADA[akar] + semi + 12 * (oktaf - 4) + 3 - 12) / 12)


def buat_musik(durasi, path, suasana="romantis"):
    bpm, akor = SUASANA.get(suasana, SUASANA["romantis"])
    ketuk = 60 / bpm
    bar = ketuk * 4
    n = int(durasi * SR) + SR
    out = np.zeros(n)
    rng = np.random.default_rng(7)
    t_bar = np.arange(int(bar * SR)) / SR
    i, mulai = 0, 0
    while mulai < n:
        akar, interval = akor[i % len(akor)]
        seg = np.zeros(len(t_bar))
        env = np.minimum(1, t_bar / .4) * np.exp(-t_bar / (bar * 1.2))
        for s in interval:
            f = _frek(akar, s, 4)
            seg += (np.sin(2 * np.pi * f * t_bar) + .3 * np.sin(4 * np.pi * f * t_bar)) * env * .08
        fb = _frek(akar, 0, 2)
        seg += np.sin(2 * np.pi * fb * t_bar) * np.exp(-((t_bar % ketuk) / .5)) * .18
        for k in range(8):
            if rng.random() < .65:
                s = interval[rng.integers(len(interval))] + (12 if rng.random() < .5 else 0)
                f = _frek(akar, s, 5)
                a = int(k * ketuk / 2 * SR)
                tt = np.arange(int(ketuk * SR)) / SR
                not_ = np.sin(2 * np.pi * f * tt) * np.exp(-tt * 5) * .07
                seg[a:a + len(not_)] += not_[:len(seg) - a]
        for k in range(4):
            a = int(k * ketuk * SR)
            tt = np.arange(int(.25 * SR)) / SR
            if k in (0, 2):
                kick = np.sin(2 * np.pi * (55 + 60 * np.exp(-tt * 30)) * tt) * np.exp(-tt * 12) * .35
                seg[a:a + len(kick)] += kick[:len(seg) - a]
            h = int((k + .5) * ketuk * SR)
            hat = rng.standard_normal(int(.05 * SR)) * np.exp(-np.arange(int(.05 * SR)) / SR * 90) * .03
            seg[h:h + len(hat)] += hat[:max(0, len(seg) - h)]
        out[mulai:mulai + len(seg)] += seg[:n - mulai]
        mulai += len(seg); i += 1
    out = out[:int(durasi * SR)]
    fade = int(1.5 * SR)
    out[:fade] *= np.linspace(0, 1, fade); out[-fade:] *= np.linspace(1, 0, fade)
    out = out / (np.abs(out).max() + 1e-9) * .8
    stereo = np.repeat((out * 32767).astype(np.int16)[:, None], 2, axis=1)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(stereo.tobytes())
