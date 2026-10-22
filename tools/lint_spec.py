#!/usr/bin/env python3
"""LINT SPEC — kiểm tra spec.json TRƯỚC khi render (vài giây, thay vì 15 phút render rồi mới thấy lỗi).
  python3 lint_spec.py spec.json --root <res>
Bắt các lỗi đã gặp ở bản pilot/Beat 1: khoảng trống sự kiện, overlay tĩnh quá lâu, phần tử quên t_out (kẹt sang cảnh sau),
chữ quá nhỏ, thẻ chồng lên nhau, cảnh quá tối, thiếu đa dạng hiệu ứng, camera đứng yên.
Thoát mã 1 nếu có LỖI (ERR). WARN là cảnh báo cần xem xét.
"""
import json, os, sys, argparse
import numpy as np, cv2
ap = argparse.ArgumentParser(); ap.add_argument("spec"); ap.add_argument("--root")
ap.add_argument("--max-gap", type=float, default=3.5); ap.add_argument("--max-static", type=float, default=3.0)
ap.add_argument("--min-text", type=int, default=26)
a = ap.parse_args()
root = a.root or os.path.dirname(os.path.abspath(a.spec))
S = json.load(open(a.spec, encoding="utf-8"))
dur = S["meta"]["duration"]; E = S["elements"]; SC = S["scenes"]
errs, warns, infos = [], [], []
CALM = bool(S.get("calm"))   # beat chủ đích thở: nới ngưỡng trống sự kiện lên 9s, bỏ kiểm "ít phần tử"
if CALM: a.max_gap = max(a.max_gap, 9.0)
ANIMATED = {"counter_down", "ticker", "gauge", "day_ticker", "rain", "mist", "dim", "spotlight", "anchored_circle", "timeline", "flash"}
NEEDS_OUT = {"label", "lower_third", "stamp", "badge_pop", "highlight_box", "strike_cards", "typed_card", "redact", "question_card"}

def span(e):
    t0 = e.get("t_in", e.get("run", [0])[0]); t1 = e.get("t_out", e.get("run", [0, dur])[1] if "run" in e else dur)
    return t0, t1

# --- 1. sự kiện (mọi thứ làm mắt người xem thấy MỚI)
ev = [0.0, dur]
for s in SC: ev.append(s["start"])
for e in E:
    t0, _ = span(e); ev.append(t0)
    for ln in e.get("lines", []): ev.append(ln["start"])
    for c in e.get("cards", []): ev += [c["t_in"], c["t_strike"]] if c.get("t_strike", 99) < dur else [c["t_in"]]
    for x in e.get("events", []): ev.append(x["t"])
    if e["type"] == "counter_down": ev.append(e["hit"])
ev = sorted(set(round(x, 2) for x in ev))
def _hold(p, q):   # cảnh đánh dấu "hold": true = nhịp để hình tự nói (có chủ đích, tối đa 9s)
    for k, sc in enumerate(SC):
        e_ = SC[k+1]["start"] if k+1 < len(SC) else dur
        if sc.get("hold") and sc["start"] - 0.01 <= p and q <= e_ + 0.01 and q - p <= 9: return True
    return False
for p, q in zip(ev, ev[1:]):
    if q - p > a.max_gap and _hold(p, q): infos.append(f"NHỊP HÌNH TỰ NÓI {p:.1f}–{q:.1f}s (scene hold) — chủ đích")
    elif q - p > a.max_gap: errs.append(f"TRỐNG SỰ KIỆN {p:.1f}–{q:.1f}s ({q-p:.1f}s > {a.max_gap}s): thêm 1 phần tử/hiệu ứng ở giữa")
infos.append(f"{len(ev)-2} mốc sự kiện / {dur:.0f}s = 1 mỗi {dur/max(len(ev)-2,1):.1f}s")

