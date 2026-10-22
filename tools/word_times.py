#!/usr/bin/env python3
"""Tra mốc thời gian trong lời đọc + gợi ý sự kiện hình cho từng mệnh đề (từ wordts.json).
  python3 word_times.py wordts.json "forty minutes" "last words"   # thời điểm cụm từ (t_start, t_end)
  python3 word_times.py wordts.json --auto                          # bảng mệnh đề -> hiệu ứng gợi ý
  python3 word_times.py wordts.json --list                          # từng từ + mốc
Gợi ý (--auto) là NGUYÊN LIỆU cho biên tập viên, không phải quyết định: luôn xem lại theo ngữ cảnh.
Quy tắc ngữ pháp hình ảnh nằm ở EDITORIAL-PATTERNS.md.
"""
import json, re, sys, argparse
ap = argparse.ArgumentParser(); ap.add_argument("wordts"); ap.add_argument("phrases", nargs="*")
ap.add_argument("--auto", action="store_true"); ap.add_argument("--list", action="store_true")
ap.add_argument("--gap", type=float, default=0.35)
a = ap.parse_args()
W = json.load(open(a.wordts, encoding="utf-8"))
norm = lambda s: re.sub(r"[^a-z0-9']", "", s.lower())
toks = [(s, e, w.strip(), norm(w)) for s, e, w in W]

if a.list:
    for s, e, w, _ in toks: print(f"{s:7.2f} {e:7.2f}  {w}")
for ph in a.phrases:
    ws = [norm(x) for x in ph.split()]
    hits = [(toks[i][0], toks[i+len(ws)-1][1]) for i in range(len(toks) - len(ws) + 1)
            if [t[3] for t in toks[i:i+len(ws)]] == ws]
    print(f'"{ph}": ' + ("; ".join(f"{s:.2f}–{e:.2f}" for s, e in hits) if hits else "KHÔNG THẤY (Whisper có thể nghe khác — dùng --list)"))

if a.auto:
    NEG = {"not", "no", "never", "nothing", "none", "nobody", "neither", "nor", "didnt", "wasnt", "wasn't", "didn't", "couldn't", "wouldn't", "isn't", "don't", "cannot", "cant", "can't"}
    NUMW = {"one","two","three","four","five","six","seven","eight","nine","ten","eleven","twelve","twenty","thirty","forty","fifty","hundred","thousand","million","half","first","second","third"}
    TIME = {"days","day","hours","minutes","weeks","months","years","later","earlier","before","after"}
    clauses, cur = [], [toks[0]]
    for p, n in zip(toks, toks[1:]):
        if n[0] - p[1] >= a.gap: clauses.append(cur); cur = []
        cur.append(n)
    clauses.append(cur)
    print(f"\n{'t_start':>7} {'t_end':>6}  mệnh đề  =>  gợi ý")
    for c in clauses:
        text = " ".join(x[2] for x in c)
        sug = []
        for s, e, w, n in c:
            if n in NEG or n.endswith("nt"): sug.append(f"PHỦ ĐỊNH '{w}' @{s:.2f} -> strike_cards (gạch đúng đối tượng bị phủ định)")
            elif re.fullmatch(r"\d[\d,]*", n) or n in NUMW: sug.append(f"SỐ '{w}' @{s:.2f} -> ticker/badge_pop (số chạy tới đích đúng lúc từ này)")
            elif n in TIME: sug.append(f"MỐC THỜI GIAN '{w}' @{s:.2f} -> timeline/day_ticker/label")
        caps = [(s, w) for i, (s, e, w, n) in enumerate(c) if w[:1].isupper() and i > 0 and w.lower() not in ("i",)]
        for s, w in caps: sug.append(f"TÊN RIÊNG '{w}' @{s:.2f} -> lower_third / highlight_box nếu có vật thể trong ảnh")
        if text.rstrip().endswith("?"): sug.append("CÂU HỎI -> question_card")
        if re.search(r"\b(said|words were|wrote|ruled|called)\b", text, re.I): sug.append("TRÍCH DẪN/PHÁN QUYẾT -> label dẫn ('HER MOTHER'S LAST WORDS') rồi typed_card chữ thường")
        if not sug: sug.append("(không có từ khoá) -> vẫn cần 1 sự kiện: label chủ đề / spotlight / đổi nhịp camera")
        print(f"{c[0][0]:7.2f} {c[-1][1]:6.2f}  {text}")
        for x in sug: print(f"{'':16}• {x}")
