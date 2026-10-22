#!/usr/bin/env python3
"""Sinh phần tử `kinetic` (chữ bật theo lời) từ wordts.json + danh sách từ khoá.
  python3 make_kinetic.py wordts.json "Koepcke:JULIANE KOEPCKE" "17" "graduated:GRADUATED" "Christmas" --hold 1.4 --size 150 > kin.json
Mỗi tham số: từ_trong_wordts[:chữ_hiển_thị[:màu]]. t_in = lúc từ bắt đầu được nói; t_out = t_in + hold (hoặc tới từ khoá kế tiếp).
Dán kết quả vào `elements` của spec. Vị trí xen kẽ quanh giữa khung để không chồng nhau.
"""
import json, re, sys, argparse
ap = argparse.ArgumentParser(); ap.add_argument("wordts"); ap.add_argument("kw", nargs="+")
ap.add_argument("--hold", type=float, default=1.4); ap.add_argument("--size", type=int, default=140)
a = ap.parse_args()
W = [(s, e, re.sub(r"[^a-z0-9']", "", w.lower())) for s, e, w in json.load(open(a.wordts, encoding="utf-8"))]
POS = [[640, 340], [520, 420], [760, 290], [640, 380]]
words = []
for i, k in enumerate(a.kw):
    parts = k.split(":"); key = re.sub(r"[^a-z0-9']", "", parts[0].lower())
    txt = parts[1] if len(parts) > 1 and parts[1] else parts[0].upper()
    hit = next((s for s, e, w in W if w == key), None)
    if hit is None:
        print(f"# KHÔNG THẤY '{parts[0]}' trong wordts (Whisper có thể viết khác)", file=sys.stderr); continue
    w = {"text": txt, "t_in": round(hit, 2), "t_out": round(hit + a.hold, 2), "pos": POS[i % len(POS)], "size": a.size}
    if len(parts) > 2: w["color"] = parts[2]
    words.append(w)
for x, y in zip(words, words[1:]):
    x["t_out"] = round(min(x["t_out"], y["t_in"] - 0.05), 2)
print(json.dumps({"type": "kinetic", "words": words}, ensure_ascii=False, indent=1))
