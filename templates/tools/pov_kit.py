"""Shared toolkit for Eazy88 POV clips (format: POV humour, no voiceover).

Everything is original: illustrations drawn in code, brand fonts and colour tokens (eazy88.com CSS),
procedural music (no samples). Used by the drafts/<date>_<Name>POV/render_*.py scripts.
The first clip (drafts/2026-11-16_ParkingSignPOV) predates this kit and keeps its own copy of these helpers.
"""
import json
import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_reel import (C, FPS, H, SR, W, BlendDraw, anton, brand_icon, draw_rich, fit_font,  # noqa: E402,F401
                         icon_share, jakarta, loudnorm, make_background, text_width, write_wav)

# extra brand tokens (eazy88.com CSS variables)
TOK = {
    "primary_dark": (0xA0, 0x43, 0x1C), "secondary_dark": (0x14, 0x78, 0x39),
    "n600": (0x6B, 0x61, 0x55), "n800": (0x33, 0x2D, 0x26),
}
SAFE = (80, 220, 940, 1380)


# ---------------------------------------------------------------- maths
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def lerp(a, b, e):
    return a + (b - a) * e


def ease_out_back(x, k=1.7):
    x = clamp(x) - 1
    return 1 + (k + 1) * x ** 3 + k * x ** 2


def ease_out_cubic(x):
    return 1 - (1 - clamp(x)) ** 3


def spring(pos, vel, target, omega, sub=4):
    """One frame of a critically damped spring (smooth start and stop)."""
    for _ in range(sub):
        vel += (omega ** 2 * (target - pos) - 2 * omega * vel) / (FPS * sub)
        pos += vel / (FPS * sub)
    return pos, vel


# ---------------------------------------------------------------- drawing
def ink(font, s):
    l, t, r, b = font.getbbox(s)
    return l, t, r - l, b - t


def draw_ink(d, x, y, s, font, col, alpha=255):
    """Draw text so that the top-left of its ink box sits at (x, y)."""
    l, t, _, _ = ink(font, s)
    d.text((x - l, y - t), s, font=font, fill=tuple(col[:3]) + (alpha,))


def faded(im, a):
    if a >= 0.999:
        return im
    out = im.copy()
    out.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
    return out


def comp(dst, src, x, y):
    """alpha_composite that accepts positions partly outside the canvas."""
    x, y = int(round(x)), int(round(y))
    sx0, sy0 = max(0, -x), max(0, -y)
    sx1, sy1 = min(src.width, dst.width - x), min(src.height, dst.height - y)
    if sx1 <= sx0 or sy1 <= sy0:
        return
    if (sx0, sy0, sx1, sy1) != (0, 0, src.width, src.height):
        src = src.crop((sx0, sy0, sx1, sy1))
    dst.alpha_composite(src, (x + sx0, y + sy0))


_scaled = {}


def scaled(key, im, w, h):
    w, h = max(1, int(round(w))), max(1, int(round(h)))
    k = (key, w, h)
    if k not in _scaled:
        if len(_scaled) > 800:
            _scaled.clear()
        _scaled[k] = im.resize((w, h), Image.LANCZOS)
    return _scaled[k]


def place_art(dst, art, res, ox, oy, s, clip=(0, 0, W, H)):
    """Draw a big world-space artwork (rendered at `res` px per world unit, world origin at its top-left)
    with screen = (ox, oy) + world * s, resampling only the visible part."""
    k = s / res
    x0, y0 = max(clip[0], ox), max(clip[1], oy)
    x1, y1 = min(clip[2], ox + art.width * k), min(clip[3], oy + art.height * k)
    if x1 - x0 < 1 or y1 - y0 < 1:
        return
    ix0, iy0, ix1, iy1 = int(math.floor(x0)), int(math.floor(y0)), int(math.ceil(x1)), int(math.ceil(y1))
    box = ((ix0 - ox) / k, (iy0 - oy) / k, (ix1 - ox) / k, (iy1 - oy) / k)
    box = (max(0, box[0]), max(0, box[1]), min(art.width, box[2]), min(art.height, box[3]))
    tile = art.resize((ix1 - ix0, iy1 - iy0), Image.BICUBIC, box=box, reducing_gap=2.0 if k < 0.5 else None)
    comp(dst, tile, ix0, iy0)


