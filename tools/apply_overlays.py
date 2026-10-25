#!/usr/bin/env python3
"""APPLY OVERLAYS — bật các lớp phủ trong sheet OVERLAYS (mũi tên, nhãn, nét đứt, ảnh L01, tuyết) lên đúng vật thể.

  # 1) tạo khung điền (mỗi dòng OVERLAYS một mục, toạ độ để null):
  python3 tools/apply_overlays.py spec.json plan/CH2_asset_plan.xlsx --template pos_ch2.json
  # 2) người dựng nhìn ảnh (lưới 320px), điền toạ độ ảnh nguồn 2560x1440 vào pos_ch2.json, rồi:
  python3 tools/apply_overlays.py spec.json plan/CH2_asset_plan.xlsx --pos pos_ch2.json --out spec_ov.json --root res

pos.json: {"<ID overlay>": {"scene":"CH2-S06", "t":[vào,ra], ...toạ độ theo loại...}}
  MŨI TÊN        {"from":[x,y], "to":[x,y]}            (nhãn lấy từ 'chữ trong nháy' của GHI CHÚ, nếu có)
  NHÃN           {"at":[x,y]}                          thẻ chữ bám vật thể (chữ lấy từ nháy đơn trong GHI CHÚ)
  ĐƯỜNG ĐỨT      {"points":[[x,y],...]}
  LỚP PHỦ/CHỒNG  {"at":[x,y], "width":600, "file":"stills/CH2_L01.png"}   ảnh nét đứt L01 (cần ảnh)
  HIỆU ỨNG tuyết tự bật, không cần toạ độ
Mục toạ độ còn null thì BỎ QUA (in danh sách). Thời gian mặc định: vào = cột GIÂY, ra = vào + 3s (đường đứt 4s, ảnh 3s).

RÀO SÁNG (phủ xong không được tối mò): ảnh phủ multiply chỉ phủ nét tối, strength <= 0.85, độ phủ TB <= 10% khung (engine tự hạ);
tool đo thêm độ sáng ảnh nền: nền < 80/255 thì không bật lớp ảnh, báo để chuyển sang nhãn/mũi tên; tuyết/hạt alpha <= 0.45.
Tối đa 2 phần tử phủ đồng thời (luật EDITORIAL-PATTERNS #3); cái thứ 3 trùng thời gian bị bỏ và báo.
"""
import argparse, json, os, re, sys
import openpyxl

ap = argparse.ArgumentParser(); ap.add_argument("spec"); ap.add_argument("xlsx")
ap.add_argument("--template"); ap.add_argument("--pos"); ap.add_argument("--out")
ap.add_argument("--root", default="res")
a = ap.parse_args()
S = json.load(open(a.spec, encoding="utf-8"))
ws = openpyxl.load_workbook(a.xlsx, data_only=True)["OVERLAYS"]
H = [c.value for c in ws[1]]
rows = [dict(zip(H, r)) for r in ws.iter_rows(min_row=2, values_only=True) if r[0]]
ids = {s["id"] for s in S["scenes"]}

def scene_of(r):
    n = int(float(r["CẢNH"])); tag = r["ID"].split("-")[0]
    cand = f"{tag}-S{n:02d}"
    return cand if cand in ids else next((i for i in ids if i.endswith(f"-S{n:02d}")), None)

def kind_of(r):
    L = (r.get("LOẠI") or "").upper(); eff = (r.get("HIỆU ỨNG ĐỀ XUẤT") or "").lower()
    if "MŨI TÊN" in L: return "arrow"
    if "ĐƯỜNG" in L: return "route"
    if "NHÃN" in L: return "tag"
    if "LỚP PHỦ" in L or "LỚP CHỒNG" in L: return "image"
    if "HIỆU ỨNG" in L and "tuyết" in eff: return "snow"
    return "todo"

def label_of(r):
    m = re.search(r"'([^']+)'", str(r.get("GHI CHÚ NỘI DUNG") or ""))
    return m.group(1) if m else None

def dur_of(k): return {"route": 4.0, "image": 3.0, "snow": 12.0}.get(k, 3.0)

