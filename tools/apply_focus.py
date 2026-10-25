#!/usr/bin/env python3
"""APPLY FOCUS — nhấn mạnh đúng chi tiết đang được nói: camera zoom vào chỗ đó + làm tối phần còn lại (spotlight).

  python3 tools/apply_focus.py spec_ch2.json focus_ch2.json --out spec_ch2_focus.json

focus.json: {"<ID cảnh>": [ {"t":[t_in,t_out], "at":[x,y], "zoom":1.6, "r":380}, ... ]}
  t  = giây tuyệt đối của video (lấy từ wordts.json: từ nói ra chi tiết đó)
  at = toạ độ trên ảnh nguồn 2560x1440 (đặt lưới lên ảnh để đọc toạ độ)
  zoom = độ phóng khi nhấn (1.4–1.8); r = bán kính vòng sáng trên ảnh nguồn; dim (tuỳ chọn, mặc định 0.62)
Mỗi beat: camera trượt tới trước t_in 0.45s, giữ tới t_out; hết beat cuối thì lùi về khung rộng dần cuối cảnh.
Cảnh không có trong focus.json giữ nguyên camera cũ.
"""
import argparse, json
ap = argparse.ArgumentParser(); ap.add_argument("spec"); ap.add_argument("focus")
ap.add_argument("--out", required=True); ap.add_argument("--lead", type=float, default=0.45)
a = ap.parse_args()
S = json.load(open(a.spec, encoding="utf-8")); F = json.load(open(a.focus, encoding="utf-8"))
sc = {s["id"]: s for s in S["scenes"]}
ends = {}
order = sorted(S["scenes"], key=lambda s: s["start"])
for i, s in enumerate(order):
    ends[s["id"]] = order[i + 1]["start"] if i + 1 < len(order) else S["meta"]["duration"]
S.setdefault("elements", [])
for sid, beats in F.items():
    if sid.startswith("_"): continue
    s = sc[sid]; t0, t1 = s["start"], ends[sid]
    keys = [{"t": round(t0, 2), "scale": 1.0, "cx": 1280, "cy": 720}]
    last = t0
    for b in beats:
        ti, to = b["t"]; z = b.get("zoom", 1.6); x, y = b["at"]
        arrive = max(last + 0.05, ti - a.lead)
        keys.append({"t": round(arrive, 2), "scale": z, "cx": x, "cy": y})
        keys.append({"t": round(max(arrive + 0.05, to), 2), "scale": z, "cx": x, "cy": y})
        last = to
        S["elements"].append({"type": "spotlight", "t_in": ti, "t_out": to, "scene": sid, "src": [x, y], "r": b.get("r", 380),
                              "from_mult": 1.7, "dim": b.get("dim", 0.62), "soft": 110, "fade_in": 0.4, "fade_out": 0.4})
    keys.append({"t": round(max(last + 0.1, t1 - 0.05), 2), "scale": 1.05, "cx": 1280, "cy": 720})
    s["camera"] = {"t0": round(t0, 2), "t1": round(t1, 2), "ease": "smooth", "scale": [1.0, 1.05], "cx": [1280, 1280], "cy": [720, 720], "keys": keys}
json.dump(S, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"{a.out}: {sum(len(v) for k, v in F.items() if not k.startswith('_'))} beat nhấn mạnh, {len(F)} cảnh")
