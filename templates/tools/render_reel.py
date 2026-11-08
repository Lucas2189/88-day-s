"""Eazy88 reel renderer — official brand identity (app + website), free and local.

Usage:
  python3 -I render_reel.py spec.json audio_dir out_dir [--music]

spec.json  scenes, cue keys (matching audio_dir/<key>.wav and vo_timings.json), texts.
audio_dir  Kokoro clips + vo_timings.json (from make_voiceover.py).
out_dir    receives <base>_A.mp4, .srt, _Voiceover.wav, _Cover.png, timeline.json.

Text convention: *word* is drawn in the highlight colour (orange #F99660).
Brand tokens come from brand/brand-identity.md (website CSS variables).
"""
import json, math, os, re, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FONTS = os.path.join(ROOT, "brand", "fonts")
ICON = os.path.join(ROOT, "brand", "logos", "eazy88_app-icon_994px_from-website_2026-11-07.png")

W, H, FPS = 1080, 1920, 30
SR = 48000
C = {  # official tokens (eazy88.com CSS)
    "bg": (0x14, 0x11, 0x0D), "surface": (0x1F, 0x1B, 0x16), "line": (0x2E, 0x28, 0x22),
    "line2": (0x3A, 0x33, 0x2B), "cream": (0xFE, 0xF4, 0xE6), "muted": (0xCF, 0xC4, 0xB4),
    "orange": (0xF9, 0x96, 0x60), "primary": (0xDB, 0x65, 0x30), "sunset": (0xF2, 0x80, 0x3F),
    "sun": (0xFC, 0xD9, 0xA8), "green": (0x1E, 0xAD, 0x54), "green_l": (0x72, 0xD8, 0x9A),
    "ink_deep": (0x0A, 0x09, 0x07),
}
SAFE_X0, SAFE_X1, SAFE_Y0, SAFE_Y1 = 80, 940, 220, 1380
CAP_Y = 1206


def anton(size):
    return ImageFont.truetype(os.path.join(FONTS, "Anton-Regular.ttf"), size)


def jakarta(size, weight="SemiBold"):
    f = ImageFont.truetype(os.path.join(FONTS, "PlusJakartaSans-Variable.ttf"), size)
    f.set_variation_by_name(weight)
    return f


def fit_font(lines, size, max_w=SAFE_X1 - SAFE_X0):
    while size > 40 and max(text_width(anton(size), l, 1) for l in lines) > max_w:
        size -= 2
    return anton(size)


def ease(x):
    x = min(1.0, max(0.0, x))
    return 1 - (1 - x) ** 3


# ---------------------------------------------------------------- text helpers
def tokens(text):
    """Split '*hi* there' into [(word, highlighted)] keeping spaces."""
    out, hl = [], False
    for part in re.split(r"(\*)", text):
        if part == "*":
            hl = not hl
        elif part:
            out.append((part, hl))
    return out


def text_width(font, text, tracking=0):
    plain = text.replace("*", "")
    return font.getlength(plain) + tracking * max(0, len(plain) - 1)


def draw_rich(draw, xy, text, font, color, hl_color, tracking=0, alpha=255):
    x, y = xy
    for seg, hl in tokens(text):
        col = (hl_color if hl else color) + (alpha,)
        if tracking == 0:
            draw.text((x, y), seg, font=font, fill=col)
            x += font.getlength(seg)
        else:
            for ch in seg:
                draw.text((x, y), ch, font=font, fill=col)
                x += font.getlength(ch) + tracking
    return x


def wrap(font, text, max_w):
    words, lines, cur = text.split(" "), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if text_width(font, test) <= max_w or not cur:
            cur = test
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- drawing primitives
def rounded(draw, box, r, fill, outline=None, width=2):
    draw.rounded_rectangle(box, r, fill=fill, outline=outline, width=width)


def icon_check(draw, cx, cy, r, color, alpha):
    if alpha <= 0:
        return
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=color + (alpha,))
    pts = [(cx - r * 0.45, cy + r * 0.02), (cx - r * 0.1, cy + r * 0.38), (cx + r * 0.5, cy - r * 0.35)]
    draw.line(pts, fill=C["bg"] + (alpha,), width=max(3, int(r * 0.28)), joint="curve")


