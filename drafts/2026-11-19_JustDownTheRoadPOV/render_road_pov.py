"""Eazy88 POV clip — "An Aussie says the next town is 'just down the road'." Day turns to night and back.

Format: POV humour, no voiceover, 13 s. Everything is original: landscape, signs and van drawn in code
(the van is the one from the parking clip), brand fonts and colour tokens, procedural music (no samples).
Distances on the signs are a joke, not real places.

Usage (from the repository root):
  python3 -I drafts/2026-11-19_JustDownTheRoadPOV/render_road_pov.py <out_dir>
Outputs: <BASE>_A.mp4, <BASE>_Cover.png, contact_sheet.png, qc.json
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageOps

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "templates", "tools"))
from pov_kit import (C, FPS, H, SR, TOK, W, BlendDraw, Encoder, Synth, anton, audio_report, band_mask,  # noqa: E402
                     clamp, comp, contact_sheet, faded, finish, jakarta, lerp, make_background, make_cta,
                     make_static, probe, scaled, smooth, text_block)

BASE = "Eazy88_TikTok_JustDownTheRoadPOV"
OUT = sys.argv[1]

# ---- public text (English)
HEADER = "EAZY88 · BACKPACKER LIFE"
LABEL = "Illustration · not a real road"
TITLE = ["POV: AN AUSSIE SAYS", "THE NEXT TOWN IS", "*'JUST DOWN THE ROAD.'*"]
PUNCH = ["6 HOURS LATER:", "*'NOT FAR, MATE.'*"]
CTA = ["SEND THIS TO THE MATE", "WHO SAYS IT'S *'NOT FAR'*"]

# ---- signs: (time the sign is read, kind, small line, big line, colour)
SIGNS = [
    (0.0, "guide", "NEXT TOWN", "80 km", "g"),
    (1.6, "guide", "NEXT TOWN", "160 km", "g"),
    (2.7, "roo", "ROOS", "200 km", None),
    (3.8, "guide", "NEXT FUEL", "320 km", "g"),
    (4.9, "guide", "NEXT TOWN", "410 km", "g"),
    (6.0, "guide", "STILL", "NOT THERE", "r"),
    (7.1, "guide", "ARE WE THERE YET?", "NO.", "r"),
    (8.2, "guide", "NEXT TOWN", "'JUST DOWN THE ROAD'", "g"),
]
T_REV, REV_D = 9.0, 0.9
T_PUNCH = 9.55
T_CTA = 11.0
DUR = 13.0

# ---- time of day: (t, sky top, sky horizon, darkness)
SKY = [
    (0.0, C["sun"], C["cream"], 0.0), (3.4, C["sun"], C["cream"], 0.0), (4.9, TOK["primary_dark"], C["sunset"], 0.15),
    (5.9, C["bg"], TOK["n800"], 1.0), (7.6, C["bg"], TOK["n800"], 1.0), (8.5, TOK["n800"], C["orange"], 0.35),
    (9.6, C["sun"], C["cream"], 0.0), (DUR, C["sun"], C["cream"], 0.0),
]

# ---- geometry (world px; road surface at y = 0, up is negative) and camera
VX = 190                       # screen x of the van's rear in the close-up
READ_X = 700                   # screen x of a sign's centre when it is read
GY_A, GY_B = 1290, 1300        # road line on screen before / after the reveal
SB = 0.40
R_TOP_A, R_TOP_B, R_BOT = 660, 812, 1380
HORIZON = 190
VMAX = 1450.0


def col_mix(a, b, e):
    return tuple(int(round(lerp(x, y, e))) for x, y in zip(a, b))


def sky_at(t):
    for (t0, a0, b0, d0), (t1, a1, b1, d1) in zip(SKY, SKY[1:]):
        if t0 <= t <= t1:
            e = smooth((t - t0) / (t1 - t0))
            return col_mix(a0, a1, e), col_mix(b0, b1, e), lerp(d0, d1, e)
    return SKY[-1][1], SKY[-1][2], SKY[-1][3]


# ---- van speed: starts from a stop, slows down near each sign so it can be read
def speed(t):
    v = VMAX * (1 - 0.78 * sum(math.exp(-((t - s[0]) / 0.3) ** 2) for s in SIGNS[1:]))
    v *= smooth(t / 1.1)
    if t > T_REV:
        v *= lerp(1.0, 0.25, smooth((t - T_REV) / 0.6))
    return v


NF = int(round(DUR * FPS))
XS = np.zeros(NF + 1)
for _i in range(1, NF + 1):
    XS[_i] = XS[_i - 1] + speed((_i - 0.5) / FPS) / FPS


def X_at(t):
    return float(np.interp(t * FPS, np.arange(NF + 1), XS))


SIGN_X = [X_at(s[0]) + (READ_X - VX) for s in SIGNS]   # world x of each sign centre


# ---------------------------------------------------------------- artwork
def van_art(ss=3):
    """Small campervan with a surfboard (same drawing as the parking clip), 340 x 170, facing right."""
    im = Image.new("RGBA", (340 * ss, 170 * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(im, "RGBA")
    S = lambda *v: tuple(int(round(x * ss)) for x in v)  # noqa: E731
    d.rounded_rectangle(S(44, 10, 308, 28), 9 * ss, fill=C["cream"] + (255,))
    d.rectangle(S(92, 17, 260, 21), fill=C["green"] + (255,))
    for x in (96, 244):
        d.rectangle(S(x, 28, x + 8, 40), fill=TOK["n800"] + (255,))
    d.rounded_rectangle(S(0, 38, 340, 146), 30 * ss, fill=C["orange"] + (255,))
    d.rectangle(S(0, 104, 340, 112), fill=C["cream"] + (255,))
    d.rounded_rectangle(S(20, 54, 96, 98), 12 * ss, fill=C["bg"] + (255,))
    d.rounded_rectangle(S(108, 54, 186, 98), 10 * ss, fill=C["bg"] + (255,))
    d.rounded_rectangle(S(198, 54, 276, 98), 10 * ss, fill=C["bg"] + (255,))
    d.line([S(192, 114), S(192, 140)], fill=C["primary"] + (255,), width=2 * ss)
    d.ellipse(S(6, 116, 22, 132), fill=C["sun"] + (255,))
    for cx in (78, 262):
        d.ellipse(S(cx - 30, 110, cx + 30, 170), fill=C["ink_deep"] + (255,))
        d.ellipse(S(cx - 11, 129, cx + 11, 151), fill=C["cream"] + (255,))
    return ImageOps.mirror(im)


SIGN_W, SIGN_H, POST = 380, 210, 135
RS = 3


def sign_art(kind, small, big, colour):
    """Sign with its posts; world size (SIGN_W, SIGN_H + POST); bottom of posts = ground."""
    w, h = SIGN_W * RS, (SIGN_H + POST) * RS
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = BlendDraw(im, "RGBA")
    if kind == "roo":
        s = 230 * RS
        cx = w / 2
        d.rectangle((cx - 6 * RS, s * 0.75, cx + 6 * RS, h), fill=TOK["n600"] + (255,))
        d.polygon([(cx, 0), (cx + s / 2, s / 2), (cx, s), (cx - s / 2, s / 2)], fill=TOK["n800"] + (255,))
        k = 9 * RS
        d.polygon([(cx, k), (cx + s / 2 - k, s / 2), (cx, s - k), (cx - s / 2 + k, s / 2)], fill=C["sun"] + (255,))
        f = anton(64 * RS)
        d.text((cx - f.getlength(small) / 2, s / 2 - 52 * RS), small, font=f, fill=TOK["n800"] + (255,))
        pw, ph = 270 * RS, 64 * RS
        py = s - 18 * RS
        d.rectangle((cx - pw / 2, py, cx + pw / 2, py + ph), fill=C["cream"] + (255,), outline=TOK["n800"] + (255,),
                    width=4 * RS)
        f2 = anton(42 * RS)
        assert f2.getlength("NEXT " + big) < pw - 24 * RS
        d.text((cx - f2.getlength("NEXT " + big) / 2, py + 4 * RS), "NEXT " + big, font=f2, fill=TOK["n800"] + (255,))
        return im
    bgc = TOK["secondary_dark"] if colour == "g" else TOK["primary_dark"]
    for px in (SIGN_W * 0.22, SIGN_W * 0.78):
        d.rectangle(((px - 6) * RS, (SIGN_H - 4) * RS, (px + 6) * RS, h), fill=TOK["n600"] + (255,))
    d.rounded_rectangle((0, 0, w - 1, SIGN_H * RS), 16 * RS, fill=bgc + (255,))
    d.rounded_rectangle((9 * RS, 9 * RS, w - 1 - 9 * RS, (SIGN_H - 9) * RS), 10 * RS, outline=C["cream"] + (255,),
                        width=4 * RS)
    fs = jakarta(34 * RS, "ExtraBold")
    size = 104
    fb = anton(size * RS)
    while fb.getlength(big) > (SIGN_W - 60) * RS:
        size -= 2
        fb = anton(size * RS)
    sl, st, sr, sb = fs.getbbox(small)
    bl, bt, br, bb = fb.getbbox(big)
    gap = 16 * RS
    total = (sb - st) + gap + (bb - bt)
    y0 = (SIGN_H * RS - total) / 2
    d.text(((w - fs.getlength(small)) / 2, y0 - st), small, font=fs, fill=C["cream"] + (255,))
    d.text(((w - fb.getlength(big)) / 2, y0 + (sb - st) + gap - bt), big, font=fb, fill=C["cream"] + (255,))
    return im


def make_bushes():
    rng = np.random.default_rng(3)
    out, x = [], -800.0
    while x < XS[-1] + 4000:
        out.append((x, rng.choice([-52, 46, 60]), rng.uniform(0.7, 1.3)))
        x += rng.uniform(160, 340)
    return out


BUSHES = make_bushes()
_rng = np.random.default_rng(11)
STARS = [(_rng.uniform(0, W), _rng.uniform(0, 1), _rng.uniform(1.5, 3.4)) for _ in range(70)]


def hill_profile(x):
    """Distant ranges: smooth bumps with flat-topped mesas."""
    h = 34 + 22 * math.sin(x / 170) + 14 * math.sin(x / 61 + 1.3) + 9 * math.sin(x / 23 + 0.4)
    return min(h, 58)


# ---------------------------------------------------------------- scene
def paste(dst, src, x, y):
    """Paste an RGBA image on the RGB scene with its alpha, clipped to the canvas."""
    x, y = int(round(x)), int(round(y))
    sx0, sy0 = max(0, -x), max(0, -y)
    sx1, sy1 = min(src.width, dst.width - x), min(src.height, dst.height - y)
    if sx1 > sx0 and sy1 > sy0:
        part = src.crop((sx0, sy0, sx1, sy1))
        dst.paste(part, (x + sx0, y + sy0), part)


def draw_scene(t, s, vx_screen, gy, top, van, signs):
    """Everything inside the scene band. Drawn on an opaque RGB canvas (semi-transparent ImageDraw fills
    blend correctly only on RGB); returns an RGBA layer for the band mask."""
    sky_top, sky_hor, dark = sky_at(t)
    X = X_at(t)
    scene = Image.new("RGB", (W, H), C["bg"])
    d = ImageDraw.Draw(scene, "RGBA")
    hz = gy - HORIZON * s
    # sky gradient
    y0 = int(top)
    for y in range(y0, int(hz) + 1, 4):
        e = clamp((y - y0) / max(1, hz - y0))
        d.rectangle((0, y, W, y + 4), fill=col_mix(sky_top, sky_hor, e ** 1.4) + (255,))
    # sun (day, sunset, sunrise) and moon (night)
    sun_y = None
    if t < 5.6:
        e = smooth((t - 1.5) / 3.9)
        sun_x, sun_y, rad = lerp(800, 760, e), lerp(top + 120, hz + 10, e), lerp(46, 64, e)
        col = col_mix(C["cream"], C["sunset"], e)
    elif t > 7.9:
        e = smooth((t - 7.9) / 2.2)
        sun_x, sun_y, rad = 800, lerp(hz + 40, top + 150, e), lerp(66, 50, e)
        col = col_mix(C["orange"], C["cream"], e)
    if sun_y is not None:
        for g, a in ((2.2, 40), (1.6, 70)):
            d.ellipse((sun_x - rad * g, sun_y - rad * g, sun_x + rad * g, sun_y + rad * g), fill=col + (a,))
        d.ellipse((sun_x - rad, sun_y - rad, sun_x + rad, sun_y + rad), fill=col + (255,))
    # distant ranges (slow parallax)
    pts = [(sx, hz - hill_profile(X * 0.12 + sx / max(s, 0.2)) * max(s, 0.35)) for sx in range(0, W + 9, 8)]
    d.polygon([(0, hz + 2)] + pts + [(W, hz + 2)], fill=col_mix(C["primary"], TOK["primary_dark"], 0.35) + (255,))
    # ground, road, centre line
    d.rectangle((0, hz, W, H), fill=TOK["primary_dark"] + (255,))
    d.rectangle((0, hz, W, hz + 10 * s), fill=C["primary"] + (200,))
    d.rectangle((0, gy - 34 * s, W, gy + 26 * s), fill=TOK["n800"] + (255,))
    d.line([(0, gy - 34 * s), (W, gy - 34 * s)], fill=C["muted"] + (90,), width=max(1, int(3 * s)))
    per, dash = 130, 70           # centre-line dashes, fixed in the world
    xw = math.floor((X - vx_screen / s) / per) * per
    while vx_screen + (xw - X) * s < W:
        x0 = vx_screen + (xw - X) * s
        d.rectangle((x0, gy - 6 * s, x0 + dash * s, gy - 1 * s), fill=C["cream"] + (220,))
        xw += per
    # bushes
    for bx, by, k in BUSHES:
        sx = vx_screen + (bx - X) * s
        if -60 < sx < W + 60:
            r = 16 * k * s
            cy = gy + by * s
            for ox, oy, rr in ((-1.1, 0.2, 0.8), (0, -0.25, 1.0), (1.1, 0.2, 0.75)):
                d.ellipse((sx + ox * r - rr * r, cy + oy * r - rr * r, sx + ox * r + rr * r, cy + oy * r + rr * r),
                          fill=TOK["secondary_dark"] + (255,))
    # van (small bounce while driving)
    v = speed(t) / VMAX
    bounce = 2.0 * v * math.sin(t * 31) * s
    vw, vh = 340 * s, 170 * s
    # night: darken the land and the sky together
    if dark > 0:
        scene = Image.blend(scene, Image.new("RGB", (W, H), C["bg"]), 0.6 * dark)
        d = ImageDraw.Draw(scene, "RGBA")
        for sx, fy, r in STARS:
            sy = top + 20 + fy * (hz - 90 * s - top - 20)
            d.ellipse((sx - r, sy - r, sx + r, sy + r), fill=C["cream"] + (int(230 * dark),))
        mx, my, mr = 820, top + 120, 40
        d.ellipse((mx - mr * 1.8, my - mr * 1.8, mx + mr * 1.8, my + mr * 1.8), fill=C["cream"] + (int(25 * dark),))
        d.ellipse((mx - mr, my - mr, mx + mr, my + mr), fill=C["cream"] + (int(255 * dark),))
        d.ellipse((mx - mr + 16, my - mr - 6, mx + mr + 16, my + mr - 6), fill=sky_top + (int(255 * dark),))
        # headlight beam
        fx, fy2 = vx_screen + vw - 6 * s, gy - 46 * s + bounce
        d.polygon([(fx, fy2 - 6 * s), (fx + 520 * s, fy2 - 70 * s), (fx + 520 * s, fy2 + 40 * s)],
                  fill=C["sun"] + (int(70 * dark),))
    # signs (retro-reflective: they stay readable at night)
    for i, art in enumerate(signs):
        sx = vx_screen + (SIGN_X[i] - X) * s
        sw, sh = SIGN_W * s, (SIGN_H + POST) * s
        if sx + sw / 2 < -20 or sx - sw / 2 > W + 20:
            continue
        paste(scene, scaled(("sign", i), art, sw, sh), sx - sw / 2, gy - 34 * s - sh)
    # the van drives in front of the signs (darkened at night like the land)
    vim = scaled(("van", round(vw)), van, vw, vh)
    if dark > 0:
        rgb = Image.blend(vim.convert("RGB"), Image.new("RGB", vim.size, C["bg"]), 0.6 * dark)
        rgb.putalpha(vim.getchannel("A"))
        vim = rgb
    paste(scene, vim, vx_screen, gy - vh + 8 * s + bounce)
    return scene.convert("RGBA")


# ---------------------------------------------------------------- music (procedural, no samples)
def make_music():
    sy = Synth(21)
    put = sy.put
    n = int(DUR * SR)
    m = np.zeros(n)
    beat = 0.6
    # D A Bm G, two beats each; ukulele-like strums and a plucked bass
    prog = [((293.66, 369.99, 440.0, 587.33), 146.83), ((277.18, 329.63, 440.0, 554.37), 110.0),
            ((293.66, 369.99, 493.88, 587.33), 123.47), ((293.66, 392.0, 493.88, 587.33), 98.0)]
    t, k = 0.0, 0
    while t < DUR - 0.5:
        ch, root = prog[(k // 2) % 4]
        night = 5.7 <= t < 7.9
        g = 0.55 if night else 1.0
        for j, f in enumerate(ch):
            put(m, sy.pluck(f, 0.7, 0.16 * g, decay=0.994), t + j * 0.014)
            put(m, sy.pluck(f, 0.4, 0.08 * g, decay=0.992), t + beat / 2 + (3 - j) * 0.012)
        put(m, sy.pluck(root * 2, 0.5, 0.2 * g, decay=0.99), t)
        if not night and t > 0.3:
            put(m, sy.kick(0.13), t)
            if k % 2 == 1:
                put(m, sy.clap(0.16), t)
            for q in (0.0, 0.3):
                put(m, sy.snare(0.05), t + q + 0.15)
        t += beat
        k += 1
    put(m, sy.bell(1174.66, 0.12), 0.02)
    # each sign: a passing whoosh and a small chime, a semitone higher each time
    for i, s_ in enumerate(SIGNS[1:], 1):
        put(m, sy.whoosh(0.55, 0.22), s_[0] - 0.3)
        put(m, sy.bell(587.33 * 2 ** (i / 12), 0.08, 0.9), s_[0])
    # night: crickets
    rng = np.random.default_rng(5)
    for tc in np.arange(5.8, 7.9, 0.33):
        for p in range(3):
            n2 = int(0.018 * SR)
            tt = np.arange(n2) / SR
            put(m, 0.035 * np.sin(2 * np.pi * 4300 * tt) * np.sin(np.pi * tt / tt[-1]), tc + p * 0.04 + rng.uniform(0, 0.02))
    # reveal: a bright held chord over the morning
    for f in (293.66, 369.99, 440.0, 587.33, 739.99):
        put(m, sy.tone(f, 1.6, 0.06, a=0.08, r=1.2, nh=10, tilt=1.2), T_REV)
    put(m, sy.cymbal(0.18, 2.0, swell=0.5, decay=2.4), T_REV - 0.5)
    put(m, sy.bell(1174.66, 0.1, 1.2), DUR - 1.3)
    put(m, sy.pluck(587.33, 1.0, 0.2, decay=0.995), DUR - 1.3)
    return sy.master(m, reverb=0.22, fade=0.5, sub=0.35)


# ---------------------------------------------------------------- render
def main():
    os.makedirs(OUT, exist_ok=True)
    tmp = os.path.join(OUT, "_tmp")
    os.makedirs(tmp, exist_ok=True)

    bg = make_background().convert("RGBA")
    static = make_static(HEADER, LABEL)
    title_im, title_bottom, title_size = text_block(TITLE, 100, 860, 80, 318)
    punch_im, punch_bottom, punch_size = text_block(PUNCH, 112, 860, 80, 318)
    cta_im, cta_bottom = make_cta(CTA, punch_bottom + 46)
    assert title_bottom <= R_TOP_A, f"title ends at {title_bottom}"
    assert cta_bottom <= R_TOP_B, f"CTA ends at {cta_bottom}, scene starts at {R_TOP_B}"
    van = van_art()
    signs = [sign_art(k, a, b, c) for _, k, a, b, c in SIGNS]

    enc = Encoder(os.path.join(tmp, "video.mp4"))
    for fi in range(NF):
        t = fi / FPS
        e = smooth((t - T_REV) / REV_D) if t >= T_REV else 0.0
        s = (SB ** e) * (1 - 0.03 * smooth((t - T_REV - REV_D) / 3))
        # keep the van's centre on a path from its close-up spot to the middle of the frame
        vcx = lerp(VX + 170, 470, e)
        gy = lerp(GY_A, GY_B, e)
        top = lerp(R_TOP_A, R_TOP_B, e)
        scene = draw_scene(t, s, vcx - 170 * s, gy, top, van, signs)
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
        enc.write(frame)
        if fi == 0:
            frame.convert("RGB").save(os.path.join(OUT, f"{BASE}_Cover.png"))
    enc.close()

    mp4 = finish(OUT, BASE, os.path.join(tmp, "video.mp4"), make_music(), tmp)
    times = [0.03, 0.9, 1.6, 2.7, 3.8, 4.4, 4.9, 5.5, 6.0, 7.1, 8.2, 8.9, 9.3, 9.8, 10.5, 11.2, 12.0, 12.8]
    contact_sheet(mp4, times, os.path.join(OUT, "contact_sheet.png"), tmp)
    qc = {"probe": probe(mp4), "audio": audio_report(mp4), "title_px": title_size, "punch_px": punch_size,
          "title_bottom": title_bottom, "punch_bottom": punch_bottom, "cta_bottom": cta_bottom,
          "sign_read_times": [s_[0] for s_ in SIGNS], "reveal": [T_REV, T_REV + REV_D], "punch": T_PUNCH, "cta": T_CTA,
          "end": DUR}
    json.dump(qc, open(os.path.join(OUT, "qc.json"), "w"), indent=1)
    print(json.dumps(qc))


if __name__ == "__main__":
    main()
