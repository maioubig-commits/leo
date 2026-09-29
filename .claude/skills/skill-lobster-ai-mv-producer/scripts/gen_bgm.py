#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
程式合成原創 instrumental BGM — Suno 生歌之外的備援路線。

用途：音檔還沒生好、或這支片不需要人聲（物件巡禮、開場暖場）時，直接合出一段
可商用的背景音樂。純 numpy 加法合成，沒有取樣素材，所以沒有任何授權問題。

跟 Suno 的取捨：這裡出的是純樂器 instrumental，做不出人聲 Rap。要洗腦歌詞還是得走 Suno。

用法：
    python3 gen_bgm.py --out bgm.wav --duration 55 --bpm 130
    python3 gen_bgm.py --out bgm.wav --duration 55 --bpm 130 --mood bright

編曲：A 小調 i-VI-III-VII（Am-F-C-G），trap 鼓組 ＋ sub bass ＋ pad ＋ hook 段 lead，
段落走 intro → verse → hook → verse → hook → bridge → final hook，每 4 小節換段。
"""
import argparse, wave
from pathlib import Path
import numpy as np

SR = 44100
A4 = 440.0
NOTE = {"C": -9, "C#": -8, "D": -7, "D#": -6, "E": -5, "F": -4,
        "F#": -3, "G": -2, "G#": -1, "A": 0, "A#": 1, "B": 2}


def hz(name, octave=4):
    return A4 * 2 ** (NOTE[name] / 12 + (octave - 4))


def env(n, attack, decay, sustain=0.0, release=None):
    """線性 ADSR；release 不給就用剩下的長度收乾淨。"""
    a, d = int(attack * SR), int(decay * SR)
    a, d = min(a, n), min(d, max(0, n - 1))
    out = np.zeros(n)
    if a:
        out[:a] = np.linspace(0, 1, a)
    tail = n - a
    if tail > 0:
        if sustain > 0:
            r = int((release or 0.05) * SR)
            r = min(r, tail)
            body = tail - r
            if body > 0:
                out[a:a + body] = np.linspace(1, sustain, body)
            if r:
                out[a + body:] = np.linspace(sustain, 0, r)
        else:
            out[a:] = np.exp(-np.linspace(0, 6, tail))
    return out


def sine(f, n, phase=0.0):
    return np.sin(2 * np.pi * f * np.arange(n) / SR + phase)


def saw(f, n):
    """疊 8 次諧波的軟鋸齒 — 直接用 sawtooth 會太刺。"""
    t = np.arange(n) / SR
    return sum(np.sin(2 * np.pi * f * k * t) / k for k in range(1, 9)) / 2.2


def lowpass(x, cutoff):
    """一階 IIR，夠用就好。"""
    a = np.exp(-2 * np.pi * cutoff / SR)
    out = np.zeros_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc = a * acc + (1 - a) * v
        out[i] = acc
    return out


def hp_noise(n, cutoff):
    """白噪音減掉低頻＝高通。cutoff 直接給 Hz：hihat 要 7k 以上才像金屬片，
    給低了會變成整片噴氣聲蓋過鼓（第一版就是栽在這）。"""
    x = np.random.randn(n)
    return x - lowpass(x, cutoff)


# ───────────────────────── 鼓組 ─────────────────────────
def kick(n):
    t = np.arange(n) / SR
    f = 110 * np.exp(-t * 32) + 42          # 掃頻：打擊感來自這條曲線
    body = np.sin(2 * np.pi * np.cumsum(f) / SR)
    click = hp_noise(n, 3000) * np.exp(-t * 220) * 0.20
    return (body * env(n, 0.001, 0.34) + click) * 0.95


def snare(n):
    t = np.arange(n) / SR
    tone = (sine(190, n) + sine(285, n)) * 0.35
    return (hp_noise(n, 1200) * 0.8 + tone) * np.exp(-t * 26) * 0.50


def hihat(n, open_=False):
    t = np.arange(n) / SR
    decay = 9 if open_ else 55
    return hp_noise(n, 7000) * np.exp(-t * decay) * (0.14 if open_ else 0.10)


def place(buf, sample, at):
    i = int(at * SR)
    j = min(len(buf), i + len(sample))
    if i < len(buf):
        buf[i:j] += sample[:j - i]


def main():
    ap = argparse.ArgumentParser(description="程式合成原創 instrumental BGM")
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--duration", type=float, default=55.0)
    ap.add_argument("--bpm", type=float, default=130.0)
    ap.add_argument("--mood", default="dark", choices=["dark", "bright"],
                    help="dark = 小調暗色（預設）；bright = 同進行但 pad 亮、lead 高八度")
    args = ap.parse_args()

    beat = 60.0 / args.bpm
    bar = 4 * beat
    total = int(args.duration * SR) + SR          # 尾巴留 1 秒讓殘響收乾淨
    nbars = int(np.ceil(args.duration / bar))

    drums = np.zeros(total)
    bass = np.zeros(total)
    pad = np.zeros(total)
    lead = np.zeros(total)

    # i - VI - III - VII：A 小調最好用的四和弦循環
    prog = [("A", 2, ["A", "C", "E"]), ("F", 2, ["F", "A", "C"]),
            ("C", 3, ["C", "E", "G"]), ("G", 2, ["G", "B", "D"])]

    # 段落表：每 4 小節一段，決定各軌開關
    def section(b):
        if b < 2:
            return "intro"
        if b >= nbars - 2:
            return "outro"
        return ["verse", "verse", "hook", "verse", "hook", "bridge", "hook"][min(6, (b - 2) // 4)]

    hook_notes = [("A", 5, 0), ("C", 6, 1.5), ("B", 5, 2.5), ("E", 5, 3)]

    for b in range(nbars):
        t0 = b * bar
        sec = section(b)
        root, octv, chord = prog[b % 4]

        # ── 鼓
        if sec not in ("intro", "outro"):
            for step in range(16):
                t = t0 + step * beat / 4
                if step in (0, 6, 10):
                    place(drums, kick(int(0.35 * SR)), t)
                if step in (4, 12):
                    place(drums, snare(int(0.25 * SR)), t)
                if sec == "bridge" and step % 4:
                    continue
                if step % 2 == 0:
                    hh = hihat(int(0.12 * SR), open_=(step == 14))
                    place(drums, hh * (1.6 if args.mood == "bright" else 1.0), t)
                elif sec == "hook" and step in (7, 15):
                    place(drums, hihat(int(0.08 * SR)), t)     # 16 分 roll 只放 hook

        # ── Bass：根音長音 ＋ 八分律動
        if sec != "intro":
            f = hz(root, octv - 1)
            n = int(bar * SR)
            b_long = sine(f, n) * env(n, 0.01, 0.1, 0.75, 0.25) * 0.5
            place(bass, b_long, t0)
            if sec in ("hook", "verse"):
                for step in (3, 7, 11, 14):
                    nn = int(beat * 0.45 * SR)
                    place(bass, sine(f * 2, nn) * env(nn, 0.005, 0.12) * 0.18,
                          t0 + step * beat / 4)

        # ── Pad：和弦三音，慢起慢收
        # bright 要升「兩個」八度才聽得出來：prog 的 octv 是 2-3，pad 原本落在 110-260Hz，
        # 升一個八度仍在低頻嗡嗡區，量到的差只有 0.3dB。升到 octave 4-5 才是明亮的中頻和聲。
        n = int(bar * SR)
        amp = 0.09 if args.mood == "dark" else 0.11
        for k, note in enumerate(chord):
            f = hz(note, octv + (2 if args.mood == "bright" else 0))
            voice = (saw(f, n) * 0.35 + sine(f, n) * 0.65) * env(n, 0.35, 0.2, 0.6, 0.45)
            pad += 0  # 佔位，實際疊在下面（保持 place 統一寫法）
            place(pad, voice * amp * (1.0 - 0.15 * k), t0)

        # ── bright 專屬：高八度 bell arp 走和弦音，整首的「閃亮感」主要來自這層。
        # 音色不能用純 sine：沒有諧波就撐不起 2-8kHz，量出來只有 +0.5dB。
        # 疊 2 倍與 3.5 倍（非整數倍＝金屬鐘聲感）才聽得出亮。
        if args.mood == "bright" and sec not in ("intro", "outro"):
            for k, step in enumerate((0, 2, 4, 6, 8, 10, 12, 14)):
                nn = int(beat * 0.4 * SR)
                f = hz(chord[k % 3], 5)
                bell = sine(f, nn) + 0.5 * sine(2 * f, nn) + 0.3 * sine(3.5 * f, nn)
                place(lead, bell * env(nn, 0.004, 0.16) * 0.07, t0 + step * beat / 4)

        # ── Lead：只有 hook 段進，旋律跟著和弦根音移調
        if sec == "hook":
            shift = NOTE[root] - NOTE["A"]
            for note, oc, at in hook_notes:
                f = hz(note, oc + (1 if args.mood == "bright" else 0)) * 2 ** (shift / 12)
                nn = int(beat * 0.9 * SR)
                tone = (sine(f, nn) * 0.6 + saw(f, nn) * 0.4) * env(nn, 0.01, 0.25, 0.35, 0.3)
                place(lead, tone * 0.13, t0 + at * beat)

    # 削掉鋸齒的刺耳高頻；bright 要真的聽起來亮，光把 pad 升八度不夠，得把這道牆也放寬
    pad = lowpass(pad, 2600 if args.mood == "dark" else 4200)
    bass = lowpass(bass, 320)
    lead = lowpass(lead, 5200)
    mix = (drums * 0.9 + bass * 1.0 + pad * 1.0 + lead * 0.85) * 0.8

    # bright 最後補一道 high-shelf。光靠編曲（升八度、加 bell arp）在 2-8kHz 只推得動
    # 0.5dB，因為那些音符佔空比低、會被頻段平均稀釋；直接對 3k 以上加成才是可靠手段。
    if args.mood == "bright":
        mix = mix + 0.8 * (mix - lowpass(mix, 3000))

    # 開場 0.4 秒淡入、結尾 1.5 秒淡出，避免爆音
    fi, fo = int(0.4 * SR), int(1.5 * SR)
    mix[:fi] *= np.linspace(0, 1, fi)
    mix[-fo:] *= np.linspace(1, 0, fo)

    mix = np.tanh(mix)                            # 軟限幅（驅動別開太大，會擠掉動態）
    mix *= 0.89 / max(1e-9, np.max(np.abs(mix)))  # 正規化到 -1dB

    pcm = (mix * 32767).astype(np.int16)
    stereo = np.repeat(pcm[:, None], 2, axis=1).ravel()
    with wave.open(str(args.out), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(stereo.tobytes())

    print(f"完成：{args.out}")
    print(f"   {args.bpm:.0f} BPM / {len(pcm)/SR:.1f}s / {nbars} 小節 / mood={args.mood}")


if __name__ == "__main__":
    main()