def icon_warn(draw, cx, cy, r, color, alpha):
    if alpha <= 0:
        return
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=color + (alpha,))
    w = max(3, int(r * 0.26))
    draw.line([(cx, cy - r * 0.5), (cx, cy + r * 0.12)], fill=C["bg"] + (alpha,), width=w)
    draw.ellipse((cx - w * 0.6, cy + r * 0.32, cx + w * 0.6, cy + r * 0.32 + w * 1.2), fill=C["bg"] + (alpha,))


def icon_dot(draw, cx, cy, r, color, alpha):
    if alpha <= 0:
        return
    draw.ellipse((cx - r * 0.45, cy - r * 0.45, cx + r * 0.45, cy + r * 0.45), fill=color + (alpha,))


def icon_share(draw, cx, cy, s, color, alpha):
    if alpha <= 0:
        return
    # generic "send" arrow in a circle (not a copy of any platform UI)
    draw.ellipse((cx - s, cy - s, cx + s, cy + s), fill=color + (alpha,))
    col = C["bg"] + (alpha,)
    w = int(s * 0.2)
    draw.line([(cx - s * 0.45, cy), (cx + s * 0.25, cy)], fill=col, width=w)
    draw.polygon([(cx + s * 0.55, cy), (cx + s * 0.05, cy - s * 0.42), (cx + s * 0.05, cy + s * 0.42)], fill=col)


def icon_bookmark(draw, cx, cy, s, color, alpha):
    if alpha <= 0:
        return
    draw.ellipse((cx - s, cy - s, cx + s, cy + s), fill=color + (alpha,))
    col = C["bg"] + (alpha,)
    x0, x1, y0, y1 = cx - s * 0.32, cx + s * 0.32, cy - s * 0.45, cy + s * 0.5
    draw.polygon([(x0, y0), (x1, y0), (x1, y1), (cx, y1 - s * 0.3), (x0, y1)], fill=col)


def icon_download(draw, cx, cy, s, color, alpha):
    if alpha <= 0:
        return
    draw.ellipse((cx - s, cy - s, cx + s, cy + s), fill=color + (alpha,))
    col = C["bg"] + (alpha,)
    w = int(s * 0.2)
    draw.line([(cx, cy - s * 0.5), (cx, cy + s * 0.1)], fill=col, width=w)
    draw.polygon([(cx, cy + s * 0.45), (cx - s * 0.4, cy + s * 0.02), (cx + s * 0.4, cy + s * 0.02)], fill=col)
    draw.line([(cx - s * 0.45, cy + s * 0.62), (cx + s * 0.45, cy + s * 0.62)], fill=col, width=int(w * 0.8))


ICONS = {"check": icon_check, "warn": icon_warn, "dot": icon_dot}
CHIP_COL = {"orange": ("orange", "bg"), "green": ("green_l", "bg"), "muted": ("line2", "cream")}


class BlendDraw(ImageDraw.ImageDraw):
    """ImageDraw whose text() is alpha-composited instead of replacing pixels
    (Pillow's text() overwrites RGBA pixels, which punches holes in cards)."""

    def text(self, xy, text, fill=None, font=None, **kw):
        if not text.strip() or (fill is not None and len(fill) == 4 and fill[3] == 0):
            return
        l, t, r, b = font.getbbox(text)
        tmp = Image.new("RGBA", (int(r - l) + 6, int(b - t) + 6), (0, 0, 0, 0))
        ImageDraw.Draw(tmp).text((-l + 3, -t + 3), text, font=font, fill=fill)
        x, y = int(round(xy[0] + l - 3)), int(round(xy[1] + t - 3))
        self._image.alpha_composite(tmp, (max(0, x), max(0, y)))


# ---------------------------------------------------------------- static layers
def make_background():
    bg = Image.new("RGB", (W, H), C["bg"])
    glow = Image.new("L", (W, H), 0)
    gd = ImageDraw.Draw(glow)
    gd.ellipse((560, -420, 1500, 520), fill=46)
    glow = glow.filter(ImageFilter.GaussianBlur(160))
    sun = Image.new("RGB", (W, H), C["sunset"])
    bg = Image.composite(sun, bg, glow)
    return bg


_icon_cache = {}


def brand_icon(size):
    if size not in _icon_cache:
        im = Image.open(ICON).convert("RGBA")
        # keep the official artwork untouched: only resample (no recolour/crop)
        _icon_cache[size] = im.resize((size, size), Image.LANCZOS)
    return _icon_cache[size]


