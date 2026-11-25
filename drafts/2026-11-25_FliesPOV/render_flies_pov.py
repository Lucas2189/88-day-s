"""Eazy88 POV clip (van series) — "You open the van door in the outback for 2 seconds." The flies arrive.

Format: POV humour, no voiceover, ~8.6 s. Orange van drawn in code, brand tokens, procedural music.
Usage (from the repository root):
  python3 -I drafts/2026-11-25_FliesPOV/render_flies_pov.py <out_dir>
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "templates", "tools"))
from pov_kit import (C, FPS, H, SR, TOK, W, BlendDraw, Encoder, Synth, anton, audio_report, band_mask, clamp,  # noqa: E402
                     comp, contact_sheet, faded, finish, jakarta, lerp, make_background, make_cta, make_signature,
                     make_static, probe, smooth, text_block)
from van_kit import VAN_W, Road, day_sun, draw_flies, van_art  # noqa: E402

BASE = "Eazy88_TikTok_FliesPOV"
OUT = sys.argv[1]
HEADER = "EAZY88 · BACKPACKER LIFE"
LABEL = "Illustration"
TITLE = ["POV: YOU OPEN THE VAN", "DOOR IN THE OUTBACK", "*FOR 2 SECONDS.*"]
PUNCH = ["YOU'VE NOW MASTERED", "*THE AUSSIE SALUTE.*"]
CTA = ["SEND THIS TO THE MATE", "WHO *HATES FLIES*"]

T_DOOR = 0.3
COUNT = [(0.4, "1", 1), (0.9, "3", 3), (1.4, "12", 12), (1.95, "47", 47), (2.5, "180", 120), (3.1, "600", 220),
         (3.75, "YES.", 300)]          # (time, label, flies drawn)
T_REV, REV_D = 4.4, 0.8
T_PUNCH = 4.9
T_CTA = 6.2
T_SIG = 6.8
DUR = 8.6
SA, SB = 1.6, 0.8
VCX_A, VCX_B = 540, 560
GY_A, GY_B = 1290, 1236
R_TOP_A, R_TOP_B, R_BOT = 660, 812, 1380

rng = np.random.default_rng(42)
FLIES = np.column_stack([rng.uniform(40, 300, 320), rng.uniform(30, 160, 320), rng.uniform(1.5, 4.5, 320),
                         rng.uniform(1.5, 4.5, 320), rng.uniform(0, 6.28, 320)])


def counter_at(t):
    cur = None
    for i, (tt, lab, n) in enumerate(COUNT):
        if t >= tt:
            cur = i
    return cur


def counter_card(label):
    w, h = 330, 150
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = BlendDraw(im, "RGBA")
    d.rounded_rectangle((0, 0, w - 1, h - 1), 22, fill=C["cream"] + (255,))
    d.rounded_rectangle((7, 7, w - 8, h - 8), 16, outline=TOK["n800"] + (255,), width=4)
    f1, f2 = jakarta(30, "ExtraBold"), anton(84)
    d.text(((w - f1.getlength("FLIES")) / 2, 12), "FLIES", font=f1, fill=TOK["n800"] + (255,))
    d.text(((w - f2.getlength(label)) / 2, 40), label, font=f2, fill=C["primary"] + (255,))
    return im


def make_music():
    sy = Synth(77)
    put = sy.put
    n = int(DUR * SR)
    m = np.zeros(n)
    # laid-back outback riff (pentatonic plucks)
    riff = [293.66, 349.23, 392.0, 440.0, 523.25, 440.0, 392.0, 349.23]
    t, k = 0.0, 0
    while t < T_REV - 0.1:
        put(m, sy.pluck(riff[k % 8], 0.4, 0.14, decay=0.99), t)
        t += 0.25
        k += 1
    put(m, sy.bell(1174.66, 0.12), 0.02)
    put(m, sy.tick(0.25, 700.0), T_DOOR)      # door slides open
    put(m, sy.whoosh(0.3, 0.1), T_DOOR)
    # buzzing: more and more detuned layers as the count goes up
    tt = np.arange(n) / SR
    buzz = np.zeros(n)
    for i, (tc, _, nf) in enumerate(COUNT):
        f = 205 + 11 * i
        ph = 2 * np.pi * np.cumsum(f * (1 + 0.03 * np.sin(2 * np.pi * (5 + i) * tt))) / SR
        saw = 2 * ((ph / (2 * np.pi)) % 1) - 1
        saw = np.convolve(saw, np.ones(4) / 4, "same")
        env = np.clip((tt - tc) / 0.2, 0, 1) * (1 + 0.4 * np.sin(2 * np.pi * 31 * tt + i))
        env *= np.where(tt < T_REV + 1.6, 1.0, np.clip(1 - (tt - T_REV - 1.6) / 1.2, 0.25, 1))
        buzz += env * saw * (0.05 + 0.012 * i)
        put(m, sy.tick(0.2, 990.0 + 60 * i), tc)
        put(m, sy.pluck(587.33 * 2 ** (i * 2 / 12), 0.4, 0.2, decay=0.99), tc)
    m += buzz
    put(m, sy.cymbal(0.3, 2.0, decay=2.2), T_REV)
    for f in (293.66, 369.99, 440.0, 587.33):
        put(m, sy.tone(f, 1.0, 0.1, a=0.02, r=0.8, nh=14, tilt=1.0, detune=(-4, 4), bright=6), T_REV)
    t, k = T_PUNCH + 0.4, 0
    while t < DUR - 0.2:
        put(m, sy.pluck(riff[k % 8], 0.4, 0.11, decay=0.99), t)
        t += 0.25
        k += 1
    return sy.master(m, reverb=0.2, fade=0.35, sub=0.4)


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
    road = Road(DUR, lambda t: 0.0, [(0.0, C["sun"], C["cream"], 0.0), (DUR, C["sun"], C["cream"], 0.0)],
                sun=lambda t, top, hz: day_sun(t, top, hz, x=880, y_off=100, rad=52))
    van_closed, van_open = van_art(), van_art(door=False)
    cards = {lab: counter_card(lab) for _, lab, _ in COUNT}

    enc = Encoder(os.path.join(tmp, "video.mp4"))
    nframes = int(round(DUR * FPS))
    for fi in range(nframes):
        t = fi / FPS
        e = smooth((t - T_REV) / REV_D) if t >= T_REV else 0.0
        s = SA * ((SB / SA) ** e) * (1 + 0.02 * smooth(t / 3.0))
        vcx = lerp(VCX_A, VCX_B, e)
        gy = lerp(GY_A, GY_B, e)
        top = lerp(R_TOP_A, R_TOP_B, e)
        ci = counter_at(t)
        nf = COUNT[ci][2] if ci is not None else 0
        if ci is not None and ci + 1 < len(COUNT):   # ramp the flies up towards the next step
            t0, _, n0 = COUNT[ci]
            t1, _, n1 = COUNT[ci + 1]
            nf = int(lerp(n0, n1, clamp((t - t0) / (t1 - t0)) ** 2))

        def swarm(scene, d, ctx):
            if nf:
                cx = ctx["vx"] + (VAN_W * 0.62) * ctx["s"]
                cy = ctx["van_y"] + 70 * ctx["s"]
                spread = 0.5 + 0.9 * min(1.0, nf / 220) + 0.6 * e
                draw_flies(d, FLIES, t, cx, cy, ctx["s"], nf, spread)

        van = van_open if t >= T_DOOR else van_closed
        scene, ctx = road.draw(t, s, vcx - VAN_W / 2 * s, gy, top, van, front_of_van=swarm)
        if ci is not None and t < T_REV + 0.2:   # the fly counter, top right of the scene
            card = cards[COUNT[ci][1]]
            pop = 1 + 0.18 * math.exp(-(t - COUNT[ci][0]) * 10)
            cw, ch = int(card.width * pop), int(card.height * pop)
            comp(scene, faded(card.resize((cw, ch), Image.LANCZOS), 1 - clamp((t - T_REV) / 0.2)),
                 900 - cw, top + 60 - (ch - card.height) / 2)
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
    times = [0.03, 0.35, 0.6, 1.0, 1.5, 2.0, 2.6, 3.2, 3.8, 4.2, 4.6, 5.0, 5.6, 6.4, 7.0, 7.6, 8.1, 8.45]
    contact_sheet(mp4, times, os.path.join(OUT, "contact_sheet.png"), tmp)
    qc = {"probe": probe(mp4), "audio": audio_report(mp4), "title_px": title_size, "punch_px": punch_size,
          "title_bottom": title_bottom, "punch_bottom": punch_bottom, "cta_bottom": cta_bottom,
          "timeline": {"door": T_DOOR, "counter": [c[0] for c in COUNT], "reveal": [T_REV, T_REV + REV_D],
                       "punch": T_PUNCH, "cta": T_CTA, "signature": T_SIG, "end": DUR}}
    json.dump(qc, open(os.path.join(OUT, "qc.json"), "w"), indent=1)
    print(json.dumps(qc))


if __name__ == "__main__":
    main()
