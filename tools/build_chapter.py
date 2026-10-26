#!/usr/bin/env python3
"""BUILD CHAPTER — một lệnh cho cả quy trình dựng một chương, chỉ dừng ở 2 chỗ cần mắt (đọc toạ độ, xem khung kiểm).

  # B1 plan: spec + TẤM GHÉP ảnh có lưới (đọc toạ độ cả chương trong 1 lần xem) + khung focus.json / pos.json để điền
  python3 tools/build_chapter.py plan   --ch 3 --xlsx plan/CH3_asset_plan.xlsx --vo ch3.mp3 --stills anh_ch3/ --preset documentary
  # (điền work/ch3/focus.json và work/ch3/pos.json bằng toạ độ đọc trên work/ch3/contact.jpg)
  # B2 check: áp điểm nhấn + lớp phủ + lint + 1 TẤM khung kiểm đúng lúc từng điểm nhấn/lớp phủ
  python3 tools/build_chapter.py check  --ch 3
  # B3 render: --quick = 1280x720 @15fps (nhanh ~2 lần, để duyệt) | mặc định 1920x1080 @30fps (bản chính). Nên chạy nền.
  python3 tools/build_chapter.py render --ch 3 --quick

Thư mục làm việc: work/chX/ (res/stills, res/vo, res/fonts, spec*.json, focus.json, pos.json, contact.jpg, check.jpg, chX_*.mp4).
In ra rất ít dòng (đủ để quyết định), để tiết kiệm token. Chi tiết lỗi xem file log trong work/chX/.
"""
import argparse, glob, json, os, re, shutil, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = lambda n: os.path.join(ROOT, "tools", n)
ap = argparse.ArgumentParser(); ap.add_argument("stage", choices=["plan", "check", "render"])
ap.add_argument("--ch", required=True); ap.add_argument("--xlsx"); ap.add_argument("--vo"); ap.add_argument("--stills")
ap.add_argument("--preset"); ap.add_argument("--work", default="work"); ap.add_argument("--quick", action="store_true")
ap.add_argument("--jobs", type=int, default=os.cpu_count() or 4)
a = ap.parse_args()
tag = f"CH{a.ch}" if str(a.ch).isdigit() else str(a.ch).upper()
W = os.path.join(a.work, tag.lower()); R = os.path.join(W, "res"); CFG = os.path.join(W, "build.json")
LOG = open(os.path.join(W, "build.log"), "a") if os.path.isdir(W) else None

def run(cmd, quiet=True):
    p = subprocess.run([sys.executable] + cmd, capture_output=True, text=True)
    if LOG: LOG.write("$ " + " ".join(cmd) + "\n" + p.stdout + p.stderr + "\n"); LOG.flush()
    if p.returncode: sys.exit(f"LỖI ở {os.path.basename(cmd[0])}:\n" + (p.stdout + p.stderr)[-1500:])
    return p.stdout

def font(sz):
    for f in glob.glob(os.path.join(ROOT, "fonts", "*Bold*.ttf")): return ImageFont.truetype(f, sz)
    return ImageFont.load_default()

