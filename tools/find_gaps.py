#!/usr/bin/env python3
"""Tìm khoảng lặng của giọng đọc từ wordts.json (Whisper word timestamps) và gợi ý điểm cắt/dissolve.
  python3 find_gaps.py wordts.json [--min 0.35]
In ra: mỗi câu (start,end,text) + các khoảng lặng >= min giây (nơi an toàn để cắt cảnh / dissolve 0.5s).
Quy tắc: dissolve 0.5s phải NẰM TRỌN trong khoảng lặng => start_dissolve >= gap_start-0.05 và start+0.5 <= gap_end+0.05.
"""
import json, sys, argparse
ap = argparse.ArgumentParser(); ap.add_argument("wordts"); ap.add_argument("--min", type=float, default=0.35)
a = ap.parse_args()
w = json.load(open(a.wordts, encoding="utf-8"))
print("== CÂU (cắt theo khoảng nghỉ >= %.2fs) ==" % a.min)
cur = [w[0]]
gaps = []
for prev, nx in zip(w, w[1:]):
    g = nx[0] - prev[1]
    if g >= a.min:
        gaps.append((prev[1], nx[0]))
        print(f"{cur[0][0]:6.2f}-{cur[-1][1]:6.2f}  {''.join(x[2] for x in cur).strip()}")
        cur = []
    cur.append(nx)
print(f"{cur[0][0]:6.2f}-{cur[-1][1]:6.2f}  {''.join(x[2] for x in cur).strip()}")
print("\n== KHOẢNG LẶNG (điểm cắt / dissolve) ==")
for s, e in gaps:
    L = e - s
    tag = "dissolve 0.5s VỪA" if L >= 0.5 else ("cắt gọn / dissolve ngắn %.2fs" % min(L, 0.4))
    print(f"{s:6.2f}-{e:6.2f}  ({L:.2f}s)  {tag}  -> đặt start dissolve ~ {max(s, e-0.5):.2f}")
