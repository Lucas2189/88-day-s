"""Van scenes for Eazy88 POV clips: the orange campervan on an outback road, seen from the side.

The van is the recurring character of the best-performing clips (parking, "just down the road").
Everything is drawn in code with the brand colour tokens; no footage, no samples.
Used by drafts/<date>_<Name>POV/render_*.py together with pov_kit.py.
"""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageOps

from pov_kit import C, FPS, TOK, W, H, BlendDraw, anton, clamp, jakarta, lerp, scaled, smooth  # noqa: F401

RS = 3                                   # artwork resolution (px per world unit)
VAN_W, VAN_H = 340, 170
SIGN_W, SIGN_H, POST = 380, 210, 135
HORIZON = 190                            # world distance from the road line up to the horizon


def col_mix(a, b, e):
    return tuple(int(round(lerp(x, y, e))) for x, y in zip(a, b))


def paste(dst, src, x, y):
    """Paste an RGBA image on an RGB canvas with its alpha, clipped to the canvas."""
    x, y = int(round(x)), int(round(y))
    sx0, sy0 = max(0, -x), max(0, -y)
    sx1, sy1 = min(src.width, dst.width - x), min(src.height, dst.height - y)
    if sx1 > sx0 and sy1 > sy0:
        part = src.crop((sx0, sy0, sx1, sy1))
        dst.paste(part, (x + sx0, y + sy0), part)


def darken(im, dark, k=0.6):
    """Darken an RGBA sprite for night scenes, keeping its alpha."""
    if dark <= 0:
        return im
    rgb = Image.blend(im.convert("RGB"), Image.new("RGB", im.size, C["bg"]), k * dark)
    rgb.putalpha(im.getchannel("A"))
    return rgb


