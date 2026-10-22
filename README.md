# Muse Overlay Kit — dựng video "ảnh tĩnh + edit chồng lớp" mượt như phim

Bộ công cụ + quy trình để một AI producer (Muse) hoặc người dựng tạo video documentary từ **ảnh tĩnh + giọng đọc**,
với camera mượt, chuyển cảnh trong khoảng lặng, và lớp đồ hoạ chồng theo đúng nhịp lời đọc.

| File | Việc |
|---|---|
| `overlay_engine.py` | Engine: đọc `spec.json` → render MP4 (hình + mix tiếng). 17 loại phần tử, camera easing/shake, dissolve, grain/vignette |
| `tools/find_gaps.py` | Từ `wordts.json` (Whisper) → danh sách câu + khoảng lặng để đặt điểm cắt/dissolve |
| `tools/analyze_video.py` | **Máy chấm từng khung hình**: jitter camera, khung chết, khoảng trống sự kiện, kiểu chuyển cảnh |
| `examples/koepcke_hook.json` | Spec thật của Hook Koepcke 28s (tái tạo pixel-identical bản đã duyệt) |
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
