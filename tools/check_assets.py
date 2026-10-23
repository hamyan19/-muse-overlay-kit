#!/usr/bin/env python3
"""KIỂM TRA NGUYÊN LIỆU MUSE ĐÃ GIAO + TẠO SHEET ẢNH THU NHỎ (tuỳ chọn, khi anh muốn xem nguyên liệu trước khi dựng).
  python3 check_assets.py plan/approved_manifest.json --root res --out plan/
Kiểm: file có mặt, ảnh đủ 2560x1440 (16:9), độ sáng, ảnh trùng/quá giống nhau, footage/âm thanh dài bao nhiêu.
Xuất asset_review.xlsx: mỗi ảnh một dòng kèm ảnh thu nhỏ + kết quả kiểm + cột DUYỆT (OK/SỬA/BỎ) + GHI CHÚ.
"""
import sys, os, json, argparse, subprocess, io
import numpy as np, cv2
import openpyxl
from openpyxl.drawing.image import Image as XLImage
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.worksheet.datavalidation import DataValidation
ap = argparse.ArgumentParser(); ap.add_argument("manifest"); ap.add_argument("--root", default="."); ap.add_argument("--out", default=".")
a = ap.parse_args()
M = json.load(open(a.manifest, encoding="utf-8"))["items"]
items = [i for i in M if i.get("status", i.get("approval")) in ("OK", "SỬA") and i.get("sheet", "SHOTS") in ("SHOTS", "SFX")]
if not items: print("Không có mục nào đã duyệt OK/SỬA"); sys.exit(1)
def dur(p):
    try: return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p], capture_output=True, text=True).stdout.strip())
    except Exception: return None
def ahash(im):
    g = cv2.resize(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY), (16, 16), interpolation=cv2.INTER_AREA).astype(np.float32)
    return (g > g.mean()).flatten()
res, hashes = [], {}
wb = openpyxl.Workbook(); ws = wb.active; ws.title = "ANH"
hdr = ["ID", "FILE", "PHỦ", "THU NHỎ", "KẾT QUẢ KIỂM", "DUYỆT", "GHI CHÚ CỦA ANH"]
ws.append(hdr)
for c in ws[1]: c.font = Font(bold=True, color="FFFFFF"); c.fill = PatternFill("solid", fgColor="1F3A2E")
for k, w in zip("ABCDEFG", [14, 28, 14, 46, 50, 9, 30]): ws.column_dimensions[k].width = w
r = 2; sfx_rows = []
for it in items:
    fp = os.path.join(a.root, it["file"]) if it.get("file") else ""
    notes = []
    if not fp or not os.path.exists(fp):
        if it["id"].find("SFX") >= 0 or it["id"].find("MUS") >= 0 or it["id"].find("ACC") >= 0: sfx_rows.append((it["id"], it["file"], "THIẾU FILE")); continue
        ws.append([it["id"], it.get("file"), it.get("covers_text", it.get("covers")), "", "❌ THIẾU FILE — Muse chưa giao", "CHỜ", ""]); r += 1; continue
    ext = os.path.splitext(fp)[1].lower()
    if ext in (".wav", ".mp3", ".m4a", ".ogg"):
        sfx_rows.append((it["id"], it["file"], f"{dur(fp) or 0:.1f}s")); continue
    im = cv2.imread(fp)
    if im is None:
        ws.append([it["id"], it["file"], it.get("covers_text", it.get("covers")), "", "❌ không đọc được ảnh", "CHỜ", ""]); r += 1; continue
    h, w = im.shape[:2]
    if (w, h) != (2560, 1440): notes.append(f"⚠ {w}x{h} (cần 2560x1440; sẽ bị phóng to/mất nét)" if w < 2560 else f"ℹ {w}x{h} (sẽ thu về 2560x1440)")
    if abs(w / h - 16 / 9) > 0.02: notes.append("❌ sai tỉ lệ 16:9")
    lum = float(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).mean())
    if lum < 38: notes.append(f"⚠ rất tối (độ sáng TB {lum:.0f}/255) — chỉ ổn nếu là cảnh 'im lặng'")
    if lum > 215: notes.append(f"⚠ rất sáng ({lum:.0f}/255)")
    hh = ahash(im)
    for oid, oh in hashes.items():
        if (hh == oh).mean() > 0.94: notes.append(f"⚠ quá giống {oid} (tránh hai cảnh liền nhau cùng một hình)")
    hashes[it["id"]] = hh
    th = cv2.resize(im, (320, 180), interpolation=cv2.INTER_AREA)
    tp = os.path.join(a.out, f"_thumb_{it['id']}.png"); cv2.imwrite(tp, th)
    ws.append([it["id"], it["file"], it.get("covers_text", it.get("covers")), "", "\n".join(notes) or "✅ đạt kiểm tự động", "CHỜ", ""])
    xi = XLImage(tp); xi.width, xi.height = 320, 180; ws.add_image(xi, f"D{r}")
    ws.row_dimensions[r].height = 140
    for c in ws[r]: c.alignment = Alignment(wrap_text=True, vertical="top")
    r += 1
dv = DataValidation(type="list", formula1='"CHỜ,OK,SỬA,BỎ"'); ws.add_data_validation(dv); dv.add(f"F2:F{r}")
ws.freeze_panes = "B2"
w2 = wb.create_sheet("AM_THANH"); w2.append(["ID", "FILE", "TRẠNG THÁI / ĐỘ DÀI"])
for x in sfx_rows: w2.append(list(x))
for k, w in zip("ABC", [16, 40, 24]): w2.column_dimensions[k].width = w
outp = os.path.join(a.out, "asset_review.xlsx"); wb.save(outp)
miss = sum(1 for x in sfx_rows if x[2] == "THIẾU FILE") + sum(1 for row in ws.iter_rows(min_row=2, values_only=True) if row[4] and "THIẾU" in str(row[4]))
print(f"Đã kiểm {len(items)} mục -> {outp}  (thiếu file: {miss})")
sys.exit(1 if miss else 0)
