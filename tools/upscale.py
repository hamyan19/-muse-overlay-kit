#!/usr/bin/env python3
"""UPSCALE — phóng ảnh nhỏ lên 4K (3840x2160) để zoom sâu vẫn nét. Chạy CPU, không cần GPU.

  python3 tools/upscale.py anh_ch3/ anh_ch3_4k/                 # mặc định FSRCNN x2 (~2–3s/ảnh trên CPU), khớp đúng 3840x2160
  python3 tools/upscale.py anh_ch3/ anh_ch3_4k/ --model edsr    # sắc hơn chút nhưng RẤT chậm trên CPU 2 nhân (>10 phút/ảnh)
Đo trên ảnh Ch2 (1672x941 -> 4K): độ nét FSRCNN 57 so với phóng thường (Lanczos) 33 — khá hơn rõ nhưng không bằng
Real-ESRGAN. Muốn đẹp nhất: An chạy Upscayl trên máy (mô hình digital art/anime) rồi gửi ảnh 4K.
  python3 tools/upscale.py anh/CH3_M02.png out/ --target 5120   # đích 5120x2880

Cần: pip install opencv-contrib-python-headless (có cv2.dnn_superres). Mô hình (.pb, chỉ là trọng số) tự tải lần đầu
từ GitHub (Saafke/EDSR_Tensorflow, Saafke/FSRCNN_Tensorflow) vào ~/.cache/muse-sr/.
Ảnh đã đủ lớn (>= đích) thì chỉ sao chép. Chạy theo ô (tile) để không tràn RAM. Mỗi ảnh in 1 dòng.
Ghi chú: Real-ESRGAN anime đẹp hơn cho nét vẽ phẳng nhưng cần chạy chương trình ngoài (Upscayl trên máy An).
"""
import argparse, glob, os, sys, time, urllib.request
import cv2, numpy as np

URL = {"edsr": "https://raw.githubusercontent.com/Saafke/EDSR_Tensorflow/master/models/EDSR_x{s}.pb",
       "fsrcnn": "https://raw.githubusercontent.com/Saafke/FSRCNN_Tensorflow/master/models/FSRCNN_x{s}.pb"}
ap = argparse.ArgumentParser(); ap.add_argument("src"); ap.add_argument("dst")
ap.add_argument("--model", choices=["edsr", "fsrcnn"], default="fsrcnn")
ap.add_argument("--target", type=int, default=3840, help="bề ngang đích (16:9)")
ap.add_argument("--tile", type=int, default=240); ap.add_argument("--pad", type=int, default=12)
a = ap.parse_args()
if not hasattr(cv2, "dnn_superres"):
    sys.exit("Thiếu cv2.dnn_superres: pip install opencv-contrib-python-headless")

def model(scale):
    d = os.path.expanduser("~/.cache/muse-sr"); os.makedirs(d, exist_ok=True)
    p = os.path.join(d, f"{a.model}_x{scale}.pb")
    if not os.path.exists(p):
        urllib.request.urlretrieve(URL[a.model].format(s=scale), p)
    sr = cv2.dnn_superres.DnnSuperResImpl_create(); sr.readModel(p); sr.setModel(a.model, scale); return sr

def up_tiled(sr, im, s):
    h, w = im.shape[:2]; T, P = a.tile, a.pad
    out = np.zeros((h * s, w * s, 3), np.uint8)
    for y in range(0, h, T):
        for x in range(0, w, T):
            y0, x0 = max(0, y - P), max(0, x - P); y1, x1 = min(h, y + T + P), min(w, x + T + P)
            o = sr.upsample(np.ascontiguousarray(im[y0:y1, x0:x1]))
            ty, tx = (y - y0) * s, (x - x0) * s; th, tw = min(T, h - y) * s, min(T, w - x) * s
            out[y * s:y * s + th, x * s:x * s + tw] = o[ty:ty + th, tx:tx + tw]
    return out

files = [a.src] if os.path.isfile(a.src) else sorted(glob.glob(os.path.join(a.src, "*.png")) + glob.glob(os.path.join(a.src, "*.jpg")))
os.makedirs(a.dst, exist_ok=True); cache = {}
TW, TH = a.target, round(a.target * 9 / 16)
for f in files:
    name = os.path.splitext(os.path.basename(f))[0] + ".png"; t = time.time()
    im = cv2.imread(f)
    if im is None: print("bỏ qua (không đọc được):", f); continue
    h, w = im.shape[:2]
    if w >= TW:
        cv2.imwrite(os.path.join(a.dst, name), im); print(f"{name}: {w}x{h} đã đủ lớn, giữ nguyên"); continue
    while im.shape[1] * 2 <= TW * 1.15:          # x2 cho tới gần đích (1672 -> 3344; 1024 -> 2048 -> 4096)
        s = 2
        if s not in cache: cache[s] = model(s)
        im = up_tiled(cache[s], im, s)
    im = cv2.resize(im, (TW, TH), interpolation=cv2.INTER_AREA if im.shape[1] > TW else cv2.INTER_LANCZOS4)
    cv2.imwrite(os.path.join(a.dst, name), im)
    print(f"{name}: {w}x{h} -> {TW}x{TH} ({a.model}, {time.time() - t:.0f}s)")
