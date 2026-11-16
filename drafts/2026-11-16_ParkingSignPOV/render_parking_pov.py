"""Eazy88 POV clip — "You found parking in Australia. Now read the sign."

Format: POV humour, no voiceover. Everything is original: illustrated scene drawn in code
(no real footage, nothing taken from another creator), brand fonts and colour tokens,
procedural music (no samples).

Usage (from the repository root):
  python3 -I drafts/2026-11-16_ParkingSignPOV/render_parking_pov.py <out_dir>
Outputs: <BASE>_A.mp4, <BASE>_Cover.png, contact_sheet.png, qc.json
"""
import json, math, os, subprocess, sys

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "templates", "tools"))
from render_reel import (C, FPS, H, SR, W, BlendDraw, anton, brand_icon, draw_rich, fit_font, icon_share,  # noqa: E402
                         jakarta, loudnorm, make_background, write_wav)

BASE = "Eazy88_TikTok_ParkingSignPOV"
OUT = sys.argv[1]

# ---- brand tokens (eazy88.com CSS variables) used for the illustration
CREAM = C["cream"]
GREEN = (0x14, 0x78, 0x39)    # --secondary-dark
RED = (0xA0, 0x43, 0x1C)      # --primary-dark
POLE = (0x6B, 0x61, 0x55)     # --neutral-600
POLE_HI = C["muted"]          # --muted-warm
POLE_SH = (0x33, 0x2D, 0x26)  # --neutral-800

# ---- public text (English)
HEADER = "EAZY88 · BACKPACKER LIFE"
LABEL = "Illustration · not a real sign"
TITLE = ["POV: YOU FOUND PARKING", "IN AUSTRALIA.", "*NOW READ THE SIGN.*"]
PUNCH = ["BY THE TIME", "YOU'VE READ IT,", "*YOUR 2 HOURS*", "*ARE UP.*"]
CTA = ["SEND THIS TO THE", "MATE WHO *ALWAYS*", "*GETS THE FINE*"]

# ---- sign panels, bottom to top. The first seven look like real signs, the last three are the joke.
PANELS = [
    dict(c="g", h=176, kind="limit", big="2P", tag=None, lines=["8AM – 6PM", "MON – FRI"], arrows="both"),
    dict(c="g", h=176, kind="limit", big="P10", tag="MINUTE", lines=["7:30 – 9AM", "2:30 – 4PM", "SCHOOL DAYS"], arrows=None),
    dict(c="r", h=150, kind="words", rows=[("NO STOPPING", "A", 76), ("3PM – 7PM · MON – FRI", "J", 28)], arrows=None),
    dict(c="g", h=176, kind="limit", big="4P", tag="TICKET", lines=["6PM – 10PM", "MON – SAT"], arrows="right"),
    dict(c="r", h=150, kind="words", rows=[("LOADING ZONE", "A", 72), ("6AM – 10AM · 30 MIN LIMIT", "J", 27)], arrows=None),
    dict(c="g", h=150, kind="words", rows=[("PERMIT HOLDERS", "A", 60), ("EXCEPTED · AREA 7", "J", 30)], arrows=None),
    dict(c="g", h=176, kind="limit", big="1/2P", tag=None, lines=["SATURDAY", "8AM – NOON"], arrows="left"),
    dict(c="r", h=176, kind="words", rows=[("EXCEPT WHEN", "A", 66), ("IT RAINS", "A", 66)], arrows=None),
    dict(c="g", h=150, kind="words", rows=[("SEE OTHER SIDE", "A", 70)], arrows="right"),
    dict(c="r", h=150, kind="words", rows=[("GOOD LUCK", "A", 88)], arrows=None),
]

# ---- timeline (seconds)
IMP = [0.0, 1.10, 1.80, 2.40, 2.90, 3.33, 3.69, 4.50, 5.40, 6.30]   # moment each panel lands
DROP_D = 0.18
START = [-1.0] + [t - DROP_D for t in IMP[1:]]
T_REV, REV_D = 7.25, 0.75      # zoom-out reveal
T_CTA = 9.25
DUR = 11.5
OMEGA = 13.0                   # camera spring (critically damped): smooth start and stop

