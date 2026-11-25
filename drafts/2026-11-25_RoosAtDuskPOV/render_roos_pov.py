"""Eazy88 POV clip (van series) — "You're driving the outback at dusk." One roo, then two, then the whole mob.

Format: POV humour, no voiceover, ~8.8 s. Orange van and kangaroos drawn in code, brand tokens, procedural music.
Usage (from the repository root):
  python3 -I drafts/2026-11-25_RoosAtDuskPOV/render_roos_pov.py <out_dir>
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "templates", "tools"))
from pov_kit import (C, FPS, H, SR, TOK, W, Encoder, Synth, audio_report, band_mask, clamp, comp,  # noqa: E402
                     contact_sheet, faded, finish, lerp, make_background, make_cta, make_signature, make_static,
                     probe, scaled, smooth, text_block)
from van_kit import VAN_W, Road, col_mix, darken, paste, roo_art, van_art  # noqa: E402

BASE = "Eazy88_TikTok_RoosAtDuskPOV"
OUT = sys.argv[1]
HEADER = "EAZY88 · BACKPACKER LIFE"
LABEL = "Illustration"
TITLE = ["POV: YOU'RE DRIVING", "THROUGH THE OUTBACK", "*AT DUSK.*"]
PUNCH = ["ETA: WHENEVER", "*THE ROOS SAY.*"]
CTA = ["SEND THIS TO THE MATE", "WHO *DRIVES AT DUSK*"]

T_STOP = 2.9
T_ROOF = 3.5            # one jumps on the roof
T_REV, REV_D = 4.2, 0.8
T_PUNCH = 4.7
T_CTA = 6.0
T_SIG = 6.6
DUR = 8.5
SA, SB = 1.35, 0.62
VCX_A, VCX_B = 470, 540
GY_A, GY_B = 1290, 1236
R_TOP_A, R_TOP_B, R_BOT = 660, 812, 1380
VMAX = 600.0

# kangaroos: (appear time, world x ahead of the van at that moment, ground offset (+ in front), facing, scale)
ROOS = [(0.35, 540, -58, "left", 0.95), (1.0, 500, 64, "left", 1.0), (1.5, 470, 70, "left", 1.05),
        (1.5, 640, -60, "left", 0.9), (2.0, 420, -62, "left", 0.95), (2.0, 560, 76, "left", 1.1),
        (2.0, 700, -66, "right", 0.9), (2.5, 380, 72, "left", 1.0), (2.5, 620, -58, "left", 0.85),
        (2.5, 760, 68, "left", 1.0), (2.8, 470, 84, "right", 1.1)]
EXTRA = [(-260, -60, "right", 0.9), (-140, 74, "right", 1.05), (-380, 70, "right", 0.95), (1080, -62, "left", 0.9),
         (1150, 74, "left", 1.0), (-470, -64, "right", 0.85)]   # revealed by the zoom-out


def speed(t):
    if t >= T_STOP:
        return 0.0
    return VMAX * (1 - smooth((t - 1.1) / (T_STOP - 1.1)))


SKY = [(0.0, TOK["primary_dark"], C["sunset"], 0.0), (3.0, TOK["primary_dark"], C["primary"], 0.12),
       (DUR, TOK["n800"], TOK["primary_dark"], 0.2)]


def sun(t, top, hz):
    e = smooth(t / 3.5)
    return 820, lerp(hz - 30, hz + 40, e), 62, col_mix(C["sunset"], C["primary"], e)


def make_music():
    sy = Synth(5)
    put = sy.put
    n = int(DUR * SR)
    m = np.zeros(n)
    for f in (220.0, 277.18, 329.63, 440.0):
        put(m, sy.tone(f, DUR, 0.045, a=0.4, r=0.4, nh=8, tilt=1.4), 0.0)
    put(m, sy.bell(880.0, 0.14), 0.02)
    t, k = 0.0, 0
    riff = [440.0, 523.25, 587.33, 659.25]
    while t < T_STOP:
        put(m, sy.pluck(riff[k % 4], 0.4, 0.12, decay=0.99), t)
        t += 0.3
        k += 1
    # each new kangaroo: a cartoon "boing", higher each time
    seen = sorted(set(r[0] for r in ROOS))
    for i, ta in enumerate(seen):
        cnt = sum(1 for r in ROOS if r[0] == ta)
        for j in range(cnt):
            f0 = 300 * 2 ** ((i * 2 + j) / 12)
            put(m, sy.tone(f0, 0.22, 0.16, a=0.005, r=0.12, nh=8, tilt=1.2, detune=(0,), glide=(f0 * 2.4, 0.0)),
                ta + j * 0.07)
    put(m, sy.tone(1500.0, 0.35, 0.06, a=0.01, r=0.1, nh=4, tilt=1.5, detune=(0,), glide=(900.0, 0.0)), T_STOP - 0.4)  # brakes
    put(m, sy.tone(330.0, 0.22, 0.2, a=0.005, r=0.12, nh=8, tilt=1.2, detune=(0,), glide=(990.0, 0.0)), T_ROOF)
    put(m, sy.timp(196.0, 0.4, 0.5, decay=9), T_ROOF + 0.18)
    rng = np.random.default_rng(3)
    for tc in np.arange(3.0, DUR - 0.2, 0.31):   # crickets
        for p in range(3):
            n2 = int(0.018 * SR)
            tt = np.arange(n2) / SR
            put(m, 0.03 * np.sin(2 * np.pi * 4300 * tt) * np.sin(np.pi * tt / tt[-1]), tc + p * 0.04 + rng.uniform(0, 0.02))
    for f in (220.0, 329.63, 440.0, 554.37):
        put(m, sy.tone(f, 1.2, 0.09, a=0.02, r=0.9, nh=14, tilt=1.0, detune=(-4, 4), bright=5), T_REV)
    t, k = T_PUNCH + 0.4, 0
    while t < DUR - 0.2:
        put(m, sy.pluck(riff[k % 4], 0.4, 0.1, decay=0.99), t)
        t += 0.3
        k += 1
    return sy.master(m, reverb=0.25, fade=0.35, sub=0.4)


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
    road = Road(DUR, speed, SKY, sun=sun, moon=None)
    van = van_art()
    x_stop = road.X(DUR)
    tan = dict(body=C["muted"], belly=C["cream"])      # light coat: stands out on red earth at dusk
    roo_l, roo_r = roo_art(facing="left", **tan), roo_art(facing="right", **tan)

    def roos(front):
        def fn(scene, d, ctx):
            t, s = ctx["t"], ctx["s"]
            items = [(a, road.X(a) + rel, gy_off, f, k) for a, rel, gy_off, f, k in ROOS]
            if t >= T_REV:
                items += [(T_REV, x_stop + ox, gy_off, f, k) for ox, gy_off, f, k in EXTRA]
            for a, wx, gy_off, facing, k in items:
                if t < a or (gy_off > 0) != front:
                    continue
                dt = t - a
                hop = 30 * abs(math.sin(dt * 7 + wx)) * (1 if dt < 0.9 or t > T_REV else 0.15)
                w, h = 110 * k * s, 150 * k * s
                x = ctx["vx"] + (wx - ctx["X"]) * s
                y = ctx["gy"] + gy_off * s - h - hop * s
                im = darken(scaled(("roo", facing, round(w)), roo_l if facing == "left" else roo_r, w, h), ctx["dark"])
                paste(scene, faded(im, clamp(dt * 5)), x - w / 2, y)
            if front and t >= T_ROOF:   # the one that sits on the roof
                dt = t - T_ROOF
                fall = smooth(dt / 0.3)
                w, h = 100 * s, 136 * s
                x = ctx["vx"] + 200 * s
                y = lerp(ctx["van_y"] - 260 * s, ctx["van_y"] + 10 * s - h, fall)
                im = darken(scaled(("roo", "left", round(w)), roo_l, w, h), ctx["dark"])
                paste(scene, im, x - w / 2, y)
        return fn

    enc = Encoder(os.path.join(tmp, "video.mp4"))
    nframes = int(round(DUR * FPS))
    for fi in range(nframes):
        t = fi / FPS
        e = smooth((t - T_REV) / REV_D) if t >= T_REV else 0.0
        s = SA * ((SB / SA) ** e)
        vcx = lerp(VCX_A, VCX_B, e)
        gy = lerp(GY_A, GY_B, e)
        top = lerp(R_TOP_A, R_TOP_B, e)
        scene, _ = road.draw(t, s, vcx - VAN_W / 2 * s, gy, top, van, behind_van=roos(False), front_of_van=roos(True))
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
    times = [0.03, 0.4, 0.7, 1.05, 1.3, 1.6, 2.05, 2.3, 2.6, 2.9, 3.6, 4.0, 4.5, 5.0, 5.8, 6.4, 7.3, 8.3]
    contact_sheet(mp4, times, os.path.join(OUT, "contact_sheet.png"), tmp)
    qc = {"probe": probe(mp4), "audio": audio_report(mp4), "title_px": title_size, "punch_px": punch_size,
          "title_bottom": title_bottom, "punch_bottom": punch_bottom, "cta_bottom": cta_bottom,
          "timeline": {"roos": sorted(set(r[0] for r in ROOS)), "stop": T_STOP, "roof": T_ROOF,
                       "reveal": [T_REV, T_REV + REV_D], "punch": T_PUNCH, "cta": T_CTA, "signature": T_SIG, "end": DUR}}
    json.dump(qc, open(os.path.join(OUT, "qc.json"), "w"), indent=1)
    print(json.dumps(qc))


if __name__ == "__main__":
    main()
