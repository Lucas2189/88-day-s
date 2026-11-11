"""Eazy88 — hostel-demo reel assembler (free, local: ffmpeg + Pillow + numpy).

Assembles: character scene clips (generated elsewhere, lip-synced) + the REAL app screen
recording (demo) + CTA card, with burned subtitles, hook title on frame 0, music bed,
loudness normalisation. Nothing is invented: when a clip is missing, a clearly marked
PLACEHOLDER card is drawn and the output is a PREVIZ (never an export).

Usage: python3 assemble_reel.py spec.json audio_dir out_dir [--hook B] [--music] [--allow-placeholders]
"""
import json, math, os, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "templates", "tools"))
from render_reel import (C, W, H, FPS, SR, SAFE_X0, SAFE_X1, CAP_Y, anton, jakarta, fit_font, draw_rich,  # noqa: E402
                         text_width, wrap, rounded, BlendDraw, brand_icon, make_background, ClipReader,
                         icon_download, music_bed, loudnorm, write_wav, load48, srt_time, draft_band, ease)

SPK_COL = {"B1": (255, 255, 255), "B2": C["sun"]}  # subtitles: two speakers, two tints


def clip_audio48(path, tmp):
    """Mono 48 kHz audio of a character clip (its own lip-synced voice)."""
    out = os.path.join(tmp, os.path.basename(path).rsplit(".", 1)[0] + "_clipaudio_48k.wav")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", path, "-vn", "-ar", str(SR), "-ac", "1", out], check=True)
    with wave.open(out) as w:
        return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768


def has_audio(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=codec_type",
                        "-of", "csv=p=0", path], capture_output=True, text=True)
    return "audio" in r.stdout


