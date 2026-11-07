# make_voiceover.py — copied from the marketing instructions (Kokoro-82M ONNX, Apache-2.0). Free, runs locally.
# Usage: python3 -I make_voiceover.py model.onnx voices.bin config.json out_dir af_heart vo_lines.json
# vo_lines.json: [["h1","Heading regional for harvest work?","hˈɛdɪŋ ɹˈiʤənəl fəɹ hˈɑɹvəst wˈɜɹk?"], ...]
# Model files (not in Git): https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/
#   kokoro-v1.0.int8.onnx, voices-v1.0.bin ; config.json = src/kokoro_onnx/config.json from the repo.
import json, os, sys, wave, numpy as np, onnxruntime as ort
model, voices, cfg, out, voice, lines = sys.argv[1:7]
SPEED = float(os.environ.get("VO_SPEED", "1.0")); vocab = json.load(open(cfg))["vocab"]
sess = ort.InferenceSession(model, providers=["CPUExecutionProvider"]); names = {i.name: i for i in sess.get_inputs()}
tok = "input_ids" if "input_ids" in names else "tokens"; pack = np.load(voices)[voice]
sdt = np.int32 if "int" in names["speed"].type else np.float32; report = {}
for key, text, ph in json.load(open(lines)):
    assert all(c in vocab for c in ph), (key, [c for c in ph if c not in vocab])
    t = [vocab[c] for c in ph]; style = pack[len(t) - 1].astype(np.float32).reshape(1, -1)
    a = sess.run(None, {tok: np.array([[0, *t, 0]], dtype=np.int64), "style": style, "speed": np.array([SPEED], dtype=sdt)})[0].squeeze()
    idx = np.where(np.abs(a) > 0.01)[0]; a = a[max(0, idx[0] - 600): idx[-1] + 2400] if len(idx) else a
    with wave.open(f"{out}/{key}.wav", "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes((np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes())
    report[key] = {"text": text, "seconds": round(len(a) / 24000, 2)}
json.dump(report, open(f"{out}/vo_timings.json", "w"), indent=1); print(report)
