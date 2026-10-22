# GỬI MUSE — đọc `QUY-TRINH.md` đầu tiên
Repo: https://github.com/hamyan19/-muse-overlay-kit

Muse là người làm chính: script, character sheet, hình, footage, voice, âm thanh. Làm TUẦN TỰ từng chương, dừng ở 2 cổng anh duyệt:

1. Đầu dự án: lập character sheet (`CHARACTER-SHEET.md`), gửi anh duyệt, khóa.
2. Mỗi chương: script + ghi chú (`SCRIPT-NOTES.md`) → `plan_assets.py` → gửi `asset_plan.xlsx` (**Cổng 1**), dừng.
3. Anh duyệt → `apply_approval.py` → chỉ làm dòng OK/SỬA (không đụng CHỜ): hình, footage, voice, âm thanh (tra/cập nhật `SOUND-LIBRARY.md`).
4. **QC cứng** (`qc_assets.py` + bảng mắt `QC-ASSETS.md`, FAIL=0) → `check_assets.py` → gửi `asset_review.xlsx` (**Cổng 2**), dừng.
5. Duyệt xong mới dựng (Muse hoặc GPT/Claude, theo anh chọn) → lint → render → analyze → ghi `LESSONS.md` → gửi video.

Cấm: tự đánh dấu OK, làm khi còn CHỜ, sang chương sau khi chương này chưa duyệt, dùng ảnh sai kích thước mà không báo.
Mỗi video/chương chọn phong cách khác nhau (`--preset`, xem `EFFECTS.md` mục PRESET).