# --- 2. overlay tĩnh + quên t_out
scene_starts = [s["start"] for s in SC]
for e in E:
    t0, t1 = span(e); ty = e["type"]
    if ty in NEEDS_OUT and "t_out" not in e and not (ty == "question_card" or e is E[-1]):
        errs.append(f"[{ty} @{t0}] THIẾU t_out: phần tử sẽ ở lại tới hết video (lỗi 'LICENCE REVOKED' kẹt sang cảnh im lặng)")
    life = t1 - t0
    if ty in ANIMATED: continue
    static = life
    if ty == "typed_card":
        end_type = max((ln["start"] + len(ln["text"]) / ln.get("cps", 14)) for ln in e["lines"])
        static = t1 - end_type
    if ty == "strike_cards":
        static = t1 - max(c["t_in"] if c.get("t_strike", 99) > dur else c["t_strike"] for c in e["cards"])
    if static > a.max_static:
        warns.append(f"[{ty} @{t0}] đứng yên {static:.1f}s (> {a.max_static}s): rút t_out hoặc thêm chuyển động/đổi nội dung")
    if "t_out" in e:
        for s in scene_starts:
            if t0 < s - 0.6 and t1 > s + 0.8:
                warns.append(f"[{ty} @{t0}] sống qua điểm đổi cảnh {s}s (t_out={t1}): có chủ đích không?")

# --- 3. cỡ chữ
for e in E:
    t0, _ = span(e); ty = e["type"]
    sizes = [("size", e.get("size")), ("sub_size", e.get("sub_size"))] + [("line", ln["size"]) for ln in e.get("lines", [])]
    if ty == "lower_third": sizes = []   # cỡ cố định trong engine (34/22)
    for nme, v in sizes:
        if v and v < a.min_text and ty not in ("gauge",):
            warns.append(f"[{ty} @{t0}] {nme}={v}px < {a.min_text}px: khó đọc trên điện thoại/TV; tăng cỡ hoặc rút chữ")
    if ty == "lower_third" and e.get("sub"): infos.append(f"lower_third @{t0}: dòng phụ 22px (chấp nhận được, đừng viết dài)") if False else None

# --- 4. chồng thẻ (ước lượng hộp)
def box(e):
    ty = e["type"]
    if ty in ("typed_card", "question_card"): return tuple(e["box"])
    if ty == "lower_third": return (60, e.get("y", 560), 700, e.get("y", 560) + 92)
    if ty == "strike_cards":
        cx = e.get("cx", 640); hw = e.get("half_w", 280); hh = e.get("half_h", 66)
        ys = [c["y"] for c in e["cards"]]; return (cx - hw, min(ys) - hh, cx + hw, max(ys) + hh)
    if ty in ("badge_pop", "label", "stamp", "ticker"):
        sz = e.get("size", 30); w = len(e.get("text", "")) * sz * 0.65 if ty != "ticker" else 560
        x, y = e.get("pos", [640, 360])
        if e.get("anchor") == "rm": return (x - w, y - sz * .6, x, y + sz * .9)
        return (x - w / 2, y - sz * .7, x + w / 2, y + sz * .7)
    return None
bx = [(e, box(e)) for e in E]; bx = [(e, b) for e, b in bx if b]
for i, (e1, b1) in enumerate(bx):
    for e2, b2 in bx[i+1:]:
        t01, t11 = span(e1); t02, t12 = span(e2)
        if min(t11, t12) - max(t01, t02) > 0.4 and not (b1[2] < b2[0] or b2[2] < b1[0] or b1[3] < b2[1] or b2[3] < b1[1]):
            warns.append(f"CHỒNG THẺ: [{e1['type']} @{t01}-{t11}] và [{e2['type']} @{t02}-{t12}] cùng chiếm một vùng trong {min(t11,t12)-max(t01,t02):.1f}s")

