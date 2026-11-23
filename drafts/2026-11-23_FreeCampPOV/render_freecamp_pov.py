"""Eazy88 POV clip (van series) — "It's 9 pm and you need a free spot to sleep in the van."

Format: POV humour, no voiceover, ~9.5 s. The orange van drives at dusk past one "no" sign after another;
next morning it is parked in a paddock, surrounded by cows. Drawn in code, brand tokens, procedural music.
The signs are a joke, not real places or rules.

Usage (from the repository root):
  python3 -I drafts/2026-11-23_FreeCampPOV/render_freecamp_pov.py <out_dir>
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageOps

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "templates", "tools"))
from pov_kit import (C, FPS, H, SR, TOK, W, Encoder, Synth, audio_report, band_mask, clamp, comp,  # noqa: E402
                     contact_sheet, faded, finish, lerp, make_background, make_cta, make_signature, make_static,
                     probe, scaled, smooth, text_block)
from van_kit import RS, VAN_W, Road, col_mix, darken, paste, sign_art, van_art  # noqa: E402

BASE = "Eazy88_TikTok_FreeCampPOV"
OUT = sys.argv[1]

HEADER = "EAZY88 · BACKPACKER LIFE"
LABEL = "Illustration · not real signs"
TITLE = ["POV: IT'S 9 PM AND YOU", "NEED A FREE SPOT TO", "*SLEEP IN THE VAN.*"]
PUNCH = ["NEXT MORNING:", "*YOUR NEW NEIGHBOURS.*"]
CTA = ["SEND THIS TO THE MATE", "WHO *SLEEPS IN THE VAN*"]

# (time read, small line, big line, colour)
SIGNS = [
    (0.0, "", "NO CAMPING", "w"),
    (0.85, "NO OVERNIGHT", "PARKING", "w"),
    (1.7, "NO SLEEPING", "IN VEHICLES", "w"),
    (2.55, "RESIDENTS", "ONLY", "r"),
    (3.4, "SERIOUSLY?", "NOPE.", "r"),
    (4.25, "NEXT FREE SPOT", "410 km", "g"),
]
T_STOP = 4.8             # the van pulls over
T_CUT = 5.0              # darkest moment: the night passes
T_REV, REV_D = 5.15, 0.8
T_PUNCH = 5.6
T_CTA = 6.8
T_SIG = 7.4
DUR = 9.4

VX = 150
READ_X = 690
GY_A, GY_B = 1290, 1236
SB = 0.75
R_TOP_A, R_TOP_B, R_BOT = 660, 812, 1380
VMAX = 1600.0

SKY = [(0.0, TOK["primary_dark"], C["sunset"], 0.12), (0.9, TOK["n800"], TOK["primary_dark"], 0.55),
       (1.8, C["bg"], TOK["n800"], 1.0), (T_CUT, C["bg"], TOK["n800"], 1.0),
       (T_CUT + 0.6, TOK["n800"], C["orange"], 0.35), (T_CUT + 1.4, C["sun"], C["cream"], 0.0), (DUR, C["sun"], C["cream"], 0.0)]


def speed(t):
    if t >= T_STOP:
        return 0.0
    v = VMAX * (1 - 0.8 * sum(math.exp(-((t - s[0]) / 0.28) ** 2) for s in SIGNS))
    return v * (1 - smooth((t - (T_STOP - 0.5)) / 0.5))


def sun(t, top, hz):
    if t < 1.2:   # sunset at the start
        e = smooth(t / 1.2)
        return 820, lerp(hz - 40, hz + 30, e), 60, C["sunset"]
    if t > T_CUT + 0.2:
        e = smooth((t - T_CUT - 0.2) / 1.4)
        return 820, lerp(hz + 30, top + 140, e), lerp(62, 48, e), col_mix(C["orange"], C["cream"], e)
    return None


def cow_art(facing="left"):
    w, h = 150, 104
    im = Image.new("RGBA", (w * RS, h * RS), (0, 0, 0, 0))
    d = ImageDraw.Draw(im, "RGBA")
    k = RS
    body, spot, nose = C["cream"] + (255,), TOK["n800"] + (255,), C["sun"] + (255,)
    for lx in (34, 52, 96, 114):                                    # legs
        d.rounded_rectangle((lx * k, 62 * k, (lx + 10) * k, 102 * k), 3 * k, fill=TOK["n600"] + (255,))
    d.rounded_rectangle((26 * k, 26 * k, 128 * k, 74 * k), 22 * k, fill=body)                 # body
    d.ellipse((50 * k, 30 * k, 80 * k, 52 * k), fill=spot)
    d.ellipse((90 * k, 46 * k, 112 * k, 66 * k), fill=spot)
    d.line([(128 * k, 34 * k), (142 * k, 64 * k)], fill=TOK["n600"] + (255,), width=4 * k)   # tail
    d.rounded_rectangle((0, 10 * k, 36 * k, 50 * k), 12 * k, fill=body)                       # head
    d.rounded_rectangle((0, 32 * k, 26 * k, 52 * k), 8 * k, fill=nose)                        # muzzle
    d.ellipse((10 * k, 18 * k, 17 * k, 25 * k), fill=C["ink_deep"] + (255,))                  # eye (staring)
    d.ellipse((24 * k, 4 * k, 44 * k, 16 * k), fill=spot)                                      # ear
    d.polygon([(8 * k, 10 * k), (2 * k, 0), (14 * k, 8 * k)], fill=C["muted"] + (255,))       # horn
    return im if facing == "left" else ImageOps.mirror(im)


def make_music():
    sy = Synth(14)
    put = sy.put
    n = int(DUR * SR)
    m = np.zeros(n)
    # dusk: slow open chords and crickets
    for f in (220.0, 329.63, 440.0, 554.37):
        put(m, sy.tone(f, T_CUT, 0.05, a=0.3, r=0.4, nh=8, tilt=1.4), 0.0)
    put(m, sy.bell(880.0, 0.14), 0.02)
    rng = np.random.default_rng(5)
    for tc in np.arange(0.9, T_CUT, 0.3):
        for p in range(3):
            n2 = int(0.018 * SR)
            tt = np.arange(n2) / SR
            put(m, 0.03 * np.sin(2 * np.pi * 4300 * tt) * np.sin(np.pi * tt / tt[-1]), tc + p * 0.04 + rng.uniform(0, 0.02))
    # each sign: a whoosh and a two-note "nope", a bit lower each time
    for i, s_ in enumerate(SIGNS[1:], 1):
        put(m, sy.whoosh(0.5, 0.18), s_[0] - 0.28)
        f0 = 523.25 * 2 ** (-i / 12)
        put(m, sy.pluck(f0, 0.4, 0.22, decay=0.99), s_[0])
        put(m, sy.pluck(f0 * 2 ** (-5 / 12), 0.5, 0.22, decay=0.99), s_[0] + 0.14)
    put(m, sy.tick(0.2, 990.0), SIGNS[0][0] + 0.02)
    # morning: birds, a cowbell, and a bright little tune
    for k, tb in enumerate(np.arange(T_CUT + 0.3, DUR - 0.6, 0.37)):
        n2 = int(0.09 * SR)
        tt = np.arange(n2) / SR
        f = 2600 + 900 * np.sin(np.pi * tt / tt[-1]) + rng.uniform(-200, 200)
        put(m, 0.05 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * tt / tt[-1]), tb + rng.uniform(0, 0.1))
    for tb in (T_REV + 0.3, T_REV + 0.9, T_PUNCH + 0.6):
        put(m, sy.bell(587.33 * 1.5, 0.22, 0.6), tb)      # cowbell-ish clonk
        put(m, sy.bell(587.33 * 2.1, 0.12, 0.5), tb)
    t, k = T_REV, 0
    prog = [(392.0, 493.88, 587.33), (440.0, 523.25, 659.25), (349.23, 440.0, 523.25), (392.0, 493.88, 587.33)]
    while t < DUR - 0.6:
        for j, f in enumerate(prog[(k // 2) % 4]):
            put(m, sy.pluck(f, 0.45, 0.12, decay=0.993), t + j * 0.012)
        t += 0.45
        k += 1
    return sy.master(m, reverb=0.25, fade=0.5, sub=0.4)


def main():
    os.makedirs(OUT, exist_ok=True)
    tmp = os.path.join(OUT, "_tmp")
    os.makedirs(tmp, exist_ok=True)
    bg = make_background().convert("RGBA")
    static = make_static(HEADER, LABEL)
    title_im, title_bottom, title_size = text_block(TITLE, 100, 860, 80, 318)
    punch_im, punch_bottom, punch_size = text_block(PUNCH, 112, 860, 80, 318)
    cta_im, cta_bottom = make_cta(CTA, punch_bottom + 46)
    sig_im, _ = make_signature(1296)
    assert title_bottom <= R_TOP_A and cta_bottom <= R_TOP_B, (title_bottom, cta_bottom)

    road = Road(DUR, speed, SKY, sun=sun, moon=(800, 110, 40))
    van = van_art()
    signs_art = [sign_art(a, b, c, big_size=88) for _, a, b, c in SIGNS]
    sign_x = [road.X(s[0]) + (READ_X - VX) for s in SIGNS]
    x_end = road.X(DUR)
    cows = [  # (world x offset from the van centre, ground offset (world, + = in front), facing, scale)
        (-560, -60, "right", 1.0), (-330, -66, "right", 1.05), (330, -62, "left", 1.0), (560, -58, "left", 0.95),
        (-470, 76, "right", 1.25), (-250, 86, "right", 1.15), (470, 80, "left", 1.25),
    ]
    cow_l, cow_r = cow_art("left"), cow_art("right")
    sig_pairs = list(zip(sign_x, signs_art))

    def cows_layer(front):
        def fn(scene, d, ctx):
            if ctx["t"] < T_CUT:
                return
            a = clamp((ctx["t"] - T_CUT) / 0.3)
            s = ctx["s"]
            for ox, gy_off, facing, k in cows:
                if (gy_off > 0) != front:
                    continue
                art = cow_l if facing == "left" else cow_r
                w, h = 150 * k * s, 104 * k * s
                x = ctx["vx"] + (x_end - ctx["X"] + VAN_W / 2 + ox) * s
                y = ctx["gy"] + gy_off * s - h + (0 if front else -10 * s)
                im = darken(scaled(("cow", facing, round(w)), art, w, h), ctx["dark"])
                paste(scene, faded(im, a), x - w / 2, y)
        return fn

    enc = Encoder(os.path.join(tmp, "video.mp4"))
    nframes = int(round(DUR * FPS))
    for fi in range(nframes):
        t = fi / FPS
        e = smooth((t - T_REV) / REV_D) if t >= T_REV else 0.0
        s = (SB ** e) * (1 - 0.02 * smooth((t - T_REV - REV_D) / 3))
        vcx = lerp(VX + VAN_W / 2, 540, e)
        gy = lerp(GY_A, GY_B, e)
        top = lerp(R_TOP_A, R_TOP_B, e)
        signs = sig_pairs if t < T_CUT else []
        scene, _ = road.draw(t, s, vcx - VAN_W / 2 * s, gy, top, van, signs=signs,
                             behind_van=cows_layer(False), front_of_van=cows_layer(True))
        scene.putalpha(Image.fromarray(np.minimum(np.asarray(scene.getchannel("A")), np.asarray(band_mask(top, R_BOT)))))
        frame = bg.copy()
        frame.alpha_composite(scene)
        frame.alpha_composite(static)
        dip = 1 - abs(t - T_CUT) / 0.22
        if dip > 0:   # quick dip to black: the night passes
            frame.alpha_composite(Image.new("RGBA", (W, H), C["bg"] + (int(255 * smooth(dip)),)))
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
    times = [0.03, 0.45, 0.85, 1.25, 1.7, 2.1, 2.55, 3.0, 3.4, 3.8, 4.25, 4.7, 5.0, 5.3, 5.8, 6.6, 7.6, 9.2]
    contact_sheet(mp4, times, os.path.join(OUT, "contact_sheet.png"), tmp)
    qc = {"probe": probe(mp4), "audio": audio_report(mp4), "title_px": title_size, "punch_px": punch_size,
          "title_bottom": title_bottom, "punch_bottom": punch_bottom, "cta_bottom": cta_bottom,
          "timeline": {"signs": [s[0] for s in SIGNS], "stop": T_STOP, "cut": T_CUT, "reveal": [T_REV, T_REV + REV_D],
                       "punch": T_PUNCH, "cta": T_CTA, "signature": T_SIG, "end": DUR}}
    json.dump(qc, open(os.path.join(OUT, "qc.json"), "w"), indent=1)
    print(json.dumps(qc))


if __name__ == "__main__":
    main()
