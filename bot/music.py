"""Telifsiz, kodla uretilen arka plan muzigi (her gun farkli akor/tempo)."""
import wave
import numpy as np

SR = 44100
PROGS = [
    [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]],  # Am F C G
    [[48, 52, 55], [55, 59, 62], [57, 60, 64], [53, 57, 60]],  # C G Am F
    [[50, 53, 57], [55, 59, 62], [48, 52, 55], [57, 60, 64]],  # Dm G C Am
    [[52, 55, 59], [48, 52, 55], [55, 59, 62], [50, 54, 57]],  # Em C G D
]


def note(m): return 440 * 2 ** ((m - 69) / 12)


def make_music(path, dur, seed=0, cuts=()):
    rng = np.random.default_rng(seed)
    bpm = [112, 118, 120, 124][seed % 4]; beat = 60 / bpm
    chords = PROGS[seed % len(PROGS)]
    n = int(SR * dur); out = np.zeros(n)

    def add(sig, start):
        i = int(start * SR); j = min(n, i + len(sig))
        if 0 <= i < n: out[i:j] += sig[:j - i]

    kt = np.arange(int(0.35 * SR)) / SR
    kick = np.sin(2 * np.pi * (45 * kt + 90 * (1 - np.exp(-kt * 30)) / 30)) * np.exp(-kt * 9) * 0.9
    hl = int(0.06 * SR); hat = np.diff(rng.standard_normal(hl) * np.exp(-np.arange(hl) / SR * 70), prepend=0) * 0.12
    cl = int(0.18 * SR); clap = rng.standard_normal(cl) * np.exp(-np.arange(cl) / SR * 22) * 0.18

    for b in range(int(dur / (4 * beat)) + 1):
        t0 = b * 4 * beat; ch = chords[b % 4]
        L = int(4 * beat * SR); pt = np.arange(L) / SR
        envl = np.minimum(1, pt / 0.3) * np.minimum(1, (4 * beat - pt) / 0.3)
        pad = sum(np.sin(2 * np.pi * note(m) * pt) + 0.3 * np.sin(2 * np.pi * note(m) * 2.003 * pt) for m in ch)
        add(pad * envl * 0.05, t0)
        for k in range(8):
            bt = np.arange(int(beat / 2 * SR)) / SR; f = note(ch[0] - 12)
            add((np.sin(2 * np.pi * f * bt) + 0.25 * np.sin(4 * np.pi * f * bt)) * np.exp(-bt * 6) * 0.22, t0 + k * beat / 2)
        arp = ch + [ch[1] + 12]
        for k in range(16):
            ptt = np.arange(int(0.25 * SR)) / SR
            add(np.sin(2 * np.pi * note(arp[k % 4] + 12) * ptt) * np.exp(-ptt * 14) * 0.06, t0 + k * beat / 4)
        for k in range(4):
            tb = t0 + k * beat
            if tb > 0.4: add(kick, tb)
            if k in (1, 3) and tb > 3: add(clap, tb)
            add(hat, tb + beat / 2)
    for ts in cuts:
        wl = int(0.6 * SR); wt = np.arange(wl) / SR
        w = np.convolve(rng.standard_normal(wl), np.ones(30) / 30, "same")
        add(w * np.sin(np.pi * wt / 0.6) ** 2 * 0.35, ts - 0.4)
    fade = np.ones(n); fl = int(1.5 * SR); fade[-fl:] = np.linspace(1, 0, fl); fade[:int(0.05 * SR)] = np.linspace(0, 1, int(0.05 * SR))
    out = np.tanh(out * fade * 1.3); out /= max(1e-6, np.max(np.abs(out))) / 0.89
    st = (np.stack([out, out], 1) * 32767).astype(np.int16)
    with wave.open(path, "wb") as f:
        f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR); f.writeframes(st.tobytes())
