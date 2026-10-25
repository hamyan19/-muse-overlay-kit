#!/usr/bin/env python3
"""APPLY FOCUS — vài điểm nhấn theo lời (ít thôi: mục tiêu 5–7 điểm cho cả chương). Mặc định không làm tối nền.

  python3 tools/apply_focus.py spec_ch2.json focus_ch2.json --out spec_ch2_focus.json

focus.json: {"<ID cảnh>": [ beat, ... ]}. Mỗi beat có "t":[vào,ra] (giây tuyệt đối, lấy từ wordts.json) và "kind":
  zoom   {at:[x,y], zoom:1.6}     camera trượt tới chi tiết (trước t vào 0,45s), giữ tới t ra, rồi lùi dần cuối cảnh. KHÔNG tối nền
  circle {box:[x0,y0,x1,y1]}      khoanh tròn vẽ tay quanh chi tiết (bám camera)
  arrow  {from:[x,y], to:[x,y]}   mũi tên vẽ tay chỉ vào chi tiết (bám camera); label tuỳ chọn
  cut    {at:[x,y], zoom:2.0}     cắt thẳng sang cận cảnh (crop cùng ảnh) trong [t vào, t ra], rồi cắt lại cảnh cũ, camera cũ chạy tiếp
Toạ độ là ảnh nguồn 2560x1440 (đặt lưới lên ảnh để đọc). Cảnh không có trong focus.json giữ nguyên camera cũ.
spot   {at:[x,y], r:380, dim:0.35}  tô sáng vật thể, hạ sáng phần còn lại. DÙNG ĐƯỢC cho vật thể then chốt, nhưng có RÀO SÁNG (xem dưới).
RÀO SÁNG cho spot (tránh phủ xong video tối mò): đo độ sáng ảnh nguồn (0–255) rồi tự giảm `dim` sao cho độ sáng TB của khung SAU KHI phủ >= --min-lum (mặc định 95);
  dim tối đa 0.45 (mặc định 0.35); ảnh gốc TB < 80 thì KHÔNG phủ tối (đổi thành vòng khoanh `circle` quanh cùng vị trí, in cảnh báo); mỗi spot <= 3.5s;
  tối đa --max-spot (mặc định 2) spot / chương. Vượt thì dừng, báo lỗi.
"""
import argparse, copy, json, math, os
ap = argparse.ArgumentParser(); ap.add_argument("spec"); ap.add_argument("focus")
ap.add_argument("--out", required=True); ap.add_argument("--lead", type=float, default=0.45)
ap.add_argument("--root", default="res", help="thư mục gốc chứa ảnh (như overlay_engine --root), để đo độ sáng cho spot")
ap.add_argument("--min-lum", type=float, default=95.0, help="độ sáng TB tối thiểu của khung sau khi phủ spot (0–255)")
ap.add_argument("--max-spot", type=int, default=2)
a = ap.parse_args()
S = json.load(open(a.spec, encoding="utf-8")); F = json.load(open(a.focus, encoding="utf-8"))
S.setdefault("elements", [])
nspot = sum(1 for bs in F.values() for b in bs if b["kind"] == "spot")
if nspot > a.max_spot:
    raise SystemExit(f"LỖI: {nspot} spot > {a.max_spot}. Spot làm tối nền, chỉ 1–2 lần/chương (bản v2 dùng 22 lần bị chê). Đổi bớt sang circle/arrow/zoom/cut.")

def luminance(img_rel):
    import cv2
    im = cv2.imread(os.path.join(a.root, img_rel))
    if im is None:
        raise SystemExit("LỖI: không đọc được ảnh để đo sáng: " + os.path.join(a.root, img_rel))
    return float(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).mean())

def safe_dim(sc, b):
    """Trả (dim, lời nhắn) hoặc (None, lý do) nếu ảnh quá tối để phủ."""
    L = luminance(sc["image"]) * float(sc.get("brightness", 1.0))
    if L < 80:
        return None, f"ảnh {sc['image']} tối (TB {L:.0f}/255)"
    r = b.get("r", 380); frac = min(1.0, math.pi * r * r / (2560 * 1440))   # phần khung được chừa sáng
    dim = min(b.get("dim", 0.35), 0.45)
    # sáng TB sau phủ ~ L * (1 - dim*(1-frac)); hạ dim cho tới khi >= min-lum
    need = 1 - a.min_lum / L
    dim = max(0.0, min(dim, need / max(1e-6, 1 - frac)))
    return round(dim, 2), f"TB {L:.0f} → sau phủ ≈ {L*(1-dim*(1-frac)):.0f}"

