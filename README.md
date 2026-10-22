# Muse Overlay Kit — dựng video "ảnh tĩnh + edit chồng lớp" mượt như phim

Bộ công cụ + quy trình để một AI producer (Muse) hoặc người dựng tạo video documentary từ **ảnh tĩnh + giọng đọc**,
với camera mượt, chuyển cảnh trong khoảng lặng, và lớp đồ hoạ chồng theo đúng nhịp lời đọc.

| File | Việc |
|---|---|
| `overlay_engine.py` | Engine: đọc `spec.json` → render MP4 (hình + mix tiếng). 24 loại phần tử, 4 fx chuyển-động-trong-ảnh-tĩnh (ripple/sway/glow/parallax), cảnh video + 3 preset phong cách, camera easing/shake, dissolve, grain/vignette |
| `tools/find_gaps.py` | Từ `wordts.json` (Whisper) → danh sách câu + khoảng lặng để đặt điểm cắt/dissolve |
| `tools/word_times.py` | Tra mốc cụm từ + bảng "mệnh đề → hiệu ứng gợi ý" (phủ định, số, tên riêng, trích dẫn) |
| `tools/lint_spec.py` | **Kiểm spec trước render**: trống sự kiện, overlay tĩnh, thiếu t_out, chữ nhỏ, chồng thẻ, cảnh tối, đơn điệu |
| `EDITORIAL-PATTERNS.md` | Ngữ pháp biên tập: mệnh đề lời đọc → sự kiện hình |
| `LESSONS.md` | Nhật ký bài học (Muse tự cập nhật mỗi beat) |
| `tools/analyze_video.py` | **Máy chấm từng khung hình**: jitter camera, khung chết, khoảng trống sự kiện, kiểu chuyển cảnh |
| `examples/koepcke_hook.json` | Spec thật của Hook Koepcke 28s (tái tạo pixel-identical bản đã duyệt) |
| `examples/beat1_lansa.json` | Spec Beat 1 thật (85s, 6 cảnh từ 4 ảnh, mưa, sương, tối dần) |
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