if a.template:
    T = {}
    for r in rows:
        k = kind_of(r); t0 = float(str(r["GIÂY"]).replace(",", "."))
        d = {"scene": scene_of(r), "kind": k, "t": [t0, round(t0 + dur_of(k), 2)], "word": r.get("TỪ KÍCH HOẠT"), "gợi ý": r.get("HIỆU ỨNG ĐỀ XUẤT")}
        if k == "arrow": d.update({"from": None, "to": None, "label": label_of(r)})
        elif k == "tag": d.update({"at": None, "text": label_of(r)})
        elif k == "route": d.update({"points": None})
        elif k == "image": d.update({"at": None, "width": 600, "file": None})
        T[r["ID"]] = d
    json.dump(T, open(a.template, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{a.template}: {len(T)} mục — điền toạ độ ảnh nguồn rồi chạy lại với --pos"); sys.exit(0)

if not (a.pos and a.out): sys.exit("cần --template hoặc (--pos và --out)")
P = json.load(open(a.pos, encoding="utf-8"))
S["colors"].setdefault("orange", [255, 140, 30]); S["colors"].setdefault("steel", [120, 150, 175])
S.setdefault("elements", []); added, skipped = [], []

def lum(scene_id):
    import cv2
    sc = next(s for s in S["scenes"] if s["id"] == scene_id)
    im = cv2.imread(os.path.join(a.root, sc["image"]))
    return None if im is None else float(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).mean()) * float(sc.get("brightness", 1.0))

def overlap(ti, to):
    return sum(1 for e in S["elements"] if e.get("_ov") and e["t_in"] < to and ti < e.get("t_out", e["t_in"] + 3))

for r in rows:
    i = r["ID"]; p = P.get(i)
    if not p: skipped.append((i, "không có trong pos")); continue
    k = p.get("kind") or kind_of(r); sc = p.get("scene") or scene_of(r); ti, to = p["t"]
    if k == "snow":
        el = {"type": "particles", "kind": "snow", "t_in": ti, "t_out": to, "n": 70, "alpha": 0.4, "seed": 7}
    else:
        need = {"arrow": ("from", "to"), "tag": ("at",), "route": ("points",), "image": ("at", "file")}.get(k)
        if need is None or any(not p.get(x) for x in need): skipped.append((i, f"thiếu toạ độ {need}")); continue
        if not sc: skipped.append((i, "không tìm thấy cảnh")); continue
        if overlap(ti, to) >= 2: skipped.append((i, "đã có 2 lớp phủ cùng lúc")); continue
        if k == "arrow":
            c = "steel" if re.search(r"xanh|xám", str(r.get("HIỆU ỨNG ĐỀ XUẤT"))) else "orange"
            el = {"type": "marker", "kind": "arrow", "t_in": ti, "t_out": to, "scene": sc, "from": p["from"], "to": p["to"],
                  "color": p.get("color", c), "width": p.get("width", 13), "draw": 0.8}
            if p.get("label"): el.update({"label": p["label"], "label_src": p.get("label_src", [p["to"][0] + 90, p["to"][1] - 110]), "label_card": True, "size": 30})
        elif k == "tag":
            el = {"type": "tag", "t_in": ti, "t_out": to, "scene": sc, "src": p["at"], "text": p.get("text") or label_of(r) or "", "size": 30}
        elif k == "route":
            el = {"type": "route", "t_in": ti, "t_out": to, "scene": sc, "points": p["points"], "draw": 1.6, "color": p.get("color", "yellow")}
        else:
            L = lum(sc)
            if L is not None and L < 80: skipped.append((i, f"nền tối (TB {L:.0f}/255) — không phủ ảnh")); continue
            if not os.path.exists(os.path.join(a.root, p["file"])): skipped.append((i, "thiếu ảnh " + p["file"])); continue
            el = {"type": "image_overlay", "t_in": ti, "t_out": to, "scene": sc, "at": p["at"], "file": p["file"],
                  "width": p.get("width", 600), "blend": "multiply", "strength": min(p.get("strength", 0.8), 0.85)}
    el["_ov"] = True; S["elements"].append(el); added.append(i)

for e in S["elements"]: e.pop("_ov", None)
json.dump(S, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"{a.out}: bật {len(added)} lớp phủ: {', '.join(added) or '-'}")
for i, why in skipped: print(f"  bỏ qua {i}: {why}")