def payslip_card(label, w=300, h=380, f_lab=None):
    """Original illustration of a generic payslip marked EXAMPLE (no real data)."""
    im = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0))
    d = BlendDraw(im, "RGBA")
    d.rounded_rectangle((20, 20, 20 + w, 20 + h), 22, fill=C["cream"] + (255,))
    fb = jakarta(26, "Bold")
    d.text((44, 44), "PAYSLIP", font=fb, fill=C["bg"] + (255,))
    n_lines = max(2, int((h - 170) / 30))
    for i, frac in enumerate([0.8, 0.55, 0.7, 0.45, 0.62, 0.5, 0.66, 0.4][:n_lines]):
        y = 92 + i * 30
        d.rounded_rectangle((44, y, 44 + (w - 48) * frac, y + 14), 7, fill=C["neutral"] + (255,))
    stamp = jakarta(30, "ExtraBold")
    sw = stamp.getlength("EXAMPLE")
    d.rounded_rectangle((44, h - 52, 44 + sw + 28, h - 4), 10, outline=C["primary"] + (255,), width=4)
    d.text((58, h - 48), "EXAMPLE", font=stamp, fill=C["primary"] + (255,))
    if label:
        lw = f_lab.getlength(label)
        cy = 92 + (n_lines * 30) / 2 - 25
        d.rounded_rectangle((20 + w / 2 - lw / 2 - 22, cy, 20 + w / 2 + lw / 2 + 22, cy + 50), 25, fill=C["bg"] + (240,))
        d.text((20 + w / 2 - lw / 2, cy + 7), label, font=f_lab, fill=C["cream"] + (255,))
    return im


C["neutral"] = (0xDD, 0xD4, 0xC5)


class ClipReader:
    """Sequential frame reader for a real screen recording, scaled to the phone screen."""

    def __init__(self, path, w, h, start=0.0):
        self.w, self.h = w, h
        self.p = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-ss", str(start), "-i", path, "-vf",
                                   f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},fps={FPS}",
                                   "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
        self.t, self.frame = -1.0, Image.new("RGB", (w, h), C["bg"])

    def at(self, t):
        while self.t + 1e-6 < t:
            buf = self.p.stdout.read(self.w * self.h * 3)
            if len(buf) < self.w * self.h * 3:
                break  # hold last frame
            self.frame = Image.frombytes("RGB", (self.w, self.h), buf)
            self.t = max(self.t, 0) + 1 / FPS if self.t >= 0 else 0.0
        return self.frame


