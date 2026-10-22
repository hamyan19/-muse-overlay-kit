# QUY TRÌNH CHUNG — đọc file này TRƯỚC (Muse làm chính)

Các file khác (PIPELINE, PLAYBOOK, EDITORIAL-PATTERNS, EFFECTS...) là **tham chiếu, chỉ đọc khi cần** ở đúng bước.

## Ai làm gì
- **Muse (chính):** script, character sheet, hình, tìm footage, voice, âm thanh (và cập nhật `SOUND-LIBRARY.md`), QC các nguyên liệu này.
- **Dựng:** Muse hoặc Claude, anh chọn (dùng `overlay_engine.py` + `EDITORIAL-PATTERNS.md`).
- **Anh:** duyệt ở 2 cổng.

## 6 bước (làm TUẦN TỰ theo chương: xong chương này mới sang chương sau)
**Đầu dự án, một lần:** Character sheet (`CHARACTER-SHEET.md`) → anh duyệt → khóa.

Mỗi chương:
1. **Script + ghi chú** (`SCRIPT-NOTES.md`): chương bình thường/sôi nổi, câu nào cần hình gì (không lặp), phong cách tiếng + âm thanh phụ trợ.
2. **Hình** theo kế hoạch → QC cứng (`QC-ASSETS.md`, `tools/qc_assets.py`).
3. **Footage** nếu script cần: nói rõ cảnh nào, ghép với ảnh hay thay ảnh (20–30% chương).
4. **Voice** → `wordts.json`.
5. **Âm thanh**: tra `SOUND-LIBRARY.md` trước, thiếu mới tạo/tìm, rồi ghi bổ sung vào thư viện.
6. **Dựng** → lint → render → analyze → video chương.

## 2 cổng anh duyệt
- **Cổng 1 — Kế hoạch:** `asset_plan.xlsx` (hình theo câu, footage, âm thanh). Anh điền OK/SỬA/BỎ. Dòng CHỜ chưa được làm.
- **Cổng 2 — Nguyên liệu thật:** `asset_review.xlsx` (ảnh thu nhỏ, kiểm tự động, voice, âm thanh). Duyệt xong mới dựng.
- Xem video chương là bước xem kết quả, không phải cổng riêng; anh nhận xét thì sửa.

## Lệnh nhanh (chạy ngầm, không phải việc của anh)
```bash
python3 tools/plan_assets.py res/vo/wordts.json --beat B2 --out plan/     # lập kế hoạch -> Cổng 1
python3 tools/apply_approval.py plan/asset_plan.xlsx --out plan/           # đọc sheet đã duyệt
python3 tools/qc_assets.py ...                                             # QC cứng (FAIL=0)
python3 tools/check_assets.py plan/approved_manifest.json --root res --out plan/   # -> Cổng 2
python3 tools/lint_spec.py spec.json --root res && python3 overlay_engine.py spec.json --root res --out beat.mp4
python3 tools/analyze_video.py beat.mp4 --out qa/
```
Chi tiết từng lệnh: `PIPELINE.md`.

## Luật cứng
1. Không tự duyệt; không làm dòng CHỜ.
2. Mọi ảnh bám character sheet; ảnh sai kích thước (không phải 2560×1440) phải báo thẳng, không phóng lớn rồi gọi là gốc.
3. Cuối mỗi chương ghi bài học vào `LESSONS.md` và cập nhật `SOUND-LIBRARY.md` / character sheet nếu có đổi.
4. Mỗi chương một phong cách hình/tiếng khác chương liền kề (tránh lặp, tránh bị quét nội dung lặp).
