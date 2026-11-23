"""Eazy88 POV clip (van series) — "4 backpackers pack one van for a road trip." Things pile up on the roof.

Format: POV humour, no voiceover, ~9 s. The orange van of the parking and "just down the road" clips,
drawn in code; brand fonts and colour tokens; procedural music (no samples).

Usage (from the repository root):
  python3 -I drafts/2026-11-23_RoofStackPOV/render_roofstack_pov.py <out_dir>
Outputs: <BASE>_A.mp4, <BASE>_Cover.png, contact_sheet.png, qc.json
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
                     contact_sheet, ease_out_cubic, faded, finish, lerp, make_background, make_cta, make_signature,
                     make_static, probe, scaled, smooth, spring, text_block)
from van_kit import RS, VAN_W, Road, darken, day_sun, paste, van_art  # noqa: E402

BASE = "Eazy88_TikTok_RoofStackPOV"
OUT = sys.argv[1]

# ---- public text (English)
HEADER = "EAZY88 · BACKPACKER LIFE"
LABEL = "Illustration"
TITLE = ["POV: 4 BACKPACKERS", "PACK ONE VAN", "*FOR A ROAD TRIP.*"]
PUNCH = ["AND SOMEONE", "STILL FORGOT", "*THE TENT.*"]
CTA = ["SEND THIS TO", "THE MATE WHO", "*ALWAYS OVERPACKS*"]

# ---- timeline (seconds): first drop lands at 0.35 s, a new item every ~0.45 s, the joke items last
LAND = [0.35, 0.80, 1.22, 1.65, 2.05, 2.45, 2.90, 3.45, 4.05]
N_PLAIN = 7
DROP = 0.16
T_REV, REV_D = 4.65, 0.75
T_PUNCH = 5.2
T_DRIVE = 6.0
T_CTA = 6.6
T_SIG = 7.2
DUR = 9.2

# ---- camera
SA, SB = 1.7, 1.08
VCX_A, VCX_B = 540, 705          # screen x of the van centre
GY_A, GY_B = 1290, 1290
CY = 1000                        # screen y kept for the newest item's centre
R_TOP_A, R_TOP_B, R_BOT = 660, 255, 1380
ROOF = 152                       # height of the roof rack top above the road line (world units)


# ---------------------------------------------------------------- items (drawn facing right, world units)
def item(w, h, fn):
    im = Image.new("RGBA", (int(w * RS), int(h * RS)), (0, 0, 0, 0))
    fn(ImageDraw.Draw(im, "RGBA"), w * RS, h * RS, RS)
    return im


def esky(d, w, h, k):
    d.rounded_rectangle((0, h * 0.25, w, h), 10 * k, fill=C["cream"] + (255,))
    d.rounded_rectangle((0, 0, w, h * 0.32), 10 * k, fill=C["green"] + (255,))
    d.rounded_rectangle((w * 0.38, -2, w * 0.62, h * 0.12), 4 * k, fill=TOK["n800"] + (255,))
    d.line([(8 * k, h * 0.62), (w - 8 * k, h * 0.62)], fill=C["muted"] + (255,), width=3 * k)


def mattress(d, w, h, k):
    d.rounded_rectangle((0, 0, w, h), 16 * k, fill=C["cream"] + (255,))
    for i in range(1, 8):
        x = w * i / 8
        d.line([(x, 5 * k), (x, h - 5 * k)], fill=C["muted"] + (255,), width=3 * k)


def surfboard(d, w, h, k):
    d.rounded_rectangle((0, 0, w, h), h / 2, fill=C["sunset"] + (255,))
    d.rectangle((w * 0.2, h * 0.42, w * 0.8, h * 0.58), fill=C["cream"] + (255,))


def bike(d, w, h, k):
    r = h * 0.36
    for cx in (r + 4 * k, w - r - 4 * k):
        d.ellipse((cx - r, h - 2 * r - 2 * k, cx + r, h - 2 * k), outline=TOK["n800"] + (255,), width=7 * k)
    a, b = (r + 4 * k, h - r - 2 * k), (w - r - 4 * k, h - r - 2 * k)
    c, e = (w * 0.45, h - r - 2 * k), (w * 0.62, h * 0.28)
    g = C["green"] + (255,)
    for p, q in ((a, c), (c, e), (a, (w * 0.38, h * 0.3)), ((w * 0.38, h * 0.3), e), (e, b), (c, b)):
        d.line([p, q], fill=g, width=8 * k)
    d.rounded_rectangle((w * 0.3, h * 0.18, w * 0.46, h * 0.27), 4 * k, fill=TOK["n800"] + (255,))
    d.line([(w * 0.66, h * 0.1), (w * 0.72, h * 0.1)], fill=TOK["n800"] + (255,), width=8 * k)


def chairs(d, w, h, k):
    for i in range(2):
        y0 = i * h * 0.5
        d.rounded_rectangle((i * 10 * k, y0, w - (1 - i) * 10 * k, y0 + h * 0.48), 8 * k, fill=C["green"] + (255,))
        d.line([(30 * k, y0 + 5 * k), (w - 30 * k, y0 + h * 0.43)], fill=C["cream"] + (255,), width=4 * k)
        d.line([(30 * k, y0 + h * 0.43), (w - 30 * k, y0 + 5 * k)], fill=C["cream"] + (255,), width=4 * k)


def guitar(d, w, h, k):
    d.ellipse((0, h * 0.08, w * 0.34, h * 0.92), fill=C["sunset"] + (255,))
    d.ellipse((w * 0.22, h * 0.2, w * 0.48, h * 0.8), fill=C["sunset"] + (255,))
    d.ellipse((w * 0.2, h * 0.36, w * 0.3, h * 0.64), fill=C["bg"] + (255,))
    d.rectangle((w * 0.45, h * 0.42, w * 0.9, h * 0.58), fill=TOK["n800"] + (255,))
    d.rounded_rectangle((w * 0.88, h * 0.32, w, h * 0.68), 6 * k, fill=TOK["n800"] + (255,))


def kayak(d, w, h, k):
    d.polygon([(0, h * 0.5), (w * 0.15, 0), (w * 0.85, 0), (w, h * 0.5), (w * 0.85, h), (w * 0.15, h)],
              fill=C["green"] + (255,))
    d.rectangle((w * 0.1, h * 0.42, w * 0.9, h * 0.58), fill=C["cream"] + (255,))
    d.ellipse((w * 0.42, h * 0.12, w * 0.58, h * 0.88), fill=TOK["n800"] + (255,))


def sink(d, w, h, k):
    d.polygon([(0, h * 0.35), (w, h * 0.35), (w * 0.88, h), (w * 0.12, h)], fill=C["muted"] + (255,))
    d.rectangle((0, h * 0.3, w, h * 0.42), fill=C["cream"] + (255,))
    d.ellipse((w * 0.45, h * 0.62, w * 0.55, h * 0.74), fill=TOK["n600"] + (255,))
    d.rectangle((w * 0.66, h * 0.05, w * 0.71, h * 0.32), fill=TOK["n600"] + (255,))
    d.arc((w * 0.5, -h * 0.02, w * 0.71, h * 0.2), 180, 360, fill=TOK["n600"] + (255,), width=6 * k)
    d.rectangle((w * 0.49, h * 0.09, w * 0.53, h * 0.17), fill=TOK["n600"] + (255,))


def roo(d, w, h, k):
    body, belly = TOK["primary_dark"] + (255,), C["sun"] + (255,)
    d.polygon([(w * 0.05, h * 0.98), (w * 0.35, h * 0.86), (w * 0.4, h * 0.95), (w * 0.15, h)], fill=body)    # tail
    d.ellipse((w * 0.25, h * 0.36, w * 0.78, h * 0.98), fill=body)                                              # body
    d.ellipse((w * 0.45, h * 0.5, w * 0.7, h * 0.92), fill=belly)
    d.ellipse((w * 0.5, h * 0.12, w * 0.9, h * 0.42), fill=body)                                                # head
    d.polygon([(w * 0.82, h * 0.24), (w, h * 0.3), (w * 0.84, h * 0.36)], fill=body)                           # snout
    for ex in (0.56, 0.68):                                                                                     # ears
        d.ellipse((w * ex, 0, w * (ex + 0.09), h * 0.22), fill=body)
    d.ellipse((w * 0.72, h * 0.2, w * 0.77, h * 0.25), fill=C["ink_deep"] + (255,))                            # eye
    d.rounded_rectangle((w * 0.62, h * 0.55, w * 0.8, h * 0.6), 4 * k, fill=body)                               # arm
    d.rounded_rectangle((w * 0.45, h * 0.92, w * 0.95, h), 6 * k, fill=body)                                    # foot


ITEMS = [  # (name, w, h, draw, x offset from the van centre, rotation)
    ("esky", 150, 80, esky, 40, 0), ("mattress", 300, 44, mattress, -6, 0), ("surfboard", 340, 24, surfboard, 14, 0),
    ("bike", 230, 120, bike, -18, 0), ("chairs", 170, 40, chairs, 34, 0), ("guitar", 240, 80, guitar, -12, 0),
    ("kayak", 400, 46, kayak, 20, 0), ("sink", 170, 90, sink, 0, 0), ("kangaroo", 110, 150, roo, 4, 0),
]
BOTTOMS = []
_y = ROOF
for _n, _w, _h, _f, _x, _r in ITEMS:
    BOTTOMS.append(_y)
    _y += _h
TOWER_TOP = _y


# ---------------------------------------------------------------- music (procedural, no samples)
def make_music():
    sy = Synth(9)
    put = sy.put
    n = int(DUR * SR)
    m = np.zeros(n)
    beat = 0.45
    prog = [((392.0, 493.88, 587.33), 196.0), ((440.0, 523.25, 659.25), 220.0),
            ((349.23, 440.0, 523.25), 174.61), ((392.0, 493.88, 587.33), 196.0)]
    t, k = 0.0, 0
    while t < T_REV - 0.05:   # bouncy ukulele while they pack
        ch, root = prog[(k // 2) % 4]
        for j, f in enumerate(ch):
            put(m, sy.pluck(f, 0.45, 0.13, decay=0.993), t + j * 0.012)
        put(m, sy.pluck(root, 0.4, 0.16, decay=0.99), t)
        if k % 2:
            put(m, sy.clap(0.12), t)
        t += beat
        k += 1
    put(m, sy.bell(1174.66, 0.14), 0.02)
    for i, tl in enumerate(LAND[:N_PLAIN]):   # each item lands: a soft thud and a note going up
        put(m, sy.timp(196.0, 0.22, 0.35, decay=12), tl)
        put(m, sy.tick(0.16, 990.0), tl)
        put(m, sy.pluck(587.33 * 2 ** (i * 2 / 12), 0.5, 0.22, decay=0.992), tl)
    # the kitchen sink: a metal clang
    put(m, sy.bell(523.25, 0.4, 1.4), LAND[7])
    put(m, sy.bell(784.0 * 1.06, 0.25, 1.2), LAND[7])
    put(m, sy.timp(220.0, 0.4, 0.6, decay=8), LAND[7])
    # the kangaroo: a cartoon "boing" going up
    put(m, sy.tone(330.0, 0.32, 0.22, a=0.005, r=0.15, nh=8, tilt=1.2, detune=(0,), glide=(880.0, 0.0), vib=0.04,
                   vib_rate=14, vib_delay=0.0), LAND[8])
    put(m, sy.timp(196.0, 0.4, 0.6, decay=8), LAND[8])
    # drum roll into the reveal, then a big chord
    t = T_REV - 0.5
    while t < T_REV - 0.02:
        put(m, sy.snare(0.4 * (0.2 + 0.8 * (t - (T_REV - 0.5)) / 0.5)), t)
        t += 0.055
    put(m, sy.cymbal(0.35, 2.2, decay=2.0), T_REV)
    for f in (392.0, 493.88, 587.33, 783.99):
        put(m, sy.tone(f, 1.0, 0.13, a=0.02, r=0.8, nh=16, tilt=0.95, detune=(-4, 4), bright=6), T_REV)
    # drive-off: the ukulele comes back, lighter
    t, k = T_DRIVE - 0.2, 0
    while t < DUR - 0.25:
        ch, root = prog[(k // 2) % 4]
        for j, f in enumerate(ch):
            put(m, sy.pluck(f, 0.45, 0.1, decay=0.993), t + j * 0.012)
        put(m, sy.pluck(root, 0.4, 0.12, decay=0.99), t)
        t += beat
        k += 1
    put(m, sy.bell(1174.66, 0.08, 1.0), DUR - 1.0)
    return sy.master(m, reverb=0.22, fade=0.35, sub=0.4)


# ---------------------------------------------------------------- render
def main():
    os.makedirs(OUT, exist_ok=True)
    tmp = os.path.join(OUT, "_tmp")
    os.makedirs(tmp, exist_ok=True)

    bg = make_background().convert("RGBA")
    static = make_static(HEADER, LABEL)
    title_im, title_bottom, title_size = text_block(TITLE, 100, 860, 80, 318)
    col_w = 400
    punch_im, punch_bottom, punch_size = text_block(PUNCH, 96, col_w, 80, 470)
    cta_im, cta_bottom = make_cta(CTA, punch_bottom + 70, max_w=col_w)
    sig_im, sig_box = make_signature(1296)
    assert title_bottom <= R_TOP_A, title_bottom
    assert cta_bottom <= sig_box[1] - 40, cta_bottom
    card = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle((52, 440, 80 + col_w + 28, cta_bottom + 30), 30, fill=C["bg"] + (226,))
    tower_px = TOWER_TOP * SB
    assert GY_B - tower_px >= R_TOP_B + 40, f"tower top at {GY_B - tower_px}"
    van = van_art()
    arts = [item(w, h, f) for _, w, h, f, _, _ in ITEMS]
    road = Road(DUR, lambda t: 0.0, [(0.0, C["sun"], C["cream"], 0.0), (DUR, C["sun"], C["cream"], 0.0)],
                sun=lambda t, top, hz: day_sun(t, top, hz, x=880, y_off=110))

    enc = Encoder(os.path.join(tmp, "video.mp4"))
    gy, gv, gy_rev0 = float(GY_A), 0.0, None
    nframes = int(round(DUR * FPS))
    for fi in range(nframes):
        t = fi / FPS
        landed = [i for i in range(len(ITEMS)) if t >= LAND[i] - DROP]
        newest = landed[-1] if landed else -1
        if t < T_REV:
            centre = (BOTTOMS[newest] + ITEMS[newest][2] / 2) if newest >= 0 else ROOF
            gy, gv = spring(gy, gv, max(GY_A, CY + centre * SA), 14.0)
            s, vcx, top = SA * (1 + 0.012 * smooth(t / 1.5)), VCX_A, R_TOP_A
            gy_now = gy
        else:
            if gy_rev0 is None:
                gy_rev0 = gy
            e = smooth((t - T_REV) / REV_D)
            s = SA * (SB / SA) ** e
            vcx = lerp(VCX_A, VCX_B, e)
            gy_now = lerp(gy_rev0, GY_B, e)
            top = lerp(R_TOP_A, R_TOP_B, e)
        drive = 0.0
        if t > T_DRIVE:   # off they go, slowly
            dt = t - T_DRIVE
            drive = 100 * dt * dt / 2 if dt < 1.2 else 100 * 0.72 + 120 * (dt - 1.2)
        shake = sum((9 if i >= N_PLAIN else 4) * math.exp(-(t - LAND[i]) * 15) * math.cos((t - LAND[i]) * 55)
                    for i in range(len(ITEMS)) if 0 <= t - LAND[i] < 0.35)
        gys = gy_now + shake
        vx = vcx - VAN_W / 2 * s + drive * s
        sway_amp = 0.0 if t < T_DRIVE else 0.06 * min(1.0, (t - T_DRIVE) / 0.6)

        def stack(scene, d, ctx):
            for i in landed:
                name, w, h, _, xo, rot = ITEMS[i]
                q = (t - (LAND[i] - DROP)) / DROP
                off, a, sq = 0.0, 1.0, 1.0
                if q < 1:
                    off, a = -170 * (1 - q * q), clamp(q * 3)
                else:
                    dt = t - LAND[i]
                    sq = 1 - 0.07 * math.sin(dt * 28) * math.exp(-dt * 10) if dt < 0.5 else 1.0
                frac = (BOTTOMS[i] - ROOF) / (TOWER_TOP - ROOF)
                sway = sway_amp * math.sin((t - T_DRIVE) * 7 - frac * 1.2) * (BOTTOMS[i] - ROOF)
                cx = ctx["vx"] + (VAN_W / 2 + xo + sway) * s
                bottom = ctx["gy"] - (BOTTOMS[i] + off) * s + ctx["bob"]
                iw, ih = w * s, h * s * sq
                im = darken(scaled(("it", i), arts[i], iw, ih), ctx["dark"])
                if a < 1:
                    im = faded(im, a)
                paste(scene, im, cx - iw / 2, bottom - ih)

        scene, ctx = road.draw(t, s, vx, gys, top, van, front_of_van=stack)
        scene.putalpha(Image.fromarray(np.minimum(np.asarray(scene.getchannel("A")), np.asarray(band_mask(top, R_BOT)))))
        frame = bg.copy()
        frame.alpha_composite(scene)
        frame.alpha_composite(static)
        ta = 1 - clamp((t - T_REV) / 0.25)
        if ta > 0:
            frame.alpha_composite(faded(title_im, ta))
        pa = clamp((t - T_PUNCH) / 0.3)
        if pa > 0:
            frame.alpha_composite(faded(card, pa))
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
    times = [0.03, 0.3, 0.6, 1.0, 1.45, 1.85, 2.25, 2.7, 3.2, 3.7, 4.3, 4.8, 5.3, 5.8, 6.5, 7.3, 8.2, 9.0]
    contact_sheet(mp4, times, os.path.join(OUT, "contact_sheet.png"), tmp)
    qc = {"probe": probe(mp4), "audio": audio_report(mp4), "title_px": title_size, "punch_px": punch_size,
          "title_bottom": title_bottom, "punch_bottom": punch_bottom, "cta_bottom": cta_bottom,
          "tower_top_after_reveal": round(GY_B - tower_px),
          "timeline": {"lands": LAND, "reveal": [T_REV, T_REV + REV_D], "punch": T_PUNCH, "drive": T_DRIVE,
                       "cta": T_CTA, "signature": T_SIG, "end": DUR}}
    json.dump(qc, open(os.path.join(OUT, "qc.json"), "w"), indent=1)
    print(json.dumps(qc))


if __name__ == "__main__":
    main()
