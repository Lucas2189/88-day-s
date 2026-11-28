"""Eazy88 POV clip — "Someone in your 10-bed dorm has an early flight." Rustle, zip, clunk, beep, LIGHT.

Format: POV humour, no voiceover, ~9 s. Dorm drawn in code, brand tokens, procedural sound and music.
The sounds are also written on screen, so the clip works with the sound off.
Usage (from the repository root):
  python3 -I drafts/2026-11-28_DormEarlyFlightPOV/render_dorm_pov.py <out_dir>
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
from van_kit import col_mix  # noqa: E402

BASE = "Eazy88_TikTok_DormEarlyFlightPOV"
OUT = sys.argv[1]
HEADER = "EAZY88 · BACKPACKER LIFE"
LABEL = "Illustration"
TITLE = ["POV: SOMEONE IN YOUR", "10-BED DORM HAS", "*AN EARLY FLIGHT.*"]
PUNCH = ["THEIR FLIGHT", "IS AT *2 PM.*"]
CTA = ["SEND THIS TO THE MATE", "WHO *PACKS AT 5 AM*"]

# (time, text, x, y, size, rotation, colour) — the sounds, written on screen
SFX = [(0.35, "rustle...", 300, 1215, 54, -6, "muted"), (0.9, "RUSTLE RUSTLE", 250, 1120, 70, 5, "cream"),
       (1.45, "ZZZIIIP", 520, 1260, 92, -4, "orange"), (2.0, "CLUNK!", 820, 1040, 96, 8, "cream"),
       (2.5, "BEEP BEEP BEEP", 420, 862, 76, -3, "sun"), (3.05, "CLICK!", 730, 768, 70, 6, "n800"),
       (3.6, "SORRY!!", 390, 1072, 110, -5, "primary"), (4.15, "rustle...", 300, 1250, 54, 4, "n600")]
CLOCK = [(0.0, "4:58"), (1.45, "4:59"), (2.5, "5:00")]
T_LIGHT = 3.05
T_REV, REV_D = 4.6, 0.6
T_PUNCH = 4.9
T_CTA = 6.3
T_SIG = 6.9
DUR = 8.8
R_TOP_A, R_TOP_B, R_BOT = 660, 812, 1380


def light(t):
    return 1.0 if t >= T_LIGHT else 0.0


def draw_dorm(t):
    L = light(t)
    scene = Image.new("RGB", (W, H), C["bg"])
    d = ImageDraw.Draw(scene, "RGBA")
    wall = col_mix(col_mix(C["surface"], TOK["n600"], 0.3), C["sun"], L)
    d.rectangle((0, 600, W, H), fill=wall + (255,))
    d.rectangle((0, 1330, W, H), fill=col_mix(TOK["n800"], C["muted"], L) + (255,))       # floor
    # window with the night outside, top right
    d.rounded_rectangle((700, 700, 960, 880), 10, fill=col_mix(C["bg"], TOK["n800"], L) + (255,),
                        outline=col_mix(TOK["n600"], C["cream"], L) + (255,), width=8)
    if L < 1:
        d.ellipse((880, 722, 926, 768), fill=C["cream"] + (255,))
        d.ellipse((896, 716, 942, 762), fill=C["bg"] + (255,))
    d.line([(830, 700), (830, 880)], fill=col_mix(TOK["n600"], C["cream"], L) + (255,), width=6)
    # ceiling bulb: off, then very on
    d.line([(520, 600), (520, 704)], fill=TOK["n800"] + (255,), width=5)
    if L:
        d.ellipse((470, 674, 570, 774), fill=C["cream"] + (90,))
        for k in range(8):
            a = k * math.pi / 4
            d.line([(520 + 62 * math.cos(a), 724 + 62 * math.sin(a)), (520 + 84 * math.cos(a), 724 + 84 * math.sin(a))],
                   fill=C["sunset"] + (255,), width=6)
    d.ellipse((500, 704, 540, 744), fill=(C["cream"] if L else TOK["n600"]) + (255,))
    # digital clock
    lab = [c for tt, c in CLOCK if t >= tt][-1]
    d.rounded_rectangle((80, 690, 300, 790), 14, fill=TOK["n800"] + (255,))
    f = anton(76)
    d.text((190 - f.getlength(lab) / 2, 694), lab, font=f, fill=C["sunset"] + (255,))
    # bunk bed
    frame = col_mix(TOK["n600"], TOK["primary_dark"], L) + (255,)
    for x in (110, 690):
        d.rectangle((x, 900, x + 22, 1330), fill=frame)
    for y in (1000, 1240):
        d.rectangle((110, y, 712, y + 24), fill=frame)
        d.rounded_rectangle((132, y - 40, 690, y), 12, fill=col_mix(TOK["n600"], C["cream"], L) + (255,))   # mattress
    # you, on the top bunk, under a green blanket (the lump moves when you jump)
    jump = 26 * math.exp(-(t - T_LIGHT) * 8) * abs(math.sin((t - T_LIGHT) * 30)) if t >= T_LIGHT else 0
    d.rounded_rectangle((170, 912 - jump, 560, 966 - jump), 26, fill=col_mix(TOK["secondary_dark"], C["green"], L) + (255,))
    d.ellipse((560, 918 - jump, 620, 970 - jump), fill=col_mix(TOK["n800"], TOK["primary_dark"], L) + (255,))  # hair
    if t < 2.0:   # asleep: eyes closed
        for ex in (577, 603):
            d.line([(ex - 7, 944), (ex + 7, 944)], fill=C["muted"] + (255,), width=3)
    else:         # the CLUNK wakes you up; eyes get bigger when the light goes on
        r = 9 if L else 7
        for ex in (577, 603):
            d.ellipse((ex - r, 944 - r - jump, ex + r, 944 + r - jump), fill=C["cream"] + (255,),
                      outline=TOK["n800"] + (255,), width=2)
            d.ellipse((ex - 3, 941 - jump, ex + 3, 947 - jump), fill=TOK["n800"] + (255,))
    # lower bunk: their stuff everywhere
    d.rounded_rectangle((180, 1120, 330, 1200), 16, fill=col_mix(TOK["primary_dark"], C["orange"], L) + (255,))  # backpack
    shake = 6 * math.sin(t * 60) if any(0 <= t - s[0] < 0.4 for s in SFX if "ustle" in s[1].lower()) else 0
    for bx in (360, 460):   # plastic bags
        d.polygon([(bx + shake, 1200), (bx + 70 + shake, 1200), (bx + 60, 1140), (bx + 35, 1125), (bx + 10, 1140)],
                  fill=col_mix(TOK["n600"], C["cream"], L) + (255,))
    # open suitcase on the floor
    d.rounded_rectangle((250, 1270, 560, 1330), 10, fill=col_mix(TOK["n800"], C["sunset"], L) + (255,))
    # locker on the right
    d.rectangle((800, 960, 980, 1330), fill=col_mix(TOK["n800"], C["muted"], L) + (255,))
    if t >= 2.0:   # the locker door bangs open
        d.polygon([(800, 960), (740, 990), (740, 1300), (800, 1330)], fill=col_mix(TOK["n600"], C["cream"], L) + (255,))
    else:
        d.rectangle((806, 966, 974, 1324), outline=col_mix(TOK["n600"], C["cream"], L) + (255,), width=4)
    # the early-flight person, crouched by the bags, hood up, headlamp on
    hood = col_mix(C["bg"], C["primary"], L) + (255,)
    d.rounded_rectangle((560, 1180, 680, 1322), 30, fill=hood)
    d.line([(578, 1212), (505 + shake, 1188)], fill=hood, width=24)
    d.ellipse((566, 1112, 640, 1186), fill=hood)
    d.ellipse((574, 1128, 612, 1172), fill=col_mix(TOK["n800"], C["bg"], 0.5) + (255,))
    if L < 1:
        d.ellipse((564, 1132, 582, 1150), fill=C["sun"] + (255,))
        if t < 2.2:   # the headlamp sweeps the room...
            ang = math.radians(198 + 26 * math.sin(2.6 * t))
        else:         # ...then lands right in your face
            ang = math.radians(lerp(198 + 26 * math.sin(2.6 * 2.2), 290, smooth((t - 2.2) / 0.3)))
        ox, oy, ln, hw = 573, 1141, 950, math.radians(11)
        d.polygon([(ox, oy), (ox + ln * math.cos(ang - hw), oy + ln * math.sin(ang - hw)),
                   (ox + ln * math.cos(ang + hw), oy + ln * math.sin(ang + hw))], fill=C["sun"] + (52,))
    # zzz while you still sleep
    if t < 0.9:
        fz = jakarta(40, "ExtraBold")
        for i, ch in enumerate("zzz"):
            y = 870 - i * 40 - 20 * ((t * 1.2 + i * 0.3) % 1)
            d.text((560 + i * 28, y), ch, font=fz, fill=C["cream"] + (200,))
    return scene, d


def sfx_layer(t):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for ts, txt, x, y, size, rot, col in SFX:
        dt = t - ts
        a = min(1 - clamp((t - T_REV) / 0.2), 1 - clamp((dt - 1.5) / 0.3))   # each sound stays ~1.5 s
        if t < ts or a <= 0:
            continue
        pop = 1 + 0.35 * math.exp(-dt * 12)
        f = anton(int(size * pop))
        w = f.getlength(txt) + 40
        tile = Image.new("RGBA", (int(w), int(size * pop * 1.6)), (0, 0, 0, 0))
        td = BlendDraw(tile, "RGBA")
        colour = TOK[col] if col in TOK else C[col]
        outline = C["bg"] if col not in ("n800", "n600") else C["cream"]
        for ox, oy in ((-4, 0), (4, 0), (0, -4), (0, 4), (-3, -3), (3, 3), (-3, 3), (3, -3)):
            td.text((20 + ox, 10 + oy), txt, font=f, fill=outline + (255,))
        td.text((20, 10), txt, font=f, fill=colour + (255,))
        tile = tile.rotate(rot, expand=True, resample=Image.BICUBIC)
        comp(im, faded(tile, a), x - tile.width / 2, y - tile.height / 2)
    return im


def boarding_pass():
    w, h = 640, 300
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = BlendDraw(im, "RGBA")
    d.rounded_rectangle((0, 0, w - 1, h - 1), 26, fill=C["cream"] + (255,))
    d.rectangle((0, 0, w, 66), fill=C["primary"] + (255,))
    d.rounded_rectangle((0, 0, w - 1, 70), 26, fill=C["primary"] + (255,))
    fs, fb = jakarta(30, "ExtraBold"), anton(92)
    d.text((32, 14), "BOARDING PASS", font=fs, fill=C["cream"] + (255,))
    d.text((32, 92), "DEPARTS", font=fs, fill=TOK["n600"] + (255,))
    d.text((32, 130), "14:00", font=fb, fill=TOK["n800"] + (255,))
    d.text((360, 92), "GATE", font=fs, fill=TOK["n600"] + (255,))
    d.text((360, 130), "8", font=fb, fill=TOK["n800"] + (255,))
    d.line([(330, 92), (330, 270)], fill=C["muted"] + (255,), width=3)
    return im


def make_music():
    sy = Synth(28)
    put = sy.put
    n = int(DUR * SR)
    m = np.zeros(n)
    rng = np.random.default_rng(4)
    tt = np.arange(n) / SR
    # a soft snore at the start (filtered noise breathing in and out)
    sn = np.convolve(rng.standard_normal(n), np.ones(30) / 30, "same") * np.clip(np.sin(2 * np.pi * 0.9 * tt), 0, None)
    m += 0.18 * sn * (tt < 0.9)
    put(m, sy.bell(880.0, 0.1), 0.02)
    for ts, txt, *_ in SFX:
        low = txt.lower()
        if "rustle" in low:   # crinkly plastic: many tiny clicks
            k = 22 if "RUSTLE" in txt else 9
            for _ in range(k):
                put(m, sy.tick(0.06 * (2 if "RUSTLE" in txt else 1), rng.uniform(2500, 5000)), ts + rng.uniform(0, 0.45))
        elif "ZIP" in txt:
            nz = int(0.5 * SR)
            q = np.arange(nz) / SR
            grit = np.sign(np.sin(2 * np.pi * np.cumsum(140 + 500 * q / 0.5) / SR)) * rng.uniform(0.6, 1, nz)
            put(m, 0.22 * grit * np.convolve(rng.standard_normal(nz), np.ones(3) / 3, "same") * np.sin(np.pi * q / 0.5), ts)
        elif "CLUNK" in txt:
            put(m, sy.timp(165.0, 0.6, 0.5, decay=10), ts)
            put(m, sy.tick(0.35, 600.0), ts)
        elif "BEEP" in txt:
            for i in range(3):
                nb = int(0.1 * SR)
                q = np.arange(nb) / SR
                put(m, 0.2 * np.sin(2 * np.pi * 1900 * q) * np.minimum(1, (0.1 - q) / 0.01), ts + i * 0.17)
        elif "CLICK" in txt:
            put(m, sy.tick(0.4, 1400.0), ts)
            for f in (523.25, 659.25, 783.99, 1046.5):   # dazzling light: a bright stab
                put(m, sy.tone(f, 0.25, 0.08, a=0.005, r=0.3, nh=10, tilt=1.0, detune=(-4, 4), bright=8), ts + 0.03)
        elif "SORRY" in txt:
            put(m, sy.tone(440.0, 0.18, 0.15, a=0.01, r=0.1, nh=12, tilt=1.0, detune=(0,), glide=(330.0, 0.05)), ts)
    # tiptoe pizzicato under the whole scene, a bit faster as it gets worse
    notes = [220.0, 261.63, 220.0, 196.0, 220.0, 261.63, 293.66, 329.63]
    t, k = 0.3, 0
    while t < T_REV:
        put(m, sy.pluck(notes[k % 8] * 2, 0.3, 0.12, decay=0.985), t)
        t += 0.32 if t < 2.0 else 0.24
        k += 1
    t0 = T_REV + 0.1   # their flight is at 2 pm: sad trombone
    put(m, sy.tone(233.08, 0.32, 0.2, a=0.03, r=0.12, nh=20, tilt=0.85, detune=(-3, 3), wah=(350, 1600)), t0)
    put(m, sy.tone(207.65, 0.9, 0.2, a=0.03, r=0.3, nh=20, tilt=0.85, detune=(-3, 3), wah=(350, 1300), vib=0.025,
                   vib_rate=6.0, vib_delay=0.2), t0 + 0.42)
    prog = [(392.0, 493.88, 587.33), (440.0, 523.25, 659.25), (349.23, 440.0, 523.25), (392.0, 493.88, 587.33)]
    t, k = T_CTA - 0.2, 0
    while t < DUR - 0.2:
        for j, f in enumerate(prog[(k // 2) % 4]):
            put(m, sy.pluck(f, 0.45, 0.1, decay=0.993), t + j * 0.012)
        t += 0.45
        k += 1
    for f in (783.99, 987.77, 1174.66):   # closing chime so the sound runs to the end
        put(m, sy.bell(f, 0.07), DUR - 0.85)
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
    bpass = boarding_pass()

    enc = Encoder(os.path.join(tmp, "video.mp4"))
    nframes = int(round(DUR * FPS))
    for fi in range(nframes):
        t = fi / FPS
        e = smooth((t - T_REV) / REV_D) if t >= T_REV else 0.0
        top = lerp(R_TOP_A, R_TOP_B, e)
        scene, d = draw_dorm(t)
        scene = scene.convert("RGBA")
        scene.alpha_composite(sfx_layer(t))
        if t >= T_REV:   # their boarding pass slides up
            q = smooth((t - T_REV - 0.1) / 0.45)
            bp = bpass.rotate(-4, expand=True, resample=Image.BICUBIC)
            comp(scene, bp, 540 - bp.width / 2, lerp(1400, 900, q))
        shake = 7 * math.exp(-(t - 2.0) * 14) * math.sin((t - 2.0) * 70) if 2.0 <= t < 2.4 else 0
        if shake:
            scene = scene.transform(scene.size, Image.AFFINE, (1, 0, 0, 0, 1, shake))
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
    times = [0.03, 0.4, 0.95, 1.5, 2.05, 2.55, 3.1, 3.65, 4.2, 4.7, 5.0, 5.5, 6.0, 6.5, 7.0, 7.6, 8.2, 8.6]
    contact_sheet(mp4, times, os.path.join(OUT, "contact_sheet.png"), tmp)
    qc = {"probe": probe(mp4), "audio": audio_report(mp4), "title_px": title_size, "punch_px": punch_size,
          "title_bottom": title_bottom, "punch_bottom": punch_bottom, "cta_bottom": cta_bottom,
          "timeline": {"sfx": [s[0] for s in SFX], "light": T_LIGHT, "reveal": [T_REV, T_REV + REV_D],
                       "punch": T_PUNCH, "cta": T_CTA, "signature": T_SIG, "end": DUR}}
    json.dump(qc, open(os.path.join(OUT, "qc.json"), "w"), indent=1)
    print(json.dumps(qc))


if __name__ == "__main__":
    main()
