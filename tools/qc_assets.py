#!/usr/bin/env python3
"""QC CỨNG nguyên liệu (ảnh + video + âm thanh) TRƯỚC khi gửi anh duyệt — Muse phải chạy và sửa hết FAIL.
  python3 tools/qc_assets.py --root res [--manifest plan/approved_manifest.json] --out qc/ [--strict]
Quét: res/stills/*.png|jpg, res/video/*.mp4|mov|webm, res/sfx/*.wav|mp3, (và res/vo/*.wav nếu có).
Xuất: qc/QC-REPORT.md + qc/qc_report.json. Mã thoát 1 nếu có FAIL (hoặc WARN khi --strict).
ẢNH : đủ 2560x1440 16:9, đọc được/không cụt, độ nét (Laplacian), cháy/đen (clipping), viền đen/trắng, ám màu (ám vàng/xanh),
      mặt người nhìn rõ (cấm), chữ/logo trong hình (OCR nếu có tesseract), ảnh trùng nhau, lệch màu so với cả bộ.
VIDEO: độ phân giải ≥1280x720 16:9, 6–10s, fps, khung đen, ĐỨNG HÌNH (AI video hay bị), nhấp nháy sáng, cắt cảnh ngầm bên trong clip,
      rung (optical flow), mặt người rõ, chữ/logo, đầu-cuối khớp để lặp.
ÂM THANH: độ dài, rung nhạc/đỉnh (peak), méo (clipping), LUFS, im lặng đầu/cuối, tần số mẫu; tên file TEMP/synthetic cần báo.
Những thứ KHÔNG tự động kiểm được (nhân vật nhất quán, tay/chân méo, đúng thời đại/đạo cụ, gore, ý nghĩa) → bắt buộc làm theo QC-ASSETS.md bằng mắt.
"""
import os, sys, json, glob, argparse, subprocess, re
import numpy as np, cv2
ap = argparse.ArgumentParser()
ap.add_argument("--root", default="."); ap.add_argument("--manifest", default=""); ap.add_argument("--out", default="qc")
ap.add_argument("--strict", action="store_true"); ap.add_argument("--min-sharp", type=float, default=60.0)
a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
R = []   # (loại, file, mức, thông điệp)
def add(kind, f, lvl, msg): R.append((kind, f, lvl, msg))

# ---- tiện ích
def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)
def probe(p):
    o = run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", p])
    try: return json.loads(o.stdout)
    except Exception: return {}
_face = None
def faces(gray):
    global _face
    if _face is None:
        try: _face = cv2.CascadeClassifier(os.path.join(cv2.data.haarcascades, "haarcascade_frontalface_default.xml"))
        except Exception: _face = False
    if not _face or _face.empty():
        global NO_FACE; NO_FACE = True; return None
    g = cv2.resize(gray, (960, int(gray.shape[0] * 960 / gray.shape[1])))
    f = _face.detectMultiScale(g, 1.1, 6, minSize=(48, 48))
    return len(f)
NO_FACE = False
HAS_TESS = bool(run(["which", "tesseract"]).stdout.strip())
def text_in(im):
    if not HAS_TESS: return None
    t = cv2.cvtColor(cv2.resize(im, (1280, int(im.shape[0] * 1280 / im.shape[1]))), cv2.COLOR_BGR2GRAY)
    p = os.path.join(a.out, "_ocr.png"); cv2.imwrite(p, t)
    o = run(["tesseract", p, "-", "--psm", "11", "-l", "eng", "tsv"]).stdout.splitlines()
    words = []
    for ln in o[1:]:
        c = ln.split("\t")
        if len(c) >= 12 and c[11].strip():
            try: conf = float(c[10])
            except Exception: continue
            t = c[11].strip()
            if conf >= 80 and len(re.findall(r"[A-Za-z]", t)) >= 3 and len(t) <= 20: words.append(t)
    return words if len(words) >= 2 else []
def ahash(im):
    g = cv2.resize(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY), (16, 16), interpolation=cv2.INTER_AREA).astype(np.float32)
    return (g > g.mean()).flatten()