def shadow_for(w, h, r=18, blur=14, alpha=130, dy=10):
    im = Image.new("RGBA", (int(w) + 80, int(h) + 80), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((40, 40 + dy, 40 + w, 40 + dy + h), r, fill=(0, 0, 0, alpha))
    return im.filter(ImageFilter.GaussianBlur(blur))


def aa_layer(draw_fn, box, ss=3):
    """Draw with `draw_fn(d, ox, oy, ss)` on a supersampled layer covering screen `box`; return (layer, x, y)."""
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    w, h = max(1, x1 - x0), max(1, y1 - y0)
    big = Image.new("RGBA", (w * ss, h * ss), (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(big, "RGBA"), x0, y0, ss)
    return big.resize((w, h), Image.LANCZOS), x0, y0


def make_static(header, label):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = BlendDraw(im, "RGBA")
    im.alpha_composite(brand_icon(60), (80, 200))
    d.text((158, 214), header, font=jakarta(28, "Bold"), fill=C["muted"] + (255,))
    d.text((80, 272), label, font=jakarta(24, "Medium"), fill=C["muted"] + (255,))
    return im


def text_block(lines, size, max_w, x, y, lh=1.1, min_size=40):
    f = fit_font(lines, size, max_w)
    assert f.size >= min_size, f"text too long for {max_w}px: {lines}"
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = BlendDraw(im, "RGBA")
    for ln in lines:
        assert x + text_width(f, ln, 1) <= SAFE[2] + 1, f"text leaves the safe area: {ln}"
        draw_rich(d, (x, y), ln, f, C["cream"], C["orange"], tracking=1)
        y += int(f.size * lh)
    return im, y, f.size


def make_cta(lines, y_icon, size=52, x=80, max_w=860):
    """Share icon + 2-3 lines in Anton. Returns (layer, bottom_y)."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = BlendDraw(im, "RGBA")
    icon_share(d, x + 36, y_icon, 36, C["orange"], 255)
    f = fit_font(lines, size, max_w)
    y = y_icon + 56
    for ln in lines:
        assert x + text_width(f, ln, 1) <= SAFE[2] + 1, f"CTA leaves the safe area: {ln}"
        draw_rich(d, (x, y), ln, f, C["cream"], C["orange"], tracking=1)
        y += int(f.size * 1.12)
    return im, y


SIGNATURE = ("Eazy88", " · free app to track your 88 days")   # verified: free iOS app, 88-day tracking


def make_signature(y=1296):
    """Brand end card (not a call to action): app icon + name + what it is, in a pill. Returns (layer, box)."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = BlendDraw(im, "RGBA")
    f1, f2 = jakarta(30, "ExtraBold"), jakarta(30, "SemiBold")
    ic, pad, gap, h = 44, 22, 14, 64
    tw = f1.getlength(SIGNATURE[0]) + f2.getlength(SIGNATURE[1])
    w = pad + ic + gap + tw + pad
    x0 = (W - w) / 2
    assert x0 >= SAFE[0] and y + h <= SAFE[3], (x0, y + h)
    d.rounded_rectangle((x0, y, x0 + w, y + h), h / 2, fill=C["surface"] + (240,), outline=C["line2"] + (255,), width=2)
    im.alpha_composite(brand_icon(ic), (int(x0 + pad), int(y + (h - ic) / 2)))
    _, t, _, b = f1.getbbox("Eazy88")
    ty = y + h / 2 - (t + b) / 2
    tx = x0 + pad + ic + gap
    d.text((tx, ty), SIGNATURE[0], font=f1, fill=C["cream"] + (255,))
    d.text((tx + f1.getlength(SIGNATURE[0]), ty), SIGNATURE[1], font=f2, fill=C["muted"] + (255,))
    return im, (x0, y, x0 + w, y + h)


_masks = {}


def band_mask(top, bottom, feather=36):
    """Vertical band (soft edges) where the illustrated scene is visible."""
    top, bottom = int(round(top)), int(round(bottom))
    k = (top, bottom, feather)
    if k not in _masks:
        if len(_masks) > 400:
            _masks.clear()
        m = Image.new("L", (W, H), 0)
        d = ImageDraw.Draw(m)
        d.rectangle((0, top + feather, W, bottom - feather), fill=255)
        for i in range(feather):
            v = int(255 * (i + 1) / (feather + 1))
            d.line([(0, top + i), (W, top + i)], fill=v)
            d.line([(0, bottom - 1 - i), (W, bottom - 1 - i)], fill=v)
        _masks[k] = m
    return _masks[k]


# ---------------------------------------------------------------- video I/O and QC
class Encoder:
    def __init__(self, path):
        self.path = path
        self.p = subprocess.Popen(
            ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
             "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
             "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.2", path], stdin=subprocess.PIPE)

    def write(self, frame):
        self.p.stdin.write(frame.convert("RGB").tobytes())

    def close(self):
        self.p.stdin.close()
        assert self.p.wait() == 0, "ffmpeg failed"


def finish(out_dir, base, silent_mp4, music, tmp):
    """Normalise the music to -16 LUFS and mux it with the silent video (AAC stereo)."""
    write_wav(os.path.join(tmp, "music_raw.wav"), music)
    loudnorm(os.path.join(tmp, "music_raw.wav"), os.path.join(tmp, "music.wav"))
    mp4 = os.path.join(out_dir, f"{base}_A.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent_mp4, "-i", os.path.join(tmp, "music.wav"),
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", str(SR), "-ac", "2", "-shortest",
                    "-movflags", "+faststart", mp4], check=True)
    return mp4