# ---- world geometry (px at scale 1; ground at y = 0, up is negative)
SS = 2
PW, GAP = 460, 14
tops, y_ = [], -270
for p_ in PANELS:
    tops.append(y_ - p_["h"])
    y_ = y_ - p_["h"] - GAP
TOWER_TOP = tops[-1] - 34

# ---- camera
SA = 1.15                       # scale while the signs stack up
G0 = 1330                       # ground line on screen at the start
GB, CX_B = 1330, 760            # ground line / tower centre after the reveal
SB = (GB - 300) / (-TOWER_TOP)  # whole tower fits between y=300 and the ground
R_TOP_A, R_TOP_B, R_BOT = 650, 255, 1380


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


# ---------------------------------------------------------------- artwork
def ink(font, s):
    l, t, r, b = font.getbbox(s)
    return l, t, r - l, b - t


def draw_ink(d, x, y, s, font, col):
    """Draw text so that the top-left of its ink box sits at (x, y)."""
    l, t, _, _ = ink(font, s)
    d.text((x - l, y - t), s, font=font, fill=col + (255,))


def arrow(d, x0, x1, y, col, th):
    sg = 1 if x1 > x0 else -1
    d.line([(x0, y), (x1 - sg * th * 1.5, y)], fill=col + (255,), width=int(th))
    d.polygon([(x1, y), (x1 - sg * th * 2.3, y - th * 1.6), (x1 - sg * th * 2.3, y + th * 1.6)], fill=col + (255,))


def arrows_row(d, cx, cy, kind, col):
    th, L = 6 * SS, 62 * SS
    if kind == "both":
        arrow(d, cx - 8 * SS, cx - 8 * SS - L, cy, col, th)
        arrow(d, cx + 8 * SS, cx + 8 * SS + L, cy, col, th)
    elif kind == "left":
        arrow(d, cx + L / 2, cx - L / 2, cy, col, th)
    else:
        arrow(d, cx - L / 2, cx + L / 2, cy, col, th)


def mk(kind, size):
    return anton(size * SS) if kind == "A" else jakarta(size * SS, "ExtraBold")


def panel_art(p):
    w, h = PW * SS, p["h"] * SS
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = BlendDraw(im, "RGBA")
    col = GREEN if p["c"] == "g" else RED
    d.rounded_rectangle((0, 0, w - 1, h - 1), 18 * SS, fill=CREAM + (255,))
    m = 8 * SS
    d.rounded_rectangle((m, m, w - 1 - m, h - 1 - m), 11 * SS, outline=col + (255,), width=5 * SS)
    pad = 30 * SS
    arow = 34 * SS  # height reserved for an arrow row (gap + arrow)
    if p["kind"] == "limit":
        fb = anton(104 * SS)
        _, _, bw, bh = ink(fb, p["big"])
        ft = jakarta(22 * SS, "ExtraBold")
        tag_h = ink(ft, p["tag"])[3] if p["tag"] else 0
        total = bh + (10 * SS + tag_h if p["tag"] else 0)
        y0 = (h - total) / 2
        draw_ink(d, pad, y0, p["big"], fb, col)
        if p["tag"]:
            tw = ink(ft, p["tag"])[2]
            draw_ink(d, pad + (bw - tw) / 2, y0 + bh + 10 * SS, p["tag"], ft, col)
        x0 = pad + bw + 26 * SS
        avail = w - pad - x0
        size = 36
        fl = jakarta(size * SS, "ExtraBold")
        while size > 18 and max(ink(fl, ln)[2] for ln in p["lines"]) > avail:
            size -= 1
            fl = jakarta(size * SS, "ExtraBold")
        lh = int(size * SS * 1.3)
        cap = ink(fl, "8")[3]
        block = (len(p["lines"]) - 1) * lh + cap + (arow if p["arrows"] else 0)
        yy = (h - block) / 2
        for ln in p["lines"]:
            draw_ink(d, x0 + (avail - ink(fl, ln)[2]) / 2, yy, ln, fl, col)
            yy += lh
        if p["arrows"]:
            arrows_row(d, x0 + avail / 2, yy - lh + cap + arow - 10 * SS, p["arrows"], col)
    else:
        rows = []
        for txt, kind, size in p["rows"]:
            f = mk(kind, size)
            while size > 14 and ink(f, txt)[2] > w - 2 * pad:
                size -= 1
                f = mk(kind, size)
            rows.append((txt, f, ink(f, txt)[3]))
        gap = 14 * SS
        total = sum(r[2] for r in rows) + gap * (len(rows) - 1) + (arow if p["arrows"] else 0)
        yy = (h - total) / 2
        for txt, f, th in rows:
            draw_ink(d, (w - ink(f, txt)[2]) / 2, yy, txt, f, col)
            yy += th + gap
        if p["arrows"]:
            arrows_row(d, w / 2, yy - gap + arow - 10 * SS, p["arrows"], col)
    return im


