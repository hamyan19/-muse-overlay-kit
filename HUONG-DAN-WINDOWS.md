# Chạy kit trên máy Windows (không cần AI)
1. Cài Python 3.10+ (python.org, tick "Add to PATH") và ffmpeg (`winget install ffmpeg`, mở lại terminal, gõ `ffmpeg -version` để kiểm tra).
2. `git clone https://github.com/hamyan19/-muse-overlay-kit` rồi `cd -muse-overlay-kit` và `pip install -r requirements.txt`.
3. Đặt tài nguyên vào một thư mục `res/` có `stills/ vo/ sfx/ fonts/` (tải zip từ Drive, giải nén).
4. Dựng: `python overlay_engine.py examples/koepcke_hook.json --root res --out hook.mp4 --jobs 2 --crf 23 --lufs -14`
   (tăng `--jobs` bằng số nhân CPU để nhanh hơn; video 1 phút ≈ 15 phút trên máy 2 nhân.)
5. Xem trước vài khung (nhanh): `--frames 1.2,20,48 --frames-dir chk`.
6. Kiểm: `python tools/lint_spec.py spec.json --root res` và `python tools/analyze_video.py beat.mp4`.
Spec là file JSON (kịch bản dựng: ảnh nào, giây nào, hiệu ứng gì) — sửa bằng trình soạn thảo bất kỳ. Chưa thử trên Windows: nếu lỗi đường dẫn/font, báo để sửa.

**Kiểm đã cài đủ chưa (Windows/Mac/Linux):** `python -c "import cv2, numpy, PIL, openpyxl, matplotlib; print(cv2.__version__)"` và `ffmpeg -version`. Thiếu `cv2` → `pip install opencv-python-headless`; thiếu `openpyxl` (công cụ đọc/ghi bảng xlsx) → `pip install openpyxl`.
