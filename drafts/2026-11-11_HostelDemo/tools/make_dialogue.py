"""Kokoro-82M (Apache-2.0) dialogue synthesis, two distinct voices. Free, local.
Usage: python3 make_dialogue.py model.onnx voices.bin config.json dialogue.json out_dir
Phonemes: misaki G2P (US or British per speaker); fixed spelling Eazy88 = ˈizi ˈAɾi ˈAt.
"""
import json, os, sys, wave, numpy as np, onnxruntime as ort
from misaki import en
model, voices, cfg, dlg, out = sys.argv[1:6]
SPEED = float(os.environ.get("VO_SPEED", "1.0"))
vocab = json.load(open(cfg))["vocab"]
sess = ort.InferenceSession(model, providers=["CPUExecutionProvider"])
names = {i.name: i for i in sess.get_inputs()}
tok = "input_ids" if "input_ids" in names else "tokens"
packs = np.load(voices)
sdt = np.int32 if "int" in names["speed"].type else np.float32
D = json.load(open(dlg)); g2p = {}
report = {}
for key, spk, text in D["lines"]:
    sp = D["speakers"][spk]
    if spk not in g2p:
        g2p[spk] = en.G2P(trf=False, british=sp["british"], fallback=None)
    ph, _ = g2p[spk](text)
    ph = ph.replace("❓", "ˈizi")  # "Eazy" is unknown to misaki -> fixed brand spelling (88 is phonemized normally)
    bad = [c for c in ph if c not in vocab]
    assert not bad, (key, bad, ph)
    t = [vocab[c] for c in ph]
    style = packs[sp["voice"]][len(t) - 1].astype(np.float32).reshape(1, -1)
    a = sess.run(None, {tok: np.array([[0, *t, 0]], dtype=np.int64), "style": style,
                        "speed": np.array([SPEED], dtype=sdt)})[0].squeeze()
    idx = np.where(np.abs(a) > 0.01)[0]
    a = a[max(0, idx[0] - 600): idx[-1] + 2400] if len(idx) else a
    with wave.open(f"{out}/{key}.wav", "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000)
        w.writeframes((np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes())
    report[key] = {"text": text, "speaker": spk, "voice": sp["voice"], "phonemes": ph, "seconds": round(len(a) / 24000, 2)}
    print(key, spk, report[key]["seconds"], ph)
json.dump(report, open(f"{out}/vo_timings.json", "w"), indent=1, ensure_ascii=False)