# ---------------------------------------------------------------- scene renderer
class Reel:
    def __init__(self, spec, timings, cue_times):
        self.spec, self.timings, self.cue = spec, timings, cue_times
        self.bg = make_background()
        self.f_label = jakarta(28, "Bold")
        self.f_tile = jakarta(26, "Bold")
        self.f_chip = jakarta(30, "Bold")
        self.f_item = jakarta(44, "SemiBold")
        self.f_foot = jakarta(27, "Medium")
        self.f_cap = jakarta(46, "SemiBold")
        self.f_brand = anton(64)
        self.layout_log = []
        self.spec_dir = spec.get("_dir", ".")
        self.clips = {}
        self.props = {}

    def t_of(self, ref, sec_start):
        if ref is None:
            return sec_start
        if isinstance(ref, (int, float)):
            return ref
        if "+" in ref:  # "cue+seconds": a moment inside a voice line
            key, off = ref.split("+")
            return self.cue[key][0] + float(off)
        return self.cue[ref][0]

    def header(self, d, img, sec, t):
        ic = brand_icon(60)
        img.alpha_composite(ic, (SAFE_X0, 200))
        d.text((SAFE_X0 + 78, 214), self.spec.get("header", "EAZY88 · BACKPACKER TIPS"), font=self.f_label, fill=C["muted"] + (255,))
        n_points = sum(1 for s in self.spec["sections"] if s["kind"] in ("point", "stats"))
        if sec.get("num") and n_points:
            cur = int(sec["num"])
            x = SAFE_X1 - n_points * 58 + 6
            for i in range(1, n_points + 1):
                on = i <= cur
                box = (x, 206, x + 50, 256)
                rounded(d, box, 12, (C["orange"] if i == cur else (C["line2"] if not on else C["surface"])) + (255,),
                        outline=(C["orange"] if on else C["line2"]) + (255,), width=2)
                col = C["bg"] if i == cur else (C["orange"] if on else C["muted"])
                tw = self.f_tile.getlength(str(i))
                d.text((x + 25 - tw / 2, 214), str(i), font=self.f_tile, fill=col + (255,))
                x += 58

    def chip(self, d, x, y, chip, alpha):
        bgk, fgk = CHIP_COL[chip.get("color", "orange")]
        tw = self.f_chip.getlength(chip["text"])
        box = (x, y, x + tw + 44, y + 58)
        rounded(d, box, 29, C[bgk] + (alpha,))
        d.text((x + 22, y + 11), chip["text"], font=self.f_chip, fill=C[fgk] + (alpha,))
        return box[3]

    def footnote(self, d, y, text, alpha):
        lines = []
        for para in text.split("\n"):
            lines += wrap(self.f_foot, para, SAFE_X1 - SAFE_X0)
        for i, ln in enumerate(lines):
            d.text((SAFE_X0, y + i * 36), ln, font=self.f_foot, fill=C["muted"] + (alpha,))
        return y + len(lines) * 36

    def draw_section(self, sec, t, s0):
        img = self.bg.copy().convert("RGBA")
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = BlendDraw(layer, "RGBA")  # blend, so faded elements never punch holes
        hook_static = sec["kind"] == "hook"

        def appear(ref):
            if hook_static and ref is None:
                return 255, 0.0
            a = ease((t - self.t_of(ref, s0)) / 0.35)
            return int(255 * a), (1 - a) * 26

        self.header(d, layer, sec, t)
        y = sec.get("y", 330)
        log = {"section": sec["id"], "boxes": []}

        if sec["kind"] == "hook":
            f = fit_font(sec["title"], sec.get("title_size", 132))
            for ln in sec["title"]:
                draw_rich(d, (SAFE_X0, y), ln, f, C["cream"], C["orange"], tracking=1)
                lw = text_width(f, ln, 1)
                log["boxes"].append(("title", SAFE_X0, y, SAFE_X0 + lw, y + f.size * 1.2))
                y += int(f.size * 1.12)
            y += 36
            if sec.get("chip"):
                a, dy = appear(sec["chip"].get("at"))
                y = self.chip(d, SAFE_X0, y + dy, sec["chip"], a) + 30
            for it in sec.get("items", []):
                a, dy = appear(it.get("at"))
                for ln in wrap(self.f_item, it["text"], SAFE_X1 - SAFE_X0):
                    draw_rich(d, (SAFE_X0, y + dy), ln, self.f_item, C["cream"], C["orange"], alpha=a)
                    y += 60
                y += 10
            if sec.get("props"):
                key = sec["id"]
                if key not in self.props:
                    fl = jakarta(28, "Bold")
                    self.props[key] = [payslip_card(pp, w=250, h=310, f_lab=fl).rotate(r, resample=Image.BICUBIC, expand=True)
                                       for pp, r in zip(sec["props"], [8, -4, 6])]
                xs = [SAFE_X0 - 14, 380, 670]
                top = y + 10
                for k, im in enumerate(self.props[key]):
                    layer.alpha_composite(im, (int(xs[k]), int(top + (k % 2) * 40)))
                y = top + max(im.height for im in self.props[key]) + 40
            if sec.get("foot"):
                a, dy = appear(sec.get("foot_at"))
                y = self.footnote(d, y + 10, sec["foot"], a)

        elif sec["kind"] == "demo":
            steps = sec["steps"]
            cur = 0
            for k, st in enumerate(steps):
                if t >= self.t_of(st.get("at"), s0) - 0.05:
                    cur = k
            fs = jakarta(30, "Bold")
            widths = [fs.getlength(st["label"]) + 40 for st in steps]
            gap = 14
            x = (W - (sum(widths) + gap * (len(steps) - 1))) / 2
            for k, st in enumerate(steps):
                on = k == cur
                rounded(d, (x, y, x + widths[k], y + 56), 28, (C["orange"] if on else C["surface"]) + (255,),
                        outline=(C["orange"] if on else C["line2"]) + (255,))
                d.text((x + 20, y + 10), st["label"], font=fs, fill=(C["bg"] if on else C["muted"]) + (255,))
                x += widths[k] + gap
            y += 80
            ph_h = sec.get("phone_h", 1172 - y)
            ph_w = int(ph_h / 2.174)
            px = (W - ph_w) // 2
            bez = 14
            rounded(d, (px - bez, y - bez, px + ph_w + bez, y + ph_h + bez), 58, C["ink_deep"] + (255,), outline=C["line2"] + (255,), width=3)
            clip = sec.get("clip")
            clip_path = os.path.join(self.spec_dir, clip) if clip else None
            if clip_path and os.path.exists(clip_path):
                if sec["id"] not in self.clips:
                    self.clips[sec["id"]] = ClipReader(clip_path, ph_w, ph_h, sec.get("clip_in", 0.0))
                scr = self.clips[sec["id"]].at(max(0.0, t - s0)).convert("RGBA")
                mask = Image.new("L", (ph_w, ph_h), 0)
                ImageDraw.Draw(mask).rounded_rectangle((0, 0, ph_w, ph_h), 46, fill=255)
                layer.paste(scr, (px, int(y)), mask)
                lab = sec.get("label", "Real app screens · demo data")
            else:
                rounded(d, (px, y, px + ph_w, y + ph_h), 46, C["surface"] + (255,))
                fp, fq = jakarta(34, "ExtraBold"), jakarta(28, "SemiBold")
                cy = y + ph_h * 0.36
                for ln in ["PLACEHOLDER"]:
                    d.text((px + (ph_w - fp.getlength(ln)) / 2, cy), ln, font=fp, fill=C["orange"] + (255,))
                cy += 60
                for ln in wrap(fq, "Real screen recording needed:", ph_w - 50) + wrap(fq, steps[cur]["placeholder"], ph_w - 50):
                    d.text((px + (ph_w - fq.getlength(ln)) / 2, cy), ln, font=fq, fill=C["cream"] + (255,))
                    cy += 40
                lab = "Placeholder · not real app footage"
            fl = jakarta(24, "SemiBold")
            # vertical label beside the phone (kept inside the safe area)
            lbl = Image.new("RGBA", (int(fl.getlength(lab)) + 10, 40), (0, 0, 0, 0))
            BlendDraw(lbl, "RGBA").text((5, 4), lab, font=fl, fill=C["muted"] + (255,))
            lbl = lbl.rotate(90, expand=True)
            layer.alpha_composite(lbl, (px + ph_w + bez + 14, int(y + ph_h - lbl.height)))
            y = y + ph_h + bez
            log["boxes"].append(("phone", px, y - ph_h, px + ph_w, y))
            # captions overlap the phone bottom by design? keep the phone above the caption band
            if sec.get("foot"):
                a, dy = appear(sec.get("foot_at"))
                y = self.footnote(d, y + 10, sec["foot"], a)

        elif sec["kind"] in ("point", "stats"):
            fn = anton(150)
            d.text((SAFE_X0, y - 30), sec["num"], font=fn, fill=C["orange"] + (255,))
            nx = SAFE_X0 + fn.getlength(sec["num"]) + 34
            ft = anton(sec.get("title_size", 78))
            ty = y - 6
            for ln in [w for part in sec["title"].split("\n") for w in wrap(ft, part, SAFE_X1 - nx)]:
                draw_rich(d, (nx, ty), ln, ft, C["cream"], C["orange"], tracking=1)
                ty += int(ft.size * 1.1)
            y = max(y + 190, ty + 34)
            if sec.get("chip"):
                a, dy = appear(sec["chip"].get("at"))
                y = self.chip(d, SAFE_X0, y + dy, sec["chip"], a) + 26
            card_top = y
            pad = 34
            if sec["kind"] == "point":
                rows = []
                for it in sec["items"]:
                    lines = wrap(self.f_item, it["text"], SAFE_X1 - SAFE_X0 - pad * 2 - 64)
                    rows.append((it, lines))
                card_h = pad * 2 + sum(len(l) * 58 + 26 for _, l in rows) - 26
                ca, cdy = appear(rows[0][0].get("at")) if rows else (255, 0)  # card fades in with its first item
                rounded(d, (SAFE_X0, card_top + cdy, SAFE_X1, card_top + cdy + card_h), 30, C["surface"] + (ca,), outline=C["line"] + (ca,))
                yy = card_top + pad
                for it, lines in rows:
                    a, dy = appear(it.get("at"))
                    ic = ICONS[it.get("icon", "dot")]
                    icol = C[it.get("icon_color", "green_l")]
                    ic(d, SAFE_X0 + pad + 22, yy + 30 + dy, 22, icol, a)
                    for k, ln in enumerate(lines):
                        draw_rich(d, (SAFE_X0 + pad + 64, yy + dy + k * 58), ln, self.f_item, C["cream"], C["orange"], alpha=a)
                    yy += len(lines) * 58 + 26
                y = card_top + card_h
            else:  # stats
                n = len(sec["stats"])
                gap = 24
                cw = (SAFE_X1 - SAFE_X0 - gap * (n - 1)) / n
                fbig, flab = anton(170), jakarta(38, "SemiBold")
                ch = 0
                for i, st in enumerate(sec["stats"]):
                    a, dy = appear(st.get("at"))
                    x0 = SAFE_X0 + i * (cw + gap)
                    labs = wrap(flab, st["label"], cw - 2 * pad)
                    hh = pad * 2 + 200 + len(labs) * 50
                    ch = max(ch, hh)
                    rounded(d, (x0, card_top + dy, x0 + cw, card_top + dy + hh), 30, C["surface"] + (a,), outline=C["line"] + (a,))
                    d.text((x0 + pad, card_top + dy + pad - 18), st["big"], font=fbig, fill=C[st.get("color", "green_l")] + (a,))
                    for k, ln in enumerate(labs):
                        d.text((x0 + pad, card_top + dy + pad + 205 + k * 50), ln, font=flab, fill=C["cream"] + (a,))
                y = card_top + ch
            log["boxes"].append(("card", SAFE_X0, card_top, SAFE_X1, y))
            if sec.get("foot"):
                a, dy = appear(sec.get("foot_at"))
                fy = y + 22
                y = self.footnote(d, fy, sec["foot"], a)
                log["boxes"].append(("foot", SAFE_X0, fy, SAFE_X1, y))

        elif sec["kind"] == "cta":
            a, dy = appear(None)
            gi = sec.get("glyph")
            if gi == "share":
                icon_share(d, SAFE_X0 + 70, y + 70 + dy, 70, C["orange"], a)
            elif gi == "bookmark":
                icon_bookmark(d, SAFE_X0 + 70, y + 70 + dy, 70, C["orange"], a)
            elif gi == "download":
                icon_download(d, SAFE_X0 + 70, y + 70 + dy, 70, C["orange"], a)
            y += 170
            f = fit_font(sec["title"], sec.get("title_size", 116))
            for ln in sec["title"]:
                draw_rich(d, (SAFE_X0, y + dy), ln, f, C["cream"], C["orange"], tracking=1, alpha=a)
                y += int(f.size * 1.12)
            y += 50
            ic = brand_icon(120)
            if a > 0:
                tmp = ic.copy()
                tmp.putalpha(tmp.getchannel("A").point(lambda v: v * a // 255))
                layer.alpha_composite(tmp, (SAFE_X0, int(y + dy)))
            d.text((SAFE_X0 + 146, y + 22 + dy), "Eazy88", font=self.f_brand, fill=C["cream"] + (a,))
            y += 150
            if sec.get("foot"):
                y = self.footnote(d, y + 10, sec["foot"], a)
            log["boxes"].append(("cta_bottom", SAFE_X0, 0, SAFE_X1, y))

        log["bottom"] = y
        self.layout_log.append(log)
        img.alpha_composite(layer)
        return img

    def caption(self, img, t):
        for key, (a, b) in self.cue.items():
            if a <= t < b:
                text = self.timings[key]["text"]
                lines = wrap(self.f_cap, text, 860)
                assert len(lines) <= 2, (key, lines)
                lh = 60
                bw = max(self.f_cap.getlength(l) for l in lines) + 56
                bh = len(lines) * lh + 30
                x0 = (W - bw) / 2
                ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                od = BlendDraw(ov, "RGBA")
                od.rounded_rectangle((x0, CAP_Y, x0 + bw, CAP_Y + bh), 22, fill=C["ink_deep"] + (210,))
                for i, ln in enumerate(lines):
                    lw = self.f_cap.getlength(ln)
                    od.text(((W - lw) / 2, CAP_Y + 12 + i * lh), ln, font=self.f_cap, fill=(255, 255, 255, 255))
                img.alpha_composite(ov)
                return (CAP_Y, CAP_Y + bh)
        return None


# ---------------------------------------------------------------- audio
def load48(path, tmpdir):
    out = os.path.join(tmpdir, os.path.basename(path).replace(".wav", "_48k.wav"))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", path, "-ar", str(SR), "-ac", "1", out], check=True)
    with wave.open(out) as w:
        return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768


def write_wav(path, a, sr=SR):
    a = np.clip(a, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((a * 32767).astype(np.int16).tobytes())


def music_bed(dur, seed=7):
    """Original procedural bed: Fmaj7-G6-Em7-Am7 at 92 BPM. No samples."""
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros(n, np.float32)
    beat = 60 / 92
    bar = 4 * beat
    m = lambda x: 440 * 2 ** ((x - 69) / 12)
    chords = [[53, 57, 60, 64], [55, 59, 62, 64], [52, 55, 59, 62], [57, 60, 64, 67]]
    bass = [41, 43, 40, 45]
    for b in range(int(dur / bar) + 1):
        ch = chords[b % 4]
        s0 = int(b * bar * SR)
        L = int(bar * SR)
        seg = slice(s0, min(n, s0 + L))
        tt = t[seg] - b * bar
        env = np.minimum(1, tt / 0.6) * np.minimum(1, (bar - tt) / 0.4)
        for note in ch:
            f = m(note)
            out[seg] += 0.05 * env * (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(2 * np.pi * 2 * f * tt + 0.3))
        fb = m(bass[b % 4])
        out[seg] += 0.10 * env * np.sin(2 * np.pi * fb * tt)
        for k in range(8):  # pluck arpeggio, eighth notes
            ps = s0 + int(k * beat / 2 * SR)
            if ps >= n:
                break
            pl = min(n - ps, int(0.5 * SR))
            tp = np.arange(pl) / SR
            f = m(ch[[0, 2, 1, 3, 2, 1, 3, 2][k]] + 12)
            out[ps:ps + pl] += 0.05 * np.exp(-tp * 7) * np.sin(2 * np.pi * f * tp)
        for k in range(4):  # soft kick + off-beat shaker
            ks = s0 + int(k * beat * SR)
            if ks < n and k in (0, 2):
                kl = min(n - ks, int(0.25 * SR))
                tk = np.arange(kl) / SR
                out[ks:ks + kl] += 0.22 * np.exp(-tk * 18) * np.sin(2 * np.pi * (50 + 60 * np.exp(-tk * 30)) * tk)
            ss = s0 + int((k + 0.5) * beat * SR)
            if ss < n:
                sl = min(n - ss, int(0.06 * SR))
                nz = rng.standard_normal(sl)
                nz = np.diff(np.concatenate([[0], nz]))  # crude high-pass
                out[ss:ss + sl] += 0.025 * nz * np.exp(-np.arange(sl) / SR * 60)
    return out / (np.abs(out).max() + 1e-9)


def loudnorm(inp, out, extra=None):
    af1 = "alimiter=limit=0.89:level=false,loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json"
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", inp, "-af", af1, "-f", "null", "-"], capture_output=True, text=True)
    js = json.loads(r.stderr[r.stderr.rfind("{"):r.stderr.rfind("}") + 1])
    af2 = ("alimiter=limit=0.89:level=false,loudnorm=I=-16:TP=-1.5:LRA=11:"
           f"measured_I={js['input_i']}:measured_TP={js['input_tp']}:measured_LRA={js['input_lra']}:"
           f"measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", inp, "-af", af2, "-ar", str(SR), out], check=True)


# ---------------------------------------------------------------- main
def draft_band(img, text):
    """Visible marker on previews (above the safe area, never on finals)."""
    d = BlendDraw(img, "RGBA")
    f = jakarta(28, "ExtraBold")
    tw = f.getlength(text)
    d.rounded_rectangle(((W - tw) / 2 - 24, 96, (W + tw) / 2 + 24, 150), 14, fill=C["primary"] + (255,))
    d.text(((W - tw) / 2, 104), text, font=f, fill=C["cream"] + (255,))


def srt_time(x):
    ms = int(round(x * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def main():
    spec_path, audio_dir, out_dir = sys.argv[1:4]
    use_music = "--music" in sys.argv
    spec = json.load(open(spec_path))
    spec["_dir"] = os.path.dirname(os.path.abspath(spec_path))
    timings = json.load(open(os.path.join(audio_dir, "vo_timings.json")))
    os.makedirs(out_dir, exist_ok=True)
    tmp = os.path.join(out_dir, "_tmp")
    os.makedirs(tmp, exist_ok=True)
    base = spec["base"]

    # timeline from real WAV lengths
    clips, cue, starts = {}, {}, {}
    t = 0.15
    for i, sec in enumerate(spec["sections"]):
        if i:
            t += spec.get("section_gap", 0.40)
        starts[sec["id"]] = t
        for j, k in enumerate(sec["cues"]):
            if j:
                t += 0.20
            clips[k] = load48(os.path.join(audio_dir, f"{k}.wav"), tmp)
            cue[k] = [t, t + len(clips[k]) / SR]
            t = cue[k][1]
    dur = t + spec.get("end_hold", 1.5)
    keys = list(cue)
    for a, b in zip(keys, keys[1:]):  # caption stays until next cue starts
        cue[a][1] = cue[b][0]
    cue[keys[-1]][1] = dur
    json.dump({"duration": dur, "sections": starts, "cues": cue}, open(os.path.join(out_dir, "timeline.json"), "w"), indent=1)

    # audio
    n = int(math.ceil(dur * SR))
    voice = np.zeros(n, np.float32)
    for k, c in clips.items():
        s = int(round(cue[k][0] * SR))  # cue starts are the real clip starts
        voice[s:s + len(c)] += c
    write_wav(os.path.join(tmp, "voice_raw.wav"), voice)
    loudnorm(os.path.join(tmp, "voice_raw.wav"), os.path.join(out_dir, f"{base}_Voiceover.wav"))
    if use_music:
        mus = music_bed(dur)
        mus = np.pad(mus, (0, max(0, n - len(mus))))[:n]
        env = np.abs(voice)
        k = int(0.15 * SR)
        env = np.convolve(env, np.ones(k) / k, "same")
        env = np.clip(env / (env.max() + 1e-9) * 3, 0, 1)
        gain = 0.11 - 0.06 * env
        fade = np.ones(n)
        fl = int(1.2 * SR)
        fade[-fl:] = np.linspace(1, 0, fl)
        mix = voice + mus * gain * fade
        write_wav(os.path.join(tmp, "music_only.wav"), mus * gain * fade)
    else:
        mix = voice
    write_wav(os.path.join(tmp, "mix_raw.wav"), mix)
    loudnorm(os.path.join(tmp, "mix_raw.wav"), os.path.join(tmp, "mix.wav"))

    # video
    reel = Reel(spec, timings, {k: tuple(v) for k, v in cue.items()})
    secs = spec["sections"]
    sec_start = [starts[s["id"]] - (0.15 if i == 0 else 0.2) for i, s in enumerate(secs)]
    sec_start[0] = -1.0
    silent = os.path.join(tmp, "video.mp4")
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                           "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.2", silent], stdin=subprocess.PIPE)
    nframes = int(round(dur * FPS))
    cap_log = []
    for fi in range(nframes):
        tt = fi / FPS
        i = max(j for j in range(len(secs)) if sec_start[j] <= tt)
        frame = reel.draw_section(secs[i], tt, max(0, sec_start[i]))
        if i > 0 and tt < sec_start[i] + 0.22:
            prev = reel.draw_section(secs[i - 1], tt, max(0, sec_start[i - 1]))
            frame = Image.blend(prev, frame, ease((tt - sec_start[i]) / 0.22))
        cb = reel.caption(frame, tt)
        cap_log.append(cb)
        if spec.get("draft"):
            draft_band(frame, spec["draft"])
        ff.stdin.write(frame.convert("RGB").tobytes())
        if fi == 0:
            cover = reel.draw_section(secs[0], 0.0, 0)
            if spec.get("draft"):
                draft_band(cover, spec["draft"])
            cover.convert("RGB").save(os.path.join(out_dir, f"{base}_Cover.png"))
    ff.stdin.close()
    ff.wait()

    # layout QC: content must end above captions and stay in safe area
    worst = max(l["bottom"] for l in reel.layout_log)
    bad = sorted({l["section"] for l in reel.layout_log if l["bottom"] > CAP_Y - 16})
    assert not bad, f"content runs into the caption band in sections {bad} (bottom {worst:.0f} > {CAP_Y - 16})"
    json.dump({"max_content_bottom": worst, "caption_top": CAP_Y}, open(os.path.join(out_dir, "layout_qc.json"), "w"))

    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", os.path.join(tmp, "mix.wav"), "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k", "-ar", str(SR), "-ac", "2", "-shortest", "-movflags", "+faststart",
                    os.path.join(out_dir, f"{base}_A.mp4")], check=True)
    with open(os.path.join(out_dir, f"{base}.srt"), "w") as f:
        for i, k in enumerate(keys, 1):
            end = min(cue[k][1], cue[k][0] + len(clips[k]) / SR + 0.3)
            f.write(f"{i}\n{srt_time(cue[k][0])} --> {srt_time(end)}\n{timings[k]['text']}\n\n")
    print(json.dumps({"duration": round(dur, 2), "max_content_bottom": worst}))


if __name__ == "__main__":
    main()
