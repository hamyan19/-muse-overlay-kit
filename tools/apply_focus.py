#!/usr/bin/env python3
"""APPLY FOCUS — vài điểm nhấn theo lời (ít thôi: mục tiêu 5–7 điểm cho cả chương). Không làm tối nền.

  python3 tools/apply_focus.py spec_ch2.json focus_ch2.json --out spec_ch2_focus.json

focus.json: {"<ID cảnh>": [ beat, ... ]}. Mỗi beat có "t":[vào,ra] (giây tuyệt đối, lấy từ wordts.json) và "kind":
  zoom   {at:[x,y], zoom:1.6}     camera trượt tới chi tiết (trước t vào 0,45s), giữ tới t ra, rồi lùi dần cuối cảnh. KHÔNG tối nền
  circle {box:[x0,y0,x1,y1]}      khoanh tròn vẽ tay quanh chi tiết (bám camera)
  arrow  {from:[x,y], to:[x,y]}   mũi tên vẽ tay chỉ vào chi tiết (bám camera); label tuỳ chọn
  cut    {at:[x,y], zoom:2.0}     cắt thẳng sang cận cảnh (crop cùng ảnh) trong [t vào, t ra], rồi cắt lại cảnh cũ, camera cũ chạy tiếp
Toạ độ là ảnh nguồn 2560x1440 (đặt lưới lên ảnh để đọc). Cảnh không có trong focus.json giữ nguyên camera cũ.
Muốn tối nền kiểu cũ: kind "spot" {at, r, dim} — chỉ dùng cho vài khoảnh khắc then chốt.
"""
import argparse, copy, json
ap = argparse.ArgumentParser(); ap.add_argument("spec"); ap.add_argument("focus")
ap.add_argument("--out", required=True); ap.add_argument("--lead", type=float, default=0.45)
a = ap.parse_args()
S = json.load(open(a.spec, encoding="utf-8")); F = json.load(open(a.focus, encoding="utf-8"))
S.setdefault("elements", [])
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
            S["elements"].append({"type": "spotlight", "t_in": ti, "t_out": to, "scene": s["id"], "src": b["at"], "r": b.get("r", 380),
                                  "from_mult": 1.7, "dim": b.get("dim", 0.62), "soft": 110, "fade_in": 0.4, "fade_out": 0.4})
        elif k != "zoom":
            raise SystemExit("kind không hợp lệ: " + k)
        if k == "zoom": count += 0
S["scenes"] = new_scenes
json.dump(S, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"{a.out}: {count} điểm nhấn, {len(S['scenes'])} cảnh")