def shadow_for(w, h):
    im = Image.new("RGBA", (w + 80, h + 80), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((40, 50, 40 + w, 50 + h), 18, fill=(0, 0, 0, 130))
    return im.filter(ImageFilter.GaussianBlur(14))


def van_art(ss=3):
    """Small campervan with a surfboard, 340 x 170 world px, facing left."""
    im = Image.new("RGBA", (340 * ss, 170 * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(im, "RGBA")
    S = lambda *v: tuple(int(round(x * ss)) for x in v)  # noqa: E731
    d.rounded_rectangle(S(44, 10, 308, 28), 9 * ss, fill=CREAM + (255,))            # surfboard
    d.rectangle(S(92, 17, 260, 21), fill=C["green"] + (255,))
    for x in (96, 244):                                                             # roof rack
        d.rectangle(S(x, 28, x + 8, 40), fill=POLE_SH + (255,))
    d.rounded_rectangle(S(0, 38, 340, 146), 30 * ss, fill=C["orange"] + (255,))      # body
    d.rectangle(S(0, 104, 340, 112), fill=CREAM + (255,))                           # stripe
    d.rounded_rectangle(S(20, 54, 96, 98), 12 * ss, fill=C["bg"] + (255,))           # windscreen
    d.rounded_rectangle(S(108, 54, 186, 98), 10 * ss, fill=C["bg"] + (255,))
    d.rounded_rectangle(S(198, 54, 276, 98), 10 * ss, fill=C["bg"] + (255,))
    d.line([S(192, 114), S(192, 140)], fill=C["primary"] + (255,), width=2 * ss)     # door line
    d.ellipse(S(6, 116, 22, 132), fill=C["sun"] + (255,))                           # headlight
    for cx in (78, 262):                                                            # wheels
        d.ellipse(S(cx - 30, 110, cx + 30, 170), fill=C["ink_deep"] + (255,))
        d.ellipse(S(cx - 11, 129, cx + 11, 151), fill=CREAM + (255,))
    return im


# ---------------------------------------------------------------- text layers
def make_static():
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = BlendDraw(im, "RGBA")
    im.alpha_composite(brand_icon(60), (80, 200))
    d.text((158, 214), HEADER, font=jakarta(28, "Bold"), fill=C["muted"] + (255,))
    d.text((80, 272), LABEL, font=jakarta(24, "Medium"), fill=C["muted"] + (255,))
    return im


def text_block(lines, size, max_w, x, y):
    f = fit_font(lines, size, max_w)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = BlendDraw(im, "RGBA")
    for ln in lines:
        draw_rich(d, (x, y), ln, f, C["cream"], C["orange"], tracking=1)
        y += int(f.size * 1.1)
    return im, y, f.size


def make_cta():
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = BlendDraw(im, "RGBA")
    icon_share(d, 116, 892, 36, C["orange"], 255)
    f, y = anton(52), 948
    for ln in CTA:
        draw_rich(d, (80, y), ln, f, C["cream"], C["orange"], tracking=1)
        y += 58
    return im, y


# ---------------------------------------------------------------- compositing helpers
def faded(im, a):
    if a >= 0.999:
        return im
    out = im.copy()
    out.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
    return out


def comp(dst, src, x, y):
    """alpha_composite that accepts positions partly outside the canvas."""
    x, y = int(round(x)), int(round(y))
    sx0, sy0 = max(0, -x), max(0, -y)
    sx1, sy1 = min(src.width, dst.width - x), min(src.height, dst.height - y)
    if sx1 <= sx0 or sy1 <= sy0:
        return
    if (sx0, sy0, sx1, sy1) != (0, 0, src.width, src.height):
        src = src.crop((sx0, sy0, sx1, sy1))
    dst.alpha_composite(src, (x + sx0, y + sy0))


_scaled = {}


def scaled(key, im, w, h):
    w, h = max(1, int(round(w))), max(1, int(round(h)))
    k = (key, w, h)
    if k not in _scaled:
        if len(_scaled) > 600:
            _scaled.clear()
        _scaled[k] = im.resize((w, h), Image.LANCZOS)
    return _scaled[k]


_masks = {}


def mask_for(rt):
    rt = int(round(rt))
    if rt not in _masks:
        m = Image.new("L", (W, H), 0)
        d = ImageDraw.Draw(m)
        F = 36
        d.rectangle((0, rt + F, W, R_BOT - F), fill=255)
        for i in range(F):
            v = int(255 * (i + 1) / (F + 1))
            d.line([(0, rt + i), (W, rt + i)], fill=v)
            d.line([(0, R_BOT - 1 - i), (W, R_BOT - 1 - i)], fill=v)
        _masks[rt] = m
    return _masks[rt]


# ---------------------------------------------------------------- music (procedural, no samples)
rng = np.random.default_rng(88)


def note(f, dur, amp, a=0.01, r=0.2, nh=14, tilt=1.2, detune=(-6, 0, 6), bright=None):
    """Band-limited additive tone: detuned stack for strings, brighter attack for brass."""
    n = int((dur + r) * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for c in detune:
        ff = f * 2 ** (c / 1200)
        ph = 2 * np.pi * ff * t + rng.uniform(0, 6.28)
        for k in range(1, nh + 1):
            if ff * k > 7000:
                break
            g = 1 / k ** tilt
            if bright:
                g = g * (1 + (k - 1) * 0.12 * np.exp(-t * bright))
            out += g * np.sin(k * ph)
    env = np.minimum(1, t / a) * np.where(t < dur, 1.0, np.exp(-(t - dur) / (r / 3.5)))
    return amp * out / len(detune) * env


def timp(f, amp, dur=1.0, decay=4.5):
    n = int(dur * SR)
    t = np.arange(n) / SR
    ph = 2 * np.pi * np.cumsum(f * (1 + 0.45 * np.exp(-t * 38))) / SR
    body = (np.sin(ph) * np.exp(-t * decay) + 0.3 * np.sin(1.5 * ph) * np.exp(-t * decay * 1.6)
            + 0.18 * np.sin(2 * ph) * np.exp(-t * decay * 2))
    thud = np.convolve(rng.standard_normal(n), np.ones(32) / 32, "same") * np.exp(-t * 42) * 2.2
    return amp * (body + thud)


def cymbal(amp, dur=2.6, swell=0.0, decay=1.9):
    n = int((dur + swell) * SR)
    t = np.arange(n) / SR
    x = np.diff(np.diff(rng.standard_normal(n), prepend=0.0), prepend=0.0)
    x /= np.abs(x).max()
    env = np.where(t < swell, 0.55 * (t / max(swell, 1e-6)) ** 2.5, np.exp(-(t - swell) * decay))
    return amp * x * env


def put(buf, sig, t0):
    i = int(round(t0 * SR))
    j = min(len(buf), i + len(sig))
    if j > i >= 0:
        buf[i:j] += sig[: j - i]


def tick(amp, f=1250.0):
    """Short woodblock-like click, so each landing is audible on a phone speaker."""
    n = int(0.12 * SR)
    t = np.arange(n) / SR
    return amp * (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2.76 * t)) * np.exp(-t * 55)


def snare(amp):
    n = int(0.14 * SR)
    t = np.arange(n) / SR
    x = np.diff(rng.standard_normal(n), prepend=0.0)
    return amp * x / np.abs(x).max() * np.exp(-t * 38)


def make_music():
    """Mock-epic score in D minor, voiced in the mid range (phone speakers barely play below 200 Hz)."""
    n = int(DUR * SR)
    m = np.zeros(n)
    D2, A2 = 73.42, 110.0
    # opening hit on the very first frame, then a drone that swells until the reveal
    put(m, timp(D2, 0.5, 1.2), 0.02)
    put(m, tick(0.16, 880.0), 0.02)
    for f in (146.83, 220.0, 293.66):
        put(m, note(f, 0.5, 0.15, a=0.03, r=0.7, nh=18, tilt=1.0, detune=(-4, 4), bright=5), 0.02)
    drone = note(146.83, T_REV, 1.0, a=0.3, r=0.6, nh=12, tilt=1.25)
    drone += 0.7 * note(220.0, T_REV, 1.0, a=0.5, r=0.6, nh=10, tilt=1.3)
    drone += 0.5 * note(D2, T_REV, 1.0, a=0.6, r=0.6, nh=8, tilt=1.5)
    put(m, drone * np.linspace(0.14, 0.24, len(drone)), 0.0)
    # each ordinary sign: a thud, a click and one step up the D minor scale
    for i, f in zip(range(1, 7), [293.66, 329.63, 349.23, 392.00, 440.00, 466.16]):
        put(m, timp(98.0, 0.30, 0.4, decay=11), IMP[i])
        put(m, tick(0.22), IMP[i])
        put(m, note(f, 0.10, 0.34, a=0.006, r=0.3, nh=12, tilt=1.0), IMP[i])
        put(m, note(f / 2, 0.10, 0.20, a=0.006, r=0.3, nh=12, tilt=1.15), IMP[i])
    # the three joke signs: brass chords Gm - A7 - A7, louder each time
    chords = [(98.0, [196.0, 233.08, 293.66, 392.0]), (110.0, [220.0, 277.18, 329.63, 392.0]),
              (110.0, [220.0, 329.63, 392.0, 440.0, 554.37])]
    for (root, ch), i, g in zip(chords, (7, 8, 9), (0.8, 0.95, 1.15)):
        put(m, timp(root, 0.6 * g, 1.1), IMP[i])
        put(m, tick(0.2 * g, 990.0), IMP[i])
        put(m, note(root, 0.55, 0.14 * g, a=0.025, r=0.55, nh=14, tilt=1.2), IMP[i])
        for f in ch:
            put(m, note(f, 0.55, 0.19 * g, a=0.025, r=0.55, nh=18, tilt=0.9, detune=(-4, 4), bright=7), IMP[i])
    # drum roll and cymbal swell into the reveal
    t = T_REV - 0.72
    while t < T_REV - 0.02:
        g = 0.12 + 0.5 * ((t - (T_REV - 0.72)) / 0.72) ** 1.5
        put(m, timp(D2, 0.6 * g, 0.5, decay=9), t)
        put(m, snare(0.55 * g), t)
        t += 0.062
    put(m, cymbal(0.45, dur=2.8, swell=0.72), T_REV - 0.72)
    # reveal: full D minor chord
    put(m, timp(D2, 1.0, 1.6, decay=3.2), T_REV)
    for f, g in [(73.42, 0.6), (110.0, 0.6), (146.83, 1), (220.0, 1), (293.66, 1), (349.23, 1), (440.0, 1), (587.33, 0.9), (698.46, 0.7)]:
        put(m, note(f, 1.5, 0.16 * g, a=0.02, r=1.5, nh=14, tilt=1.1), T_REV)
    for f in [293.66, 440.0, 587.33]:
        put(m, note(f, 1.3, 0.19, a=0.03, r=1.2, nh=20, tilt=0.9, detune=(-4, 4), bright=5), T_REV)
    # under the call to action: soft open fifths to the end, and three plucked notes
    for f in [146.83, 220.0, 293.66, 440.0]:
        put(m, note(f, DUR - T_CTA + 0.2, 0.10, a=0.6, r=0.9, nh=10, tilt=1.3), T_CTA - 0.2)
    for f, t0 in ((587.33, T_CTA), (880.0, T_CTA + 0.16), (1174.66, T_CTA + 0.32)):
        put(m, note(f, 0.04, 0.30, a=0.004, r=0.5, nh=5, tilt=1.7, detune=(0,)), t0)
    # hall reverb: FFT convolution with decaying noise
    ir_n = int(1.7 * SR)
    ti = np.arange(ir_n) / SR
    ir = np.convolve(rng.standard_normal(ir_n) * np.exp(-ti * 3.4), np.ones(10) / 10, "same")
    ir[: int(0.012 * SR)] = 0
    N = 1 << int(np.ceil(np.log2(n + ir_n)))
    wet = np.fft.irfft(np.fft.rfft(m, N) * np.fft.rfft(ir, N), N)[:n]
    wet *= 0.9 * np.abs(m).max() / (np.abs(wet).max() + 1e-9)
    mix = m + 0.33 * wet
    # tone shaping: no rumble, less sub-bass, gentle low-pass; then soft limiter and fade-out
    F = np.fft.rfft(mix)
    fr = np.fft.rfftfreq(n, 1 / SR)
    F *= 1 / np.sqrt(1 + (fr / 9000) ** 6)
    F *= 0.55 + 0.45 / (1 + (120 / np.maximum(fr, 1e-3)) ** 4)
    F[fr < 45] = 0
    mix = np.fft.irfft(F, n)
    mix = np.tanh(1.5 * mix / np.abs(mix).max()) / np.tanh(1.5)
    fade = np.ones(n)
    fl = int(0.6 * SR)
    fade[-fl:] = np.linspace(1, 0, fl) ** 1.5
    return 0.9 * mix * fade


# ---------------------------------------------------------------- render
def main():
    os.makedirs(OUT, exist_ok=True)
    tmp = os.path.join(OUT, "_tmp")
    os.makedirs(tmp, exist_ok=True)

    bg = make_background().convert("RGBA")
    static = make_static()
    title_im, title_bottom, title_size = text_block(TITLE, 112, 860, 80, 318)
    punch_im, punch_bottom, punch_size = text_block(PUNCH, 96, 460, 80, 430)
    cta_im, cta_bottom = make_cta()
    assert title_bottom <= R_TOP_A, f"title ends at {title_bottom}, scene starts at {R_TOP_A}"
    assert punch_bottom <= 892 - 36 - 20, f"punchline ends at {punch_bottom}, too close to the CTA icon"
    assert cta_bottom <= 1380
    arts = [panel_art(p) for p in PANELS]
    shadows = [shadow_for(PW, p["h"]) for p in PANELS]
    van = van_art()

    silent = os.path.join(tmp, "video.mp4")
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                           "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.2", silent], stdin=subprocess.PIPE)
    gy, gv, pole_top, gy_rev0 = float(G0), 0.0, tops[0] - 34.0, None
    nframes = int(round(DUR * FPS))
    for fi in range(nframes):
        t = fi / FPS
        newest = max(i for i in range(len(PANELS)) if t >= START[i])
        if t < T_REV:   # camera follows the newest sign up the pole
            target = max(G0, 760 - tops[newest] * SA)
            for _ in range(4):
                gv += (OMEGA ** 2 * (target - gy) - 2 * OMEGA * gv) / (FPS * 4)
                gy += gv / (FPS * 4)
            s, cx, rt, gy_now = SA, 540.0, R_TOP_A, gy
        else:           # zoom out to the whole tower, then drift slightly
            if gy_rev0 is None:
                gy_rev0 = gy
            e = smooth((t - T_REV) / REV_D)
            s = SA * (SB / SA) ** e * (1 - 0.015 * smooth((t - T_REV - REV_D) / 3.5))
            gy_now = gy_rev0 + (GB - gy_rev0) * e
            cx = 540 + (CX_B - 540) * e
            rt = R_TOP_A + (R_TOP_B - R_TOP_A) * e
        pole_top += (tops[newest] - 34 - pole_top) * (1 - math.exp(-14.0 / FPS))
        shake = sum((9 if i >= 7 else 5) * math.exp(-(t - IMP[i]) * 15)
                    for i in range(1, len(PANELS)) if 0 <= t - IMP[i] < 0.4)
        gys = gy_now + shake

        scene = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(scene, "RGBA")
        if gys < R_BOT + 20:   # ground line and van
            d.line([(cx - 520 * s, gys), (cx + 700 * s, gys)], fill=C["muted"] + (120,), width=max(2, int(round(4 * s))))
            comp(scene, scaled("van", van, 340 * s, 170 * s), cx - 400 * s, gys - 170 * s)
        px0, px1, py0 = cx - 13 * s, cx + 13 * s, gys + pole_top * s
        d.rectangle((px0, py0, px1, gys), fill=POLE + (255,))
        d.rectangle((px0, py0, px0 + 8 * s, gys), fill=POLE_HI + (80,))
        d.rectangle((px1 - 8 * s, py0, px1, gys), fill=POLE_SH + (150,))
        d.rounded_rectangle((cx - 20 * s, py0 - 12 * s, cx + 20 * s, py0 + 4 * s), max(1, int(5 * s)), fill=POLE_HI + (255,))
        for i, p in enumerate(PANELS):
            if t < START[i]:
                continue
            q = (t - START[i]) / DROP_D
            if i == 0:
                off, a = 0.0, 1.0
            elif q < 1:        # falling
                off, a = -130 * (1 - q * q), clamp(q * 3)
            else:              # small bounce after landing
                dt = t - IMP[i]
                off, a = (-10 * abs(math.sin(dt * 22)) * math.exp(-dt * 9) if dt < 0.5 else 0.0), 1.0
            x, y = cx - PW / 2 * s, gys + (tops[i] + off) * s
            comp(scene, faded(scaled(("sh", i), shadows[i], (PW + 80) * s, (p["h"] + 80) * s), a), x - 40 * s, y - 40 * s)
            comp(scene, faded(scaled(("p", i), arts[i], PW * s, p["h"] * s), a), x, y)
        scene.putalpha(ImageChops.multiply(scene.getchannel("A"), mask_for(rt)))

        frame = bg.copy()
        frame.alpha_composite(scene)
        frame.alpha_composite(static)
        ta = 1 - clamp((t - T_REV) / 0.25)
        if ta > 0:
            frame.alpha_composite(faded(title_im, ta))
        pa = clamp((t - T_REV - 0.5) / 0.3)
        if pa > 0:
            comp(frame, faded(punch_im, pa), -24 * (1 - smooth(pa)), 0)
        ca = clamp((t - T_CTA) / 0.3)
        if ca > 0:
            comp(frame, faded(cta_im, ca), 0, 16 * (1 - smooth(ca)))
        ff.stdin.write(frame.convert("RGB").tobytes())
        if fi == 0:
            frame.convert("RGB").save(os.path.join(OUT, f"{BASE}_Cover.png"))
    ff.stdin.close()
    ff.wait()

    write_wav(os.path.join(tmp, "music_raw.wav"), make_music())
    loudnorm(os.path.join(tmp, "music_raw.wav"), os.path.join(tmp, "music.wav"))
    mp4 = os.path.join(OUT, f"{BASE}_A.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", os.path.join(tmp, "music.wav"), "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k", "-ar", str(SR), "-ac", "2", "-shortest", "-movflags", "+faststart", mp4],
                   check=True)

    # contact sheet from the final MP4
    times = [0.03, 0.9, 1.0, 1.35, 2.05, 2.65, 3.15, 3.55, 4.0, 4.9, 5.8, 6.8, 7.5, 7.8, 8.3, 9.0, 9.8, 11.2]
    ims = []
    for tt in times:
        fp = os.path.join(tmp, f"f_{tt:.2f}.png")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{tt:.2f}", "-i", mp4, "-frames:v", "1", fp], check=True)
        im = Image.open(fp).resize((270, 480))
        ImageDraw.Draw(im).text((6, 6), f"{tt:.2f}s", fill=(255, 0, 255))
        ims.append(im)
    cols = 6
    sheet = Image.new("RGB", (cols * 274, ((len(ims) + cols - 1) // cols) * 484), "white")
    for i, im in enumerate(ims):
        sheet.paste(im, ((i % cols) * 274, (i // cols) * 484))
    sheet.save(os.path.join(OUT, "contact_sheet.png"))
    qc = {"duration": DUR, "frames": nframes, "title_px": title_size, "punch_px": punch_size, "scale_reveal": round(SB, 3),
          "tower_top_world": TOWER_TOP, "impacts": IMP, "reveal": T_REV, "cta": T_CTA}
    json.dump(qc, open(os.path.join(OUT, "qc.json"), "w"), indent=1)
    print(json.dumps(qc))


if __name__ == "__main__":
    main()
