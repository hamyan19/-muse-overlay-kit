#!/usr/bin/env python3
"""MAPPING -> SPEC: đổi bảng mapping đã duyệt (asset_plan.xlsx, sheet SHOTS) thành spec.json cho overlay_engine.py.

  python3 tools/mapping_to_spec.py plan/CH1_asset_plan.xlsx --vo vo/ch1.mp3 --stills stills \
      --preset storybook --out spec_ch1.json
  python3 tools/lint_spec.py spec_ch1.json --root res

Làm gì: mỗi dòng SHOTS (bỏ dòng lớp phủ CẢNH 0, bỏ dòng DUYỆT=BỎ) thành một cảnh: ảnh = cột TÊN FILE ĐÍCH,
start = đầu cột PHỦ THỜI GIAN, camera suy từ cột CHUYỂN ĐỘNG ĐỀ XUẤT (đẩy vào -> zoom vào, lia/dolly -> pan,
cố định -> gần như đứng, còn lại -> zoom nhẹ), xen hướng để hai cảnh liền nhau không cùng chuyển động.
KHÔNG làm: lớp chữ/mũi tên/nét đứt (sheet OVERLAYS) — chỉ ghi vào meta.overlays_todo; bật chúng bằng tools/apply_overlays.py;
âm thanh ngoài lời đọc. Mặc định chỉ lấy dòng DUYỆT=OK (dùng --include-pending để thử với dòng CHỜ).
"""
import argparse, json, re, sys
import openpyxl

ap = argparse.ArgumentParser()
ap.add_argument("xlsx"); ap.add_argument("--vo", required=True, help="đường dẫn voice trong res/, ví dụ vo/ch1.mp3")
ap.add_argument("--stills", default="stills"); ap.add_argument("--preset", default=None)
ap.add_argument("--duration", type=float, default=None, help="độ dài video (giây); mặc định = hết shot cuối. Nên đặt = độ dài file voice")
ap.add_argument("--calm", action="store_true", help="đánh dấu calm=true (spec chưa có lớp phủ nên lint không báo thiếu phần tử)")
ap.add_argument("--dissolve", type=float, default=0.5); ap.add_argument("--out", default="spec.json")
ap.add_argument("--name-from-id", action="store_true", help="tên ảnh = <ID>.png với dấu - thành _ (CH2-S10 -> CH2_S10.png), dùng khi ảnh đặt tên ngắn theo mã shot")
ap.add_argument("--include-pending", action="store_true", help="lấy cả dòng CHỜ (chỉ để thử, không dựng thật)")
a = ap.parse_args()

def num(s):
    return float(str(s).replace(",", "."))

wb = openpyxl.load_workbook(a.xlsx, data_only=True)
ws = wb["SHOTS"]
H = [c.value for c in ws[1]]
col = {h: i for i, h in enumerate(H)}
need = ["ID", "CẢNH", "PHỦ THỜI GIAN", "DÀI (s)", "CHUYỂN ĐỘNG ĐỀ XUẤT", "TÊN FILE ĐÍCH", "DUYỆT"]
miss = [h for h in need if h not in col]
if miss: sys.exit(f"Thiếu cột trong SHOTS: {miss}")

rows = []
for r in ws.iter_rows(min_row=2, values_only=True):
    if not r[col["ID"]]: continue
    scene_no = str(r[col["CẢNH"]]).strip()
    dur = num(r[col["DÀI (s)"]] or 0)
    status = str(r[col["DUYỆT"]] or "").strip().upper()
    if scene_no == "0" or dur == 0: continue          # lớp phủ / cặp dissolve 0s
    if status == "BỎ": continue
    if status != "OK" and not a.include_pending:
        print(f"bỏ qua {r[col['ID']]} (DUYỆT={status or 'trống'})", file=sys.stderr); continue
    m = re.match(r"\s*([\d.,]+)\s*[–-]\s*([\d.,]+)", str(r[col["PHỦ THỜI GIAN"]]))
    t0, t1 = num(m.group(1)), num(m.group(2))
    rows.append(dict(id=r[col["ID"]], t0=t0, t1=t1, motion=str(r[col["CHUYỂN ĐỘNG ĐỀ XUẤT"]] or ""),
                     image=(str(r[col["ID"]]).replace("-", "_") + ".png") if a.name_from_id else r[col["TÊN FILE ĐÍCH"]]))
if not rows: sys.exit("Không có dòng nào để dựng (kiểm cột DUYỆT, hoặc dùng --include-pending để thử).")
rows.sort(key=lambda x: x["t0"])

def camera(motion, t0, t1, k):
    m = motion.lower(); flip = -1 if k % 2 else 1
    cx0, cy0 = 1280, 720
    if "cố định" in m or "giữ yên" in m:
        sc, dx, dy, ease = (1.0, 1.04), 0, 0, "smooth"
    elif "đẩy" in m or "dolly" in m and "theo" not in m:
        sc, dx, dy, ease = (1.0, 1.16), 60 * flip, 0, "smooth"
    elif "lia" in m or "pan" in m or "dolly" in m:
        sc, dx, dy, ease = (1.08, 1.08), 260 * flip, 0, "smooth"
    elif "camera a" in m or "→" in m:
        sc, dx, dy, ease = (1.0, 1.12), 140 * flip, 20, "smooth"
    else:
        sc, dx, dy, ease = (1.0, 1.10), 0, 0, "smooth"
    return {"t0": round(t0, 2), "t1": round(t1, 2), "ease": ease, "scale": list(sc),
            "cx": [cx0 - dx, cx0 + dx], "cy": [cy0 - dy, cy0 + dy]}

scenes = []
for k, s in enumerate(rows):
    scenes.append({"id": s["id"], "image": f"{a.stills}/{s['image']}", "start": s["t0"],
                   "camera": camera(s["motion"], s["t0"], s["t1"], k)})

ov = []
if "OVERLAYS" in wb.sheetnames:
    o = wb["OVERLAYS"]; OH = [c.value for c in o[1]]
    for r in o.iter_rows(min_row=2, values_only=True):
        if r[0]: ov.append(dict(zip(OH, r)))
dur = max(rows[-1]["t1"], a.duration or 0)
spec = {"meta": {"width": 1920, "height": 1080, "fps": 30, "duration": round(dur, 2),
                 "overlays_todo": [{k: v for k, v in x.items() if k in ("ID", "GIÂY", "TỪ KÍCH HOẠT", "LOẠI", "HIỆU ỨNG ĐỀ XUẤT", "GHI CHÚ NỘI DUNG")} for x in ov]},
        "colors": {"yellow": [255, 209, 26], "red": [235, 50, 40], "cream": [255, 240, 200], "edge": [230, 225, 200], "card": [10, 12, 10], "white": [255, 255, 255]}, "fonts": {"sans": "fonts/DejaVuSans-Bold.ttf", "mono": "fonts/DejaVuSansMono-Bold.ttf"},
        "dissolve": a.dissolve, "scenes": scenes, "elements": [],
        "audio": {"total": round(dur, 2), "vo": {"file": a.vo}, "tracks": []}}
if a.preset: spec["preset"] = a.preset
if a.calm: spec["calm"] = True
json.dump(spec, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"{a.out}: {len(scenes)} cảnh, {dur:.1f}s, {len(ov)} overlay chờ thêm tay")
