#!/usr/bin/env python3
"""WORDTS — mọi việc với mốc từng từ của lời đọc, gom một chỗ (thay align.py, check_wordts.py, find_gaps.py,
word_times.py, make_kinetic.py).

  python3 tools/wordts.py align   chX.mp3 chX.txt wordts.json      # căn theo script (PocketSphinx); tự đổi mp3 -> wav 16k
  python3 tools/wordts.py check   wordts.json CHX_asset_plan.xlsx [--voice chX.mp3]
  python3 tools/wordts.py find    wordts.json "last words" fire     # giây của cụm từ (để điền t trong focus.json)
  python3 tools/wordts.py list    wordts.json                       # từng từ + mốc
  python3 tools/wordts.py gaps    wordts.json [--min 0.35]          # câu + khoảng lặng (điểm cắt / dissolve)
  python3 tools/wordts.py auto    wordts.json                       # mệnh đề -> gợi ý hiệu ứng (EDITORIAL-PATTERNS.md)
  python3 tools/wordts.py kinetic wordts.json "Koepcke:JULIANE KOEPCKE" 17 --hold 1.4 > kin.json

wordts.json = [[bắt đầu, kết thúc, "từ"], ...] (giây). build_chapter.py gọi align/check/find tự động.
"""
import argparse, json, os, re, subprocess, sys, tempfile

norm = lambda s: re.sub(r"[^a-z0-9']", "", s.lower().replace("’", "'"))
load = lambda p: json.load(open(p, encoding="utf-8"))

# từ PocketSphinx không có trong từ điển -> từ phát âm gần giống (thêm khi align báo OOV)
SUB = {"awl": "all", "paleolithic": "prehistoric", "sinew": "sin", "combustible": "comfortable", "covering's": "coverings"}


