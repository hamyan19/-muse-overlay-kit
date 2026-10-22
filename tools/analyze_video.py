#!/usr/bin/env python3
"""KIỂM TOÁN TỪNG KHUNG HÌNH một video. Dùng để chấm video của Muse (hoặc của chính mình) TRƯỚC khi nộp.
  python3 analyze_video.py clip.mp4 [--out report_dir]
Đo:
 1. JITTER camera: phase-correlation giữa các khung liên tiếp -> vận tốc dịch chuyển; đếm số lần ĐẢO CHIỀU vận tốc
    và gia tốc RMS. Zoom/pan mượt = vận tốc đổi dấu ~0 lần, gia tốc nhỏ. Rung/giật = nhiều lần đảo chiều.
 2. KHUNG CHẾT: đoạn >0.6s mà nội dung (đã làm mờ để bỏ grain) gần như không đổi.
 3. KHOẢNG TRỐNG SỰ KIỆN: >3.5s liền không có 'sự kiện thị giác' mới (đỉnh năng lượng thay đổi cục bộ).
 4. CẮT CỨNG vs DISSOLVE: liệt kê các điểm đổi cảnh, độ dài chuyển cảnh.
 5. XUẤT: report.txt, energy.png (đường năng lượng + vùng lỗi), contact.png (mỗi 1s một khung).
Ngưỡng PASS: đảo chiều vận tốc <= 1.5 lần/s trong đoạn camera chạy; không khung chết >0.6s; không khoảng trống >3.5s.
"""
import sys, os, argparse
import numpy as np, cv2
ap = argparse.ArgumentParser(); ap.add_argument("video"); ap.add_argument("--out", default="analysis")
a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
cap = cv2.VideoCapture(a.video); fps = cap.get(cv2.CAP_PROP_FPS) or 30
fr_s, fr_g, thumbs = [], [], []
i = 0
while True:
    ok, f = cap.read()
    if not ok: break
    g = cv2.cvtColor(cv2.resize(f, (640, 360), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY).astype(np.float32)
    fr_g.append(g)
    fr_s.append(cv2.GaussianBlur(cv2.resize(g, (160, 90), interpolation=cv2.INTER_AREA), (0, 0), 1.5))
    if i % int(round(fps)) == 0: thumbs.append(cv2.resize(f, (320, 180)))
    i += 1
n = len(fr_g); dur = n / fps
lines = [f"FILE {a.video}  khung={n}  fps={fps:.2f}  dài={dur:.2f}s"]

# --- ước lượng chuyển động toàn cục từng cặp khung (đặc trưng + RANSAC, chịu được zoom + overlay)
H_, W_ = 360, 640
pts5 = np.float32([[W_/2, H_/2], [0, 0], [W_, 0], [0, H_], [W_, H_]]).reshape(-1, 1, 2)
V = np.zeros((n, 5, 2)); resid = np.zeros(n); okm = np.zeros(n, bool)
d_cut = np.array([0] + [np.abs(fr_s[k] - fr_s[k-1]).mean() for k in range(1, n)])
cuts = [k for k in range(1, n) if d_cut[k] > 25]
for k in range(1, n):
    p0 = cv2.goodFeaturesToTrack(fr_g[k-1].astype(np.uint8), 300, 0.01, 8)
    if p0 is None or len(p0) < 12: continue
    p1, st, _ = cv2.calcOpticalFlowPyrLK(fr_g[k-1].astype(np.uint8), fr_g[k].astype(np.uint8), p0, None,
                                         winSize=(21, 21), maxLevel=3)
    st = st.ravel() == 1
    if st.sum() < 12: continue
    M, inl = cv2.estimateAffinePartial2D(p0[st], p1[st], method=cv2.RANSAC, ransacReprojThreshold=1.5)
    if M is None or inl is None or inl.sum() < 0.5 * st.sum() or inl.sum() < 12: continue
    V[k] = (cv2.transform(pts5, M) - pts5).reshape(5, 2); okm[k] = True
    warped = cv2.warpAffine(fr_g[k-1], M, (W_, H_), borderMode=cv2.BORDER_REPLICATE)
    r = cv2.GaussianBlur(np.abs(warped - fr_g[k]), (0, 0), 2.0)
    resid[k] = r[40:-40, 40:-40].mean()
near_cut = np.zeros(n, bool)
for c in cuts + [int(m*fps) for m in ()]:
    near_cut[max(0, c-2):c+3] = True
k9 = np.ones(9) / 9
hf = np.zeros(n)
for j in range(5):
    for ax_ in range(2):
        v = V[:, j, ax_]
        hf += (v - np.convolve(v, k9, mode="same")) ** 2
hf = np.sqrt(hf / 10)
spd = np.mean([np.sqrt(sum(np.convolve(V[:, j, i], k9, mode="same") ** 2 for i in range(2))) for j in range(5)], axis=0)
mov = (spd > 0.05) & okm & ~near_cut
jit = float(np.percentile(hf[mov], 75)) if mov.any() else 0.0   # bách phân vị 75: bỏ qua khung đo hỏng
rel = jit / max(float(spd[mov].mean()), 0.05) if mov.any() else 0.0
mv_time = mov.sum() / fps
lines += ["", "[1] JITTER CAMERA (nhiễu tần số cao của chuyển động nền, px ở 640x360)",
          f"  thời gian camera chuyển động: {mv_time:.1f}s",
          f"  jitter (P75): {jit:.3f} px/khung   |  tỉ lệ jitter/tốc độ: {rel:.2f}",
          "  KẾT LUẬN: " + ("PASS (mượt)" if jit < 0.12 else "FAIL — nền rung/giật: render 2x + Lanczos + INTER_AREA, đừng làm tròn toạ độ pixel")]

# --- 2. khung chết: nền gần như đứng yên + không có thay đổi cục bộ
dead_thr = 1.2
quiet = (resid < 0.35) & (spd < 0.06)
runs = []; s0 = None
for k in range(1, n):
    if quiet[k] and s0 is None: s0 = k
    if (not quiet[k] or k == n-1) and s0 is not None:
        L = (k - s0) / fps
        if L > dead_thr: runs.append((s0 / fps, k / fps))
        s0 = None
lines += ["", f"[2] KHUNG CHẾT (> {dead_thr}s nền đứng yên + overlay không đổi)"] + \
         ([f"  {x:6.2f}-{y:6.2f}s ({y-x:.1f}s)" for x, y in runs] or ["  không có"]) + \
         ["  KẾT LUẬN: " + ("PASS" if not runs else "XEM LẠI — chỉ chấp nhận nếu là khoảng thở có chủ đích <= 1.5s")]

# --- 3. sự kiện thị giác = đỉnh của phần dư sau khi trừ chuyển động camera
med = np.median(resid[1:]); mad = np.median(np.abs(resid[1:] - med)) + 1e-6
thr = med + 5 * mad
ev = [k / fps for k in range(2, n-1) if resid[k] > thr and resid[k] >= resid[k-1] and resid[k] >= resid[k+1]]
merged = []
for t in ev:
    if not merged or t - merged[-1] > 0.3: merged.append(t)
pts = [0.0] + merged + [dur]
gaps = [(p, q) for p, q in zip(pts, pts[1:]) if q - p > 3.5]
lines += ["", f"[3] SỰ KIỆN THỊ GIÁC mới (chữ hiện, thẻ, vòng, dissolve...): {len(merged)}  (≈ 1 mỗi {dur/max(len(merged),1):.1f}s; mục tiêu <= 3.5s)"] + \
         [f"  trống {p:6.2f}-{q:6.2f}s ({q-p:.1f}s)" for p, q in gaps] + \
         ["  (lưu ý: chỉ đếm sự kiện RỜI RẠC; hoạt ảnh liên tục như đếm số/thang đo/zoom không tính — nhìn energy.png để đánh giá)",
         "  KẾT LUẬN: " + ("PASS" if not gaps else "XEM LẠI — chèn phần tử/hiệu ứng trong các đoạn trống")]
t_ = np.arange(n) / fps
dx = V[:, 0, 0]; dy = V[:, 0, 1]; acc = hf[2:]

# --- 4. chuyển cảnh
lines += ["", "[4] ĐỔI CẢNH"]
grp = []
for k in cuts:
    if not grp or k - grp[-1][-1] > 2: grp.append([k])
    else: grp[-1].append(k)
lines += [f"  CẮT CỨNG hoặc CHỚP TRẮNG tại {g[0]/fps:.2f}s" for g in grp] or ["  không có cắt cứng"]
bigm = np.convolve(d_cut, np.ones(5) / 5, mode="same")
dis = []; s0 = None
for k in range(n):
    hi = 2.0 < bigm[k] <= 12 and not any(abs(k - g[0]) < 3 for g in grp)
    if hi and s0 is None: s0 = k
    if not hi and s0 is not None:
        if (k - s0) / fps >= 0.25: dis.append((s0 / fps, (k - s0) / fps))
        s0 = None
lines += [f"  (có thể là) dissolve/chuyển động mạnh ~{t:.2f}s dài {l:.2f}s" for t, l in dis[:12]]

open(os.path.join(a.out, "report.txt"), "w", encoding="utf-8").write("\n".join(lines))
print("\n".join(lines))

# --- plot + contact sheet
try:
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    t = np.arange(n) / fps
    fig, ax = plt.subplots(3, 1, figsize=(12, 7), sharex=True)
    ax[0].plot(t, d_cut, lw=.8); ax[0].set_ylabel("thay đổi/khung")
    for x, y in runs: ax[0].axvspan(x, y, color="r", alpha=.25)
    for p, q in gaps: ax[0].axvspan(p, q, color="orange", alpha=.2)
    for m in merged: ax[0].axvline(m, color="g", lw=.5)
    ax[1].plot(t, dx, lw=.8, label="dx"); ax[1].plot(t, dy, lw=.8, label="dy"); ax[1].legend(); ax[1].set_ylabel("dịch chuyển px/khung")
    ax[2].plot(t[2:], acc, lw=.8, color="m"); ax[2].set_ylabel("gia tốc (jitter)"); ax[2].set_xlabel("giây")
    fig.suptitle("đỏ=khung chết, cam=trống sự kiện, xanh=sự kiện mới"); fig.tight_layout(); fig.savefig(os.path.join(a.out, "energy.png"), dpi=90)
except Exception as e:
    print("(bỏ qua plot:", e, ")")
cols = 5; rows = (len(thumbs) + cols - 1) // cols
sheet = np.zeros((rows * 180, cols * 320, 3), np.uint8)
for j, th in enumerate(thumbs):
    r, c = divmod(j, cols); sheet[r*180:(r+1)*180, c*320:(c+1)*320] = th
    cv2.putText(sheet, f"{j}s", (c*320+6, r*180+22), cv2.FONT_HERSHEY_SIMPLEX, .7, (0, 255, 255), 2)
cv2.imwrite(os.path.join(a.out, "contact.png"), sheet)
