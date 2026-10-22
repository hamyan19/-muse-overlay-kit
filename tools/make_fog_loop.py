#!/usr/bin/env python3
"""Tạo clip lặp liền mạch (procedural) để dùng khi chưa có footage thật: sương, khói, bụi sáng.
  python3 make_fog_loop.py fog out.mp4 [--seconds 6] [--w 1280 --h 720]
Dùng với element video_overlay (blend 'screen', nền đen -> trong suốt) hoặc làm 'video' của một cảnh.
Lặp liền mạch vì nhiễu cuộn theo chu kỳ đúng bằng bề rộng texture.
"""
import sys, argparse, subprocess
import numpy as np, cv2
ap = argparse.ArgumentParser(); ap.add_argument("kind", choices=["fog", "smoke"]); ap.add_argument("out")
ap.add_argument("--seconds", type=float, default=6.0); ap.add_argument("--w", type=int, default=1280); ap.add_argument("--h", type=int, default=720)
ap.add_argument("--fps", type=int, default=30)
a = ap.parse_args()
W, H, N = a.w, a.h, int(a.seconds * a.fps)
def tex(seed, scale, w):
    rng = np.random.default_rng(seed)
    sm = rng.random((max(4, H // scale), max(8, w // scale))).astype(np.float32)
    big = cv2.resize(sm, (w, H), interpolation=cv2.INTER_CUBIC)
    big = cv2.GaussianBlur(np.tile(big, (1, 3)), (0, 0), scale * 0.6)[:, w:2 * w]   # lát 3 lần rồi lấy giữa => liền mạch ở mép
    return (big - big.min()) / (big.max() - big.min() + 1e-6)
layers = [(tex(1, 160, W), 1.0, 0.6), (tex(2, 80, W), 2.0, 0.4)]   # (tex, vòng/clip, trọng số)
pr = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "gray", "-s", f"{W}x{H}", "-r", str(a.fps),
                       "-i", "-", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", a.out], stdin=subprocess.PIPE)
for i in range(N):
    u = i / N; acc = np.zeros((H, W), np.float32)
    for t_, rounds, wt in layers:
        off = (u * rounds * W) % W; i0 = int(off); fr = off - i0
        A_ = np.roll(t_, -i0, axis=1); B_ = np.roll(t_, -i0 - 1, axis=1)
        acc += (A_ * (1 - fr) + B_ * fr) * wt
    lo, gain = (0.42, 2.4) if a.kind == "fog" else (0.5, 3.2)
    v = np.clip((acc - lo) * gain, 0, 1) * (0.85 if a.kind == "fog" else 0.7)
    pr.stdin.write((v * 255).astype(np.uint8).tobytes())
pr.stdin.close(); pr.wait(); print("xong", a.out)