def align(audio, txt, out):
    from pocketsphinx import Decoder
    import wave
    # luôn chuẩn hoá về wav 16 kHz mono (mp3, hay wav khác tần số, đều làm hỏng căn) — không cần gõ ffmpeg riêng
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", audio, "-ar", "16000", "-ac", "1", tmp], check=True)
    audio = tmp
    raw = open(txt, encoding="utf-8").read().replace("—", " ").replace("-", "- ").split()
    words = []
    for w in raw:
        d = re.sub(r"[^a-z']", "", w.lower().replace("’", "'")).strip("'")
        if d: words.append((w, SUB.get(d, d)))
    dec = Decoder(samprate=16000, bestpath=False, beam=1e-80, wbeam=1e-60, pbeam=1e-80)
    oov = []
    for _, d in words:
        try:
            if not dec.lookup_word(d): oov.append(d)
        except Exception: oov.append(d)
    if oov: print("OOV (thêm vào SUB đầu tools/wordts.py):", sorted(set(oov)))
    dec.set_align_text(" ".join(d for _, d in words))
    with wave.open(audio) as f: data = f.readframes(f.getnframes())
    dec.start_utt(); dec.process_raw(data, full_utt=True); dec.end_utt()
    if tmp: os.unlink(tmp)
    if dec.hyp() is None: sys.exit("LỖI căn: PocketSphinx không khớp được script với voice (script sai chương / voice lệch script?)")
    seg =[(w.word, w.start_frame / 100, (w.end_frame + 1) / 100) for w in dec.seg()]
    seg = [s for s in seg if not s[0].startswith(("<", "["))]
    if len(seg) != len(words): sys.exit(f"LỖI căn: {len(seg)} mốc cho {len(words)} từ — script lệch voice?")
    W = [[round(s, 2), round(e, 2), disp] for (disp, _), (_, s, e) in zip(words, seg)]
    json.dump(W, open(out, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"{len(W)} từ, từ cuối kết thúc {W[-1][1]}s -> {out}")


def check(wordts, xlsx, voice=None):
    """Trả về số lỗi. (1) mốc tăng dần, không từ dài bất thường; (2) ranh giới shot gần khoảng lặng; (3) voice ≈ từ cuối."""
    import openpyxl
    W = load(wordts); bad = 0; prev = 0
    def err(m):
        nonlocal bad; bad += 1; print("ERR ", m)
    for i, (s, e, w) in enumerate(W):
        if e < s or s < prev - 0.001: err(f"mốc lệch thứ tự ở từ #{i} '{w}' ({s}-{e})")
        if e - s > 1.5: print(f"WARN DÀI: '{w}' {e - s:.2f}s tại {s}s (căn có thể trôi)")
        if e - s <= 0: err(f"từ '{w}' dài 0 tại {s}s")
        prev = e
    ws = openpyxl.load_workbook(xlsx, data_only=True)["SHOTS"]
    ci = {h: k for k, h in enumerate(c.value for c in ws[1])}
    gaps = [(W[i][1], W[i + 1][0]) for i in range(len(W) - 1) if W[i + 1][0] - W[i][1] >= 0.25]
    n = 0
    for r in ws.iter_rows(min_row=2, values_only=True):
        if not r[0] or str(r[ci["CẢNH"]]).strip() == "0": continue
        m = re.match(r"\s*([\d.,]+)\s*[–-]\s*([\d.,]+)", str(r[ci["PHỦ THỜI GIAN"]]))
        if not m: continue
        t0, t1 = (float(x.replace(",", ".")) for x in m.groups()); n += 1
        if not [x for x in W if x[0] >= t0 - 0.05 and x[1] <= t1 + 0.05]: err(f"{r[0]}: không có từ nào trong {t0}-{t1}s"); continue
        if not (any(g0 - 0.3 <= t0 <= g1 + 0.3 for g0, g1 in gaps) or t0 < 0.5):
            print(f"WARN {r[0]}: ranh giới {t0}s không gần khoảng lặng nào (≥0,25s)")
    print(f"{len(W)} từ, {n} shot, {len(gaps)} khoảng lặng ≥0,25s, từ cuối kết thúc {W[-1][1]}s")
    if voice:
        d = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", voice]))
        print(f"voice {d:.2f}s, lệch với từ cuối {abs(d - W[-1][1]):.2f}s")
        if abs(d - W[-1][1]) > 1.5: err("voice và từ cuối lệch > 1,5s")
    return bad


def find(wordts, phrases):
    toks = [(s, e, w.strip(), norm(w)) for s, e, w in load(wordts)]
    for ph in phrases:
        ws = [norm(x) for x in ph.split()]
        hits = [(toks[i][0], toks[i + len(ws) - 1][1]) for i in range(len(toks) - len(ws) + 1)
                if [t[3] for t in toks[i:i + len(ws)]] == ws]
        print(f'"{ph}": ' + ("; ".join(f"{s:.2f}–{e:.2f}" for s, e in hits) if hits else "KHÔNG THẤY (thử `list`)"))


def gaps(wordts, mn):
    w = load(wordts); cur = [w[0]]; G = []
    print(f"== CÂU (cắt theo khoảng nghỉ >= {mn:.2f}s) ==")
    for p, nx in zip(w, w[1:]):
        if nx[0] - p[1] >= mn:
            G.append((p[1], nx[0])); print(f"{cur[0][0]:6.2f}-{cur[-1][1]:6.2f}  {' '.join(x[2] for x in cur).strip()}"); cur = []
        cur.append(nx)
    print(f"{cur[0][0]:6.2f}-{cur[-1][1]:6.2f}  {' '.join(x[2] for x in cur).strip()}")
    print("\n== KHOẢNG LẶNG (điểm cắt / dissolve; dissolve 0.5s phải nằm TRỌN trong khoảng lặng) ==")
    for s, e in G:
        L = e - s; tag = "dissolve 0.5s VỪA" if L >= 0.5 else f"cắt gọn / dissolve ngắn {min(L, 0.4):.2f}s"
        print(f"{s:6.2f}-{e:6.2f}  ({L:.2f}s)  {tag}  -> start dissolve ~ {max(s, e - 0.5):.2f}")


def auto(wordts, gap):
    toks = [(s, e, w.strip(), norm(w)) for s, e, w in load(wordts)]
    NEG = {"not", "no", "never", "nothing", "none", "nobody", "neither", "nor", "didnt", "wasnt", "couldnt", "wouldnt", "isnt", "dont", "cannot", "cant",
           "didn't", "wasn't", "couldn't", "wouldn't", "isn't", "don't", "can't"}
    NUMW = {"one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve", "twenty", "thirty", "forty", "fifty",
            "hundred", "thousand", "million", "half", "first", "second", "third"}
    TIME = {"days", "day", "hours", "minutes", "weeks", "months", "years", "later", "earlier", "before", "after"}
    clauses, cur = [], [toks[0]]
    for p, n in zip(toks, toks[1:]):
        if n[0] - p[1] >= gap: clauses.append(cur); cur = []
        cur.append(n)
    clauses.append(cur)
    print(f"{'t_start':>7} {'t_end':>6}  mệnh đề  =>  gợi ý (nguyên liệu cho biên tập, không phải quyết định)")
    for c in clauses:
        text = " ".join(x[2] for x in c); sug = []
        for s, e, w, n in c:
            if re.fullmatch(r"\d[\d,]*", n) or n in NUMW: sug.append(f"SỐ '{w}' @{s:.2f} -> ticker (số chạy) / counter_down (đếm lùi)")
            elif n in TIME: sug.append(f"MỐC THỜI GIAN '{w}' @{s:.2f} -> timeline/label")
        sug += [f"TÊN RIÊNG '{w}' @{s:.2f} -> lower_third / tag" for i, (s, e, w, n) in enumerate(c) if w[:1].isupper() and i > 0 and w.lower() != "i"]
        print(f"{c[0][0]:7.2f} {c[-1][1]:6.2f}  {text}")
        for x in sug or ["(không có từ khoá) -> vẫn cần 1 sự kiện: label / spotlight / đổi nhịp camera"]: print(f"{'':16}• {x}")


def kinetic(wordts, kws, hold, size):
    W = [(s, e, norm(w)) for s, e, w in load(wordts)]
    POS = [[640, 340], [520, 420], [760, 290], [640, 380]]; out = []
    for i, k in enumerate(kws):
        parts = k.split(":"); key = norm(parts[0])
        hit = next((s for s, e, w in W if w == key), None)
        if hit is None: print(f"# KHÔNG THẤY '{parts[0]}' trong wordts", file=sys.stderr); continue
        w = {"text": parts[1] if len(parts) > 1 and parts[1] else parts[0].upper(), "t_in": round(hit, 2), "t_out": round(hit + hold, 2),
             "pos": POS[i % len(POS)], "size": size}
        if len(parts) > 2: w["color"] = parts[2]
        out.append(w)
    for x, y in zip(out, out[1:]): x["t_out"] = round(min(x["t_out"], y["t_in"] - 0.05), 2)
    print(json.dumps({"type": "kinetic", "words": out}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("align"); p.add_argument("audio"); p.add_argument("script"); p.add_argument("out")
    p = sp.add_parser("check"); p.add_argument("wordts"); p.add_argument("xlsx"); p.add_argument("--voice")
    p = sp.add_parser("find"); p.add_argument("wordts"); p.add_argument("phrases", nargs="+")
    p = sp.add_parser("list"); p.add_argument("wordts")
    p = sp.add_parser("gaps"); p.add_argument("wordts"); p.add_argument("--min", type=float, default=0.35)
    p = sp.add_parser("auto"); p.add_argument("wordts"); p.add_argument("--gap", type=float, default=0.35)
    p = sp.add_parser("kinetic"); p.add_argument("wordts"); p.add_argument("kw", nargs="+")
    p.add_argument("--hold", type=float, default=1.4); p.add_argument("--size", type=int, default=140)
    a = ap.parse_args()
    if a.cmd == "align": align(a.audio, a.script, a.out)
    elif a.cmd == "check": sys.exit(1 if check(a.wordts, a.xlsx, a.voice) else 0)
    elif a.cmd == "find": find(a.wordts, a.phrases)
    elif a.cmd == "list": [print(f"{s:7.2f} {e:7.2f}  {w}") for s, e, w in load(a.wordts)]
    elif a.cmd == "gaps": gaps(a.wordts, a.min)
    elif a.cmd == "auto": auto(a.wordts, a.gap)
    elif a.cmd == "kinetic": kinetic(a.wordts, a.kw, a.hold, a.size)
