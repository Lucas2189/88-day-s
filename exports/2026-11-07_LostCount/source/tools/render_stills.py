"""Eazy88 still renderer: Instagram carousel slides (1080x1350) and Stories (1080x1920).

Usage:  python3 -I render_stills.py spec.json out_dir

Same brand system as render_reel.py (official tokens, Anton + Plus Jakarta Sans, official icon).
Each slide is a vertical stack of blocks. The script fails if a block leaves the safe area.
`guide` blocks (sticker areas) are drawn only in the *_guide.png versions, never in finals.
"""
import json, os, sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_reel import (C, BlendDraw, anton, brand_icon, draw_rich, icon_bookmark, icon_check, icon_dot,  # noqa: E402
                         icon_download, icon_share, icon_warn, jakarta, make_background, rounded, text_width, wrap)

FORMATS = {
    # safe areas keep clear of Instagram UI: feed crop/indicators; Stories top bar and reply bar
    "carousel": {"size": (1080, 1350), "x0": 90, "x1": 990, "y0": 60, "y1": 1290},
    "story": {"size": (1080, 1920), "x0": 90, "x1": 990, "y0": 250, "y1": 1580},
}
ICONS = {"check": icon_check, "warn": icon_warn, "dot": icon_dot}
GLYPHS = {"share": icon_share, "bookmark": icon_bookmark, "download": icon_download}


def background(size):
    bg = make_background()  # 1080x1920
    return bg.crop((0, 0) + size).convert("RGBA")


