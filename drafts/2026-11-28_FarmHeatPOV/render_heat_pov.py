"""Eazy88 POV clip — "Day 1 of farm work in the Aussie summer." The clock barely moves, the heat does.

Format: POV humour, no voiceover, ~8.5 s. Farm scene drawn in code (2x supersampled), brand tokens,
procedural sound and music (cicadas, rising steps, a slide whistle as you melt).
The temperatures are a joke, not a weather report (label on screen).
Usage (from the repository root):
  python3 -I drafts/2026-11-28_FarmHeatPOV/render_heat_pov.py <out_dir>
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "templates", "tools"))
from pov_kit import (C, FPS, H, SR, TOK, W, BlendDraw, Encoder, Synth, anton, audio_report, band_mask, clamp, comp,  # noqa: E402
                     contact_sheet, ease_out_back, faded, finish, lerp, make_background, make_cta, make_signature,
                     make_static, match_loudness, probe, smooth, text_block)
from van_kit import col_mix  # noqa: E402

BASE = "Eazy88_TikTok_FarmHeatPOV"
OUT = sys.argv[1]
HEADER = "EAZY88 · BACKPACKER LIFE"
LABEL = "Illustration · not a weather report"
TITLE = ["POV: DAY 1 OF FARM", "WORK IN THE", "*AUSSIE SUMMER.*"]
PUNCH = ["AND IT'S ONLY", "*9:30 AM.*"]
CTA = ["SEND THIS TO THE MATE", "WITH *ONE* WATER BOTTLE"]

STEPS = [(0.0, "6:00 AM", 24), (0.5, "7:00 AM", 29), (1.2, "8:00 AM", 34), (1.9, "8:45 AM", 39),
         (2.5, "9:15 AM", 43), (3.05, "9:30 AM", 47)]
T_MELT0, T_MELT1 = 1.9, 3.5       # you slowly turn into a puddle
T_POP = 3.4                        # the thermometer gives up
T_REV, REV_D = 3.95, 0.5
T_PUNCH = 4.2
T_CTA = 5.6
T_SIG = 6.2
DUR = 8.4
R_TOP_A, R_TOP_B, R_BOT = 660, 812, 1380

SS, OY, BH = 2, 600, 800
HORIZON = 1112
OUTL = TOK["n800"]
CX = 360                           # you
YOU_K, YOU_DY = 1.45, -70          # you: drawn 1.45x, feet at y 1302 so the puddle stays above the signature
CARD = (540, 850, 940, 1062)       # clock + thermometer card


class P:
    """Draw on the 2x strip with screen coordinates, optionally scaled by `k` around `anchor`."""

    def __init__(self, im, k=1.0, anchor=(0, 0), dy=0):
        self.d = ImageDraw.Draw(im, "RGBA")
        self.k, (self.ax, self.ay), self.dy = k, anchor, dy

    def tx(self, x, y):
        return ((self.ax + (x - self.ax) * self.k) * SS, (self.ay + (y - self.ay) * self.k + self.dy - OY) * SS)

    def b(self, box):
        return self.tx(box[0], box[1]) + self.tx(box[2], box[3])

    def pts(self, pts):
        return [self.tx(x, y) for x, y in pts]

    def w(self, v):
        return max(1, int(v * SS * self.k))

    def ell(self, box, fill, ow=0, oc=OUTL):
        self.d.ellipse(self.b(box), fill=fill, outline=oc if ow else None, width=self.w(ow) if ow else 0)

    def rr(self, box, r, fill, ow=0, oc=OUTL):
        self.d.rounded_rectangle(self.b(box), self.w(r), fill=fill, outline=oc if ow else None,
                                 width=self.w(ow) if ow else 0)

    def rect(self, box, fill):
        self.d.rectangle(self.b(box), fill=fill)

    def poly(self, pts, fill, ow=0, oc=OUTL):
        self.d.polygon(self.pts(pts), fill=fill, outline=oc if ow else None, width=self.w(ow) if ow else 0)

    def chord(self, box, a0, a1, fill, ow=0, oc=OUTL):
        self.d.chord(self.b(box), a0, a1, fill=fill, outline=oc if ow else None, width=self.w(ow) if ow else 0)

    def line(self, pts, fill, w):
        self.d.line(self.pts(pts), fill=fill, width=self.w(w), joint="curve")
        for x, y in (pts[0], pts[-1]):
            r = w / 2
            self.ell((x - r, y - r, x + r, y + r), fill)

    def limb(self, pts, fill, w, ow=4):
        self.line(pts, OUTL, w + 2 * ow)
        self.line(pts, fill, w)


def step_at(t):
    return max(i for i, s in enumerate(STEPS) if t >= s[0])


def temp_at(t):
    """Displayed temperature: counts up over 0.25 s at each step."""
    i = step_at(t)
    if i == 0:
        return STEPS[0][2]
    return lerp(STEPS[i - 1][2], STEPS[i][2], smooth((t - STEPS[i][0]) / 0.25))


def heat(t):
    return clamp((temp_at(t) - 24) / (47 - 24))


def heat_col(h):
    if h < 0.5:
        return col_mix(C["green_l"], C["sun"], h / 0.5)
    return col_mix(C["sun"], C["primary"], (h - 0.5) / 0.5)


def melt(t):
    return smooth((t - T_MELT0) / (T_MELT1 - T_MELT0))


def drop(p, x, y, s, a=255):
    """Sweat drop (cream with outline)."""
    p.poly([(x, y - 1.9 * s), (x - 0.85 * s, y - 0.3 * s), (x + 0.85 * s, y - 0.3 * s)], C["cream"] + (a,))
    p.ell((x - s, y - s, x + s, y + s), C["cream"] + (a,), 2)
    p.line([(x - 0.95 * s, y - 0.35 * s), (x, y - 1.95 * s), (x + 0.95 * s, y - 0.35 * s)], OUTL + (a,), 2)


def draw_world(t):
    h = heat(t)
    hb = BH * SS
    ys = OY + np.arange(hb) / SS
    top = np.array(col_mix(col_mix(C["orange"], C["sunset"], 0.5), C["sun"], h))
    hor = np.array(col_mix(C["sun"], C["cream"], h))
    g0 = np.array(col_mix(col_mix(C["sunset"], TOK["primary_dark"], 0.35), C["sun"], 0.3 * h))
    g1 = np.array(col_mix(col_mix(C["sunset"], TOK["primary_dark"], 0.7), C["sunset"], 0.3 * h))
    se = np.clip((ys - OY) / (HORIZON - OY), 0, 1)[:, None]
    ge = np.clip((ys - HORIZON) / (OY + BH - HORIZON), 0, 1)[:, None]
    col = np.where((ys < HORIZON)[:, None], (1 - se) * top + se * hor, (1 - ge) * g0 + ge * g1)
    im = Image.fromarray(col[:, None, :].astype(np.uint8), "RGB").resize((W * SS, hb), Image.NEAREST)
    p = P(im)
    # the sun climbs, grows and bleaches
    sx, sy_ = lerp(200, 300, smooth(h)), lerp(1080, 800, smooth(h))
    r = lerp(46, 128, h)
    sc = col_mix(C["sunset"], C["cream"], h)
    p.ell((sx - r * 1.5, sy_ - r * 1.5, sx + r * 1.5, sy_ + r * 1.5), sc + (int(60 + 60 * h),))
    for k in range(12):
        a = k * math.pi / 6 + t * 0.8
        l0, l1 = r * 1.18, r * (1.5 + 0.35 * h + 0.08 * math.sin(t * 9 + k))
        p.line([(sx + l0 * math.cos(a), sy_ + l0 * math.sin(a)), (sx + l1 * math.cos(a), sy_ + l1 * math.sin(a))],
               C["sunset"] + (255,), 7 + 4 * h)
    p.ell((sx - r, sy_ - r, sx + r, sy_ + r), sc + (255,), 4, C["sunset"] + (255,))
    # horizon trees, then rows of plants that wilt and yellow
    rng = np.random.default_rng(7)
    x = -20
    while x < W + 20:
        rr = rng.uniform(14, 30)
        p.ell((x - rr, HORIZON - rr * 1.1 * (1 - 0.3 * h), x + rr, HORIZON + 6), TOK["secondary_dark"])
        x += rr * 1.5
    p.rect((0, HORIZON - 2, W, HORIZON + 4), TOK["secondary_dark"])
    leaf = col_mix(C["green"], col_mix(C["sun"], C["muted"], 0.4), 0.75 * h)
    for y, s in ((1140, 16), (1182, 24), (1244, 36)):
        p.rect((0, y + s * 0.35, W, y + s * 0.55), col_mix(TOK["n800"], TOK["primary_dark"], 0.5))
        x = -s
        while x < W + s:
            p.ell((x - s * (1 + 0.15 * h), y - s * (1 - 0.5 * h), x + s * (1 + 0.15 * h), y + s * 0.6), leaf, 2,
                  TOK["secondary_dark"])
            x += s * 1.7
    return im, p


def draw_you(p, t):
    m = melt(t)
    i = step_at(t)
    # bucket of strawberries and the water bottle
    p.rr((CX - 190, 1300, CX - 100, 1372), 10, C["cream"], 4)
    for k, (bx, by) in enumerate(((-176, 1296), (-152, 1290), (-128, 1297), (-164, 1282), (-140, 1280))):
        p.ell((CX + bx - 11, by - 11, CX + bx + 11, by + 11), C["primary"], 2)
    level = 1 - smooth(t / 2.6)
    bx0, by0, by1 = CX + 150, 1258, 1372
    p.rr((bx0, by0, bx0 + 48, by1), 14, C["cream"] + (255,), 4)
    if level > 0.02:
        p.rr((bx0 + 6, by1 - 6 - (by1 - by0 - 20) * level, bx0 + 42, by1 - 6), 8, C["green_l"])
    p.rr((bx0 + 12, by0 - 18, bx0 + 36, by0 + 2), 4, C["green"], 3)
    # puddle grows under you
    pw = lerp(0, 150, m)
    if pw > 2:
        p.ell((CX - pw, 1352 - 0.22 * pw, CX + pw, 1372 + 0.1 * pw), C["green"], 4)
    # body squashes down as you melt
    bw = lerp(58, 96, m)
    ytop = lerp(1214, 1338, m ** 1.2)
    if m < 0.97:
        p.rr((CX - bw, ytop, CX + bw, 1372), lerp(40, 30, m), C["green"], 4)
        if m < 0.6:   # picking arm, then it droops
            hand = (CX + 98, 1300 + 14 * math.sin(t * 9)) if i < 3 else (CX + 80, lerp(1300, 1350, m / 0.6))
            p.limb([(CX + 44, lerp(1240, 1300, m)), hand], C["green"], 24)
            p.ell((hand[0] - 14, hand[1] - 14, hand[0] + 14, hand[1] + 14), C["cream"], 3)
        for k in range(int(m * 6)):   # drips running down
            dx = (-1 if k % 2 else 1) * (bw - 6)
            dy = ytop + 30 + ((t * 120 + k * 37) % max(20, 1372 - ytop - 40))
            p.ell((CX + dx - 7, dy - 9, CX + dx + 7, dy + 9), C["green"], 3)
    # head sinks into the body / puddle
    hr = lerp(46, 40, m)
    hx, hy = CX, lerp(1170, 1322, m ** 1.1)
    p.ell((hx - hr, hy - hr, hx + hr, hy + hr), C["cream"] if m < 0.97 else C["green"], 4)
    # face
    if m >= 0.97:   # just eyes in the puddle
        for ex in (hx - 16, hx + 16):
            p.ell((ex - 9, hy - 9, ex + 9, hy + 9), C["cream"], 3)
            p.ell((ex - 3, hy - 3, ex + 3, hy + 3), OUTL)
    else:
        for ex in (hx - 14, hx + 18):
            p.ell((ex - 5, hy - 10, ex + 5, hy), OUTL)
        if i == 0:
            p.chord((hx - 16, hy + 2, hx + 22, hy + 24), 0, 180, OUTL)           # smile
        elif i == 1:
            p.line([(hx - 10, hy + 16), (hx + 18, hy + 16)], OUTL, 4)              # meh
        else:
            p.ell((hx - 8, hy + 8, hx + 16, hy + 28), OUTL)                        # panting
            p.rr((hx - 2, hy + 18, hx + 12, hy + 38), 7, C["primary"], 2)          # tongue
    # cap slides down
    cy = hy - hr * 0.3
    p.chord((hx - 50, cy - 50, hx + 50, cy + 40), 180, 360, C["primary"], 4)
    p.rr((hx + 22, cy - 10, hx + 76, cy + 2), 6, C["primary"], 3)
    # sweat drops: one more per step, falling
    for k in range(min(i, 4) * 2 if m < 0.97 else 0):
        ang = -2.6 + k * 0.55
        ph = (t * 1.6 + k * 0.37) % 1
        x = hx + (hr + 16) * math.cos(ang)
        y = hy + (hr + 10) * math.sin(ang) + 70 * ph
        drop(p, x, y, 9, int(255 * (1 - ph)))


def card_layer(t):
    """Clock + temperature card (not shimmered)."""
    x0, y0, x1, y1 = CARD
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = BlendDraw(im, "RGBA")
    d.rounded_rectangle(CARD, 28, fill=OUTL + (240,))
    temp = temp_at(t)
    h = clamp((temp - 24) / 23)
    hc = heat_col(h)
    i = step_at(t)
    # thermometer
    tx, tb = x0 + 46, y1 - 40
    d.rounded_rectangle((tx - 14, y0 + 22, tx + 14, tb), 14, fill=C["cream"] + (255,))
    popped = t >= T_POP
    lvl = 1.0 if popped else clamp((temp - 15) / 35)
    d.rounded_rectangle((tx - 7, lerp(tb - 6, y0 + 30, lvl), tx + 7, tb), 7, fill=hc + (255,))
    d.ellipse((tx - 24, tb - 24, tx + 24, tb + 24), fill=hc + (255,), outline=C["cream"] + (255,), width=5)
    # time and temperature (pop on each step)
    ft = anton(54)
    d.text((x0 + 100, y0 + 14), STEPS[i][1], font=ft, fill=C["cream"] + (255,))
    label = f"{int(round(temp))}°" + ("?!" if i == len(STEPS) - 1 else "")
    s = 1 + 0.25 * math.exp(-(t - STEPS[i][0]) * 10) if i else 1
    fb = anton(int(96 * s))
    d.text((x0 + 100, y0 + 78 - 40 * (s - 1)), label, font=fb, fill=hc + (255,))
    if popped:   # mercury flies out of the top
        q = t - T_POP
        for k in range(7):
            vx, vy = (k - 3) * 70, -380 - 40 * (k % 3)
            px, py = tx + vx * q, y0 + 22 + vy * q + 900 * q * q
            if q < 1.0:
                d.ellipse((px - 9, py - 9, px + 9, py + 9), fill=C["primary"] + (int(255 * (1 - q)),))
        a = clamp(1 - (q - 0.6) / 0.3)
        if a > 0:
            fp = anton(int(86 * (1 + 0.3 * math.exp(-q * 12))))
            tile = Image.new("RGBA", (300, 150), (0, 0, 0, 0))
            td = BlendDraw(tile, "RGBA")
            for ox, oy in ((-4, 0), (4, 0), (0, -4), (0, 4), (-3, -3), (3, 3), (-3, 3), (3, -3)):
                td.text((20 + ox, 10 + oy), "POP!", font=fp, fill=OUTL + (255,))
            td.text((20, 10), "POP!", font=fp, fill=C["cream"] + (255,))
            tile = tile.rotate(-10, expand=True, resample=Image.BICUBIC)
            comp(im, faded(tile, a), x0 - 40, y0 - 110)
    return im


def shimmer(strip_rgb, t):
    """Heat haze: rows wobble sideways, more as it gets hotter."""
    amp = 6 * SS * heat(t) ** 1.3
    if amp < 0.5:
        return strip_rgb
    a = np.asarray(strip_rgb)
    h, w = a.shape[:2]
    ys = np.arange(h)
    shift = (amp * np.sin(ys / (14 * SS) + t * 9) * np.clip((ys / SS - 150) / 300, 0, 1)).astype(int)
    idx = (np.arange(w)[None, :] - shift[:, None]) % w
    return Image.fromarray(a[ys[:, None], idx])


def make_music():
    sy = Synth(47)
    put = sy.put
    n = int(DUR * SR)
    m = np.zeros(n)
    rng = np.random.default_rng(9)
    tt = np.arange(n) / SR
    # cicadas: band-limited noise, pulsing, louder as it heats up
    x = rng.standard_normal(n)
    F = np.fft.rfft(x)
    fr = np.fft.rfftfreq(n, 1 / SR)
    F *= np.exp(-((fr - 4700) / 700) ** 2)
    cic = np.fft.irfft(F, n)
    cic /= np.abs(cic).max()
    pulse = 0.55 + 0.45 * np.sign(np.sin(2 * np.pi * 42 * tt))
    swell = 0.7 + 0.3 * np.sin(2 * np.pi * 0.8 * tt)
    hcurve = np.interp(tt, [0, 0.5, 1.2, 1.9, 2.5, 3.05, T_REV, T_REV + 0.4, DUR],
                       [0.15, 0.3, 0.45, 0.6, 0.75, 0.95, 1.0, 0.25, 0.2])
    m += 0.075 * cic * pulse * swell * hcurve
    # each step: a clock flip and a note one step higher
    notes = [523.25, 587.33, 659.25, 783.99, 880.0, 1046.5]
    for (ts, _, _), f in zip(STEPS, notes):
        put(m, sy.tick(0.16, 1800.0), ts + 0.01)
        put(m, sy.pluck(f, 0.5, 0.14, decay=0.993), ts + 0.02)
        put(m, sy.pluck(f / 2, 0.5, 0.08, decay=0.993), ts + 0.02)
    # lazy morning strum at the start, getting faster and more nervous
    t, k = 0.1, 0
    while t < T_POP:
        f = (392.0, 493.88, 587.33)[k % 3]
        put(m, sy.pluck(f, 0.25, 0.05, decay=0.985), t)
        t += lerp(0.3, 0.14, clamp(t / T_POP))
        k += 1
    # slide whistle down as you melt
    put(m, sy.tone(1400.0, 1.3, 0.1, a=0.04, r=0.15, nh=3, tilt=2.0, detune=(0,), glide=(260.0, 0.0), vib=0.01,
                   vib_rate=7.0, vib_delay=0.0), T_MELT0 + 0.3)
    # POP + boing
    put(m, sy.tick(0.5, 900.0), T_POP)
    put(m, sy.tone(330.0, 0.35, 0.14, a=0.005, r=0.15, nh=6, tilt=1.2, detune=(0,), glide=(660.0, 0.0), vib=0.12,
                   vib_rate=18.0, vib_delay=0.0), T_POP + 0.03)
    # punch: two drips into the puddle
    for k, t0 in enumerate((T_PUNCH, T_PUNCH + 0.28)):
        put(m, sy.tone(1300.0 - 200 * k, 0.07, 0.16, a=0.003, r=0.06, nh=2, tilt=2.0, detune=(0,), glide=(420.0, 0.0)), t0)
    prog = [(392.0, 493.88, 587.33), (440.0, 523.25, 659.25), (349.23, 440.0, 523.25), (392.0, 493.88, 587.33)]
    t, k = T_CTA - 0.4, 0
    while t < DUR - 0.25:
        for j, f in enumerate(prog[(k // 2) % 4]):
            put(m, sy.pluck(f, 0.45, 0.09, decay=0.993), t + j * 0.012)
        t += 0.45
        k += 1
    for f in (783.99, 987.77, 1174.66):
        put(m, sy.bell(f, 0.06), DUR - 0.85)
    return sy.master(m, reverb=0.18, fade=0.3, sub=0.4)


def main():
    os.makedirs(OUT, exist_ok=True)
    tmp = os.path.join(OUT, "_tmp")
    os.makedirs(tmp, exist_ok=True)
    bg = make_background().convert("RGBA")
    static = make_static(HEADER, LABEL)
    title_im, title_bottom, title_size = text_block(TITLE, 100, 860, 80, 318)
    punch_im, punch_bottom, punch_size = text_block(PUNCH, 120, 860, 80, 318)
    cta_im, cta_bottom = make_cta(CTA, punch_bottom + 46)
    sig_im, _ = make_signature(1296)
    assert title_bottom <= R_TOP_A and cta_bottom <= R_TOP_B, (title_bottom, cta_bottom)

    enc = Encoder(os.path.join(tmp, "video.mp4"))
    nframes = int(round(DUR * FPS))
    for fi in range(nframes):
        t = fi / FPS
        e = smooth((t - T_REV) / REV_D) if t >= T_REV else 0.0
        top = lerp(R_TOP_A, R_TOP_B, e)
        strip, _ = draw_world(t)
        draw_you(P(strip, YOU_K, (CX, 1372), YOU_DY), t)
        strip = shimmer(strip, t)
        scene = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        scene.paste(strip.resize((W, BH), Image.LANCZOS), (0, OY))
        scene.alpha_composite(card_layer(t))
        scene.putalpha(Image.fromarray(np.minimum(np.asarray(scene.getchannel("A")), np.asarray(band_mask(top, R_BOT)))))
        frame = bg.copy()
        frame.alpha_composite(scene)
        frame.alpha_composite(static)
        ta = 1 - clamp((t - T_REV) / 0.25)
        if ta > 0:
            frame.alpha_composite(faded(title_im, ta))
        pa = clamp((t - T_PUNCH) / 0.3)
        if pa > 0:
            comp(frame, faded(punch_im, pa), -24 * (1 - smooth(pa)), 0)
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
    loud_fix_db = match_loudness(mp4, tmp)
    times = [0.03, 0.4, 0.7, 1.1, 1.45, 1.8, 2.15, 2.45, 2.75, 3.1, 3.45, 3.75, 4.1, 4.5, 5.0, 5.8, 7.0, 8.1]
    contact_sheet(mp4, times, os.path.join(OUT, "contact_sheet.png"), tmp)
    qc = {"probe": probe(mp4), "audio": audio_report(mp4), "loudness_fix_db": loud_fix_db, "title_px": title_size,
          "punch_px": punch_size, "title_bottom": title_bottom, "punch_bottom": punch_bottom, "cta_bottom": cta_bottom,
          "timeline": {"steps": [s[0] for s in STEPS], "melt": [T_MELT0, T_MELT1], "pop": T_POP,
                       "reveal": [T_REV, T_REV + REV_D], "punch": T_PUNCH, "cta": T_CTA, "signature": T_SIG, "end": DUR}}
    json.dump(qc, open(os.path.join(OUT, "qc.json"), "w"), indent=1)
    print(json.dumps(qc))


if __name__ == "__main__":
    main()
