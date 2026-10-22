# GỬI MUSE — LỆNH LÀM MỘT BEAT (đọc file này đầu tiên)
Repo: https://github.com/hamyan19/-muse-overlay-kit

Khi anh nói "làm beat X": làm đúng `PIPELINE.md`, dừng ở MỖI cổng duyệt (xlsx) và chờ anh trả lời. Tóm tắt:

1. Có VO + `wordts.json` của beat → chạy **LỆNH 1** (`tools/plan_assets.py`) → gửi `plan/asset_plan.xlsx`. Dừng.
2. Anh trả lại xlsx đã điền cột DUYỆT → **LỆNH 2** (`tools/apply_approval.py`) → làm theo `MUSE-TODO.md`: chỉ làm OK và SỬA; bỏ BỎ; không đụng CHỜ.
3. Sinh ảnh / tìm footage / tìm sfx đúng tên file đích → **QC CỨNG** (`tools/qc_assets.py` + bảng mắt trong `QC-ASSETS.md`, FAIL=0) → **LỆNH 3** (`tools/check_assets.py`) → gửi `plan/asset_review.xlsx`. Dừng.
4. Anh duyệt ảnh → viết spec (`EDITORIAL-PATTERNS.md`, `EFFECTS.md`) → `lint_spec.py` → render → `analyze_video.py` → ghi `LESSONS.md` → gửi video.

Cấm: tự đánh dấu OK, làm khi còn CHỜ, bỏ qua kiểm `lint`/`analyze`, dùng ảnh sai kích thước mà không báo.
Chọn phong cách mỗi video khác nhau (`--preset` / `"preset"` trong spec): xem `EFFECTS.md` mục PRESET.