# ---------------------------------------------------------------- the van
def van_art(ss=RS, hubcaps=(True, True), wheels=(True, True), door=True, bumpers=(False, False), surfboard=True):
    """Campervan facing right, VAN_W x VAN_H world units. Parts can be left out (for the breakdown gag).
    Wheels: (rear, front). Bumpers: (rear, front)."""
    im = Image.new("RGBA", (VAN_W * ss, VAN_H * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(im, "RGBA")
    S = lambda *v: tuple(int(round(x * ss)) for x in v)  # noqa: E731
    # drawn facing left (same coordinates as the parking clip), mirrored at the end
    if surfboard:
        d.rounded_rectangle(S(44, 10, 308, 28), 9 * ss, fill=C["cream"] + (255,))
        d.rectangle(S(92, 17, 260, 21), fill=C["green"] + (255,))
    for x in (96, 244):
        d.rectangle(S(x, 28, x + 8, 40), fill=TOK["n800"] + (255,))
    d.rounded_rectangle(S(0, 38, 340, 146), 30 * ss, fill=C["orange"] + (255,))
    d.rectangle(S(0, 104, 340, 112), fill=C["cream"] + (255,))
    d.rounded_rectangle(S(20, 54, 96, 98), 12 * ss, fill=C["bg"] + (255,))
    d.rounded_rectangle(S(108, 54, 186, 98), 10 * ss, fill=C["bg"] + (255,))
    if door:
        d.rounded_rectangle(S(198, 54, 276, 98), 10 * ss, fill=C["bg"] + (255,))
        d.line([S(192, 114), S(192, 140)], fill=C["primary"] + (255,), width=2 * ss)
    else:   # open hole where the side door was
        d.rounded_rectangle(S(194, 50, 282, 142), 8 * ss, fill=C["ink_deep"] + (255,))
    d.ellipse(S(6, 116, 22, 132), fill=C["sun"] + (255,))                     # headlight (front, before mirror)
    if bumpers[1]:
        d.rounded_rectangle(S(-4, 132, 40, 142), 4 * ss, fill=TOK["n600"] + (255,))
    if bumpers[0]:
        d.rounded_rectangle(S(300, 132, 344, 142), 4 * ss, fill=TOK["n600"] + (255,))
    for cx, has_wheel, cap in ((78, wheels[1], hubcaps[1]), (262, wheels[0], hubcaps[0])):
        if has_wheel:
            d.ellipse(S(cx - 30, 110, cx + 30, 170), fill=C["ink_deep"] + (255,))
            d.ellipse(S(cx - 11, 129, cx + 11, 151), fill=(C["cream"] if cap else TOK["n600"]) + (255,))
        else:
            d.pieslice(S(cx - 32, 108, cx + 32, 172), 180, 360, fill=C["ink_deep"] + (255,))   # empty wheel arch
    return ImageOps.mirror(im)


def wheel_art(ss=RS, cap=True):
    im = Image.new("RGBA", (60 * ss, 60 * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(im, "RGBA")
    d.ellipse((0, 0, 60 * ss - 1, 60 * ss - 1), fill=C["ink_deep"] + (255,))
    d.ellipse((19 * ss, 19 * ss, 41 * ss, 41 * ss), fill=(C["cream"] if cap else TOK["n600"]) + (255,))
    d.rectangle((28 * ss, 6 * ss, 32 * ss, 18 * ss), fill=TOK["n800"] + (255,))    # tread mark shows the spin
    return im


# ---------------------------------------------------------------- road signs
SIGN_COLOURS = {"g": (TOK["secondary_dark"], C["cream"]), "r": (TOK["primary_dark"], C["cream"]),
                "y": (C["sun"], TOK["n800"]), "w": (C["cream"], TOK["n800"])}


def sign_art(small, big, colour="g", w=SIGN_W, h=SIGN_H, post=POST, big_size=104):
    """Rectangular sign on two posts. World size (w, h + post); bottom of the posts = ground."""
    bgc, ink = SIGN_COLOURS[colour]
    im = Image.new("RGBA", (w * RS, (h + post) * RS), (0, 0, 0, 0))
    d = BlendDraw(im, "RGBA")
    for px in (w * 0.22, w * 0.78):
        d.rectangle(((px - 6) * RS, (h - 4) * RS, (px + 6) * RS, (h + post) * RS), fill=TOK["n600"] + (255,))
    d.rounded_rectangle((0, 0, w * RS - 1, h * RS), 16 * RS, fill=bgc + (255,))
    d.rounded_rectangle((9 * RS, 9 * RS, w * RS - 1 - 9 * RS, (h - 9) * RS), 10 * RS, outline=ink + (255,), width=4 * RS)
    size = big_size
    fb = anton(size * RS)
    while fb.getlength(big) > (w - 60) * RS:
        size -= 2
        fb = anton(size * RS)
    if small:
        fs = jakarta(34 * RS, "ExtraBold")
        while fs.getlength(small) > (w - 50) * RS:
            fs = jakarta(int(fs.size * 0.95), "ExtraBold")
        _, st, _, sb = fs.getbbox(small)
    else:
        st = sb = 0
    _, bt, _, bb = fb.getbbox(big)
    gap = 16 * RS if small else 0
    total = (sb - st) + gap + (bb - bt)
    y0 = (h * RS - total) / 2
    if small:
        d.text(((w * RS - fs.getlength(small)) / 2, y0 - st), small, font=fs, fill=ink + (255,))
    d.text(((w * RS - fb.getlength(big)) / 2, y0 + (sb - st) + gap - bt), big, font=fb, fill=ink + (255,))
    return im


def hill_profile(x):
    """Distant ranges: smooth bumps with flat-topped mesas."""
    h = 34 + 22 * math.sin(x / 170) + 14 * math.sin(x / 61 + 1.3) + 9 * math.sin(x / 23 + 0.4)
    return min(h, 58)


# ---------------------------------------------------------------- the road
class Road:
    """Outback road scene. `speed(t)` in world px/s; `sky` = [(t, top, horizon, darkness), ...];
    `sun(t, top, hz)` -> (x, y, radius, colour) or None."""

    def __init__(self, dur, speed, sky, sun=None, moon=(820, 120, 40), seed=3, bush_rows=(-52, 46, 60)):
        self.dur, self.speed, self.sky_keys, self.sun, self.moon = dur, speed, sky, sun, moon
        n = int(round(dur * FPS))
        self.XS = np.zeros(n + 2)
        for i in range(1, n + 2):
            self.XS[i] = self.XS[i - 1] + speed((i - 0.5) / FPS) / FPS
        rng = np.random.default_rng(seed)
        self.bushes, x = [], -2500.0
        while x < self.XS[-1] + 4000:
            self.bushes.append((x, rng.choice(bush_rows), rng.uniform(0.7, 1.3)))
            x += rng.uniform(160, 340)
        self.vmax = max(1.0, max(speed(q / FPS) for q in range(0, n + 1)))
        r2 = np.random.default_rng(11)
        self.stars = [(r2.uniform(0, W), r2.uniform(0, 1), r2.uniform(1.5, 3.4)) for _ in range(70)]

    def X(self, t):
        return float(np.interp(t * FPS, np.arange(len(self.XS)), self.XS))

    def sky_at(self, t):
        for (t0, a0, b0, d0), (t1, a1, b1, d1) in zip(self.sky_keys, self.sky_keys[1:]):
            if t0 <= t <= t1:
                e = smooth((t - t0) / (t1 - t0))
                return col_mix(a0, a1, e), col_mix(b0, b1, e), lerp(d0, d1, e)
        k = self.sky_keys[-1]
        return k[1], k[2], k[3]

    def draw(self, t, s, vx, gy, top, van, signs=(), behind_van=None, front_of_van=None, van_dy=0.0, van_angle=0.0,
             bounce=2.0, headlights=True):
        """Draw the band. vx = screen x of the van's rear, gy = road line on screen, top = band top.
        signs = [(world_x_centre, art)]. behind_van / front_of_van: callbacks f(scene, d, ctx).
        Returns (RGBA scene, ctx)."""
        sky_top, sky_hor, dark = self.sky_at(t)
        X = self.X(t)
        scene = Image.new("RGB", (W, H), C["bg"])
        d = ImageDraw.Draw(scene, "RGBA")
        hz = gy - HORIZON * s
        y0 = int(top)
        for y in range(y0, int(hz) + 1, 4):
            e = clamp((y - y0) / max(1, hz - y0))
            d.rectangle((0, y, W, y + 4), fill=col_mix(sky_top, sky_hor, e ** 1.4) + (255,))
        sun = self.sun(t, top, hz) if self.sun else None
        if sun:
            sx, sy, rad, col = sun
            for g, a in ((2.2, 40), (1.6, 70)):
                d.ellipse((sx - rad * g, sy - rad * g, sx + rad * g, sy + rad * g), fill=col + (a,))
            d.ellipse((sx - rad, sy - rad, sx + rad, sy + rad), fill=col + (255,))
        pts = [(x, hz - hill_profile(X * 0.12 + x / max(s, 0.2)) * max(s, 0.35)) for x in range(0, W + 9, 8)]
        d.polygon([(0, hz + 2)] + pts + [(W, hz + 2)], fill=col_mix(C["primary"], TOK["primary_dark"], 0.35) + (255,))
        if hz < H:   # the camera can be high enough to see only sky
            d.rectangle((0, hz, W, H), fill=TOK["primary_dark"] + (255,))
            d.rectangle((0, hz, W, min(H, hz + 10 * s)), fill=C["primary"] + (200,))
        if gy - 34 * s < H:
            d.rectangle((0, gy - 34 * s, W, max(gy - 34 * s, min(H, gy + 26 * s))), fill=TOK["n800"] + (255,))
        d.line([(0, gy - 34 * s), (W, gy - 34 * s)], fill=C["muted"] + (90,), width=max(1, int(3 * s)))
        per, dash = 130, 70
        xw = math.floor((X - vx / s) / per) * per
        while vx + (xw - X) * s < W:
            x0 = vx + (xw - X) * s
            d.rectangle((x0, gy - 6 * s, x0 + dash * s, gy - 1 * s), fill=C["cream"] + (220,))
            xw += per
        for bx, by, k in self.bushes:
            sx = vx + (bx - X) * s
            if -60 < sx < W + 60:
                r = 16 * k * s
                cy = gy + by * s
                for ox, oy, rr in ((-1.1, 0.2, 0.8), (0, -0.25, 1.0), (1.1, 0.2, 0.75)):
                    d.ellipse((sx + ox * r - rr * r, cy + oy * r - rr * r, sx + ox * r + rr * r, cy + oy * r + rr * r),
                              fill=TOK["secondary_dark"] + (255,))
        bob = bounce * (self.speed(t) / self.vmax) * math.sin(t * 31) * s
        vw, vh = VAN_W * s, VAN_H * s
        ctx = dict(t=t, X=X, s=s, vx=vx, gy=gy, top=top, hz=hz, dark=dark, vw=vw, vh=vh,
                   van_y=gy - vh + 8 * s + bob + van_dy, bob=bob, sky_top=sky_top)
        if dark > 0:
            scene = Image.blend(scene, Image.new("RGB", (W, H), C["bg"]), 0.6 * dark)
            d = ImageDraw.Draw(scene, "RGBA")
            for sx, fy, r in self.stars:
                sy = top + 20 + fy * (hz - 90 * s - top - 20)
                d.ellipse((sx - r, sy - r, sx + r, sy + r), fill=C["cream"] + (int(230 * dark),))
            if self.moon:
                mx, my, mr = self.moon[0], top + self.moon[1], self.moon[2]
                d.ellipse((mx - mr * 1.8, my - mr * 1.8, mx + mr * 1.8, my + mr * 1.8), fill=C["cream"] + (int(25 * dark),))
                d.ellipse((mx - mr, my - mr, mx + mr, my + mr), fill=C["cream"] + (int(255 * dark),))
                d.ellipse((mx - mr + 16, my - mr - 6, mx + mr + 16, my + mr - 6), fill=sky_top + (int(255 * dark),))
            if headlights and van is not None:
                fx, fy2 = vx + vw - 6 * s, gy - 46 * s + bob + van_dy
                d.polygon([(fx, fy2 - 6 * s), (fx + 520 * s, fy2 - 70 * s), (fx + 520 * s, fy2 + 40 * s)],
                          fill=C["sun"] + (int(70 * dark),))
        for wx, art in signs:
            sx = vx + (wx - X) * s
            aw, ah = art.width / RS * s, art.height / RS * s
            if sx + aw / 2 < -20 or sx - aw / 2 > W + 20:
                continue
            paste(scene, scaled(("sign", id(art)), art, aw, ah), sx - aw / 2, gy - 34 * s - ah)
        if behind_van:
            behind_van(scene, ImageDraw.Draw(scene, "RGBA"), ctx)
        if van is not None:
            vim = darken(scaled(("van", id(van), round(vw)), van, vw, vh), dark)
            if van_angle:
                vim = vim.rotate(van_angle, expand=True, resample=Image.BICUBIC)
                paste(scene, vim, vx + vw / 2 - vim.width / 2, ctx["van_y"] + vh / 2 - vim.height / 2)
            else:
                paste(scene, vim, vx, ctx["van_y"])
        if front_of_van:
            front_of_van(scene, ImageDraw.Draw(scene, "RGBA"), ctx)
        return scene.convert("RGBA"), ctx


def day_sun(t, top, hz, x=800, y_off=120, rad=46):
    return x, top + y_off, rad, C["cream"]