def sheet(items, out, tw=640, cols=3, grid=True):
    """items = [(nhãn, đường dẫn ảnh)] -> 1 ảnh ghép. grid: lưới mỗi 320px ảnh nguồn 2560x1440, số ở mỗi 640px."""
    th = tw * 9 // 16; rows = (len(items) + cols - 1) // cols
    S = Image.new("RGB", (cols * tw, rows * (th + 26)), (20, 20, 20)); d = ImageDraw.Draw(S); f, f2 = font(18), font(13)
    for i, (lab, path) in enumerate(items):
        x, y = (i % cols) * tw, (i // cols) * (th + 26)
        im = Image.open(path).convert("RGB").resize((tw, th)); S.paste(im, (x, y + 26)); d.text((x + 6, y + 4), lab, fill=(255, 220, 40), font=f)
        if grid:
            k = tw / 2560
            for gx in range(320, 2560, 320):
                d.line((x + gx * k, y + 26, x + gx * k, y + 26 + th), fill=(255, 60, 60) if gx % 640 == 0 else (255, 160, 160), width=1)
                if gx % 640 == 0: d.text((x + gx * k + 2, y + 28), str(gx), fill=(255, 255, 0), font=f2)
            for gy in range(320, 1440, 320):
                d.line((x, y + 26 + gy * k, x + tw, y + 26 + gy * k), fill=(255, 60, 60) if gy % 640 == 0 else (255, 160, 160), width=1)
                d.text((x + 2, y + 26 + gy * k + 2), str(gy), fill=(255, 255, 0), font=f2)
    S.save(out, quality=82); return out

if a.stage == "plan":
    for x in ("xlsx", "vo", "stills"):
        if not getattr(a, x): sys.exit(f"plan cần --{x}")
    os.makedirs(os.path.join(R, "stills"), exist_ok=True); os.makedirs(os.path.join(R, "vo"), exist_ok=True)
    LOG = open(os.path.join(W, "build.log"), "a")
    shutil.copytree(os.path.join(ROOT, "fonts"), os.path.join(R, "fonts"), dirs_exist_ok=True)
    vo = os.path.join(R, "vo", os.path.basename(a.vo)); shutil.copy(a.vo, vo)
    small = []
    for p in sorted(glob.glob(os.path.join(a.stills, "*.png")) + glob.glob(os.path.join(a.stills, "*.jpg"))):
        name = os.path.splitext(os.path.basename(p))[0] + ".png"
        if re.search(r"_L\d", name): shutil.copy(p, os.path.join(R, "stills", name)); continue   # ảnh lớp phủ L01: giữ nguyên cỡ
        im = Image.open(p).convert("RGB")
        if im.size[0] >= 2560 and abs(im.size[1] / im.size[0] - 0.5625) < 0.01: pass   # ảnh lớn (4K…) giữ nguyên: engine zoom sâu vẫn nét
        elif im.size != (2560, 1440): small.append(f"{name} {im.size[0]}x{im.size[1]}"); im = im.resize((2560, 1440), Image.LANCZOS)
        im.save(os.path.join(R, "stills", name))
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", vo], capture_output=True, text=True).stdout or 0)
    cmd = [T("mapping_to_spec.py"), a.xlsx, "--vo", "vo/" + os.path.basename(vo), "--name-from-id", "--include-pending", "--calm",
           "--duration", f"{dur:.2f}", "--out", os.path.join(W, "spec.json")]
    if a.preset: cmd += ["--preset", a.preset]
    run(cmd)
    S = json.load(open(os.path.join(W, "spec.json"), encoding="utf-8"))
    miss = [s["image"] for s in S["scenes"] if not os.path.exists(os.path.join(R, s["image"]))]
    run([T("apply_overlays.py"), os.path.join(W, "spec.json"), a.xlsx, "--template", os.path.join(W, "pos.json")])
    fp = os.path.join(W, "focus.json")
    if not os.path.exists(fp): json.dump({"_mẫu": "xem examples/focus/CH2_focus.json; 5–7 điểm, mỗi điểm một kiểu; t lấy từ wordts"}, open(fp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump({"xlsx": os.path.abspath(a.xlsx)}, open(CFG, "w"))
    items = [(f"{s['id']}  {s['start']:.1f}s", os.path.join(R, s["image"])) for s in S["scenes"] if os.path.exists(os.path.join(R, s["image"]))]
    sheet(items, os.path.join(W, "contact.jpg"))
    print(f"{tag}: {len(S['scenes'])} cảnh, {dur:.1f}s | ảnh nhỏ phải phóng lên 2560x1440 (zoom sâu sẽ mờ, nên upscale 4K): {len(small)} | THIẾU ẢNH: {miss or 'không'}")
    print(f"Xem 1 lần {W}/contact.jpg (lưới 320px) → điền {W}/focus.json + {W}/pos.json → chạy: build_chapter.py check --ch {a.ch}")

elif a.stage == "check":
    xlsx = json.load(open(CFG))["xlsx"]; spec = os.path.join(W, "spec.json"); cur = spec
    F = {k: v for k, v in json.load(open(os.path.join(W, "focus.json"), encoding="utf-8")).items() if not k.startswith("_")}
    times = []
    if F:
        json.dump(F, open(os.path.join(W, "_focus.json"), "w", encoding="utf-8"), ensure_ascii=False)
        out = os.path.join(W, "spec_focus.json"); run([T("apply_focus.py"), cur, os.path.join(W, "_focus.json"), "--out", out, "--root", R]); cur = out
        times += [(f"{sid} {b['kind']}", round((b["t"][0] + b["t"][1]) / 2, 2)) for sid, bs in F.items() for b in bs]
    P = json.load(open(os.path.join(W, "pos.json"), encoding="utf-8"))
    out = os.path.join(W, "spec_full.json"); msg = run([T("apply_overlays.py"), cur, xlsx, "--pos", os.path.join(W, "pos.json"), "--out", out, "--root", R]); cur = out
    on = [l for l in msg.splitlines() if "bật" in l]; off = [l.strip() for l in msg.splitlines() if "bỏ qua" in l]
    times += [(f"{k} {v.get('kind')}", round(v["t"][0] + 1.0, 2)) for k, v in P.items() if not any(k in o for o in off)]
    lint = subprocess.run([sys.executable, T("lint_spec.py"), cur, "--root", R, "--max-gap", "12"], capture_output=True, text=True).stdout
    errs = [l for l in lint.splitlines() if l.startswith("ERR")]; warns = [l for l in lint.splitlines() if l.startswith("WARN")]
    LOG.write(lint)
    fd = os.path.join(W, "chk"); shutil.rmtree(fd, ignore_errors=True); os.makedirs(fd)
    if times:
        run([os.path.join(ROOT, "overlay_engine.py"), cur, "--root", R, "--frames", ",".join(str(t) for _, t in times), "--frames-dir", fd])
        items = [(f"{lab} @{t}s", p) for (lab, t) in times for p in glob.glob(os.path.join(fd, f"chk_{t}.png"))]
        sheet(items, os.path.join(W, "check.jpg"), tw=640, cols=3, grid=False)
    print(f"điểm nhấn: {sum(len(v) for v in F.values())} | {on[0] if on else 'lớp phủ: 0'} | bỏ qua {len(off)} | lint: {len(errs)} ERR, {len(warns)} WARN")
    for l in errs[:8] + off[:8]: print("  " + l)
    if times: print(f"Xem 1 lần {W}/check.jpg → ổn thì: build_chapter.py render --ch {a.ch} --quick")

else:
    cur = next(p for p in (os.path.join(W, "spec_full.json"), os.path.join(W, "spec_focus.json"), os.path.join(W, "spec.json")) if os.path.exists(p))
    S = json.load(open(cur, encoding="utf-8"))
    S["meta"].update({"width": 1280, "height": 720, "fps": 15} if a.quick else {"width": 1920, "height": 1080, "fps": 30})
    rs = os.path.join(W, "spec_render.json"); json.dump(S, open(rs, "w", encoding="utf-8"), ensure_ascii=False)
    out = os.path.join(W, f"{tag.lower()}_{'quick' if a.quick else 'final'}.mp4")
    run([os.path.join(ROOT, "overlay_engine.py"), rs, "--root", R, "--out", out, "--jobs", str(a.jobs)])
    print("xong:", out)