order = sorted(S["scenes"], key=lambda s: s["start"])
ends = {s["id"]: (order[i + 1]["start"] if i + 1 < len(order) else S["meta"]["duration"]) for i, s in enumerate(order)}
new_scenes, count = [], 0
for s in order:
    beats = F.get(s["id"], [])
    t0, t1 = s["start"], ends[s["id"]]
    zooms = [b for b in beats if b["kind"] == "zoom"]
    if zooms:
        keys = [{"t": round(t0, 2), "scale": 1.0, "cx": 1280, "cy": 720}]; last = t0
        for b in zooms:
            ti, to = b["t"]; z = b.get("zoom", 1.6); x, y = b["at"]
            arr = max(last + 0.05, ti - a.lead)
            keys += [{"t": round(arr, 2), "scale": z, "cx": x, "cy": y}, {"t": round(max(arr + 0.05, to), 2), "scale": z, "cx": x, "cy": y}]
            last = to
        keys.append({"t": round(max(last + 0.1, t1 - 0.05), 2), "scale": 1.05, "cx": 1280, "cy": 720})
        s["camera"] = {"t0": round(t0, 2), "t1": round(t1, 2), "ease": "smooth", "scale": [1.0, 1.05], "cx": [1280, 1280], "cy": [720, 720], "keys": keys}
    new_scenes.append(s); cur = s
    for b in beats:
        ti, to = b["t"]; k = b["kind"]; count += 1
        if k == "cut":
            z = b.get("zoom", 2.0); x, y = b["at"]
            new_scenes.append({"id": s["id"] + "-cut", "image": s["image"], "start": ti, "dissolve": 0,
                               "camera": {"t0": ti, "t1": to, "ease": "smooth", "scale": [z, z * 1.05], "cx": [x, x], "cy": [y, y]}})
            back = copy.deepcopy(s); back["id"] = s["id"] + "-back"; back["start"] = to; back["dissolve"] = 0
            new_scenes.append(back)
        elif k == "circle":
            S["elements"].append({"type": "marker", "kind": "circle", "t_in": ti, "t_out": to, "scene": s["id"], "box": b["box"],
                                  "color": b.get("color", "red"), "width": b.get("width", 9), "draw": 0.7})
        elif k == "arrow":
            e = {"type": "marker", "kind": "arrow", "t_in": ti, "t_out": to, "scene": s["id"], "from": b["from"], "to": b["to"],
                 "color": b.get("color", "red"), "width": b.get("width", 9), "draw": 0.7}
            if b.get("label"): e["label"] = b["label"]
            S["elements"].append(e)
        elif k == "spot":
            to = min(to, ti + 3.5)
            dim, note = safe_dim(s, b)
            if dim is None or dim < 0.08:
                print(f"CẢNH BÁO {s['id']}: bỏ spot ({note}) → đổi thành khoanh tròn cùng vị trí")
                r = b.get("r", 380); x, y = b["at"]
                S["elements"].append({"type": "marker", "kind": "circle", "t_in": ti, "t_out": to, "scene": s["id"],
                                      "box": [x - r, y - r, x + r, y + r], "color": b.get("color", "red"), "width": 9, "draw": 0.7})
            else:
                print(f"spot {s['id']} {ti}–{to}s: dim {dim} ({note})")
                S["elements"].append({"type": "spotlight", "t_in": ti, "t_out": to, "scene": s["id"], "src": b["at"], "r": b.get("r", 380),
                                      "from_mult": 1.7, "dim": dim, "soft": 110, "fade_in": 0.4, "fade_out": 0.4})
        elif k != "zoom":
            raise SystemExit("kind không hợp lệ: " + k)
        if k == "zoom": count += 0
S["scenes"] = new_scenes
json.dump(S, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"{a.out}: {count} điểm nhấn, {len(S['scenes'])} cảnh")