def check_frame(kind, name, im, strict_size=True):
    h, w = im.shape[:2]
    if kind == "ẢNH" and (w, h) != (2560, 1440):
        add(kind, name, "FAIL" if w < 2560 or abs(w / h - 16 / 9) > 0.02 else "WARN", f"kích thước {w}x{h} (cần 2560x1440, 16:9)")
    g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    small = cv2.resize(g, (1280, int(1280 * h / w)))
    sharp = float(cv2.Laplacian(small, cv2.CV_64F).var())
    if sharp < a.min_sharp: add(kind, name, "WARN" if sharp > a.min_sharp / 2 else "FAIL", f"mờ/ít chi tiết (độ nét {sharp:.0f} < {a.min_sharp:.0f})")
    lum = float(g.mean())
    if lum < 30: add(kind, name, "WARN", f"rất tối ({lum:.0f}/255) — chỉ ổn nếu là cảnh im lặng chủ đích")
    if lum > 215: add(kind, name, "WARN", f"quá sáng ({lum:.0f}/255)")
    clip_hi = float((g >= 250).mean()); clip_lo = float((g <= 4).mean())
    if clip_hi > 0.12: add(kind, name, "WARN", f"cháy sáng {clip_hi*100:.0f}% điểm ảnh")
    if clip_lo > 0.35: add(kind, name, "WARN", f"đen đặc {clip_lo*100:.0f}% điểm ảnh")
    top, bot = g[: max(2, h // 60)].mean(), g[-max(2, h // 60):].mean()
    left, right = g[:, : max(2, w // 60)].mean(), g[:, -max(2, w // 60):].mean()
    if min(top, bot) < 6 or min(left, right) < 6: add(kind, name, "FAIL", "viền đen ở mép khung (letterbox/pillarbox dính vào ảnh) — render lại full khung")
    if max(top, bot, left, right) > 248 and lum < 200: add(kind, name, "WARN", "viền trắng ở mép khung")
    b, gg, r = [float(im[:, :, i].mean()) for i in range(3)]
    if r / max(b, 1) > 1.55 and r > gg * 1.08: add(kind, name, "WARN", f"ÁM VÀNG/CAM (R/B={r/max(b,1):.2f}) — warmth làm ở hậu kỳ, gen ảnh màu tự nhiên")
    if b / max(r, 1) > 1.5: add(kind, name, "WARN", f"ám xanh lạnh (B/R={b/max(r,1):.2f})")
    nf = faces(g)
    if nf: add(kind, name, "FAIL", f"phát hiện {nf} mặt người nhìn rõ — quy ước: KHÔNG thấy rõ mặt (quay lưng/silhouette)")
    tw = text_in(im)
    if tw and len(tw) >= 2: add(kind, name, "FAIL", f"có thể có CHỮ/LOGO trong hình: {', '.join(tw[:6])} — cấm chữ/logo")
    return b, gg, r, lum

# ---- ẢNH
stills = sorted(glob.glob(os.path.join(a.root, "stills", "*.*")))
stills = [s for s in stills if s.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))]
H, cols = {}, {}
for p in stills:
    n = os.path.relpath(p, a.root)
    im = cv2.imread(p)
    if im is None: add("ẢNH", n, "FAIL", "không đọc được / file hỏng / cụt"); continue
    try:
        from PIL import Image; Image.open(p).verify()
    except Exception as e: add("ẢNH", n, "FAIL", f"file ảnh lỗi: {e}"); continue
    b, g, r, lum = check_frame("ẢNH", n, im)
    cols[n] = (b, g, r, lum); hh = ahash(im)
    for o, oh in H.items():
        if (hh == oh).mean() > 0.94: add("ẢNH", n, "WARN", f"quá giống {o} — hai cảnh cùng một hình")
    H[n] = hh
if len(cols) >= 4:
    arr = np.array([[v[2] / max(v[0], 1), v[3]] for v in cols.values()]); med = np.median(arr, axis=0)
    for n, (b, g, r, lum) in cols.items():
        rb = r / max(b, 1)
        if abs(rb - med[0]) > 0.45: add("ẢNH", n, "WARN", f"lệch tông màu so với cả bộ (R/B {rb:.2f} vs trung vị {med[0]:.2f}) — kiểm style bible")
        if abs(lum - med[1]) > 70: add("ẢNH", n, "WARN", f"độ sáng lệch cả bộ ({lum:.0f} vs trung vị {med[1]:.0f}) — chủ đích?")

# ---- VIDEO
vids = [p for p in sorted(glob.glob(os.path.join(a.root, "video", "*.*"))) if p.lower().endswith((".mp4", ".mov", ".webm", ".mkv"))]
for p in vids:
    n = os.path.relpath(p, a.root); info = probe(p)
    vs = [s for s in info.get("streams", []) if s.get("codec_type") == "video"]
    if not vs: add("VIDEO", n, "FAIL", "không có luồng hình"); continue
    v = vs[0]; w, h = int(v["width"]), int(v["height"]); d = float(info["format"].get("duration", 0))
    fr = v.get("avg_frame_rate", "0/1"); fps = (lambda x: float(x[0]) / max(float(x[1]), 1))(fr.split("/"))
    if w < 1280 or abs(w / h - 16 / 9) > 0.02: add("VIDEO", n, "FAIL", f"{w}x{h} (cần ≥1280x720, 16:9)")
    if not (5.5 <= d <= 10.5): add("VIDEO", n, "WARN", f"dài {d:.1f}s (nên 6–10s)")
    if fps < 23: add("VIDEO", n, "WARN", f"fps thấp {fps:.1f}")
    cap = cv2.VideoCapture(p); N = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or int(d * fps)
    idx = np.linspace(0, max(N - 2, 0), min(24, max(N, 2))).astype(int); fr_ = []
    for i in idx:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(i)); ok, f = cap.read()
        if ok: fr_.append(f)
    if len(fr_) < 6: add("VIDEO", n, "FAIL", "không đọc đủ khung hình"); continue
    lums = np.array([cv2.cvtColor(f, cv2.COLOR_BGR2GRAY).mean() for f in fr_])
    if (lums < 8).any(): add("VIDEO", n, "FAIL", f"có khung ĐEN ({int((lums<8).sum())}/{len(lums)} mẫu) — cắt bỏ")
    if lums.std() > 22: add("VIDEO", n, "WARN", f"nhấp nháy sáng/đổi sáng mạnh (σ={lums.std():.0f})")
    gs = [cv2.cvtColor(cv2.resize(f, (320, 180)), cv2.COLOR_BGR2GRAY).astype(np.float32) for f in fr_]
    diffs = np.array([np.abs(x - y).mean() for x, y in zip(gs, gs[1:])])
    if diffs.max() < 0.35: add("VIDEO", n, "FAIL", "ĐỨNG HÌNH (gần như không chuyển động) — video AI lỗi/không có giá trị hơn ảnh tĩnh")
    elif diffs.mean() < 0.9: add("VIDEO", n, "WARN", f"chuyển động rất ít (Δ trung bình {diffs.mean():.2f}) — cân nhắc dùng ảnh + fx thay vì video")
    hists = [cv2.calcHist([f], [0, 1, 2], None, [8, 8, 8], [0, 256] * 3) for f in fr_]
    cuts = [i for i, (x, y) in enumerate(zip(hists, hists[1:])) if cv2.compareHist(cv2.normalize(x, x).flatten(), cv2.normalize(y, y).flatten(), cv2.HISTCMP_CORREL) < 0.55]
    if cuts: add("VIDEO", n, "FAIL", f"có CẮT CẢNH ngầm bên trong clip (tại mẫu {cuts}) — mỗi clip phải là 1 cảnh liền")
    # rung: optical flow trung vị giữa các mẫu liên tiếp mật độ cao
    jit = []
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0); prev = None; cnt = 0
    while cnt < 90:
        ok, f = cap.read()
        if not ok: break
        s = cv2.cvtColor(cv2.resize(f, (320, 180)), cv2.COLOR_BGR2GRAY)
        if prev is not None:
            fl = cv2.calcOpticalFlowFarneback(prev, s, None, 0.5, 2, 15, 2, 5, 1.1, 0)
            jit.append(np.median(fl.reshape(-1, 2), axis=0))
        prev = s; cnt += 1
    if len(jit) > 12:
        j = np.array(jit); acc = np.abs(np.diff(j, axis=0)).mean()
        if acc > 0.35: add("VIDEO", n, "WARN", f"camera RUNG/giật (gia tốc {acc:.2f}) — yêu cầu camera ổn định")
    nf = max(((faces(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)) or 0) for f in fr_[::4]))
    if nf: add("VIDEO", n, "FAIL", "phát hiện mặt người nhìn rõ trong clip — quy ước: không thấy rõ mặt")
    tw = text_in(fr_[len(fr_) // 2])
    if tw and len(tw) >= 2: add("VIDEO", n, "FAIL", f"có thể có CHỮ/LOGO trong clip: {', '.join(tw[:6])}")
    loop = np.abs(gs[0] - gs[-1]).mean()
    if loop > 25: add("VIDEO", n, "INFO", f"đầu/cuối khác nhau nhiều ({loop:.0f}) — sẽ lộ chỗ nối nếu clip phải lặp")
    if any(s.get("codec_type") == "audio" for s in info.get("streams", [])): add("VIDEO", n, "INFO", "có luồng âm thanh — sẽ KHÔNG dùng (chỉ lấy hình)")

# ---- ÂM THANH
auds = [p for p in sorted(glob.glob(os.path.join(a.root, "sfx", "*.*")) + glob.glob(os.path.join(a.root, "vo", "*.wav"))) if p.lower().endswith((".wav", ".mp3", ".m4a", ".ogg", ".flac"))]
TEMP = re.compile(r"(temp|synth|placeholder|_tam)", re.I)
for p in auds:
    n = os.path.relpath(p, a.root); info = probe(p)
    st = [s for s in info.get("streams", []) if s.get("codec_type") == "audio"]
    if not st: add("ÂM", n, "FAIL", "không đọc được âm thanh"); continue
    d = float(info["format"].get("duration", 0)); sr = int(st[0].get("sample_rate", 0))
    if d < 0.2: add("ÂM", n, "FAIL", f"quá ngắn {d:.2f}s")
    if sr and sr < 32000: add("ÂM", n, "WARN", f"tần số mẫu thấp {sr} Hz")
    o = run(["ffmpeg", "-hide_banner", "-nostats", "-i", p, "-af", "ebur128=peak=true,astats=metadata=0", "-f", "null", "-"]).stderr
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", o); lufs = float(m[-1]) if m else None
    pk = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", o); peak = float(pk[-1]) if pk else None
    if peak is not None and peak > -0.5: add("ÂM", n, "WARN", f"đỉnh {peak:.1f} dBFS — nguy cơ méo (clipping)")
    if lufs is not None and lufs < -50 and "silence" not in n: add("ÂM", n, "WARN", f"gần như im lặng ({lufs:.0f} LUFS) — kiểm lại")
    if "/vo/" in n.replace("\\", "/") and lufs is not None and abs(lufs + 14) > 1.5: add("ÂM", n, "WARN", f"VO {lufs:.1f} LUFS (chuẩn −14 ±1.5)")
    sil = run(["ffmpeg", "-hide_banner", "-i", p, "-af", "silencedetect=n=-45dB:d=1.0", "-f", "null", "-"]).stderr
    st0 = re.search(r"silence_start: (-?[\d.]+)", sil)
    if st0 and float(st0.group(1)) <= 0.05 and "/vo/" not in n.replace("\\", "/") and "near_silence" not in n: add("ÂM", n, "INFO", "im lặng/fade ở đầu file (≥1s) — cắt bớt nếu không chủ đích")
    if TEMP.search(os.path.basename(p)): add("ÂM", n, "WARN", "tên file gợi ý TEMP/tổng hợp tạm — ghi rõ trong báo cáo để anh biết thay bản thật")

# ---- manifest: file thiếu
if a.manifest and os.path.exists(a.manifest):
    for it in json.load(open(a.manifest, encoding="utf-8"))["items"]:
        if it.get("approval", it.get("status")) in ("OK", "SỬA") and it.get("file") and not os.path.exists(os.path.join(a.root, it["file"])):
            add("THIẾU", it["file"], "FAIL", f"{it['id']} đã duyệt nhưng chưa giao file")

# ---- báo cáo
order = {"FAIL": 0, "WARN": 1, "INFO": 2}
R.sort(key=lambda x: (order[x[2]], x[0], x[1]))
nf, nw = sum(1 for r in R if r[2] == "FAIL"), sum(1 for r in R if r[2] == "WARN")
L = ["# QC REPORT — nguyên liệu", "", f"Ảnh: {len(stills)} · Video: {len(vids)} · Âm thanh: {len(auds)} · **FAIL {nf} · WARN {nw}**", ""
     f"(OCR chữ/logo: {'bật' if HAS_TESS else 'TẮT — không có tesseract: phải kiểm bằng mắt'} · nhận diện mặt: {'TẮT — không có haarcascade: phải kiểm bằng mắt' if NO_FACE else 'bật'})", "",
     "| Mức | Loại | File | Vấn đề |", "|---|---|---|---|"]
for k, f, l, m in R: L.append(f"| {l} | {k} | `{f}` | {m} |")
if not R: L.append("| — | — | — | không phát hiện vấn đề tự động |")
L += ["", "> Tự động KHÔNG thay được mắt: làm tiếp QC-ASSETS.md (nhân vật nhất quán, tay/chân, đúng thời đại, gore, ý nghĩa) và điền bảng QC thủ công."]
open(os.path.join(a.out, "QC-REPORT.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
json.dump([{"kind": k, "file": f, "level": l, "msg": m} for k, f, l, m in R], open(os.path.join(a.out, "qc_report.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("\n".join(L[:3]))
for k, f, l, m in R[:40]: print(f"  {l:4} {k:5} {f}: {m}")
sys.exit(1 if nf or (a.strict and nw) else 0)