def render(slide, fmt, guide=False, spec_dir="."):
    F = FORMATS[fmt]
    W, H = F["size"]
    x0, x1 = F["x0"], F["x1"]
    img = background((W, H))
    d = BlendDraw(img, "RGBA")
    y = F["y0"]
    width = x1 - x0
    for b in slide["blocks"]:
        k = b["type"]
        if k == "header":
            img.alpha_composite(brand_icon(56), (x0, y))
            d.text((x0 + 74, y + 13), "EAZY88 · BACKPACKER TIPS", font=jakarta(27, "Bold"), fill=C["muted"] + (255,))
            if b.get("counter"):
                f = jakarta(27, "Bold")
                d.text((x1 - f.getlength(b["counter"]), y + 13), b["counter"], font=f, fill=C["muted"] + (255,))
            y += 56 + b.get("after", 70)
        elif k == "spacer":
            y += b["h"]
        elif k == "title":
            size = b.get("size", 120)
            lines = b["lines"]
            while size > 40 and max(text_width(anton(size), l, 1) for l in lines) > width:
                size -= 2
            f = anton(size)
            for ln in lines:
                draw_rich(d, (x0, y), ln, f, C["cream"], C["orange"], tracking=1)
                y += int(size * 1.1)
            y += b.get("after", 30)
        elif k == "numtitle":
            fn = anton(b.get("num_size", 150))
            d.text((x0, y - 28), b["num"], font=fn, fill=C["orange"] + (255,))
            nx = x0 + fn.getlength(b["num"]) + 32
            ft = anton(b.get("size", 84))
            ty = y - 4
            for ln in b["lines"]:
                draw_rich(d, (nx, ty), ln, ft, C["cream"], C["orange"], tracking=1)
                ty += int(ft.size * 1.1)
            y = max(y + 180, ty + 20) + b.get("after", 20)
        elif k == "text":
            f = jakarta(b.get("size", 40), b.get("weight", "Medium"))
            col = C[b.get("color", "cream")]
            lh = int(f.size * 1.35)
            for ln in wrap(f, b["text"], width):
                draw_rich(d, (x0, y), ln, f, col, C["orange"])
                y += lh
            y += b.get("after", 26)
        elif k == "chip":
            f = jakarta(30, "Bold")
            bg, fg = {"orange": ("orange", "bg"), "green": ("green_l", "bg"), "muted": ("line2", "cream")}[b.get("color", "muted")]
            tw = f.getlength(b["text"])
            rounded(d, (x0, y, x0 + tw + 44, y + 58), 29, C[bg] + (255,))
            d.text((x0 + 22, y + 11), b["text"], font=f, fill=C[fg] + (255,))
            y += 58 + b.get("after", 30)
        elif k == "card":
            pad = 36
            f = jakarta(b.get("size", 42), "SemiBold")
            rows = [(it, wrap(f, it["text"], width - pad * 2 - 62)) for it in b["items"]]
            lh = int(f.size * 1.32)
            ch = pad * 2 + sum(len(l) * lh + 24 for _, l in rows) - 24
            rounded(d, (x0, y, x1, y + ch), 30, C["surface"] + (255,), outline=C["line"] + (255,))
            yy = y + pad
            for it, lines in rows:
                ICONS[it.get("icon", "check")](d, x0 + pad + 21, yy + lh / 2, 21, C[it.get("icon_color", "green_l")], 255)
                for i, ln in enumerate(lines):
                    draw_rich(d, (x0 + pad + 62, yy + i * lh), ln, f, C["cream"], C["orange"])
                yy += len(lines) * lh + 24
            y += ch + b.get("after", 26)
        elif k == "note":
            f = jakarta(b.get("size", 36), "SemiBold")
            lines = wrap(f, b["text"], width - 48)
            lh = int(f.size * 1.35)
            hgt = len(lines) * lh + 36
            rounded(d, (x0, y, x1, y + hgt), 22, C["primary_surface_dark"] + (255,), outline=C["orange"] + (255,))
            for i, ln in enumerate(lines):
                draw_rich(d, (x0 + 24, y + 18 + i * lh), ln, f, C["sun"], C["orange"])
            y += hgt + b.get("after", 26)
        elif k == "foot":
            f = jakarta(b.get("size", 25), "Medium")
            for ln in [w for p in b["text"].split("\n") for w in wrap(f, p, width)]:
                d.text((x0, y), ln, font=f, fill=C["muted"] + (255,))
                y += int(f.size * 1.35)
            y += b.get("after", 20)
        elif k == "cta":
            GLYPHS[b.get("glyph", "bookmark")](d, x0 + 46, y + 46, 46, C["orange"], 255)
            f = anton(b.get("size", 64))
            draw_rich(d, (x0 + 116, y + 46 - f.size * 0.62), b["text"], f, C["cream"], C["orange"], tracking=1)
            y += 92 + b.get("after", 24)
        elif k == "brand":
            img.alpha_composite(brand_icon(84), (x0, y))
            d.text((x0 + 104, y + 12), "Eazy88", font=anton(52), fill=C["cream"] + (255,))
            if b.get("sub"):
                sx = x0 + 104 + anton(52).getlength("Eazy88") + 24
                d.text((sx, y + 26), b["sub"], font=jakarta(30, "SemiBold"), fill=C["muted"] + (255,))
            y += 84 + b.get("after", 20)
        elif k == "phone":
            ph_h = b["h"]
            ph_w = int(ph_h / 2.174)
            px = x0 + (width - ph_w) // 2 if b.get("align") == "center" else x0
            bez = 12
            rounded(d, (px - bez, y, px + ph_w + bez, y + ph_h + 2 * bez), 52, C["ink_deep"] + (255,), outline=C["line2"] + (255,), width=3)
            scr = Image.open(os.path.join(spec_dir, b["src"])).convert("RGBA").resize((ph_w, ph_h), Image.LANCZOS)
            mask = Image.new("L", (ph_w, ph_h), 0)
            ImageDraw.Draw(mask).rounded_rectangle((0, 0, ph_w, ph_h), 42, fill=255)
            img.paste(scr, (px, y + bez), mask)
            if b.get("label"):
                f = jakarta(24, "SemiBold")
                lx = px + ph_w + bez + 24
                for i, ln in enumerate(wrap(f, b["label"], x1 - lx)):
                    d.text((lx, y + ph_h - 60 + i * 32), ln, font=f, fill=C["muted"] + (255,))
            y += ph_h + 2 * bez + b.get("after", 24)
        elif k == "guide":
            h = b["h"]
            if guide:
                for gx in range(x0, x1, 28):  # dashed outline
                    d.line([(gx, y), (min(gx + 14, x1), y)], fill=C["orange"] + (255,), width=3)
                    d.line([(gx, y + h), (min(gx + 14, x1), y + h)], fill=C["orange"] + (255,), width=3)
                for gy in range(y, y + h, 28):
                    d.line([(x0, gy), (x0, min(gy + 14, y + h))], fill=C["orange"] + (255,), width=3)
                    d.line([(x1, gy), (x1, min(gy + 14, y + h))], fill=C["orange"] + (255,), width=3)
                f = jakarta(32, "Bold")
                for i, ln in enumerate(wrap(f, b["text"], width - 60)):
                    d.text((x0 + 30, y + 30 + i * 44), ln, font=f, fill=C["orange"] + (255,))
            y += h + b.get("after", 26)
        else:
            raise ValueError(k)
        assert y <= F["y1"], f"{slide['name']}: block {k} ends at y={y} > safe limit {F['y1']}"
    return img, y


def main():
    spec_path, out_dir = sys.argv[1:3]
    spec = json.load(open(spec_path))
    spec_dir = os.path.dirname(os.path.abspath(spec_path))
    os.makedirs(out_dir, exist_ok=True)
    report = {}
    for slide in spec["slides"]:
        img, bottom = render(slide, spec["format"], False, spec_dir)
        img.convert("RGB").save(os.path.join(out_dir, slide["name"] + ".png"))
        if any(b["type"] == "guide" for b in slide["blocks"]):
            g, _ = render(slide, spec["format"], True, spec_dir)
            g.convert("RGB").save(os.path.join(out_dir, slide["name"] + "_guide.png"))
        report[slide["name"]] = bottom
    print(json.dumps(report))


C.setdefault("primary_surface_dark", (0x3A, 0x1D, 0x10))  # site token --ember

if __name__ == "__main__":
    main()
