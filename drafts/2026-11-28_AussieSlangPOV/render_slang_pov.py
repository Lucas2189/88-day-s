"""Eazy88 POV clip — "Your Aussie boss explains the job on day 1." Slang bubbles pile up; you answer "Yeah… nah… yeah?".

Format: POV humour, no voiceover, ~9 s. Farm scene drawn in code (2x supersampled), brand tokens,
procedural sound and music ("wah-wah" mumbles stand for the boss's voice; the words are on screen).
Usage (from the repository root):
  python3 -I drafts/2026-11-28_AussieSlangPOV/render_slang_pov.py <out_dir>
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
                     contact_sheet, ease_out_back, faded, finish, jakarta, lerp, make_background, make_cta,
                     make_signature, make_static, match_loudness, probe, smooth, text_block)
from render_reel import draw_rich, text_width  # noqa: E402
from van_kit import col_mix  # noqa: E402

BASE = "Eazy88_TikTok_AussieSlangPOV"
OUT = sys.argv[1]
HEADER = "EAZY88 · BACKPACKER LIFE"
LABEL = "Illustration"
TITLE = ["POV: YOUR AUSSIE BOSS", "EXPLAINS THE JOB", "*ON DAY 1.*"]
PUNCH = ["YOU:", "*“YEAH… NAH… YEAH?”*"]
CTA = ["SEND THIS TO THE MATE", "WHO *NODS ANYWAY*"]

# what the boss says (slang in orange). Meanings go in the caption.
BUBBLES = [(0.3, ["G'DAY! GRAB THE *ESKY*", "FROM THE *UTE*."]),
           (1.25, ["THEN CHUCK A *U-EY*", "AT THE *SERVO*."]),
           (2.1, ["*SMOKO*'S AT 10."]),
           (2.6, ["BRING YOUR *SUNNIES*", "THIS *ARVO*."]),
           (3.25, ["*RECKON* YOU'LL", "*BE RIGHT*?"])]
GOOD = (5.25, ["*GOOD ON YA!*"])
Q_POS = [(240, 1098, 66), (168, 1080, 74), (312, 1078, 80), (100, 1050, 88), (380, 1046, 100)]   # your "?" marks
Q_LAG = 0.3
T_REV, REV_D = 4.1, 0.5
T_PUNCH = 4.35
T_CTA = 6.1
T_SIG = 6.7
DUR = 8.6
R_TOP_A, R_TOP_B, R_BOT = 660, 812, 1380

SS, OY, BH = 2, 600, 800          # the scene strip (y 600..1400) is drawn at 2x, then reduced
HORIZON = 1112
OUTL = TOK["n800"]
HAT = TOK["primary_dark"]
MOUST = col_mix(TOK["n800"], TOK["primary_dark"], 0.35)
BUB_R, BUB_BOTTOM, BUB_GAP, BUB_MIN_X = 940, 995, 18, 90
TAIL_TIP = (728, 1062)
PUSH = 0.14   # older bubbles move up this fast when a new one pops


class P:
    """Draw on the 2x strip with screen coordinates."""

    def __init__(self, im):
        self.d = ImageDraw.Draw(im, "RGBA")

    @staticmethod
    def b(box):
        x0, y0, x1, y1 = box
        return (x0 * SS, (y0 - OY) * SS, x1 * SS, (y1 - OY) * SS)

    @staticmethod
    def pts(pts):
        return [(x * SS, (y - OY) * SS) for x, y in pts]

    def ell(self, box, fill, ow=0, oc=OUTL):
        self.d.ellipse(self.b(box), fill=fill, outline=oc if ow else None, width=int(ow * SS))

    def rr(self, box, r, fill, ow=0, oc=OUTL):
        self.d.rounded_rectangle(self.b(box), int(r * SS), fill=fill, outline=oc if ow else None, width=int(ow * SS))

    def rect(self, box, fill):
        self.d.rectangle(self.b(box), fill=fill)

    def poly(self, pts, fill, ow=0, oc=OUTL):
        self.d.polygon(self.pts(pts), fill=fill, outline=oc if ow else None, width=int(ow * SS))

    def chord(self, box, a0, a1, fill, ow=0, oc=OUTL):
        self.d.chord(self.b(box), a0, a1, fill=fill, outline=oc if ow else None, width=int(ow * SS))

    def line(self, pts, fill, w):
        self.d.line(self.pts(pts), fill=fill, width=int(w * SS), joint="curve")
        for x, y in (pts[0], pts[-1]):
            r = w / 2
            self.ell((x - r, y - r, x + r, y + r), fill)

    def limb(self, pts, fill, w, ow=4):
        self.line(pts, OUTL, w + 2 * ow)
        self.line(pts, fill, w)


def make_strip_bg():
    """Hot sky, red dirt, rows of vines, the ute with the esky on its tray."""
    h = BH * SS
    ys = OY + np.arange(h) / SS
    sky_e = np.clip((ys - OY) / (HORIZON - OY), 0, 1)[:, None]
    gnd_e = np.clip((ys - HORIZON) / (OY + BH - HORIZON), 0, 1)[:, None]
    sky = (1 - sky_e) * np.array(C["orange"]) + sky_e * np.array(C["sun"])
    g0, g1 = np.array(col_mix(C["sunset"], TOK["primary_dark"], 0.35)), np.array(col_mix(C["sunset"], TOK["primary_dark"], 0.7))
    gnd = (1 - gnd_e) * g0 + gnd_e * g1
    col = np.where((ys < HORIZON)[:, None], sky, gnd)
    arr = np.repeat(col[:, None, :], W * SS, axis=1).astype(np.uint8)
    im = Image.fromarray(arr, "RGB")
    p = P(im)
    # distant tree line
    rng = np.random.default_rng(7)
    x = -20
    while x < W + 20:
        r = rng.uniform(14, 30)
        p.ell((x - r, HORIZON - r * 1.1, x + r, HORIZON + 6), TOK["secondary_dark"])
        x += r * 1.5
    p.rect((0, HORIZON - 2, W, HORIZON + 4), TOK["secondary_dark"])
    # vine rows, bigger as they come closer
    for y, s in ((1140, 16), (1180, 24), (1240, 36), (1330, 54)):
        p.rect((0, y + s * 0.35, W, y + s * 0.55), col_mix(TOK["n800"], TOK["primary_dark"], 0.5))
        x = -s
        while x < W + s:
            p.ell((x - s, y - s, x + s, y + s * 0.6), C["green"], 2, TOK["secondary_dark"])
            x += s * 1.7
    # the ute (tray on the left, cab on the right), with the esky on the tray
    ute = TOK["secondary_dark"]
    p.rr((402, 1064, 548, 1100), 6, ute, 3)
    p.rr((540, 1036, 628, 1100), 14, ute, 3)
    p.rr((556, 1046, 612, 1070), 6, C["sun"], 2)
    p.rr((620, 1066, 664, 1100), 8, ute, 3)
    p.rr((430, 1030, 506, 1066), 6, C["cream"], 3)
    p.rect((432, 1032, 504, 1042), C["primary"])
    for wx in (446, 612):
        p.ell((wx - 18, 1084, wx + 18, 1120), OUTL)
        p.ell((wx - 8, 1094, wx + 8, 1110), C["muted"])
    return im


def draw_boss(p, t, talking, thumbs):
    bob = 3 * math.sin(t * 9) if talking else 0
    p.rr((718, 1218 + bob, 882, 1460), 46, C["sun"], 4)                    # hi-vis shirt
    for y in (1290, 1336):
        p.rect((722, y + bob, 878, y + 12 + bob), C["muted"])
    if thumbs:   # thumbs up
        p.limb([(738, 1256 + bob), (700, 1200)], C["sun"], 30)
        p.rr((682, 1150, 698, 1186), 8, C["cream"], 3)
        p.ell((680, 1176, 718, 1212), C["cream"], 3)
    else:        # points at the ute while talking
        hx, hy = 652 + 10 * math.sin(t * 6), 1192 + 8 * math.sin(t * 5)
        p.limb([(738, 1256 + bob), (hx, hy)], C["sun"], 30)
        p.limb([(hx, hy), (hx - 34, hy - 6)], C["cream"], 10, 3)
        p.ell((hx - 19, hy - 19, hx + 19, hy + 19), C["cream"], 3)
    p.ell((746, 1112 + bob, 854, 1220 + bob), C["cream"], 4)               # head
    for ex in (776, 808):
        p.ell((ex - 6, 1148 + bob, ex + 6, 1160 + bob), OUTL)
    mo = 4 + 13 * abs(math.sin(t * 23)) if talking else 3                    # mouth opens and closes
    p.ell((768, 1190 + bob, 796, 1194 + mo + bob), OUTL)
    p.ell((752, 1172 + bob, 788, 1194 + bob), MOUST)                        # moustache
    p.ell((780, 1172 + bob, 816, 1194 + bob), MOUST)
    p.ell((704, 1098 + bob, 896, 1134 + bob), HAT, 4)                       # hat brim
    p.rr((742, 1050 + bob, 858, 1118 + bob), 26, HAT, 4)                   # crown
    p.rect((745, 1096 + bob, 855, 1108 + bob), OUTL)                        # band


def draw_you(p, t, nq, thumbs, nod):
    tilt = min(nq, 5) * 3
    p.rr((148, 1236, 220, 1372), 22, TOK["secondary_dark"], 4)             # backpack
    p.rr((178, 1240, 302, 1460), 40, C["green"], 4)                         # tee
    if thumbs:
        p.limb([(292, 1272), (330, 1216)], C["green"], 28)
        p.rr((326, 1164, 342, 1200), 8, C["cream"], 3)
        p.ell((318, 1190, 356, 1226), C["cream"], 3)
    hx, hy = 240 + tilt, 1192 + nod
    p.ell((hx - 48, hy - 48, hx + 48, hy + 48), C["cream"], 4)             # head
    er = 4 + nq * 1.6                                                         # eyes widen as the "?" pile up
    for ex in (hx + 12, hx + 34):
        if nq >= 2:
            p.ell((ex - er, hy - 8 - er, ex + er, hy - 8 + er), C["cream"], 3)
            p.ell((ex - 3, hy - 11, ex + 3, hy - 5), OUTL)
        else:
            p.ell((ex - 5, hy - 13, ex + 5, hy - 3), OUTL)
    if thumbs:
        p.chord((hx + 6, hy + 4, hx + 38, hy + 26), 0, 180, OUTL)          # grin
    else:
        amp = min(nq, 5) * 1.4                                                # wobbly mouth
        p.line([(hx + 8 + k * 6, hy + 18 + amp * math.sin(k * 1.9)) for k in range(6)], OUTL, 4)
    p.chord((hx - 50, hy - 56, hx + 50, hy + 36), 180, 360, C["cream"])    # cap (crown, then brim)
    p.chord((hx - 50, hy - 56, hx + 50, hy + 36), 180, 360, C["primary"], 4)
    p.rr((hx + 22, hy - 16, hx + 76, hy - 4), 6, C["primary"], 3)


def bubble_tile(lines, size):
    f = jakarta(size * SS, "ExtraBold")
    pad_x, pad_y, lh = 30, 20, int(size * 1.22)
    tw = max(text_width(f, ln) for ln in lines) / SS
    w, h = int(tw + 2 * pad_x), int(len(lines) * lh + 2 * pad_y - (lh - size) + 6)
    im = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
    d = BlendDraw(im, "RGBA")
    d.rounded_rectangle((2 * SS, 2 * SS, (w - 2) * SS, (h - 2) * SS), 30 * SS, fill=C["cream"] + (255,),
                        outline=OUTL + (255,), width=5 * SS)
    y = pad_y
    for ln in lines:
        draw_rich(d, (pad_x * SS, y * SS), ln, f, OUTL, C["primary"])
        y += lh
    return im.resize((w, h), Image.LANCZOS)


def bubble_size():
    for size in range(54, 43, -1):
        f = jakarta(size, "ExtraBold")
        if all(BUB_R - (max(text_width(f, ln) for ln in lines) + 60) >= BUB_MIN_X for _, lines in BUBBLES):
            return size
    raise SystemExit("bubbles too wide")


def draw_tail(scene, bx_r, by, a):
    if a <= 0:
        return
    lay = Image.new("RGBA", scene.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay, "RGBA")
    pts = [(bx_r - 200, by - 10), (bx_r - 140, by - 10), TAIL_TIP]
    d.polygon(pts, fill=C["cream"] + (255,), outline=OUTL + (255,), width=5)
    scene.alpha_composite(faded(lay, a))


def q_layer(t, nq, a):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if a <= 0:
        return im
    for i in range(nq):
        x, y, size = Q_POS[i]
        tq = BUBBLES[i][0] + Q_LAG
        s = size * (0.5 + 0.5 * ease_out_back(clamp((t - tq) / 0.25)))
        f = anton(int(s))
        tile = Image.new("RGBA", (int(s * 1.1), int(s * 1.6)), (0, 0, 0, 0))
        td = BlendDraw(tile, "RGBA")
        for ox, oy in ((-4, 0), (4, 0), (0, -4), (0, 4), (-3, -3), (3, 3), (-3, 3), (3, -3)):
            td.text((int(s * 0.2) + ox, 6 + oy), "?", font=f, fill=OUTL + (255,))
        td.text((int(s * 0.2), 6), "?", font=f, fill=C["cream"] + (255,))
        tile = tile.rotate(12 * math.sin(i * 2.1 + t * 3), expand=True, resample=Image.BICUBIC)
        comp(im, faded(tile, a), x - tile.width / 2, y - tile.height / 2)
    return im


def make_music():
    sy = Synth(31)
    put = sy.put
    n = int(DUR * SR)
    m = np.zeros(n)
    rng = np.random.default_rng(5)

    def mumble(t0, t1, base, rate, amp=0.17):
        """Muted 'wah-wah' syllables: the boss talking fast."""
        t = t0
        while t < t1:
            d = rng.uniform(0.06, 0.1)
            f = base * rng.uniform(0.85, 1.25)
            put(m, sy.tone(f, d, amp, a=0.008, r=0.04, nh=16, tilt=0.9, detune=(-3, 3), wah=(320, 1500),
                           glide=(f * rng.uniform(0.8, 1.15), 0.02)), t)
            t += 1 / rate * rng.uniform(0.85, 1.15)

    # bouncy pluck groove while the boss talks, then it stops dead (awkward silence)
    beat, t, k = 0.25, 0.0, 0
    bass = [196.0, 196.0, 261.63, 196.0, 293.66, 196.0, 261.63, 246.94]
    while t < 3.55:
        if k % 2 == 0:
            put(m, sy.pluck(bass[(k // 2) % 8], 0.3, 0.12, decay=0.99), t)
        else:
            for j, f in enumerate((392.0, 493.88, 587.33) if (k // 8) % 2 == 0 else (523.25, 659.25, 783.99)):
                put(m, sy.pluck(f, 0.2, 0.05, decay=0.985), t + j * 0.008)
            put(m, sy.tick(0.05, 6000.0), t)
        t += beat
        k += 1
    for i, (tb, lines) in enumerate(BUBBLES):
        end = (BUBBLES[i + 1][0] if i + 1 < len(BUBBLES) else tb + 0.55) - 0.12
        mumble(tb - 0.02, end, 230.0 + 12 * i, 9.5 + 0.8 * i)
        put(m, sy.tick(0.12, 2400.0), tb)                                                   # bubble pop
        q = BUBBLES[i][0] + Q_LAG                                                            # "?" bloop
        put(m, sy.tone(620.0 + 90 * i, 0.07, 0.11, a=0.004, r=0.05, nh=6, tilt=1.4, detune=(0,),
                       glide=(1250.0 + 120 * i, 0.0)), q)
    for tc in (3.72, 3.98):   # crickets
        for j in range(3):
            nb = int(0.022 * SR)
            qq = np.arange(nb) / SR
            put(m, 0.06 * np.sin(2 * np.pi * 4600 * qq) * np.sin(np.pi * qq / 0.022), tc + j * 0.034)
    # "Yeah… nah… yeah?"
    for t0, f, f1 in ((T_PUNCH, 294.0, 330.0), (T_PUNCH + 0.27, 262.0, 220.0), (T_PUNCH + 0.54, 262.0, 415.0)):
        put(m, sy.tone(f, 0.2, 0.2, a=0.02, r=0.08, nh=18, tilt=0.85, detune=(-3, 3), wah=(400, 1500),
                       glide=(f1, 0.04)), t0)
    mumble(GOOD[0], GOOD[0] + 0.32, 300.0, 10.0, 0.15)   # "Good on ya!"
    for f in (1046.5, 1318.5):
        put(m, sy.bell(f, 0.06), GOOD[0] + 0.35)
    prog = [(392.0, 493.88, 587.33), (523.25, 659.25, 783.99), (440.0, 523.25, 659.25), (392.0, 493.88, 587.33)]
    t, k = 5.7, 0
    while t < DUR - 0.25:
        put(m, sy.pluck(prog[(k // 2) % 4][0] / 2, 0.3, 0.09, decay=0.99), t)
        for j, f in enumerate(prog[(k // 2) % 4]):
            put(m, sy.pluck(f, 0.3, 0.07, decay=0.99), t + 0.25 + j * 0.01)
        t += 0.5
        k += 1
    for f in (783.99, 987.77, 1174.66):
        put(m, sy.bell(f, 0.06), DUR - 0.85)
    return sy.master(m, reverb=0.16, fade=0.3, sub=0.4)


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
    bsize = bubble_size()
    tiles = [bubble_tile(lines, bsize) for _, lines in BUBBLES]
    good_tile = bubble_tile(GOOD[1], bsize + 6)
    strip_bg = make_strip_bg()

    enc = Encoder(os.path.join(tmp, "video.mp4"))
    nframes = int(round(DUR * FPS))
    for fi in range(nframes):
        t = fi / FPS
        e = smooth((t - T_REV) / REV_D) if t >= T_REV else 0.0
        top = lerp(R_TOP_A, R_TOP_B, e)
        shown = [i for i, (tb, _) in enumerate(BUBBLES) if t >= tb]
        nq = sum(1 for tb, _ in BUBBLES if t >= tb + Q_LAG)
        talking = any(tb - 0.02 <= t < (BUBBLES[i + 1][0] if i + 1 < len(BUBBLES) else tb + 0.55) - 0.12
                      for i, (tb, _) in enumerate(BUBBLES)) or GOOD[0] <= t < GOOD[0] + 0.32
        you_thumbs = t >= T_PUNCH
        nod = 7 * math.sin((t - T_PUNCH) * 14) * math.exp(-(t - T_PUNCH) * 2) if you_thumbs else 0
        strip = strip_bg.copy()
        p = P(strip)
        draw_you(p, t, nq if t < T_REV else 0, you_thumbs, nod)
        draw_boss(p, t, talking, t >= GOOD[0] + 0.35)
        scene = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        scene.paste(strip.resize((W, BH), Image.LANCZOS), (0, OY))
        # the speech bubbles: newest at the bottom, older ones pushed up and dimmed
        ga = 1 - clamp((t - T_REV) / 0.2)
        if shown and ga > 0:
            newest = shown[-1]
            draw_tail(scene, BUB_R, BUB_BOTTOM, ga * clamp((t - BUBBLES[newest][0]) / 0.1))
            for i in shown:
                by = BUB_BOTTOM - sum((tiles[j].height + BUB_GAP) * smooth((t - BUBBLES[j][0]) / PUSH)
                                      for j in shown if j > i)
                tile = tiles[i]
                if i == newest:
                    s = 0.6 + 0.4 * ease_out_back(clamp((t - BUBBLES[i][0]) / 0.22))
                    if s != 1:
                        tile = tile.resize((max(1, int(tile.width * s)), max(1, int(tile.height * s))), Image.BICUBIC)
                    a = ga
                else:
                    a = ga * lerp(1, 0.6, smooth((t - BUBBLES[i + 1][0]) / PUSH))
                comp(scene, faded(tile, a), BUB_R - tile.width, by - tile.height)
        scene.alpha_composite(q_layer(t, nq, ga))
        if t >= GOOD[0]:   # the boss is happy with your answer
            s = 0.6 + 0.4 * ease_out_back(clamp((t - GOOD[0]) / 0.25))
            gt = good_tile.resize((max(1, int(good_tile.width * s)), max(1, int(good_tile.height * s))), Image.BICUBIC)
            draw_tail(scene, BUB_R - 40, 995, clamp((t - GOOD[0]) / 0.1))
            comp(scene, gt, BUB_R - 40 - gt.width, 995 - gt.height)
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
    loud_fix_db = match_loudness(mp4, tmp)   # loudnorm lands at -14.8 on this mix (see pov_kit.match_loudness)
    times = [0.03, 0.4, 0.9, 1.4, 1.7, 2.2, 2.7, 3.0, 3.4, 3.8, 4.2, 4.6, 5.0, 5.5, 6.2, 7.0, 7.8, 8.3]
    contact_sheet(mp4, times, os.path.join(OUT, "contact_sheet.png"), tmp)
    qc = {"probe": probe(mp4), "audio": audio_report(mp4), "title_px": title_size, "punch_px": punch_size,
          "bubble_px": bsize, "loudness_fix_db": loud_fix_db, "title_bottom": title_bottom, "punch_bottom": punch_bottom, "cta_bottom": cta_bottom,
          "timeline": {"bubbles": [b[0] for b in BUBBLES], "reveal": [T_REV, T_REV + REV_D], "punch": T_PUNCH,
                       "good_on_ya": GOOD[0], "cta": T_CTA, "signature": T_SIG, "end": DUR}}
    json.dump(qc, open(os.path.join(OUT, "qc.json"), "w"), indent=1)
    print(json.dumps(qc))


if __name__ == "__main__":
    main()
