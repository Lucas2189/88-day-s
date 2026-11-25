"""Eazy88 POV clip (van series) — "You drove your 2WD van onto the beach for the sunset." It sinks.

Format: POV humour, no voiceover, ~8.6 s. Orange van, beach and signs drawn in code, brand tokens,
procedural music. The signs are a joke, not a real beach or rule.
Usage (from the repository root):
  python3 -I drafts/2026-11-25_BeachSinkPOV/render_beach_pov.py <out_dir>
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "templates", "tools"))
from pov_kit import (C, FPS, H, SR, TOK, W, Encoder, Synth, audio_report, band_mask, clamp, comp,  # noqa: E402
                     contact_sheet, faded, finish, lerp, make_background, make_cta, make_signature, make_static,
                     probe, scaled, smooth, text_block)
from van_kit import RS, VAN_W, Road, col_mix, paste, sign_art, van_art  # noqa: E402

BASE = "Eazy88_TikTok_BeachSinkPOV"
OUT = sys.argv[1]
HEADER = "EAZY88 · BACKPACKER LIFE"
LABEL = "Illustration · not a real beach"
TITLE = ["POV: YOU DROVE YOUR 2WD", "VAN ONTO THE BEACH", "*FOR THE SUNSET.*"]
PUNCH = ["THE SIGN DID SAY", "*'4WD ONLY'.*"]
CTA = ["SEND THIS TO THE MATE", "WHO *NEVER READS SIGNS*"]

SINK = [(0.0, 0), (0.9, 0), (1.5, 30), (2.2, 62), (2.9, 92), (3.6, 112), (4.6, 118)]   # (t, depth in world units)
T_GULL = 3.7
T_REV, REV_D = 4.3, 0.8
T_PUNCH = 4.8
T_CTA = 6.0
T_SIG = 6.6
DUR = 8.6
SA, SB = 1.5, 0.7
VCX_A, VCX_B = 620, 640
GY_A, GY_B = 1290, 1236
R_TOP_A, R_TOP_B, R_BOT = 660, 812, 1380
VMAX = 420.0


def speed(t):
    return VMAX * (1 - smooth(t / 1.0))


def depth(t):
    return float(np.interp(t, [a for a, _ in SINK], [b for _, b in SINK]))


SKY = [(0.0, TOK["primary_dark"], C["sunset"], 0.0), (DUR, TOK["n800"], C["primary"], 0.05)]


def sun(t, top, hz):
    e = smooth(t / DUR)
    return 790, lerp(hz - 70, hz - 20, e), 64, col_mix(C["sun"], C["sunset"], e)


def gull_art():
    w, h = 90, 60
    im = Image.new("RGBA", (w * RS, h * RS), (0, 0, 0, 0))
    d = ImageDraw.Draw(im, "RGBA")
    k = RS
    d.ellipse((18 * k, 22 * k, 70 * k, 50 * k), fill=C["cream"] + (255,))             # body
    d.ellipse((56 * k, 12 * k, 80 * k, 34 * k), fill=C["cream"] + (255,))             # head
    d.polygon([(78 * k, 22 * k), (90 * k, 26 * k), (78 * k, 29 * k)], fill=C["orange"] + (255,))   # beak
    d.ellipse((68 * k, 18 * k, 72 * k, 22 * k), fill=C["ink_deep"] + (255,))           # eye
    d.polygon([(26 * k, 28 * k), (52 * k, 30 * k), (34 * k, 44 * k)], fill=TOK["n600"] + (255,))   # wing
    for lx in (38, 48):
        d.line([(lx * k, 50 * k), (lx * k, 60 * k)], fill=C["orange"] + (255,), width=3 * k)
    return im


def make_music():
    sy = Synth(12)
    put = sy.put
    n = int(DUR * SR)
    m = np.zeros(n)
    prog = [((392.0, 493.88, 587.33), 196.0), ((440.0, 523.25, 659.25), 220.0),
            ((349.23, 440.0, 523.25), 174.61), ((392.0, 493.88, 587.33), 196.0)]
    t, k = 0.0, 0
    while t < 1.3:   # carefree sunset strum... until the wheels start spinning
        ch, root = prog[(k // 2) % 4]
        for j, f in enumerate(ch):
            put(m, sy.pluck(f, 0.5, 0.13, decay=0.993), t + j * 0.012)
        put(m, sy.pluck(root, 0.4, 0.14, decay=0.99), t)
        t += 0.45
        k += 1
    put(m, sy.bell(1174.66, 0.12), 0.02)
    # engine revving and sand spraying while it digs in
    tt = np.arange(n) / SR
    rev = np.zeros(n)
    for a, b in ((1.0, 1.6), (1.8, 2.5), (2.7, 3.4)):
        sel = (tt >= a) & (tt < b)
        f = 170 + 140 * np.clip((tt - a) / (b - a), 0, 1)
        ph = 2 * np.pi * np.cumsum(f) / SR
        saw = 2 * ((ph / (2 * np.pi)) % 1) - 1
        env = np.sin(np.pi * np.clip((tt - a) / (b - a), 0, 1))
        rev += np.where(sel, 0.08 * saw * env, 0)
        put(m, sy.whoosh(b - a, 0.1, peak=0.4), a)
    m += np.convolve(rev, np.ones(5) / 5, "same")
    # each stage of sinking: a soft "gloop" going down
    for i, (ts, _) in enumerate(SINK[2:6]):
        f0 = 520 * 2 ** (-i * 2 / 12)
        put(m, sy.tone(f0, 0.25, 0.14, a=0.01, r=0.15, nh=6, tilt=1.4, detune=(0,), glide=(f0 * 0.55, 0.0)), ts)
    put(m, sy.tone(2200.0, 0.18, 0.05, a=0.01, r=0.1, nh=3, tilt=1.5, detune=(0,), glide=(1400.0, 0.0)), T_GULL)   # gull
    put(m, sy.tone(2000.0, 0.14, 0.04, a=0.01, r=0.1, nh=3, tilt=1.5, detune=(0,), glide=(1300.0, 0.0)), T_GULL + 0.22)
    t0 = T_REV + 0.05   # two sad trombone notes
    put(m, sy.tone(233.08, 0.32, 0.2, a=0.03, r=0.12, nh=20, tilt=0.85, detune=(-3, 3), wah=(350, 1600)), t0)
    put(m, sy.tone(207.65, 0.9, 0.2, a=0.03, r=0.3, nh=20, tilt=0.85, detune=(-3, 3), wah=(350, 1300), vib=0.025,
                   vib_rate=6.0, vib_delay=0.2), t0 + 0.42)
    t, k = T_PUNCH + 0.6, 0
    while t < DUR - 0.2:
        ch, _ = prog[(k // 2) % 4]
        for j, f in enumerate(ch):
            put(m, sy.pluck(f, 0.5, 0.1, decay=0.993), t + j * 0.012)
        t += 0.45
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
    road = Road(DUR, speed, SKY, sun=sun, moon=None, terrain="beach")
    van = van_art()
    gull = gull_art()
    sign = sign_art("BEACH ACCESS", "4WD ONLY", "y", w=260, h=160, post=110)
    sign_x = road.X(0.0) - 120                  # the van has just driven past it on the first frame
    rng = np.random.default_rng(8)
    grains = rng.uniform(0, 1, (60, 3))

    def sand_front(scene, d, ctx):
        t, s, gy, vx = ctx["t"], ctx["s"], ctx["gy"], ctx["vx"]
        dep = depth(t)
        # sand in front of the van hides whatever has sunk below the beach line
        d.rectangle((0, gy - 2 * s, W, H), fill=C["sun"] + (255,))
        if dep > 0:   # little mounds of dug-up sand on both sides (low, so the van stays visible)
            for cx in (vx - 30 * s, vx + VAN_W * s + 30 * s):
                rr = 60 * s * min(1.0, dep / 60)
                d.ellipse((cx - rr * 1.5, gy - rr * 0.3, cx + rr * 1.5, gy + rr * 0.3), fill=C["sun"] + (255,))
                d.arc((cx - rr * 1.5, gy - rr * 0.3, cx + rr * 1.5, gy + rr * 0.3), 190, 350,
                      fill=C["muted"] + (255,), width=max(1, int(3 * s)))
        if 0.9 <= t < 3.4:   # sand spraying from the rear wheel
            for gx, gy0, ph in grains:
                q = (t * 2.2 + ph) % 1
                x = vx + (60 - 260 * q * gx) * s
                y = gy - (10 + 150 * q * (1 - q) * 4 * gy0) * s
                r = (3 + 4 * gx) * s
                d.ellipse((x - r, y - r, x + r, y + r), fill=C["sunset"] + (int(230 * (1 - q)),))
        if t >= T_GULL:   # a gull lands on what is left of the van
            dt = t - T_GULL
            fall = smooth(dt / 0.35)
            gw, gh = 90 * s, 60 * s
            gx = vx + 200 * s
            gy1 = ctx["van_y"] + 10 * s - gh + 2 * s
            paste(scene, scaled(("gull", round(gw)), gull, gw, gh), gx - gw / 2, lerp(gy1 - 220 * s, gy1, fall))

    enc = Encoder(os.path.join(tmp, "video.mp4"))
    nframes = int(round(DUR * FPS))
    for fi in range(nframes):
        t = fi / FPS
        e = smooth((t - T_REV) / REV_D) if t >= T_REV else 0.0
        s = SA * ((SB / SA) ** e)
        vcx = lerp(VCX_A, VCX_B, e)
        gy = lerp(GY_A, GY_B, e)
        top = lerp(R_TOP_A, R_TOP_B, e)
        dep = depth(t)
        wobble = 1.5 * math.sin(t * 40) if 0.9 <= t < 3.4 else 0.0
        scene, _ = road.draw(t, s, vcx - VAN_W / 2 * s, gy, top, van, signs=[(sign_x, sign)], front_of_van=sand_front,
                             van_dy=dep * s, van_angle=wobble * min(1.0, dep / 40), bounce=0.0, headlights=False)
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
    times = [0.03, 0.5, 0.9, 1.2, 1.5, 1.85, 2.2, 2.55, 2.9, 3.25, 3.6, 4.0, 4.5, 5.0, 5.7, 6.4, 7.4, 8.4]
    contact_sheet(mp4, times, os.path.join(OUT, "contact_sheet.png"), tmp)
    qc = {"probe": probe(mp4), "audio": audio_report(mp4), "title_px": title_size, "punch_px": punch_size,
          "title_bottom": title_bottom, "punch_bottom": punch_bottom, "cta_bottom": cta_bottom,
          "timeline": {"sink": SINK, "gull": T_GULL, "reveal": [T_REV, T_REV + REV_D], "punch": T_PUNCH,
                       "cta": T_CTA, "signature": T_SIG, "end": DUR}}
    json.dump(qc, open(os.path.join(OUT, "qc.json"), "w"), indent=1)
    print(json.dumps(qc))


if __name__ == "__main__":
    main()
