"""Eazy88 POV clip — "You just finished day 1 of your 88 days." -> "Only 87 to go."

Format: POV humour, no voiceover, about 10 s. Everything is original: a paper wall chart drawn in code
(not an app screen), brand fonts and colour tokens, procedural music (no samples).

Usage (from the repository root):
  python3 -I drafts/2026-11-19_Day1POV/render_day1_pov.py <out_dir>
Outputs: <BASE>_A.mp4, <BASE>_Cover.png, contact_sheet.png, qc.json
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "templates", "tools"))
from pov_kit import (C, FPS, H, SR, TOK, W, BlendDraw, Encoder, Synth, aa_layer, anton, audio_report,  # noqa: E402
                     band_mask, clamp, comp, contact_sheet, ease_out_back, ease_out_cubic, faded, finish, jakarta,
                     lerp, make_background, make_cta, make_signature, make_static, place_art, probe, smooth,
                     text_block)

BASE = "Eazy88_TikTok_Day1POV"
OUT = sys.argv[1]

# ---- public text (English)
HEADER = "EAZY88 · BACKPACKER LIFE"
LABEL = "Illustration"
TITLE = ["POV: YOU JUST FINISHED", "DAY 1 OF YOUR", "*88 DAYS.*"]
PUNCH = ["ONLY *87 TO GO.*"]
HERE = ["YOU ARE", "HERE"]
CTA = ["SEND THIS TO THE MATE", "*DOING THEIR 88 DAYS*"]

# ---- timeline (seconds). v2 (19 Nov, after the TikTok retention data): the tick is drawn from 0.35 s,
# zoom-out at 2.1 s instead of 3.05 s, punchline at 3.4 s instead of 4.55 s, 8.2 s instead of 9.8 s, end card.
T_TICK0, T_TICK1 = 0.35, 0.70   # the marker draws the tick in box 1
T_POP = 0.70                    # confetti + fanfare
T_SCRATCH = 2.0                 # record scratch: the party stops
T_REV, REV_D = 2.1, 1.2         # zoom out to the whole chart
T_PUNCH = 3.4
T_HERE = 3.95
T_CTA = 5.0
T_SIG = 5.6
DUR = 8.2

# ---- chart geometry (world units = px at scale 1)
M, HH, B, G = 18, 86, 46, 6
P = B + G
COLS, ROWS = 8, 11
CW = 2 * M + COLS * P - G        # 446
CH = HH + ROWS * P - G + M       # 670
PAD = 24                         # room around the paper for tape and shadow
RS = 4                           # artwork resolution (px per world unit)

# ---- camera: screen = origin + world * scale
SA, OA = 3.3, (40.0, 700.0)      # close-up on the first boxes
SB, OB = 0.82, (357.0, 300.0)    # whole chart, centred
R_TOP_A, R_TOP_B, R_BOT = 660, 250, 1380
ANCHOR = (M + B / 2, HH + B / 2)  # centre of box 1
TICK = [(0.2, 0.55), (0.42, 0.78), (0.84, 0.22)]

CONFETTI_COLS = [C["orange"], C["green"], C["green_l"], C["sun"], C["cream"], C["primary"], C["sunset"]]


# ---------------------------------------------------------------- artwork
def chart_art():
    w, h = int((CW + 2 * PAD) * RS), int((CH + 2 * PAD) * RS)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    o = PAD * RS
    sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((o, o + 8 * RS, o + CW * RS, o + (CH + 8) * RS), 6 * RS, fill=(0, 0, 0, 120))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(9 * RS)))
    d = BlendDraw(im, "RGBA")
    d.rounded_rectangle((o, o, o + CW * RS, o + CH * RS), 5 * RS, fill=C["cream"] + (255,))
    # header "MY 88 DAYS" (88 in brand orange)
    f = anton(44 * RS)
    _, t, _, b = f.getbbox("MY 88 DAYS")   # BlendDraw.text has no anchor: position = top-left of the layout box
    y = o + HH * RS / 2 - (t + b) / 2
    x = o + M * RS
    for s, col in (("MY ", TOK["n800"]), ("88", C["primary"]), (" DAYS", TOK["n800"])):
        d.text((x, y), s, font=f, fill=col + (255,))
        x += f.getlength(s)
    # small sun doodle, top right
    cx, cy, r = o + (CW - M - 22) * RS, o + HH * RS / 2, 11 * RS
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=C["sunset"] + (255,), width=3 * RS)
    for k in range(8):
        a = k * math.pi / 4
        d.line([(cx + math.cos(a) * r * 1.45, cy + math.sin(a) * r * 1.45),
                (cx + math.cos(a) * r * 1.95, cy + math.sin(a) * r * 1.95)], fill=C["sunset"] + (255,), width=3 * RS)
    # 88 boxes with small numbers
    fn = jakarta(11 * RS, "Bold")
    for i in range(COLS * ROWS):
        r_, c_ = divmod(i, COLS)
        x0, y0 = o + (M + c_ * P) * RS, o + (HH + r_ * P) * RS
        d.rounded_rectangle((x0, y0, x0 + B * RS, y0 + B * RS), 5 * RS, outline=TOK["n600"] + (255,), width=2 * RS)
        d.text((x0 + 5 * RS, y0 + 4 * RS), str(i + 1), font=fn, fill=TOK["n600"] + (210,))
    # two strips of tape
    for (tx, ty, ang) in ((o + 6 * RS, o + 2 * RS, 28), (o + (CW - 6) * RS, o + 2 * RS, -28)):
        tape = Image.new("RGBA", (84 * RS, 24 * RS), C["sun"] + (165,))
        ImageDraw.Draw(tape).rectangle((0, 0, 84 * RS - 1, 3 * RS), fill=C["cream"] + (90,))
        tape = tape.rotate(ang, expand=True, resample=Image.BICUBIC)
        im.alpha_composite(tape, (int(tx - tape.width / 2), int(ty - tape.height / 2)))
    return im


def box1_screen(ox, oy, s):
    return ox + M * s, oy + HH * s, B * s


def draw_tick(dst, ox, oy, s, p):
    bx, by, bs = box1_screen(ox, oy, s)
    pts = [(bx + u * bs, by + v * bs) for u, v in TICK]
    seg = [math.dist(pts[0], pts[1]), math.dist(pts[1], pts[2])]
    L = p * sum(seg)
    path = [pts[0]]
    if L <= seg[0]:
        e = L / seg[0]
        path.append((lerp(pts[0][0], pts[1][0], e), lerp(pts[0][1], pts[1][1], e)))
    else:
        e = (L - seg[0]) / seg[1]
        path += [pts[1], (lerp(pts[1][0], pts[2][0], e), lerp(pts[1][1], pts[2][1], e))]
    wid = 0.15 * bs

    def fn(d, x0, y0, ss):
        q = [((x - x0) * ss, (y - y0) * ss) for x, y in path]
        col = C["green"] + (255,)
        d.line(q, fill=col, width=max(1, int(wid * ss)), joint="curve")
        for x, y in (q[0], q[-1]):
            rr = wid * ss / 2
            d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=col)

    lay, x, y = aa_layer(fn, (bx - 0.2 * bs, by - 0.2 * bs, bx + 1.2 * bs, by + 1.2 * bs))
    comp(dst, lay, x, y)
    return path[-1], bs


def draw_pen(dst, tip, bs, alpha):
    """Green marker pen; its tip sits at `tip`, the body goes down and to the right (away from the header)."""
    if alpha <= 0:
        return
    ux, uy = math.cos(math.radians(38)), math.sin(math.radians(38))
    nx, ny = -uy, ux
    wid = 0.26 * bs

    def quad(a, b, w):
        return [(tip[0] + ux * a + nx * w / 2, tip[1] + uy * a + ny * w / 2),
                (tip[0] + ux * b + nx * w / 2, tip[1] + uy * b + ny * w / 2),
                (tip[0] + ux * b - nx * w / 2, tip[1] + uy * b - ny * w / 2),
                (tip[0] + ux * a - nx * w / 2, tip[1] + uy * a - ny * w / 2)]

    parts = [(quad(0.0, 0.16 * bs, 0.09 * bs), TOK["n800"]), (quad(0.12 * bs, 0.32 * bs, 0.2 * bs), TOK["n800"]),
             (quad(0.3 * bs, 1.5 * bs, wid), C["green"]), (quad(0.74 * bs, 0.86 * bs, wid), TOK["secondary_dark"]),
             (quad(1.45 * bs, 1.95 * bs, wid * 1.08), TOK["secondary_dark"])]
    xs = [p[0] for q, _ in parts for p in q]
    ys = [p[1] for q, _ in parts for p in q]

    def fn(d, x0, y0, ss):
        for q, col in parts:
            d.polygon([((x - x0) * ss, (y - y0) * ss) for x, y in q], fill=col + (int(255 * alpha),))

    lay, x, y = aa_layer(fn, (min(xs) - 4, min(ys) - 4, max(xs) + 4, max(ys) + 4))
    comp(dst, lay, x, y)


class Confetti:
    def __init__(self, n, x0, y0, t0, rng):
        self.t0, self.x0, self.y0 = t0, x0, y0
        ang = rng.uniform(-math.pi * 0.93, -math.pi * 0.07, n)
        spd = rng.uniform(650, 1900, n)
        self.vx, self.vy = np.cos(ang) * spd, np.sin(ang) * spd
        self.w, self.h = rng.uniform(18, 32, n), rng.uniform(10, 16, n)
        self.r0, self.rv = rng.uniform(0, 6.28, n), rng.uniform(-9, 9, n)
        self.flip, self.sway, self.swf = rng.uniform(4, 11, n), rng.uniform(8, 30, n), rng.uniform(3, 7, n)
        self.col = [CONFETTI_COLS[i % len(CONFETTI_COLS)] for i in range(n)]

    def draw(self, dst, t, fade_by):
        tau = t - self.t0
        if tau < 0 or t > fade_by:
            return
        k, g = 3.2, 1500.0
        vt = g / k
        e = 1 - math.exp(-k * tau)
        x = self.x0 + self.vx * e / k + self.sway * np.sin(self.swf * tau)
        y = self.y0 + vt * tau + (self.vy - vt) * e / k
        a = (1 - smooth((tau - 1.3) / 0.5)) * (1 - smooth((t - (fade_by - 0.25)) / 0.25))
        if a <= 0:
            return
        d = ImageDraw.Draw(dst, "RGBA")
        for i in range(len(x)):
            r = self.r0[i] + self.rv[i] * tau
            hw, hh = self.w[i] / 2, self.h[i] / 2 * (0.15 + abs(math.cos(self.flip[i] * tau)))
            cr, sr = math.cos(r), math.sin(r)
            pts = [(x[i] + cr * px - sr * py, y[i] + sr * px + cr * py) for px, py in ((-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh))]
            d.polygon(pts, fill=self.col[i] + (int(255 * a),))


def make_here():
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = BlendDraw(im, "RGBA")
    f = jakarta(34, "ExtraBold")
    y = 362
    for ln in HERE:
        d.text((80, y), ln, font=f, fill=C["orange"] + (255,))
        y += 42
    return im, 80 + max(f.getlength(ln) for ln in HERE)


def draw_here_marks(dst, ox, oy, s, p, x_text_end):
    """Arrow from the label to box 1 and a hand-drawn ring around it, drawn progressively (p in 0..1)."""
    bx, by, bs = box1_screen(ox, oy, s)
    cx, cy = bx + bs / 2, by + bs / 2
    rad = 0.82 * bs
    pa = clamp(p / 0.45)
    pr = clamp((p - 0.35) / 0.65)
    xa0, xa1 = x_text_end + 14, cx - rad - 6

    def fn(d, x0, y0, ss):
        col = C["orange"] + (255,)
        wid = int(5 * ss)
        if pa > 0:
            xe = lerp(xa0, xa1, ease_out_cubic(pa))
            d.line([((xa0 - x0) * ss, (cy - y0) * ss), ((xe - x0) * ss, (cy - y0) * ss)], fill=col, width=wid)
            if pa >= 1:
                hx, hy = (xa1 - x0) * ss, (cy - y0) * ss
                d.polygon([(hx + 4 * ss, hy), (hx - 14 * ss, hy - 11 * ss), (hx - 14 * ss, hy + 11 * ss)], fill=col)
        if pr > 0:
            bb = [(cx - rad - x0) * ss, (cy - rad * 0.92 - y0) * ss, (cx + rad - x0) * ss, (cy + rad * 0.92 - y0) * ss]
            d.arc(bb, start=200, end=200 + 345 * ease_out_cubic(pr), fill=col, width=wid)

    lay, x, y = aa_layer(fn, (xa0 - 10, cy - rad - 14, cx + rad + 14, cy + rad + 14))
    comp(dst, lay, x, y)


# ---------------------------------------------------------------- music (procedural, no samples)
def make_music():
    sy = Synth(188)
    n = int(DUR * SR)
    party = np.zeros(n)
    put = sy.put
    # soft hopeful pad + a small chime on the very first frame
    for f in (261.63, 329.63, 392.0, 587.33):
        put(party, sy.tone(f, T_SCRATCH, 0.08, a=0.35, r=0.3, nh=8, tilt=1.4), 0.0)
    put(party, sy.bell(1046.5, 0.16), 0.02)
    put(party, sy.tick(0.12, 880.0), 0.02)
    # marker squeaks while the tick is drawn
    put(party, sy.squeak(0.15, 0.10, 1800, 2300), T_TICK0)
    put(party, sy.squeak(0.19, 0.12, 2000, 2800), T_TICK0 + 0.16)
    # snare roll building to the pop
    t = 0.05
    while t < T_POP - 0.03:
        put(party, sy.snare(0.5 * (0.08 + 0.4 * ((t - 0.05) / (T_POP - 0.05)) ** 2)), t)
        t += 0.055
    # "ta-DA!": pickup note, then a bright C major brass chord, timpani and cymbal
    put(party, sy.tone(392.0, 0.1, 0.16, a=0.01, r=0.08, nh=18, tilt=0.9, detune=(-4, 4), bright=6), T_POP - 0.16)
    for f in (261.63, 329.63, 392.0, 523.25, 659.25):
        put(party, sy.tone(f, 0.9, 0.19, a=0.02, r=0.6, nh=18, tilt=0.9, detune=(-4, 4), bright=6), T_POP)
    put(party, sy.timp(130.81, 0.6, 1.0), T_POP)
    put(party, sy.cymbal(0.38, 2.0, decay=2.2), T_POP)
    for k, f in enumerate((1046.5, 1318.5, 1568.0, 1760.0, 2093.0, 1568.0, 1318.5, 2093.0, 1760.0)):
        put(party, sy.bell(f, 0.06, 0.8), T_POP + 0.08 + k * 0.14)
    # bouncy oom-pah until the scratch
    for i, tb in enumerate(np.arange(T_POP + 0.25, T_SCRATCH - 0.05, 0.25)):
        if i % 2 == 0:
            put(party, sy.tone(130.81 if i % 4 == 0 else 98.0, 0.12, 0.24, a=0.005, r=0.12, nh=12, tilt=1.0, detune=(0,)), tb)
            put(party, sy.kick(0.14), tb)
        else:
            for f in (329.63, 392.0, 523.25):
                put(party, sy.tone(f, 0.08, 0.06, a=0.005, r=0.1, nh=14, tilt=0.9, detune=(-4, 4), bright=8), tb)
            put(party, sy.clap(0.18), tb)
    party = sy.master(party, reverb=0.3, fade=0)
    i0 = int(T_SCRATCH * SR)
    party[i0:] *= np.concatenate([np.linspace(1, 0, int(0.03 * SR)), np.zeros(n - i0 - int(0.03 * SR))])

    after = np.zeros(n)
    put(after, sy.scratch(0.4), T_SCRATCH)
    # sad trombone: three short "wah"s down by semitones, then a long one with vibrato
    t0 = T_REV + 0.07
    for i, f in enumerate((233.08, 220.0, 207.65)):
        put(after, sy.tone(f, 0.34, 0.24, a=0.03, r=0.12, nh=20, tilt=0.85, detune=(-3, 3), wah=(350, 1600)), t0 + i * 0.42)
    put(after, sy.tone(196.0, 1.25, 0.24, a=0.03, r=0.35, nh=20, tilt=0.85, detune=(-3, 3), wah=(350, 1300),
                       vib=0.025, vib_rate=6.0, vib_delay=0.2, glide=(185.0, 0.9)), t0 + 3 * 0.42)
    # resigned ukulele strum under the punchline and the call to action: Am F C G Am F
    chords = [(440.0, 261.63, 329.63, 440.0), (440.0, 261.63, 349.23, 440.0), (392.0, 261.63, 329.63, 523.25),
              (392.0, 293.66, 392.0, 493.88), (440.0, 261.63, 329.63, 440.0), (440.0, 261.63, 349.23, 440.0)]
    roots = (110.0, 87.31, 130.81, 98.0, 110.0, 87.31)
    for k, (ch, root) in enumerate(zip(chords, roots)):
        tc = T_PUNCH + 0.35 + k * 0.8
        g = 0.55 if tc < T_CTA else 0.8
        for j, f in enumerate(ch):
            put(after, sy.pluck(f, 0.9, 0.24 * g, decay=0.995), tc + j * 0.016)
            put(after, sy.pluck(f, 0.5, 0.12 * g, decay=0.993), tc + 0.4 + (3 - j) * 0.012)
        put(after, sy.tone(root * 2, 0.6, 0.1 * g, a=0.02, r=0.3, nh=10, tilt=1.2, detune=(0,)), tc)
    after = sy.master(after, reverb=0.25, fade=0.6)
    mix = party + 0.6 * after   # each part is mastered to full scale: the party stays the loudest moment
    return 0.9 * mix / np.abs(mix).max()


# ---------------------------------------------------------------- render
def camera(t):
    if t < T_REV:
        wob = 0.05 * math.exp(-(t - T_POP) * 5) * math.sin((t - T_POP) * 17) if t >= T_POP else 0.0
        push = -0.04 * (1 - smooth(t / T_POP))      # slow push-in from the very first frame
        s = SA * (1 + wob + push)
        ax, ay = OA[0] + ANCHOR[0] * SA, OA[1] + ANCHOR[1] * SA
        rt = R_TOP_A
    else:
        e = smooth((t - T_REV) / REV_D)
        s = SA * (SB / SA) ** e * (1 - 0.012 * smooth((t - T_REV - REV_D) / 4))
        ax = lerp(OA[0] + ANCHOR[0] * SA, OB[0] + ANCHOR[0] * SB, e)
        ay = lerp(OA[1] + ANCHOR[1] * SA, OB[1] + ANCHOR[1] * SB, e)
        rt = lerp(R_TOP_A, R_TOP_B, e)
    return ax - ANCHOR[0] * s, ay - ANCHOR[1] * s, s, rt


def main():
    os.makedirs(OUT, exist_ok=True)
    tmp = os.path.join(OUT, "_tmp")
    os.makedirs(tmp, exist_ok=True)

    bg = make_background().convert("RGBA")
    static = make_static(HEADER, LABEL)
    title_im, title_bottom, title_size = text_block(TITLE, 112, 860, 80, 318)
    punch_y, cta_y = 885, 1098
    punch_im, punch_bottom, punch_size = text_block(PUNCH, 140, 860, 80, punch_y)
    cta_im, cta_bottom = make_cta(CTA, cta_y)
    sig_im, sig_box = make_signature(1296)
    here_im, here_x_end = make_here()
    chart_bottom = OB[1] + CH * SB
    assert title_bottom <= R_TOP_A, f"title ends at {title_bottom}, scene starts at {R_TOP_A}"
    assert OB[0] + CW * SB <= 940 and chart_bottom <= punch_y - 20, "chart outside the safe area or on the punchline"
    assert punch_bottom <= cta_y - 40 and cta_bottom <= sig_box[1] - 8, (punch_bottom, cta_bottom)
    art = chart_art()
    rng = np.random.default_rng(7)
    ox0, oy0, s0, _ = camera(T_POP)
    bx, by, bs = box1_screen(ox0, oy0, SA)
    confetti = Confetti(150, bx + bs / 2, by + bs / 2, T_POP, rng)

    enc = Encoder(os.path.join(tmp, "video.mp4"))
    nframes = int(round(DUR * FPS))
    for fi in range(nframes):
        t = fi / FPS
        ox, oy, s, rt = camera(t)
        scene = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        place_art(scene, art, RS, ox - PAD * s, oy - PAD * s, s)
        p = smooth((t - T_TICK0) / (T_TICK1 - T_TICK0))
        bx, by, bs = box1_screen(ox, oy, s)
        tip = (bx + TICK[0][0] * bs, by + TICK[0][1] * bs)
        if p > 0:
            tip, _ = draw_tick(scene, ox, oy, s, p)
        if t < T_POP + 0.5:   # pen hovers, draws, then lifts away
            lift = ease_out_cubic((t - T_TICK1) / 0.45) if t > T_TICK1 else 0.0
            bob = 4 * math.sin(t * 7) if t < T_TICK0 else 0.0
            pt = (tip[0] + 300 * lift, tip[1] + 260 * lift + bob)
            draw_pen(scene, pt, bs, 1 - lift)
        scene.putalpha(Image.fromarray(np.minimum(np.asarray(scene.getchannel("A")),
                                                  np.asarray(band_mask(rt, R_BOT)))))
        frame = bg.copy()
        frame.alpha_composite(scene)
        frame.alpha_composite(static)
        ta = 1 - clamp((t - T_REV) / 0.25)
        if ta > 0:
            frame.alpha_composite(faded(title_im, ta))
        confetti.draw(frame, t, T_REV + 0.2)
        pa = clamp((t - T_PUNCH) / 0.3)
        if pa > 0:
            comp(frame, faded(punch_im, pa), -24 * (1 - smooth(pa)), 0)
        if t >= T_HERE:
            ha = clamp((t - T_HERE) / 0.25)
            frame.alpha_composite(faded(here_im, ha))
            draw_here_marks(frame, ox, oy, s, clamp((t - T_HERE) / 0.6), here_x_end)
        ca = clamp((t - T_CTA) / 0.3)
        if ca > 0:
            comp(frame, faded(cta_im, ca), 0, 16 * (1 - smooth(ca)))
        sa = clamp((t - T_SIG) / 0.3)
        if sa > 0:
            frame.alpha_composite(faded(sig_im, sa))
        enc.write(frame)
        if fi == 0:
            frame.convert("RGB").save(os.path.join(OUT, f"{BASE}_Cover.png"))
    enc.close()

    mp4 = finish(OUT, BASE, os.path.join(tmp, "video.mp4"), make_music(), tmp)
    times = [0.03, 0.3, 0.5, 0.7, 0.9, 1.3, 1.7, 2.0, 2.3, 2.7, 3.1, 3.5, 3.9, 4.4, 5.1, 5.7, 6.8, 7.9]
    contact_sheet(mp4, times, os.path.join(OUT, "contact_sheet.png"), tmp)
    qc = {"probe": probe(mp4), "audio": audio_report(mp4), "title_px": title_size, "punch_px": punch_size,
          "title_bottom": title_bottom, "chart_box": [OB[0], OB[1], round(OB[0] + CW * SB), round(chart_bottom)],
          "punch_bottom": punch_bottom, "cta_bottom": cta_bottom,
          "timeline": {"tick": [T_TICK0, T_TICK1], "pop": T_POP, "scratch": T_SCRATCH, "reveal": [T_REV, T_REV + REV_D],
                       "punch": T_PUNCH, "here": T_HERE, "cta": T_CTA, "signature": T_SIG,
                       "end": DUR}}
    json.dump(qc, open(os.path.join(OUT, "qc.json"), "w"), indent=1)
    print(json.dumps(qc))


if __name__ == "__main__":
    main()
