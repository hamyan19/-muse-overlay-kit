#!/usr/bin/env python3
"""KIỂM wordts.json so với bảng mapping (asset_plan.xlsx) — chạy trước khi dựng.
  python3 tools/check_wordts.py wordts.json asset_plan.xlsx [--voice vo/chX.mp3]
Kiểm: (1) mốc đơn điệu tăng, không từ nào dài bất thường (>1,5s) hoặc bằng 0; (2) mỗi ranh giới shot rơi vào một khoảng
lặng giữa hai từ (≥0,25s) hoặc sát nó; (3) từ đầu/cuối mỗi shot nằm trong khoảng của shot; (4) độ dài voice ≈ từ cuối.
Bước căn bằng PocketSphinx dễ trôi ở từ bị thay cách đọc (awl, sinew, Paleolithic, combustible): xem cảnh báo 'DÀI'."""
import argparse, json, re, subprocess, sys
import openpyxl
ap = argparse.ArgumentParser(); ap.add_argument("wordts"); ap.add_argument("xlsx"); ap.add_argument("--voice")
a = ap.parse_args()
W = json.load(open(a.wordts, encoding="utf-8")); bad = 0
def err(m):
    global bad; bad += 1; print("ERR ", m)
prev = 0
for i, (s, e, w) in enumerate(W):
    if e < s or s < prev - 0.001: err(f"mốc lệch thứ tự ở từ #{i} '{w}' ({s}-{e})")
    if e - s > 1.5: print(f"WARN DÀI: '{w}' {e - s:.2f}s tại {s}s (căn có thể trôi)")
    if e - s <= 0: err(f"từ '{w}' dài 0 tại {s}s")
    prev = e
ws = openpyxl.load_workbook(a.xlsx, data_only=True)["SHOTS"]
H = [c.value for c in ws[1]]; ci = {h: k for k, h in enumerate(H)}
gaps = [(W[i][1], W[i + 1][0]) for i in range(len(W) - 1) if W[i + 1][0] - W[i][1] >= 0.25]
n = 0
for r in ws.iter_rows(min_row=2, values_only=True):
    if not r[0] or str(r[ci["CẢNH"]]).strip() == "0": continue
    m = re.match(r"\s*([\d.,]+)\s*[–-]\s*([\d.,]+)", str(r[ci["PHỦ THỜI GIAN"]]))
    t0, t1 = (float(x.replace(",", ".")) for x in m.groups()); n += 1
    inside = [x for x in W if x[0] >= t0 - 0.05 and x[1] <= t1 + 0.05]
    if not inside: err(f"{r[0]}: không có từ nào trong {t0}-{t1}s"); continue
    near = any(g0 - 0.3 <= t0 <= g1 + 0.3 for g0, g1 in gaps) or t0 < 0.5
    if not near: print(f"WARN {r[0]}: ranh giới {t0}s không gần khoảng lặng nào (≥0,25s)")
print(f"{len(W)} từ, {n} shot, {len(gaps)} khoảng lặng ≥0,25s, từ cuối kết thúc {W[-1][1]}s")
if a.voice:
    d = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", a.voice]))
    print(f"voice {d:.2f}s, lệch với từ cuối {abs(d - W[-1][1]):.2f}s")
    if abs(d - W[-1][1]) > 1.5: err("voice và từ cuối lệch > 1,5s")
sys.exit(1 if bad else 0)
