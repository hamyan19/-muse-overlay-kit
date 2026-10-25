# usage: align.py audio16k.wav script.txt out_wordts.json
import sys, re, json, wave
from pocketsphinx import Decoder
wav, txt, out = sys.argv[1:4]
raw = open(txt).read().replace("—"," ").replace("-", "- ").split()
SUB={"awl":"all","paleolithic":"prehistoric","sinew":"sin","combustible":"comfortable","covering's":"coverings"}
words = []          # (display word, dict word)
for w in raw:
    d = re.sub(r"[^a-z']", "", w.lower().replace("’", "'")).strip("'")
    if d: words.append((w, SUB.get(d, d)))
dec = Decoder(samprate=16000, bestpath=False, beam=1e-80, wbeam=1e-60, pbeam=1e-80)
oov = []
for _, d in words:
    try:
        if not dec.lookup_word(d): oov.append(d)
    except Exception: oov.append(d)
if oov: print("OOV:", sorted(set(oov)))
dec.set_align_text(" ".join(d for _, d in words))
with wave.open(wav) as f: data = f.readframes(f.getnframes())
dec.start_utt(); dec.process_raw(data, full_utt=True); dec.end_utt()
print("hyp ok:", dec.hyp() is not None)
seg = [(w.word, w.start_frame / 100, (w.end_frame + 1) / 100) for w in dec.seg()]
seg = [s for s in seg if not s[0].startswith(("<", "["))]
assert len(seg) == len(words), (len(seg), len(words))
W = [[round(s, 2), round(e, 2), disp] for (disp, _), (_, s, e) in zip(words, seg)]
json.dump(W, open(out, "w"), ensure_ascii=False)
print(len(W), "words, last ends", W[-1][1])
