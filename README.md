# Muse Overlay Kit — dựng video "ảnh tĩnh + edit chồng lớp" mượt như phim

Bộ công cụ + quy trình để một AI producer (Muse) hoặc người dựng tạo video documentary từ **ảnh tĩnh + giọng đọc**,
với camera mượt, chuyển cảnh trong khoảng lặng, và lớp đồ hoạ chồng theo đúng nhịp lời đọc.

## BẮT ĐẦU Ở ĐÂY — đọc `QUY-TRINH.md` (Muse làm chính, 2 cổng duyệt) — 6 bước
1. **Script** — kịch bản kèm ghi chú rõ theo `SCRIPT-NOTES.md`: câu nào cần hình gì (không lặp), mỗi chương là *bình thường* hay *sôi nổi*, phong cách tiếng và **âm thanh phụ trợ** gì (nền, tiếng động, nhạc, im lặng).
2. **Character sheet (một lần, đầu dự án)** — nhân vật, đạo cụ, bối cảnh, phong cách + ảnh master, anh duyệt rồi khóa (`CHARACTER-SHEET.md`).
3. **Tạo hình** — ảnh tĩnh theo kế hoạch đã duyệt (một bên làm: Muse *hoặc* GPT).
4. **Tìm footage nếu có** — video chỉ khi script cần, ghi rõ cảnh nào, để làm gì.
5. **Voice** — thu giọng đọc theo beat, xuất mốc thời gian từng từ.
6. **Dựng** — Claude dựng từ ảnh + voice + âm thanh, anh xem bản cuối.

**Ai làm gì:** Muse làm script, voice, hình, tìm footage và âm thanh (và cập nhật `SOUND-LIBRARY.md`). Dựng do Muse **hoặc** GPT/Claude, anh chọn.
**Làm tuần tự theo chương:** xong NGUYÊN LIỆU của một chương (script, hình, footage, voice, âm thanh, đã QC và anh duyệt) rồi mới sang chương tiếp theo. Không làm song song nhiều chương.

Mọi thứ khác trong repo (plan_assets, lint, QC, cổng duyệt...) là công cụ chạy ngầm phục vụ 5 bước này, không phải việc thêm cho anh.

| File | Việc |
|---|---|
| `overlay_engine.py` | Engine: đọc `spec.json` → render MP4 (hình + mix tiếng). 24 loại phần tử, 4 fx chuyển-động-trong-ảnh-tĩnh (ripple/sway/glow/parallax), cảnh video + 3 preset phong cách, camera easing/shake, dissolve, grain/vignette |
| `tools/find_gaps.py` | Từ `wordts.json` (Whisper) → danh sách câu + khoảng lặng để đặt điểm cắt/dissolve |
| `MUSE-COMMANDS.md`, `PIPELINE.md` | **Lệnh cho Muse + quy trình 3 cổng duyệt**: plan_assets → anh duyệt xlsx → sinh nguyên liệu → check_assets → anh duyệt ảnh → dựng |
| `tools/plan_assets.py` | Từ `wordts.json` liệt kê TOÀN BỘ nguyên liệu cần (ảnh theo cảnh, overlay, sfx) → `asset_plan.xlsx` có cột DUYỆT (OK/SỬA/BỎ) |
| `tools/apply_approval.py` | Đọc sheet đã duyệt → `MUSE-TODO.md` (chỉ làm OK/SỬA, không đụng CHỜ) |
| `tools/qc_assets.py` + `QC-ASSETS.md` | **QC CỨNG** ảnh/video/âm thanh (độ nét, đen/cháy, viền, ám màu, mặt, chữ/logo, đứng hình, cắt ngầm, rung, LUFS...) + bảng kiểm mắt 12 mục. Muse chạy TRƯỚC khi gửi anh duyệt |
| `tools/check_assets.py` | Kiểm nguyên liệu Muse giao (kích thước, độ sáng, trùng) → `asset_review.xlsx` có ảnh thu nhỏ để duyệt lần 2 |
| `tools/word_times.py` | Tra mốc cụm từ + bảng "mệnh đề → hiệu ứng gợi ý" (phủ định, số, tên riêng, trích dẫn) |
| `tools/lint_spec.py` | **Kiểm spec trước render**: trống sự kiện, overlay tĩnh, thiếu t_out, chữ nhỏ, chồng thẻ, cảnh tối, đơn điệu |
| `QUY-TRINH.md` | **ĐỌC ĐẦU TIÊN** — quy trình chung gọn: ai làm gì, 6 bước, 2 cổng |
| `SOUND-LIBRARY.md` | **Thư viện âm thanh dùng lại** — Muse cập nhật mỗi khi có âm thanh mới |
| `CHARACTER-SHEET.md` | **Character sheet** làm đầu dự án, áp dụng xuyên suốt mọi chương |
| `SCRIPT-NOTES.md` | **Ghi chú script**: hình theo từng câu (không lặp), phong cách tiếng theo chương, tránh bị quét nội dung lặp |
| `EDITORIAL-PATTERNS.md` | Ngữ pháp biên tập: mệnh đề lời đọc → sự kiện hình |
| `LESSONS.md` | Nhật ký bài học (Muse tự cập nhật mỗi beat) |
| `tools/analyze_video.py` | **Máy chấm từng khung hình**: jitter camera, khung chết, khoảng trống sự kiện, kiểu chuyển cảnh |
| `examples/koepcke_hook.json` | Spec thật của Hook Koepcke 28s (tái tạo pixel-identical bản đã duyệt) |
| `examples/styles/*.json` | 3 preset phong cách (phim cũ / điện ảnh tối giản / chữ chạy theo lời) trên cùng một đoạn |
| `examples/demo_motion.json` + `tools/make_fog_loop.py` | Chuyển động trong ảnh tĩnh: ripple, sway, glow, parallax, bụi/tàn lửa, clip sương chồng, cảnh video |
| `examples/demo_effects.json` | Demo các hiệu ứng mới (spotlight, highlight_box, stamp, lower_third, timeline, ticker, redact, flash, shake) |
| `PLAYBOOK.md` | Quy trình làm từng beat + lỗi thường gặp + checklist QC |
| `EFFECTS.md` | Tham chiếu từng hiệu ứng: tham số + khi nào dùng |

## Chạy nhanh
```bash
pip install -r requirements.txt
python3 overlay_engine.py examples/koepcke_hook.json --root ../res --frames 1.0,9.8,15.4   # xem vài khung
python3 overlay_engine.py examples/koepcke_hook.json --root ../res --out hook.mp4 --jobs 4  # render đầy đủ
python3 tools/analyze_video.py hook.mp4 --out qa/                                           # chấm trước khi nộp
python3 tools/find_gaps.py ../res/vo/wordts.json                                            # tìm điểm cắt
```
`--root` = thư mục chứa `stills/ vo/ sfx/ fonts/` (đường dẫn trong spec tính từ đây).
