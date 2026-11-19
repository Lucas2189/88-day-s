"""Eazy88 POV clip — "You check the hostel fridge after one week." Notes pile up on the door.

Format: POV humour, no voiceover, about 12 s. Everything is original: fridge and notes drawn in code,
brand fonts and colour tokens, procedural music (no samples).

Usage (from the repository root):
  python3 -I drafts/2026-11-19_HostelFridgePOV/render_fridge_pov.py <out_dir>
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
from pov_kit import (C, FPS, H, SR, TOK, W, BlendDraw, Encoder, Synth, anton, audio_report, band_mask,  # noqa: E402
                     clamp, comp, contact_sheet, faded, finish, jakarta, lerp, make_background, make_cta,
                     make_static, place_art, probe, scaled, smooth, spring, text_block)

BASE = "Eazy88_TikTok_HostelFridgePOV"
OUT = sys.argv[1]

# ---- public text (English)
HEADER = "EAZY88 · BACKPACKER LIFE"
LABEL = "Illustration"
TITLE = ["POV: YOU CHECK THE", "HOSTEL FRIDGE", "*AFTER ONE WEEK.*"]
PUNCH = ["AND STILL", "NOBODY KNOWS", "*WHO TOOK*", "*THE MILK.*"]
CTA = ["SEND THIS TO THE", "MATE WHO *'BORROWS'*", "*YOUR FOOD*"]

# ---- notes on the door (world units; fridge body is 520 x 1010). The last three are the escalation.
NOTES = [
    dict(kind="sheet", c=(265, 870), w=260, h=190, rot=0, lines=["PLEASE LABEL", "YOUR FOOD"], sub="— Management"),
    dict(c=(150, 735), w=215, h=180, rot=-7, col="sun", lines=["WHO TOOK", "MY MILK??"]),
    dict(c=(380, 690), w=210, h=175, rot=6, col="orange", lines=["LABELLED.", "NOT FREE."]),
    dict(c=(165, 588), w=235, h=190, rot=4, col="green_l", lines=["MY HUMMUS", "HAD MY NAME", "ON IT"]),
    dict(c=(385, 528), w=215, h=175, rot=-5, col="cream", lines=["I COUNTED", "THE EGGS."]),
    dict(c=(150, 442), w=205, h=170, rot=-3, col="sun", lines=["IT WAS", "ROOM 6."]),
    dict(c=(378, 398), w=235, h=180, rot=7, col="green_l", lines=["ROOM 6 HERE.", "IT WASN'T US."]),
    dict(c=(150, 262), w=215, h=185, rot=-6, col="orange", lines=["WHO TOOK", "THE PEN?"]),
    dict(c=(386, 222), w=240, h=180, rot=5, col="cream", lines=["IT'S A FRIDGE,", "NOT A BUFFET"]),
    dict(c=(262, 88), w=270, h=178, rot=-3, col="sun", lines=["PLEASE.", "I'M BEGGING."]),
]
# more notes on the lower door, added while the camera is at the top (out of frame), seen at the zoom-out
EXTRAS = [
    dict(c=(95, 958), w=140, h=100, rot=8, col="green_l", lines=["MINE!!"]),
    dict(c=(440, 952), w=150, h=110, rot=-6, col="orange", lines=["NOT", "YOURS"]),
    dict(c=(468, 822), w=120, h=100, rot=10, col="sun", lines=["WHY"]),
    dict(c=(64, 842), w=118, h=100, rot=-12, col="cream", lines=["ROOM 6??"]),
]

# ---- timeline (seconds)
IMP = [0.0, 1.10, 1.85, 2.55, 3.25, 3.90, 4.50, 5.30, 6.10, 6.90]   # moment each note lands
DROP_D = 0.16
T_EXTRA = 7.45
T_REV, REV_D = 7.75, 0.8
T_PUNCH = T_REV + 0.55
T_CTA = 10.2
DUR = 12.4
OMEGA = 12.0

# ---- geometry and camera (screen = origin + world * scale)
FW, FH, FEET = 520, 1010, 16
PAD = 30
RS = 3
SA = 1.6
OXA = 540 - FW / 2 * SA
CY_TARGET = 1030                   # screen y where the newest note is kept
SB = 440 / FW                      # whole fridge on the right after the reveal
OXB, OYB = 940 - FW * SB, 400
R_TOP_A, R_TOP_B, R_BOT = 660, 368, 1380


# ---------------------------------------------------------------- artwork
def fridge_art():
    w, h = int((FW + 2 * PAD) * RS), int((FH + FEET + 2 * PAD) * RS)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    o = PAD * RS
    sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((o + 8 * RS, o + 14 * RS, o + (FW + 8) * RS, o + (FH + 10) * RS), 26 * RS,
                                         fill=(0, 0, 0, 140))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10 * RS)))
    d = ImageDraw.Draw(im, "RGBA")
    for fx in (60, FW - 90):   # feet
        d.rectangle((o + fx * RS, o + (FH - 6) * RS, o + (fx + 30) * RS, o + (FH + FEET) * RS), fill=TOK["n800"] + (255,))
    d.rounded_rectangle((o, o, o + FW * RS, o + FH * RS), 26 * RS, fill=TOK["n600"] + (255,))
    d.rounded_rectangle((o + 10 * RS, o + 28 * RS, o + 20 * RS, o + (FH - 28) * RS), 5 * RS, fill=C["muted"] + (70,))
    d.rounded_rectangle((o + (FW - 22) * RS, o + 28 * RS, o + (FW - 10) * RS, o + (FH - 28) * RS), 5 * RS,
                        fill=TOK["n800"] + (130,))
    d.rectangle((o + 4 * RS, o + 300 * RS, o + (FW - 4) * RS, o + 311 * RS), fill=TOK["n800"] + (255,))   # door gap
    for y0, y1 in ((150, 282), (330, 560)):   # handles
        d.rounded_rectangle((o + 30 * RS, o + y0 * RS, o + 48 * RS, o + y1 * RS), 8 * RS, fill=C["muted"] + (255,))
        d.rounded_rectangle((o + 30 * RS, o + y0 * RS, o + 36 * RS, o + y1 * RS), 3 * RS, fill=C["cream"] + (120,))
    for (mx, my, col) in ((478, 330, C["orange"]), (40, 20, C["green"])):   # magnets
        r = 14 * RS
        d.ellipse((o + mx * RS - r, o + my * RS - r, o + mx * RS + r, o + my * RS + r), fill=col + (255,))
    return im


def fit_lines(lines, max_w, max_h, start):
    size = start
    while size > 10:
        f = jakarta(size, "ExtraBold")
        lh = int(size * 1.18)
        if max(f.getlength(ln) for ln in lines) <= max_w and lh * len(lines) <= max_h:
            return f, lh
        size -= 1
    raise ValueError(lines)


def note_art(nd):
    ws, hs = nd["w"] * RS, nd["h"] * RS
    pad = 22 * RS
    im = Image.new("RGBA", (ws + 2 * pad, hs + 2 * pad), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle((pad + 3 * RS, pad + 7 * RS, pad + ws + 2 * RS, pad + hs + 6 * RS), fill=(0, 0, 0, 120))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6 * RS)))
    d = BlendDraw(im, "RGBA")
    ink = TOK["n800"] + (255,)
    if nd.get("kind") == "sheet":
        d.rectangle((pad, pad, pad + ws, pad + hs), fill=C["cream"] + (255,))
        fa = anton(int(44 * RS))
        lh = int(46 * RS)
        sub = jakarta(int(17 * RS), "SemiBold")
        total = lh * len(nd["lines"]) + 26 * RS
        y = pad + (hs - total) / 2
        for ln in nd["lines"]:
            d.text((pad + (ws - fa.getlength(ln)) / 2, y), ln, font=fa, fill=ink)
            y += lh
        d.text((pad + (ws - sub.getlength(nd["sub"])) / 2, y + 6 * RS), nd["sub"], font=sub, fill=TOK["n600"] + (255,))
        tape = Image.new("RGBA", (90 * RS, 24 * RS), C["sun"] + (170,))
        im.alpha_composite(tape, (int(pad + (ws - tape.width) / 2), int(pad - 12 * RS)))
    else:
        col = C[nd["col"]]
        d.rectangle((pad, pad, pad + ws, pad + hs), fill=col + (255,))
        d.rectangle((pad, pad, pad + ws, pad + int(hs * 0.16)), fill=tuple(int(v * 0.93) for v in col) + (255,))
        f, lh = fit_lines(nd["lines"], ws - 30 * RS, hs - 40 * RS, int(36 * RS))
        y = pad + int(hs * 0.16) / 2 + (hs - lh * len(nd["lines"])) / 2
        for ln in nd["lines"]:
            d.text((pad + (ws - f.getlength(ln)) / 2, y), ln, font=f, fill=ink)
            y += lh
        nd["font_px_world"] = round(f.size / RS, 1)
    return im.rotate(nd["rot"], expand=True, resample=Image.BICUBIC)


# ---------------------------------------------------------------- music (procedural, no samples)
def make_music():
    sy = Synth(66)
    put = sy.put
    n = int(DUR * SR)
    m = np.zeros(n)
    # sneaky pizzicato ostinato in A minor (8th notes) until the reveal
    bass = [110.0, 164.81, 220.0, 164.81, 87.31, 130.81, 174.61, 130.81, 98.0, 146.83, 196.0, 146.83,
            82.41, 123.47, 164.81, 207.65]
    step = 0.3
    t, k = 0.0, 0
    while t < T_REV - 0.05:
        put(m, sy.pluck(bass[k % len(bass)] * 2, 0.35, 0.22, decay=0.982, soft=2), t)
        t += step
        k += 1
    put(m, sy.tick(0.16, 880.0), 0.02)
    # each note landing: a paper slap and a pizzicato step up the scale
    for i, f in zip(range(1, 7), (440.0, 493.88, 523.25, 587.33, 659.25, 698.46)):
        put(m, sy.slap(0.32), IMP[i])
        put(m, sy.pluck(f, 0.5, 0.3, decay=0.99), IMP[i])
        put(m, sy.bell(f * 2, 0.05, 0.6), IMP[i])
    # the three escalation notes: orchestra stabs, louder each time (Dm, E, E7b9)
    stabs = [(146.83, [293.66, 349.23, 440.0, 587.33]), (164.81, [329.63, 415.30, 493.88, 659.25]),
             (164.81, [329.63, 415.30, 587.33, 698.46])]
    for (root, ch), i, g in zip(stabs, (7, 8, 9), (0.8, 0.95, 1.15)):
        put(m, sy.slap(0.38 * g), IMP[i])
        put(m, sy.timp(root, 0.3 * g, 0.8, decay=6), IMP[i])
        for f in ch:
            put(m, sy.tone(f, 0.28, 0.17 * g, a=0.012, r=0.4, nh=18, tilt=0.9, detune=(-4, 4), bright=8), IMP[i])
    # drum roll and cymbal swell into the reveal
    t = T_REV - 0.7
    while t < T_REV - 0.02:
        g = 0.12 + 0.5 * ((t - (T_REV - 0.7)) / 0.7) ** 1.5
        put(m, sy.snare(0.55 * g), t)
        t += 0.06
    put(m, sy.cymbal(0.4, dur=2.6, swell=0.7), T_REV - 0.7)
    # reveal: "dun, dun, DUNNN"
    for k2, tt in enumerate((T_REV, T_REV + 0.28)):
        put(m, sy.timp(110.0, 0.45, 0.5, decay=9), tt)
        put(m, sy.tick(0.25, 990.0), tt)
        for f in (220.0, 329.63, 440.0, 659.25):
            put(m, sy.tone(f, 0.16, 0.16, a=0.008, r=0.2, nh=18, tilt=0.9, detune=(-4, 4), bright=8), tt)
    t3 = T_REV + 0.58
    put(m, sy.timp(87.31, 0.5, 1.4, decay=3.5), t3)
    for f in (174.61, 261.63, 349.23, 415.30, 523.25, 698.46):
        put(m, sy.tone(f, 1.4, 0.15, a=0.02, r=1.2, nh=16, tilt=1.0, detune=(-5, 5), bright=4, vib=0.006,
                       vib_rate=7, vib_delay=0.3), t3)
    # under the call to action: the sneaky pizzicato comes back, softer, and ends on two plucks
    t, k = T_CTA - 0.3, 0
    while t < DUR - 0.9:
        put(m, sy.pluck(bass[k % 8] * 2, 0.35, 0.2, decay=0.982, soft=2), t)
        t += step
        k += 1
    put(m, sy.pluck(220.0, 0.6, 0.22, decay=0.99), DUR - 0.75)
    put(m, sy.pluck(220.0, 0.6, 0.22, decay=0.99), DUR - 0.45)
    return sy.master(m, reverb=0.28, fade=0.35, sub=0.4)


# ---------------------------------------------------------------- render
def main():
    os.makedirs(OUT, exist_ok=True)
    tmp = os.path.join(OUT, "_tmp")
    os.makedirs(tmp, exist_ok=True)

    bg = make_background().convert("RGBA")
    static = make_static(HEADER, LABEL)
    title_im, title_bottom, title_size = text_block(TITLE, 100, 860, 80, 318)
    punch_im, punch_bottom, punch_size = text_block(PUNCH, 96, OXB - 80 - 24, 80, 430)
    cta_im, cta_bottom = make_cta(CTA, 880, max_w=OXB - 80 - 24)
    assert title_bottom <= R_TOP_A, f"title ends at {title_bottom}, scene starts at {R_TOP_A}"
    assert punch_bottom <= 880 - 36 - 20, f"punchline ends at {punch_bottom}"
    assert cta_bottom <= 1380 and OYB + (FH + FEET) * SB <= 1380
    fridge = fridge_art()
    arts = [note_art(nd) for nd in NOTES]
    extras = [note_art(nd) for nd in EXTRAS]

    enc = Encoder(os.path.join(tmp, "video.mp4"))
    oy, ov, oy_rev0 = CY_TARGET - NOTES[0]["c"][1] * SA, 0.0, None
    nframes = int(round(DUR * FPS))
    for fi in range(nframes):
        t = fi / FPS
        newest = max(i for i in range(len(NOTES)) if t >= IMP[i] - DROP_D or i == 0)
        if t < T_REV:   # camera follows the newest note up the door
            oy, ov = spring(oy, ov, CY_TARGET - NOTES[newest]["c"][1] * SA, OMEGA)
            s, ox, oy_now, rt = SA, OXA, oy, R_TOP_A
        else:           # zoom out to the whole fridge, then drift slightly
            if oy_rev0 is None:
                oy_rev0 = oy
            e = smooth((t - T_REV) / REV_D)
            s = SA * (SB / SA) ** e * (1 - 0.015 * smooth((t - T_REV - REV_D) / 4))
            cx = lerp(OXA + FW / 2 * SA, OXB + FW / 2 * SB, e)          # fridge centre moves on screen
            ox, oy_now = cx - FW / 2 * s, lerp(oy_rev0, OYB, e)          # top of the fridge only moves up
            rt = lerp(R_TOP_A, R_TOP_B, e)
        shake = sum((8 if i >= 7 else 4) * math.exp(-(t - IMP[i]) * 16) * math.cos((t - IMP[i]) * 60)
                    for i in range(1, len(NOTES)) if 0 <= t - IMP[i] < 0.35)
        oys = oy_now + shake

        scene = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(scene, "RGBA")
        gy = oys + (FH + FEET) * s
        if gy < R_BOT + 20:   # floor line
            d.line([(ox - 300 * s, gy), (ox + (FW + 300) * s, gy)], fill=C["muted"] + (110,), width=max(2, int(round(4 * s))))
        place_art(scene, fridge, RS, ox - PAD * s, oys - PAD * s, s)
        for nd, art in [(NOTES[i], arts[i]) for i in range(len(NOTES)) if t >= IMP[i] - DROP_D or i == 0] + \
                       [(EXTRAS[j], extras[j]) for j in range(len(EXTRAS)) if t >= T_EXTRA]:
            sc, a = 1.0, 1.0
            if nd in NOTES and NOTES.index(nd) > 0:
                i = NOTES.index(nd)
                q = (t - (IMP[i] - DROP_D)) / DROP_D
                if q < 1:   # flying onto the door
                    sc, a = lerp(1.4, 1.0, q * q), clamp(q * 3)
                else:       # small squash after the slap
                    dt = t - IMP[i]
                    sc = 1 - 0.035 * math.sin(dt * 30) * math.exp(-dt * 12) if dt < 0.5 else 1.0
            ww, hh = art.width / RS * s * sc, art.height / RS * s * sc
            cx, cy = ox + nd["c"][0] * s, oys + nd["c"][1] * s
            comp(scene, faded(scaled(id(art), art, ww, hh), a), cx - ww / 2, cy - hh / 2)
        scene.putalpha(Image.fromarray(np.minimum(np.asarray(scene.getchannel("A")), np.asarray(band_mask(rt, R_BOT)))))

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
    times = [0.03, 0.9, 1.25, 2.0, 2.7, 3.4, 4.05, 4.65, 5.45, 6.25, 7.05, 7.6, 8.0, 8.6, 9.3, 10.0, 10.8, 12.2]
    contact_sheet(mp4, times, os.path.join(OUT, "contact_sheet.png"), tmp)
    qc = {"probe": probe(mp4), "audio": audio_report(mp4), "title_px": title_size, "punch_px": punch_size,
          "title_bottom": title_bottom, "punch_bottom": punch_bottom, "cta_bottom": cta_bottom,
          "note_text_px_on_screen": {"/".join(nd["lines"]): round(nd.get("font_px_world", 44) * SA)
                                     for nd in NOTES},
          "fridge_box_after_reveal": [round(OXB), OYB, 940, round(OYB + (FH + FEET) * SB)],
          "timeline": {"impacts": IMP, "reveal": [T_REV, T_REV + REV_D], "punch": T_PUNCH, "cta": T_CTA, "end": DUR}}
    json.dump(qc, open(os.path.join(OUT, "qc.json"), "w"), indent=1)
    print(json.dumps(qc))


if __name__ == "__main__":
    main()