# --- 5. cảnh: độ sáng, camera, mật độ
for k, s in enumerate(SC):
    end = SC[k+1]["start"] if k+1 < len(SC) else dur
    L = end - s["start"]
    if "image" not in s:   # cảnh video: bỏ qua kiểm độ sáng (không có ảnh tĩnh)
        im = None
    else:
        im = cv2.imread(os.path.join(root, s["image"]))
        if im is None: errs.append(f"không đọc được ảnh {s['image']}"); continue
    if im is None:
        n = sum(1 for e in E if s["start"] - 0.1 <= span(e)[0] < end)
        if L > 7 and n < 2 and not CALM: errs.append(f"CẢNH {s['id']} ({s['start']}–{end}s) chỉ có {n} phần tử cho {L:.0f}s")
        continue
    if s.get("blur"): im = cv2.GaussianBlur(im, (0, 0), float(s["blur"]) / 2)
    lum = float(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).mean()) * float(s.get("brightness", 1.0))
    if lum < 38 and L > 4: warns.append(f"CẢNH {s['id']} ({s['start']}–{end}s): quá tối (độ sáng TB {lum:.0f}/255) trong {L:.0f}s — nếu không chủ đích 'im lặng', tăng brightness hoặc thêm spotlight/mist")
    c = s["camera"]; dz = abs(c["scale"][1] - c["scale"][0]); dc = abs(c["cx"][1] - c["cx"][0]) + abs(c["cy"][1] - c["cy"][0])
    if L > 4 and dz < 0.05 and dc < 60: warns.append(f"CẢNH {s['id']}: camera gần đứng yên ({L:.0f}s) — thêm đẩy/lùi 8–30% hoặc pan")
    n = sum(1 for e in E if s["start"] - 0.1 <= span(e)[0] < end)
    if L > 7 and n < 2 and not CALM: errs.append(f"CẢNH {s['id']} ({s['start']}–{end}s) chỉ có {n} phần tử cho {L:.0f}s")

# --- 6. đa dạng
from collections import Counter
cnt = Counter(e["type"] for e in E)
top, tn = cnt.most_common(1)[0]
if len(E) >= 6 and tn / len(E) > 0.4: warns.append(f"ĐƠN ĐIỆU: '{top}' chiếm {tn}/{len(E)} phần tử — trộn thêm kiểu khác (xem EFFECTS.md)")
if dur > 45 and len(cnt) < 7: warns.append(f"chỉ {len(cnt)} kiểu hiệu ứng cho {dur:.0f}s (mục tiêu ≥ 7)")
if dur > 20 and not any(e["type"] in ("rain", "mist") for e in E): infos.append("chưa dùng chuyển động trong khung (rain/mist): cân nhắc cho cảnh tĩnh dài")
if not any(e["type"] == "strike_cards" for e in E): infos.append("chưa có motif phủ định (strike_cards) — xem EDITORIAL-PATTERNS.md")

# --- 7. lặp motif (nhịp dựng phải đổi theo diễn biến)
def _dir(c):
    dz = c["scale"][1] - c["scale"][0]
    return "in" if dz > 0.04 else "out" if dz < -0.04 else "pan"
dirs = [_dir(s["camera"]) for s in SC]
for k in range(len(dirs) - 2):
    if dirs[k] == dirs[k+1] == dirs[k+2] and dirs[k] != "pan":
        warns.append(f"LẶP CAMERA: cảnh {SC[k]['id']}–{SC[k+2]['id']} cùng đẩy {dirs[k]} 3 lần liền — đổi 1 cảnh sang lùi/pan/tĩnh")
        break
acc = [t for t in (S.get("audio", {}).get("tracks", [])) if "accent" in t.get("file", "")]
if len(acc) > 4: warns.append(f"ÂM NHẤN: {len(acc)} lần dùng cùng tiếng 'accent' — chọn tối đa 3–4 mốc thật sự quan trọng (và 1 lần mạnh nhất ở cú ngoặt)")
if dur > 30 and not any(s.get("hold") for s in SC): infos.append("chưa có cảnh 'hold': true — cân nhắc 1 nhịp để hình tự nói (không chữ/hiệu ứng) sau câu quan trọng")
tpos = [tuple(e.get("pos", ())) for e in E if e["type"] in ("label", "badge_pop", "stamp") and e.get("pos")]
for k in range(len(tpos) - 3):
    if len(set(tpos[k:k+4])) == 1: warns.append(f"LẶP VỊ TRÍ CHỮ: 4 thẻ liền cùng vị trí {tpos[k]} — đổi chỗ/kiểu"); break

print(f"SPEC {a.spec}: {len(E)} phần tử, {len(SC)} cảnh, {dur}s, kiểu: {dict(cnt)}")
for x in infos: print("INFO ", x)
for x in warns: print("WARN ", x)
for x in errs: print("ERR  ", x)
print(f"\n=> {len(errs)} lỗi, {len(warns)} cảnh báo")
sys.exit(1 if errs else 0)
