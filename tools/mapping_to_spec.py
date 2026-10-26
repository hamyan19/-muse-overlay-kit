#!/usr/bin/env python3
"""MAPPING -> SPEC: đổi bảng mapping đã duyệt (asset_plan.xlsx, sheet SHOTS) thành spec.json cho overlay_engine.py.

  python3 tools/mapping_to_spec.py plan/CH1_asset_plan.xlsx --vo vo/ch1.mp3 --stills stills \
      --preset storybook --out spec_ch1.json
  python3 tools/lint_spec.py spec_ch1.json --root res

Làm gì: mỗi dòng SHOTS (bỏ dòng lớp phủ CẢNH 0, bỏ dòng DUYỆT=BỎ) thành một cảnh: ảnh = cột TÊN FILE ĐÍCH,
start = đầu cột PHỦ THỜI GIAN, camera suy từ cột CHUYỂN ĐỘNG ĐỀ XUẤT (đẩy vào -> zoom vào, lia/dolly -> pan,
cố định -> gần như đứng, còn lại -> zoom nhẹ), xen hướng để hai cảnh liền nhau không cùng chuyển động.
CỤM Ý (cột CỤM / VÙNG / CHUYỂN TRONG CỤM, nếu có): các shot liền nhau cùng mã CỤM dùng chung 1 ảnh gốc (--name-from-id: <CỤM>.png),
nối liền không dissolve; camera đi qua từng VÙNG (toạ độ từ --regions vung.json hoặc số '480,820 x2' trong cột VÙNG);
CHUYỂN có 'cắt' = cắt thẳng sang vùng; có 'ô'/'lộ dần' = lộ dần từng ô (panel_reveal, 3 shot -> 3 cột, 4 -> 2x2);
  một shot ghi 'mở 3 ô' = tự mở 3 ô trong shot đó, mốc lấy từ (giây–giây) của cột CHUYỂN ĐỘNG ĐỀ XUẤT.
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
ap.add_argument("--regions", help="vung.json {ID shot: {at:[x,y], zoom:z}} — toạ độ vùng cho shot trong CỤM (ghi đè toạ độ trong cột VÙNG)")
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
    g = lambda h: str(r[col[h]] or "").strip() if h in col else ""
    cum = g("CỤM")
    img = (str(r[col["ID"]]).replace("-", "_") + ".png") if a.name_from_id else r[col["TÊN FILE ĐÍCH"]]
    if cum and a.name_from_id: img = cum.replace("-", "_") + ".png"          # cả cụm dùng chung 1 ảnh gốc
    rows.append(dict(id=r[col["ID"]], t0=t0, t1=t1, motion=str(r[col["CHUYỂN ĐỘNG ĐỀ XUẤT"]] or ""), image=img,
                     cum=cum, vung=g("VÙNG"), chuyen=g("CHUYỂN TRONG CỤM").lower()))
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

# ---- CỤM Ý: nhiều shot liền nhau dùng chung 1 ảnh gốc; mỗi shot là một VÙNG (KY-THUAT-DUNG.md mục 1–2)
REG = json.load(open(a.regions, encoding="utf-8")) if a.regions else {}
def region(s):
    """(cx, cy, zoom) theo toạ độ ảnh nguồn 2560x1440: vung.json > số trong cột VÙNG ('480,820 x2') > toàn cảnh."""
    r = REG.get(s["id"]) or {}
    if r.get("at") and r["at"][0] is not None:
        return float(r["at"][0]), float(r["at"][1]), float(r.get("zoom") or 1.6)
    m = re.search(r"(\d{2,4})\s*,\s*(\d{2,4})(?:\s*[x×]\s*([\d.]+))?", s["vung"])
    if m: return float(m.group(1)), float(m.group(2)), float(m.group(3) or 1.6)
    if re.search(r"toàn cảnh|lùi|toàn bộ", s["vung"].lower() + " " + s["chuyen"]): return 1280.0, 720.0, 1.0
    return None

def clamp(cx, cy, z):    # không để lộ mép ảnh
    hw, hh = 1280 / z, 720 / z
    return min(max(cx, hw), 2560 - hw), min(max(cy, hh), 1440 - hh), z

scenes, extra_el, need_reg = [], [], []
k = 0
while k < len(rows):
    s = rows[k]
    if not s["cum"]:
        scenes.append({"id": s["id"], "image": f"{a.stills}/{s['image']}", "start": s["t0"], "camera": camera(s["motion"], s["t0"], s["t1"], k)})
        k += 1; continue
    grp = [s]
    while k + len(grp) < len(rows) and rows[k + len(grp)]["cum"] == s["cum"]: grp.append(rows[k + len(grp)])
    T0, T1 = grp[0]["t0"], grp[-1]["t1"]
    panel = [x for x in grp if re.search(r"\bô\b|mở ô|lộ dần", x["chuyen"])]
    if panel:      # LỘ DẦN TỪNG Ô: camera chung cả cụm đẩy rất nhẹ, mỗi shot mở 1 ô
        cam = {"t0": round(T0, 2), "t1": round(T1, 2), "ease": "smooth", "scale": [1.0, 1.04], "cx": [1280, 1280], "cy": [720, 720]}
        for i, x in enumerate(grp):
            scenes.append({"id": x["id"], "image": f"{a.stills}/{x['image']}", "start": x["t0"], "camera": cam, **({"dissolve": 0} if i else {})})
        rev = [round(p["t0"] + 0.15, 2) for p in panel]
        mN = re.search(r"(\d)\s*ô", panel[0]["chuyen"]) if len(panel) == 1 else None
        if mN:     # MỘT shot tự kể N ý ("mở 3 ô"): mốc mở lấy từ (giây–giây) trong CHUYỂN ĐỘNG ĐỀ XUẤT, không có thì chia đều
            N = int(mN.group(1)); p0 = panel[0]
            ts = [float(x.replace(",", ".")) for x in re.findall(r"\((\d+[.,]\d+)\s*[–-]", p0["motion"])]
            rev = [round(t, 2) for t in ts[:N]] if len(ts) >= N else [round(p0["t0"] + 0.15 + i * (p0["t1"] - p0["t0"] - 1.5) / N, 2) for i in range(N)]
        n = len(rev); lay = "2x2" if n == 4 and "cột" not in " ".join(p["chuyen"] for p in panel) else f"{n}col"
        extra_el.append({"type": "panel_reveal", "scene": grp[0]["id"], "layout": lay, "reveal": rev,
                         "t_in": round(T0, 2), "t_out": round(T1 - 0.6, 2)})
    else:          # ZOOM TỪNG VÙNG: camera đi từ vùng trước sang vùng này rồi giữ (trôi nhẹ); 'cắt' = cắt thẳng
        prev = None
        for i, x in enumerate(grp):
            R = region(x)
            if R is None: need_reg.append(x["id"]); R = (1280.0, 720.0, 1.12)
            cx, cy, z = clamp(*R)
            cut = "cắt" in x["chuyen"] or "cut" in x["chuyen"]
            travel = min(1.3, 0.4 * (x["t1"] - x["t0"]))
            if prev is None:
                start = clamp(cx, cy, max(1.0, z * 0.92)) if z > 1.01 else (1280.0, 720.0, 1.06)
            else:
                start = (cx, cy, z) if cut else prev
            hold = clamp(cx, cy, z * 1.03)
            keys = [{"t": round(x["t0"], 2), "scale": start[2], "cx": start[0], "cy": start[1]}]
            if not cut and prev is not None or prev is None:
                keys.append({"t": round(x["t0"] + travel, 2), "scale": z, "cx": cx, "cy": cy})
            keys.append({"t": round(x["t1"], 2), "scale": hold[2], "cx": hold[0], "cy": hold[1]})
            scenes.append({"id": x["id"], "image": f"{a.stills}/{x['image']}", "start": x["t0"], **({"dissolve": 0} if i else {}),
                           "camera": {"t0": round(x["t0"], 2), "t1": round(x["t1"], 2), "ease": "smooth", "scale": [1, 1], "cx": [1280, 1280], "cy": [720, 720], "keys": keys}})
            prev = hold
    k += len(grp)
if need_reg:
    print(f"CỤM: {len(need_reg)} shot chưa có toạ độ VÙNG (đang để toàn cảnh): {', '.join(need_reg)} — điền vung.json rồi chạy lại với --regions", file=sys.stderr)

ov = []
if "OVERLAYS" in wb.sheetnames:
    o = wb["OVERLAYS"]; OH = [c.value for c in o[1]]
    for r in o.iter_rows(min_row=2, values_only=True):
        if r[0]: ov.append(dict(zip(OH, r)))
dur = max(rows[-1]["t1"], a.duration or 0)
spec = {"meta": {"width": 1920, "height": 1080, "fps": 30, "duration": round(dur, 2),
                 "overlays_todo": [{k: v for k, v in x.items() if k in ("ID", "GIÂY", "TỪ KÍCH HOẠT", "LOẠI", "HIỆU ỨNG ĐỀ XUẤT", "GHI CHÚ NỘI DUNG")} for x in ov]},
        "colors": {"yellow": [255, 209, 26], "red": [235, 50, 40], "cream": [255, 240, 200], "edge": [230, 225, 200], "card": [10, 12, 10], "white": [255, 255, 255]}, "fonts": {"sans": "fonts/DejaVuSans-Bold.ttf", "mono": "fonts/DejaVuSansMono-Bold.ttf"},
        "dissolve": a.dissolve, "scenes": scenes, "elements": extra_el,
        "audio": {"total": round(dur, 2), "vo": {"file": a.vo}, "tracks": []}}
if a.preset: spec["preset"] = a.preset
if a.calm: spec["calm"] = True
json.dump(spec, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"{a.out}: {len(scenes)} cảnh, {dur:.1f}s, {len(ov)} overlay chờ thêm tay")