class Assembler:
    def __init__(self, spec, timings, cue, hook):
        self.spec, self.timings, self.cue, self.hook = spec, timings, cue, hook
        self.bg = make_background()
        self.f_cap = jakarta(46, "SemiBold")
        self.f_label = jakarta(28, "Bold")
        self.f_small = jakarta(30, "SemiBold")
        self.f_ph = jakarta(34, "ExtraBold")
        self.f_foot = jakarta(27, "Medium")
        self.f_brand = anton(64)
        self.readers, self.placeholders, self.log = {}, set(), []
        self.home = None

    # ------------------------------------------------------------ helpers
    def reader(self, sc, key, path, w, h, start=0.0):
        if key not in self.readers:
            self.readers[key] = ClipReader(path, w, h, start)
        return self.readers[key]

    def placeholder(self, d, box, title, lines):
        x0, y0, x1, y1 = box
        rounded(d, box, 40, C["surface"] + (255,), outline=C["line2"] + (255,), width=3)
        y = y0 + (y1 - y0) * 0.30
        for ln in wrap(self.f_ph, title, x1 - x0 - 80):
            d.text((x0 + (x1 - x0 - self.f_ph.getlength(ln)) / 2, y), ln, font=self.f_ph, fill=C["orange"] + (255,))
            y += 46
        y += 20
        for para in lines:
            for ln in wrap(self.f_small, para, x1 - x0 - 80):
                d.text((x0 + (x1 - x0 - self.f_small.getlength(ln)) / 2, y), ln, font=self.f_small, fill=C["cream"] + (255,))
                y += 42
            y += 10

    def header(self, d, layer):
        layer.alpha_composite(brand_icon(60), (SAFE_X0, 200))
        d.text((SAFE_X0 + 78, 214), self.spec.get("header", "EAZY88"), font=self.f_label, fill=C["muted"] + (255,))

    def hook_title(self, d, t, sc):
        until = sc.get("title_until", 3.6)
        if t > until + 0.3:
            return
        a = int(255 * (1 - ease((t - until) / 0.3))) if t > until else 255
        lines = self.spec["hook_title_B"] if self.hook == "B" else self.spec["hook_title"]
        f = fit_font(lines, 150)
        y = 300
        for ln in lines:
            lw = text_width(f, ln, 1)
            rounded(d, (SAFE_X0 - 18, y - 6, SAFE_X0 + lw + 18, y + f.size * 1.08), 18, C["ink_deep"] + (int(a * 0.72),))
            draw_rich(d, (SAFE_X0, y), ln, f, C["cream"], C["orange"], tracking=1, alpha=a)
            y += int(f.size * 1.12)

    # ------------------------------------------------------------ scenes
    def char_scene(self, sc, t, img, layer, d):
        path = os.path.join(self.spec["_dir"], sc["clip"])
        if os.path.exists(path):
            fr = self.reader(sc, sc["id"], path, W, H, sc.get("clip_in", 0.0)).at(max(0, t - sc["start"]))
            img.paste(fr, (0, 0))
        else:
            self.placeholders.add(sc["id"])
            self.placeholder(d, (SAFE_X0, 520, SAFE_X1, 1150), "CHARACTER SCENE · TO BE GENERATED",
                             [sc["shot"], "File: " + sc["clip"]])
        if sc.get("hook"):
            self.hook_title(d, t, sc)

    def demo_scene(self, sc, t, img, layer, d):
        steps = sc["steps"]
        cur = max(k for k, st in enumerate(steps) if t >= st["t"] - 0.05) if t >= steps[0]["t"] - 0.05 else 0
        # step pills
        fs = jakarta(30, "Bold")
        y = 296
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
        ph_h = 1172 - y
        ph_w = int(ph_h / 2.174)
        px = (W - ph_w) // 2
        bez = 14
        rounded(d, (px - bez, y - bez, px + ph_w + bez, y + ph_h + bez), 58, C["ink_deep"] + (255,), outline=C["line2"] + (255,), width=3)
        path = os.path.join(self.spec["_dir"], sc["clip"])
        if os.path.exists(path):
            st = steps[cur]
            rd = self.reader(sc, "demo", path, ph_w, ph_h, 0.0)
            # recording time: each step maps to a segment of the recording (clip_in), played at natural speed
            frame = rd.at(max(0.0, st["clip_in"] + (t - st["t"])))
            # optional zoom on the field that matters (focus box in 0..1 coordinates of the phone screen)
            if st.get("focus"):
                fx, fy, fw, fh = st["focus"]
                z = st.get("zoom", 1.35)
                zz = 1 + (z - 1) * ease((t - st["t"] - 0.6) / 0.5)  # start zoom 0.6 s into the step
                cx, cy = (fx + fw / 2) * ph_w, (fy + fh / 2) * ph_h
                cw, chh = ph_w / zz, ph_h / zz
                x0 = min(max(0, cx - cw / 2), ph_w - cw)
                y0 = min(max(0, cy - chh / 2), ph_h - chh)
                frame = frame.crop((int(x0), int(y0), int(x0 + cw), int(y0 + chh))).resize((ph_w, ph_h), Image.LANCZOS)
                if zz > 1.02:  # highlight the field
                    hl = ImageDraw.Draw(frame)
                    hx0, hy0 = (fx * ph_w - x0) * zz, (fy * ph_h - y0) * zz
                    hl.rounded_rectangle((hx0 - 8, hy0 - 8, hx0 + fw * ph_w * zz + 8, hy0 + fh * ph_h * zz + 8), 18,
                                         outline=C["orange"], width=5)
            mask = Image.new("L", (ph_w, ph_h), 0)
            ImageDraw.Draw(mask).rounded_rectangle((0, 0, ph_w, ph_h), 46, fill=255)
            layer.paste(frame.convert("RGBA"), (px, int(y)), mask)
            lab = "Real app screens · demo data"
            self.home = frame if cur == len(steps) - 1 else self.home
        else:
            self.placeholders.add("demo")
            self.placeholder(d, (px, y, px + ph_w, y + ph_h), "REAL SCREEN RECORDING NEEDED",
                             ["Step " + str(cur + 1) + " · " + steps[cur]["label"], steps[cur]["shows"], "No interface is invented here."])
            lab = "Placeholder · not real app footage"
        fl = jakarta(24, "SemiBold")
        lbl = Image.new("RGBA", (int(fl.getlength(lab)) + 10, 40), (0, 0, 0, 0))
        BlendDraw(lbl, "RGBA").text((5, 4), lab, font=fl, fill=C["muted"] + (255,))
        lbl = lbl.rotate(90, expand=True)
        layer.alpha_composite(lbl, (px + ph_w + bez + 14, int(y + ph_h - lbl.height)))

    def cta_scene(self, sc, t, img, layer, d):
        a = int(255 * ease((t - sc["start"]) / 0.35))
        y = 300
        f = fit_font(sc["title"], 104)
        for ln in sc["title"]:
            draw_rich(d, (SAFE_X0, y), ln, f, C["cream"], C["orange"], tracking=1, alpha=a)
            y += int(f.size * 1.12)
        y += 44
        ph_h = 1172 - y
        ph_w = int(ph_h / 2.174)
        px = SAFE_X1 - ph_w
        # left column: official icon + name + store line + footnote
        ic = brand_icon(132).copy()
        ic.putalpha(ic.getchannel("A").point(lambda v: v * a // 255))
        layer.alpha_composite(ic, (SAFE_X0, y))
        d.text((SAFE_X0, y + 150), "Eazy88", font=self.f_brand, fill=C["cream"] + (a,))
        d.text((SAFE_X0, y + 236), "Free on the", font=jakarta(36, "SemiBold"), fill=C["orange"] + (a,))
        d.text((SAFE_X0, y + 282), "App Store", font=jakarta(36, "SemiBold"), fill=C["orange"] + (a,))
        fy = y + 360
        for ln in wrap(self.f_foot, sc["foot"], px - SAFE_X0 - 70):
            d.text((SAFE_X0, fy), ln, font=self.f_foot, fill=C["muted"] + (a,))
            fy += 36
        # right column: a real app screen (last frame of the recording, else the official website screen)
        rounded(d, (px - 12, y - 12, px + ph_w + 12, y + ph_h + 12), 48, C["ink_deep"] + (a,), outline=C["line2"] + (a,), width=3)
        src, lab = None, ""
        if self.home is not None:
            src, lab = self.home, "Real app screen · demo data"
        elif sc.get("screen_fallback") and os.path.exists(os.path.join(ROOT, sc["screen_fallback"])):
            src, lab = Image.open(os.path.join(ROOT, sc["screen_fallback"])).convert("RGB"), sc.get("screen_fallback_label", "Real app screen")
        if src is not None:
            scr = src.resize((ph_w, ph_h), Image.LANCZOS).convert("RGBA")
            scr.putalpha(scr.getchannel("A").point(lambda v: v * a // 255))
            mask = Image.new("L", (ph_w, ph_h), 0)
            ImageDraw.Draw(mask).rounded_rectangle((0, 0, ph_w, ph_h), 40, fill=255)
            layer.paste(scr, (px, y), mask)
            fl = jakarta(22, "SemiBold")
            lbl = Image.new("RGBA", (int(fl.getlength(lab)) + 10, 36), (0, 0, 0, 0))
            BlendDraw(lbl, "RGBA").text((5, 3), lab, font=fl, fill=C["muted"] + (a,))
            lbl = lbl.rotate(90, expand=True)
            layer.alpha_composite(lbl, (px - 56, y + ph_h - lbl.height))

    def frame(self, sc, t):
        img = self.bg.copy().convert("RGBA")
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = BlendDraw(layer, "RGBA")
        if sc["kind"] != "char":
            self.header(d, layer)
        getattr(self, sc["kind"] + "_scene")(sc, t, img, layer, d)
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
                od.rounded_rectangle((x0, CAP_Y, x0 + bw, CAP_Y + bh), 22, fill=C["ink_deep"] + (215,))
                col = SPK_COL.get(self.timings[key].get("speaker"), (255, 255, 255))
                for i, ln in enumerate(lines):
                    od.text(((W - self.f_cap.getlength(ln)) / 2, CAP_Y + 12 + i * lh), ln, font=self.f_cap, fill=col + (255,))
                img.alpha_composite(ov)
                return


def build_timeline(spec, audio_dir, hook, tmp):
    """Cue times from real WAV lengths inside the fixed scene windows."""
    clips, cue = {}, {}
    for sc in spec["scenes"]:
        if sc["kind"] == "demo":
            n = len(sc["steps"])
            span = (sc["end"] - sc["start"]) / n
            for k, st in enumerate(sc["steps"]):
                st["t"] = sc["start"] + k * span
                key = st["cue"]
                clips[key] = load48(os.path.join(audio_dir, f"{key}.wav"), tmp)
                cue[key] = [st["t"] + 0.15, st["t"] + 0.15 + len(clips[key]) / SR]
                assert cue[key][1] <= st["t"] + span, (key, "voice longer than its step")
        else:
            t = sc["start"] + sc.get("lead", 0.15)
            for j, key in enumerate(sc["cues"]):
                if hook == "B" and key == spec.get("hook_B_cue_replaces"):
                    key = spec["hook_B_cue"]
                if j:
                    t += 0.30
                clips[key] = load48(os.path.join(audio_dir, f"{key}.wav"), tmp)
                cue[key] = [t, t + len(clips[key]) / SR]
                t = cue[key][1]
            if sc.get("end"):
                assert t <= sc["end"], (sc["id"], "voice runs past the scene end", t)
    return clips, cue


def main():
    spec_path, audio_dir, out_dir = sys.argv[1:4]
    hook = sys.argv[sys.argv.index("--hook") + 1] if "--hook" in sys.argv else "A"
    use_music, allow_ph = "--music" in sys.argv, "--allow-placeholders" in sys.argv
    spec = json.load(open(spec_path))
    spec["_dir"] = os.path.dirname(os.path.abspath(spec_path))
    timings = json.load(open(os.path.join(audio_dir, "vo_timings.json")))
    os.makedirs(out_dir, exist_ok=True)
    tmp = os.path.join(out_dir, "_tmp")
    os.makedirs(tmp, exist_ok=True)
    base = spec["base"] + ("_B" if hook == "B" else "_A")
    clips, cue = build_timeline(spec, audio_dir, hook, tmp)
    dur = spec["duration"]
    # caption display: stays until the next cue starts, at most +0.6 s after the voice ends
    keys = sorted(cue, key=lambda k: cue[k][0])
    show = {}
    scene_end = lambda t0: min(sc["end"] for sc in spec["scenes"] if sc["start"] <= t0 + 1e-6 and sc["end"] > t0)
    for a, b in zip(keys, keys[1:] + [None]):
        end = min(cue[a][1] + 0.6, scene_end(cue[a][0]))
        if b:
            end = min(end, cue[b][0])
        show[a] = (cue[a][0], min(end, dur))

    # ---- audio: Kokoro voice (or the clip's own lip-synced audio for character scenes)
    n = int(math.ceil(dur * SR))
    voice = np.zeros(n, np.float32)
    for sc in spec["scenes"]:
        path = os.path.join(spec["_dir"], sc.get("clip", "")) if sc.get("clip") else None
        if sc["kind"] == "char" and sc.get("audio") == "clip" and path and os.path.exists(path) and has_audio(path):
            a = clip_audio48(path, tmp)
            s = int(sc["start"] * SR)
            voice[s:s + len(a)] += a[:n - s]
            continue
        cues = [st["cue"] for st in sc["steps"]] if sc["kind"] == "demo" else sc["cues"]
        for key in cues:
            if hook == "B" and key == spec.get("hook_B_cue_replaces"):
                key = spec["hook_B_cue"]
            s = int(round(cue[key][0] * SR))
            voice[s:s + len(clips[key])] += clips[key]
    write_wav(os.path.join(tmp, "voice_raw.wav"), voice)
    loudnorm(os.path.join(tmp, "voice_raw.wav"), os.path.join(out_dir, f"{base}_Voiceover.wav"))
    if use_music:
        mus = np.pad(music_bed(dur), (0, n))[:n]
        env = np.abs(voice)
        k = int(0.15 * SR)
        env = np.clip(np.convolve(env, np.ones(k) / k, "same") / (env.max() + 1e-9) * 3, 0, 1)
        gain = 0.11 - 0.06 * env
        fade = np.ones(n)
        fade[-int(1.2 * SR):] = np.linspace(1, 0, int(1.2 * SR))
        mix = voice + mus * gain * fade
        write_wav(os.path.join(tmp, "music_only.wav"), mus * gain * fade)
    else:
        mix = voice
    write_wav(os.path.join(tmp, "mix_raw.wav"), mix)
    loudnorm(os.path.join(tmp, "mix_raw.wav"), os.path.join(tmp, "mix.wav"))

    # ---- video
    asm = Assembler(spec, timings, show, hook)
    scenes = spec["scenes"]
    silent = os.path.join(tmp, "video.mp4")
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                           "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.2", silent], stdin=subprocess.PIPE)
    nframes = int(round(dur * FPS))
    cover = None
    for fi in range(nframes):
        tt = fi / FPS
        i = max(j for j in range(len(scenes)) if scenes[j]["start"] <= tt + 1e-6)
        fr = asm.frame(scenes[i], tt)
        if i > 0 and tt < scenes[i]["start"] + 0.2 and scenes[i].get("transition", "cut") == "blend":
            fr = Image.blend(asm.frame(scenes[i - 1], tt), fr, ease((tt - scenes[i]["start"]) / 0.2))
        asm.caption(fr, tt)
        if asm.placeholders:
            draft_band(fr, "PREVIZ · PLACEHOLDER SCENES · NOT FOR POSTING")
        if fi == 0:
            cover = fr.copy()
        ff.stdin.write(fr.convert("RGB").tobytes())
    ff.stdin.close()
    ff.wait()
    for rd in asm.readers.values():
        rd.p.stdout.close()
        rd.p.terminate()
    if asm.placeholders and not allow_ph:
        sys.exit(f"missing footage for {sorted(asm.placeholders)}: refusing to produce a finished-looking file")
    tag = "_PREVIZ-not-for-posting" if asm.placeholders else ""
    cover.convert("RGB").save(os.path.join(out_dir, f"{base}{tag}_Cover.png"))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", os.path.join(tmp, "mix.wav"), "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k", "-ar", str(SR), "-ac", "2", "-shortest", "-movflags", "+faststart",
                    os.path.join(out_dir, f"{base}{tag}.mp4")], check=True)
    with open(os.path.join(out_dir, f"{base}.srt"), "w") as f:
        for i, k in enumerate(keys, 1):
            f.write(f"{i}\n{srt_time(cue[k][0])} --> {srt_time(show[k][1])}\n{timings[k]['text']}\n\n")
    json.dump({"duration": dur, "hook": hook, "cues": cue, "placeholders": sorted(asm.placeholders)},
              open(os.path.join(out_dir, f"timeline_{hook}.json"), "w"), indent=1)
    print(json.dumps({"out": f"{base}{tag}.mp4", "duration": dur, "placeholders": sorted(asm.placeholders)}))


if __name__ == "__main__":
    main()
