"""Eazy88 POV clip (van series) — "The backpacker who sold you the van said 'never had a problem'."

Format: POV humour, no voiceover, ~9 s. The orange van loses a hubcap, backfires, drops its bumper,
loses its door, steams, and finally its wheel overtakes it. Drawn in code, brand tokens, procedural music.

Usage (from the repository root):
  python3 -I drafts/2026-11-23_NeverHadAProblemPOV/render_neverhadaproblem_pov.py <out_dir>
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
from van_kit import RS, VAN_W, Road, day_sun, paste, van_art, wheel_art  # noqa: E402

BASE = "Eazy88_TikTok_NeverHadAProblemPOV"
OUT = sys.argv[1]

HEADER = "EAZY88 · BACKPACKER LIFE"
LABEL = "Illustration"
TITLE = ["POV: THE BACKPACKER WHO", "SOLD YOU THE VAN SAID", "*'NEVER HAD A PROBLEM.'*"]
PUNCH = ["DAY 1 OF THE ROAD TRIP:", "*'NEVER HAD A PROBLEM.'*"]
CTA = ["SEND THIS TO THE MATE", "*BUYING A VAN*"]

# ---- timeline (seconds)
T_HUB, T_SMOKE, T_BUMP, T_DOOR, T_STEAM, T_WHEEL = 0.45, 1.1, 1.75, 2.45, 3.15, 3.85
T_STOPPED = 4.45
T_REV, REV_D = 4.7, 0.8
T_PUNCH = 5.2
T_CTA = 6.4
T_SIG = 7.0
DUR = 8.8

SA = 1.8                                 # close-up: the van is big, so every part that falls off reads
VCX_A = 540
GY_A, GY_B = 1290, 1236
SB = 0.55
R_TOP_A, R_TOP_B, R_BOT = 660, 812, 1380
VMAX = 700.0
FRONT_WHEEL, REAR_WHEEL = 262, 78        # wheel centres, world x from the van's rear (van faces right)


def speed(t):
    v = VMAX * smooth(0.6 + t / 0.5)
    if t > T_WHEEL:
        v *= 1 - smooth((t - T_WHEEL) / (T_STOPPED - T_WHEEL))
    return v


def state(t):
    return dict(hubcaps=(True, t < T_HUB), bumpers=(t < T_BUMP, True), door=t < T_DOOR, wheels=(t < T_WHEEL, True))


def door_art():
    w, h = 88, 92
    im = Image.new("RGBA", (w * RS, h * RS), (0, 0, 0, 0))
    d = ImageDraw.Draw(im, "RGBA")
    d.rounded_rectangle((0, 0, w * RS, h * RS), 8 * RS, fill=C["orange"] + (255,))
    d.rounded_rectangle((6 * RS, 4 * RS, (w - 6) * RS, 48 * RS), 8 * RS, fill=C["bg"] + (255,))
    d.rectangle((0, 54 * RS, w * RS, 62 * RS), fill=C["cream"] + (255,))
    return im


def bumper_art():
    im = Image.new("RGBA", (48 * RS, 12 * RS), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, 48 * RS - 1, 12 * RS - 1), 4 * RS, fill=TOK["n600"] + (255,))
    return im


def hubcap_art():
    im = Image.new("RGBA", (24 * RS, 24 * RS), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((0, 0, 24 * RS - 1, 24 * RS - 1), fill=C["cream"] + (255,))
    d.rectangle((10 * RS, 2 * RS, 14 * RS, 22 * RS), fill=C["muted"] + (255,))
    return im


def puff(d, x, y, r, col, a):
    if a > 0 and r > 0:
        d.ellipse((x - r, y - r, x + r, y + r), fill=col + (int(255 * a),))


def make_music():
    sy = Synth(31)
    put = sy.put
    n = int(DUR * SR)
    m = np.zeros(n)
    beat = 0.5
    prog = [((293.66, 369.99, 440.0, 587.33), 146.83), ((277.18, 329.63, 440.0, 554.37), 110.0),
            ((293.66, 369.99, 493.88, 587.33), 123.47), ((293.66, 392.0, 493.88, 587.33), 98.0)]
    t, k = 0.0, 0
    while t < T_WHEEL + 0.3:     # happy road-trip strum, until the wheel goes
        ch, root = prog[(k // 2) % 4]
        for j, f in enumerate(ch):
            put(m, sy.pluck(f, 0.6, 0.15, decay=0.994), t + j * 0.014)
        put(m, sy.pluck(root * 2, 0.5, 0.18, decay=0.99), t)
        put(m, sy.kick(0.12), t)
        if k % 2:
            put(m, sy.clap(0.13), t)
        t += beat
        k += 1
    put(m, sy.bell(1174.66, 0.12), 0.02)
    put(m, sy.bell(1567.98, 0.25, 0.8), T_HUB)                          # hubcap: ting
    for q in range(5):
        put(m, sy.tick(0.08, 1800.0), T_HUB + 0.1 + q * 0.09)
    put(m, sy.snare(0.9), T_SMOKE)                                      # backfire: bang
    put(m, sy.timp(110.0, 0.45, 0.5, decay=9), T_SMOKE)
    put(m, sy.bell(392.0 * 1.07, 0.3, 0.8), T_BUMP)                     # bumper: clang, then a scrape
    put(m, sy.whoosh(0.6, 0.14, peak=0.3), T_BUMP + 0.05)
    put(m, sy.timp(147.0, 0.4, 0.5, decay=9), T_DOOR)                   # door: clunk
    put(m, sy.tick(0.3, 700.0), T_DOOR)
    put(m, sy.whoosh(1.4, 0.09, peak=0.2), T_STEAM)                     # steam: hiss
    put(m, sy.tone(330.0, 0.3, 0.2, a=0.005, r=0.15, nh=8, tilt=1.2, detune=(0,), glide=(880.0, 0.0), vib=0.04,
                   vib_rate=14, vib_delay=0.0), T_WHEEL)                # wheel: boing
    put(m, sy.bell(330.0 * 1.06, 0.3, 0.9), T_WHEEL + 0.05)
    put(m, sy.whoosh(0.6, 0.16, peak=0.2), T_WHEEL + 0.1)               # scrape to a stop
    t0 = T_REV + 0.05                                                   # two sad trombone notes
    put(m, sy.tone(233.08, 0.32, 0.2, a=0.03, r=0.12, nh=20, tilt=0.85, detune=(-3, 3), wah=(350, 1600)), t0)
    put(m, sy.tone(207.65, 0.9, 0.2, a=0.03, r=0.3, nh=20, tilt=0.85, detune=(-3, 3), wah=(350, 1300), vib=0.025,
                   vib_rate=6.0, vib_delay=0.2), t0 + 0.42)
    t, k = T_PUNCH + 0.6, 0
    while t < DUR - 0.2:   # light strum under the call to action, to the last frame
        ch, root = prog[(k // 2) % 4]
        for j, f in enumerate(ch):
            put(m, sy.pluck(f, 0.6, 0.11, decay=0.994), t + j * 0.014)
        t += beat
        k += 1
    put(m, sy.bell(1174.66, 0.1, 1.0), DUR - 0.9)
    return sy.master(m, reverb=0.22, fade=0.35, sub=0.35)


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

    road = Road(DUR, speed, [(0.0, C["sun"], C["cream"], 0.0), (DUR, C["sun"], C["cream"], 0.0)],
                sun=lambda t, top, hz: day_sun(t, top, hz, x=860, y_off=110))
    vans = {}
    door, bumper, hubcap, wheel = door_art(), bumper_art(), hubcap_art(), wheel_art(cap=True)
    xh, xb, xd, xw = (road.X(T_HUB) + FRONT_WHEEL, road.X(T_BUMP + 0.6) + 300, road.X(T_DOOR) + 100,
                      road.X(T_WHEEL) + REAR_WHEEL)

    def behind(scene, d, ctx):
        t, s, X, gy, vx = ctx["t"], ctx["s"], ctx["X"], ctx["gy"], ctx["vx"]
        sx = lambda wx: vx + (wx - X) * s  # noqa: E731
        if t >= T_HUB:   # hubcap rolls on, slows down and falls flat
            dt = t - T_HUB
            wx = xh + 700 * (1 - math.exp(-1.6 * dt)) / 1.6
            hop = 22 * abs(math.sin(dt * 9)) * math.exp(-dt * 3)
            r = 24 * s
            im = scaled(("hub", round(r)), hubcap, r, r).rotate(-dt * 900 if dt < 1.2 else 0, resample=Image.BICUBIC)
            paste(scene, im, sx(wx) - r / 2, gy - r - hop * s + 4 * s)
        if T_SMOKE <= t < T_SMOKE + 1.6:   # backfire smoke, left behind in the world
            x0 = road.X(T_SMOKE)
            for i in range(5):
                dt = t - T_SMOKE - i * 0.05
                if dt > 0:
                    a = 0.75 * (1 - dt / 1.5)
                    puff(d, sx(x0 - 10 - i * 16), gy - 50 * s - dt * 30 * s - i * 6 * s, (18 + dt * 40 + i * 4) * s,
                         TOK["n600"], a)
        if t >= T_BUMP:   # rear bumper: drags with sparks, then stays behind
            dt = t - T_BUMP
            if dt < 0.6:
                bx, ang = vx - 30 * s, -8
                for i in range(6):
                    ph = (t * 40 + i * 1.7) % 1
                    x1, y1 = bx + (10 - 40 * ph) * s, gy - 4 * s
                    d.line([(x1, y1), (x1 - 14 * s, y1 - (6 + 10 * ph) * s)], fill=C["sun"] + (220,), width=max(1, int(3 * s)))
            else:
                bx, ang = sx(xb - 340), -4
            im = scaled(("bump", round(48 * s)), bumper, 48 * s, 12 * s).rotate(ang, expand=True, resample=Image.BICUBIC)
            paste(scene, im, bx, gy - 18 * s)
        if t >= T_DOOR:   # side door falls flat on the road and stays there
            dt = t - T_DOOR
            fall = smooth(dt / 0.35)
            wx = xd + 60 * fall
            ang = -90 * fall
            im = scaled(("door", round(88 * s)), door, 88 * s, 92 * s).rotate(ang, expand=True, resample=Image.BICUBIC)
            top_y = lerp(gy - 140 * s, gy - im.height - 2 * s, fall)
            paste(scene, im, sx(wx) - im.width / 2, top_y)

    def front(scene, d, ctx):
        t, s, X, gy, vx = ctx["t"], ctx["s"], ctx["X"], ctx["gy"], ctx["vx"]
        sx = lambda wx: vx + (wx - X) * s  # noqa: E731
        if t >= T_STEAM:   # steam from the bonnet
            for i in range(14):
                ph = ((t - T_STEAM) * 1.3 + i / 14) % 1
                if t - T_STEAM < i / 14 / 1.3:
                    continue
                puff(d, vx + (330 + 30 * ph) * s, ctx["van_y"] + (40 - 120 * ph) * s, (10 + 26 * ph) * s,
                     C["cream"], 0.55 * (1 - ph))
        if t >= T_WHEEL:   # the rear wheel overtakes the van and rolls on
            dt = t - T_WHEEL
            wx = xw + 620 * dt + 260 * dt * dt
            hop = 30 * abs(math.sin(dt * 7)) * math.exp(-dt * 1.2)
            r = 60 * s
            im = scaled(("wheel", round(r)), wheel, r, r).rotate(-dt * 1100, resample=Image.BICUBIC)
            paste(scene, im, sx(wx) - r / 2, gy - r - hop * s + 8 * s)
            if dt < 0.7:   # sparks under the dropped corner
                for i in range(7):
                    ph = (t * 37 + i * 1.3) % 1
                    x1, y1 = vx + (6 - 30 * ph) * s, gy - 2 * s
                    d.line([(x1, y1), (x1 - 16 * s, y1 - (8 + 12 * ph) * s)], fill=C["sun"] + (230,), width=max(1, int(3 * s)))

    enc = Encoder(os.path.join(tmp, "video.mp4"))
    nframes = int(round(DUR * FPS))
    for fi in range(nframes):
        t = fi / FPS
        st = state(t)
        key = tuple(sorted((k, v if not isinstance(v, tuple) else tuple(v)) for k, v in st.items()))
        if key not in vans:
            vans[key] = van_art(**st)
        e = smooth((t - T_REV) / REV_D) if t >= T_REV else 0.0
        s = SA * ((SB / SA) ** e) * (1 - 0.02 * smooth((t - T_REV - REV_D) / 3))
        vcx = lerp(VCX_A, 600, e)
        gy = lerp(GY_A, GY_B, e)
        top = lerp(R_TOP_A, R_TOP_B, e)
        tilt = 4.5 * smooth((t - T_WHEEL) / 0.25) if t >= T_WHEEL else 0.0
        scene, _ = road.draw(t, s, vcx - VAN_W / 2 * s, gy, top, vans[key], behind_van=behind, front_of_van=front,
                             van_angle=tilt, van_dy=tilt * 3 * s)
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
    times = [0.03, 0.45, 0.8, 1.15, 1.5, 1.85, 2.2, 2.55, 2.9, 3.3, 3.9, 4.15, 4.5, 4.9, 5.4, 6.2, 7.2, 8.6]
    contact_sheet(mp4, times, os.path.join(OUT, "contact_sheet.png"), tmp)
    qc = {"probe": probe(mp4), "audio": audio_report(mp4), "title_px": title_size, "punch_px": punch_size,
          "title_bottom": title_bottom, "punch_bottom": punch_bottom, "cta_bottom": cta_bottom,
          "timeline": {"hubcap": T_HUB, "smoke": T_SMOKE, "bumper": T_BUMP, "door": T_DOOR, "steam": T_STEAM,
                       "wheel": T_WHEEL, "reveal": [T_REV, T_REV + REV_D], "punch": T_PUNCH, "cta": T_CTA,
                       "signature": T_SIG, "end": DUR}}
    json.dump(qc, open(os.path.join(OUT, "qc.json"), "w"), indent=1)
    print(json.dumps(qc))


if __name__ == "__main__":
    main()