def contact_sheet(mp4, times, out_png, tmp, cols=6):
    ims = []
    for tt in times:
        fp = os.path.join(tmp, f"f_{tt:.2f}.png")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{tt:.2f}", "-i", mp4, "-frames:v", "1", fp],
                       check=True)
        im = Image.open(fp).resize((270, 480))
        ImageDraw.Draw(im).text((6, 6), f"{tt:.2f}s", fill=(255, 0, 255))
        ims.append(im)
    sheet = Image.new("RGB", (cols * 274, ((len(ims) + cols - 1) // cols) * 484), "white")
    for i, im in enumerate(ims):
        sheet.paste(im, ((i % cols) * 274, (i // cols) * 484))
    sheet.save(out_png)


def audio_report(mp4):
    """Loudness, true peak, share of energy below 150 Hz, level of the first and last half-second."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", mp4, "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    summ = r[r.rfind("Summary:"):]
    lufs = float(summ.split("I:")[1].split("LUFS")[0])
    peak = float(summ.split("Peak:")[1].split("dBFS")[0])
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", mp4, "-vn", "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                         capture_output=True).stdout
    a = np.frombuffer(raw, np.int16) / 32768
    P = np.abs(np.fft.rfft(a)) ** 2
    fr = np.fft.rfftfreq(len(a), 1 / SR)
    db = lambda x: round(20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9), 1)  # noqa: E731
    h = SR // 2
    return {"lufs": lufs, "true_peak_dbfs": peak, "share_below_150hz": round(float(P[fr < 150].sum() / P.sum()), 3),
            "first_half_s_dbfs": db(a[:h]), "last_half_s_dbfs": db(a[-h:]), "duration_s": round(len(a) / SR, 2)}


def probe(mp4):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                          "stream=codec_name,width,height,r_frame_rate,channels,sample_rate",
                          "-show_entries", "format=duration", "-of", "json", mp4], capture_output=True, text=True).stdout
    j = json.loads(out)
    v = [s for s in j["streams"] if s["codec_name"] == "h264"][0]
    a = [s for s in j["streams"] if s["codec_name"] == "aac"][0]
    return {"video": f'{v["codec_name"]} {v["width"]}x{v["height"]} {v["r_frame_rate"]}',
            "audio": f'{a["codec_name"]} {a["sample_rate"]} Hz {a["channels"]} ch',
            "duration_s": round(float(j["format"]["duration"]), 2)}


# ---------------------------------------------------------------- procedural music (no samples)
class Synth:
    def __init__(self, seed=88):
        self.rng = np.random.default_rng(seed)

    @staticmethod
    def put(buf, sig, t0):
        i = int(round(t0 * SR))
        j = min(len(buf), i + len(sig))
        if j > i >= 0:
            buf[i:j] += sig[: j - i]

    def tone(self, f, dur, amp, a=0.01, r=0.2, nh=14, tilt=1.2, detune=(-6, 0, 6), bright=None,
             glide=None, vib=0.0, vib_rate=5.5, vib_delay=0.15, wah=None):
        """Band-limited additive tone. glide=(f_end, start_s); vib = depth (ratio); wah=(fc_start, fc_end) Hz."""
        n = int((dur + r) * SR)
        t = np.arange(n) / SR
        fr = np.full(n, float(f))
        if glide:
            f1, g0 = glide
            g = np.clip((t - g0) / max(dur - g0, 1e-3), 0, 1)
            fr = f * (f1 / f) ** g
        if vib:
            fr = fr * (1 + vib * np.clip((t - vib_delay) / 0.25, 0, 1) * np.sin(2 * np.pi * vib_rate * t))
        fmax = fr.max()
        out = np.zeros(n)
        for c in detune:
            ph = 2 * np.pi * np.cumsum(fr * 2 ** (c / 1200)) / SR + self.rng.uniform(0, 6.28)
            for k in range(1, nh + 1):
                if fmax * k > 7000:
                    break
                g = 1 / k ** tilt
                if bright:
                    g = g * (1 + (k - 1) * 0.12 * np.exp(-t * bright))
                if wah:
                    fc = wah[0] + (wah[1] - wah[0]) * np.clip(t / dur, 0, 1)
                    g = g / (1 + (k * fr / fc) ** 4)
                out += g * np.sin(k * ph)
        env = np.minimum(1, t / a) * np.where(t < dur, 1.0, np.exp(-(t - dur) / (r / 3.5)))
        return amp * out / len(detune) * env

    def pluck(self, f, dur, amp, decay=0.996, soft=3):
        """Karplus-Strong plucked string (ukulele / guitar)."""
        n = int(dur * SR)
        N = max(2, int(round(SR / f)))
        y = np.zeros(n + 2 * N)
        burst = self.rng.uniform(-1, 1, N)
        if soft > 1:
            burst = np.convolve(burst, np.ones(soft) / soft, "same")
        y[:N] = burst
        b = 1
        while b * N < len(y):
            s0, s1 = b * N, min((b + 1) * N, len(y))
            prev = y[s0 - N:s1 - N]
            prev2 = y[s0 - N - 1:s1 - N - 1] if s0 - N - 1 >= 0 else np.concatenate([[0.0], y[s0 - N:s1 - N - 1]])
            y[s0:s1] = decay * 0.5 * (prev + prev2)
            b += 1
        out = y[:n]
        fl = min(n, int(0.05 * SR))
        out[-fl:] *= np.linspace(1, 0, fl)
        return amp * out / (np.abs(out).max() + 1e-9)

    def timp(self, f, amp, dur=1.0, decay=4.5):
        n = int(dur * SR)
        t = np.arange(n) / SR
        ph = 2 * np.pi * np.cumsum(f * (1 + 0.45 * np.exp(-t * 38))) / SR
        body = (np.sin(ph) * np.exp(-t * decay) + 0.3 * np.sin(1.5 * ph) * np.exp(-t * decay * 1.6)
                + 0.18 * np.sin(2 * ph) * np.exp(-t * decay * 2))
        thud = np.convolve(self.rng.standard_normal(n), np.ones(32) / 32, "same") * np.exp(-t * 42) * 2.2
        return amp * (body + thud)

    def cymbal(self, amp, dur=2.6, swell=0.0, decay=1.9):
        n = int((dur + swell) * SR)
        t = np.arange(n) / SR
        x = np.diff(np.diff(self.rng.standard_normal(n), prepend=0.0), prepend=0.0)
        x /= np.abs(x).max()
        env = np.where(t < swell, 0.55 * (t / max(swell, 1e-6)) ** 2.5, np.exp(-(t - swell) * decay))
        return amp * x * env

    def tick(self, amp, f=1250.0):
        n = int(0.12 * SR)
        t = np.arange(n) / SR
        return amp * (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2.76 * t)) * np.exp(-t * 55)

    def snare(self, amp):
        n = int(0.14 * SR)
        t = np.arange(n) / SR
        x = np.diff(self.rng.standard_normal(n), prepend=0.0)
        return amp * x / np.abs(x).max() * np.exp(-t * 38)

    def kick(self, amp):
        n = int(0.3 * SR)
        t = np.arange(n) / SR
        ph = 2 * np.pi * np.cumsum(55 + 110 * np.exp(-t * 30)) / SR
        return amp * np.sin(ph) * np.exp(-t * 9)

    def clap(self, amp):
        n = int(0.2 * SR)
        t = np.arange(n) / SR
        x = np.diff(self.rng.standard_normal(n), prepend=0.0)
        env = sum(np.exp(-np.clip(t - d, 0, None) * 60) * (t >= d) for d in (0, 0.011, 0.023)) / 3
        return amp * x / np.abs(x).max() * env

    def slap(self, amp):
        """Paper note slapped on a fridge door: bright noise burst + a small thump."""
        n = int(0.16 * SR)
        t = np.arange(n) / SR
        x = np.diff(self.rng.standard_normal(n), prepend=0.0)
        x = np.convolve(x, np.ones(6) / 6, "same")   # softer top end: fewer inter-sample peaks
        thump = np.sin(2 * np.pi * 170 * t) * np.exp(-t * 35)
        return amp * (0.8 * x / np.abs(x).max() * np.exp(-t * 70) + 0.6 * thump)

    def bell(self, f, amp, dur=1.2):
        n = int(dur * SR)
        t = np.arange(n) / SR
        out = sum(g * np.sin(2 * np.pi * f * m * t) * np.exp(-t * d)
                  for m, g, d in ((1, 1, 3.5), (2.76, 0.45, 6), (5.4, 0.22, 10), (8.93, 0.1, 16)))
        return amp * out * np.minimum(1, t / 0.002)

    def squeak(self, dur, amp, f0=1900, f1=2500):
        """Marker pen squeak on paper."""
        n = int(dur * SR)
        t = np.arange(n) / SR
        fr = f0 + (f1 - f0) * t / dur + 120 * np.sin(2 * np.pi * 23 * t)
        ph = 2 * np.pi * np.cumsum(fr) / SR
        env = np.minimum(1, t / 0.02) * np.minimum(1, (dur - t) / 0.03)
        noise = np.convolve(self.rng.standard_normal(n), np.ones(4) / 4, "same") * 0.25
        return amp * env * (np.sin(ph) * (0.6 + 0.4 * np.sin(2 * np.pi * 37 * t)) + noise)

    def scratch(self, amp):
        """Record scratch: fast pitch drop with grit, then a short pull back."""
        n = int(0.32 * SR)
        t = np.arange(n) / SR
        fr = np.where(t < 0.2, 1400 * (130 / 1400) ** (t / 0.2), 130 + 900 * (t - 0.2) / 0.12)
        ph = 2 * np.pi * np.cumsum(fr) / SR
        saw = 2 * ((ph / (2 * np.pi)) % 1) - 1
        grit = np.convolve(self.rng.standard_normal(n), np.ones(6) / 6, "same")
        env = np.minimum(1, t / 0.005) * np.exp(-t * 4)
        return amp * env * (0.7 * saw + 0.5 * grit)

    def whoosh(self, dur, amp, peak=0.6):
        """Air whoosh: noise through a moving one-pole low-pass, swelling to `peak` (fraction of dur)."""
        n = int(dur * SR)
        t = np.arange(n) / SR
        x = self.rng.standard_normal(n)
        pos = t / dur
        env = np.where(pos < peak, (pos / peak) ** 2, ((1 - pos) / (1 - peak)) ** 1.5)
        cut = 300 + 3500 * env
        a = np.exp(-2 * np.pi * cut / SR)
        y = np.empty(n)
        acc = 0.0
        for i in range(n):
            acc = a[i] * acc + (1 - a[i]) * x[i]
            y[i] = acc
        return amp * env * y / (np.abs(y).max() + 1e-9)

    def master(self, m, reverb=0.3, rev_time=1.6, fade=0.6, sub=0.55):
        """Hall reverb, no rumble, less sub-bass, gentle low-pass, soft limiter, fade-out."""
        n = len(m)
        ir_n = int(rev_time * SR)
        ti = np.arange(ir_n) / SR
        ir = np.convolve(self.rng.standard_normal(ir_n) * np.exp(-ti * 5.5 / rev_time), np.ones(10) / 10, "same")
        ir[: int(0.012 * SR)] = 0
        N = 1 << int(np.ceil(np.log2(n + ir_n)))
        wet = np.fft.irfft(np.fft.rfft(m, N) * np.fft.rfft(ir, N), N)[:n]
        wet *= 0.9 * np.abs(m).max() / (np.abs(wet).max() + 1e-9)
        mix = m + reverb * wet
        F = np.fft.rfft(mix)
        fr = np.fft.rfftfreq(n, 1 / SR)
        F *= 1 / np.sqrt(1 + (fr / 9000) ** 6)
        F *= sub + (1 - sub) / (1 + (120 / np.maximum(fr, 1e-3)) ** 4)
        F[fr < 45] = 0
        mix = np.fft.irfft(F, n)
        mix = np.tanh(1.5 * mix / np.abs(mix).max()) / np.tanh(1.5)
        if fade:
            fl = int(fade * SR)
            mix[-fl:] *= np.linspace(1, 0, fl) ** 1.5
        return 0.9 * mix
