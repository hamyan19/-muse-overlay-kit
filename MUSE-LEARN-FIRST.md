# GỬI MUSE — ĐỌC TRƯỚC KHI DỰNG BẤT KỲ BEAT NÀO
(Bắt đầu từ `MUSE-COMMANDS.md`: lệnh làm một beat với các cổng duyệt của anh.)

Đây là bộ công cụ + quy trình để dựng video ảnh tĩnh + overlay **mượt đúng chuẩn bản Hook Koepcke đã duyệt**.
Bản pilot v2 trước đó bị chấm từng khung hình và có lỗi: nền rung (jitter), cảnh trống 7–8s không có sự kiện mới,
đoạn tĩnh dài. Từ nay mọi beat phải qua máy chấm `tools/analyze_video.py` TRƯỚC khi nộp.

Cập nhật 22/10: bản Beat 1 của Muse (10 phần tử/85s, thẻ đứng yên, chữ nhỏ, dấu kẹt cảnh cuối) thua bản tham chiếu ở TƯ DUY BIÊN TẬP, không phải kỹ thuật.
Kit đã thêm: `EDITORIAL-PATTERNS.md` (mệnh đề → sự kiện), `tools/word_times.py`, `tools/lint_spec.py` (bắt buộc trước render), `LESSONS.md` (nhật ký tự học).

Thứ tự học (≈10 phút):
1. `PLAYBOOK.md` — 8 nguyên tắc + quy trình 8 bước + bảng lỗi.
2. `EFFECTS.md` — 17 hiệu ứng có sẵn, tham số và khi nào dùng.
3. `examples/koepcke_hook.json` — spec mẫu hoàn chỉnh (28s); `examples/demo_effects.json` — hiệu ứng mới.
4. Chạy thử: `pip install -r requirements.txt` rồi
   `python3 overlay_engine.py examples/koepcke_hook.json --root <thư mục res> --frames 1.0,9.8,15.4`
   (res = thư mục có stills/ vo/ sfx/ fonts/ của Hook Resources).
5. Với beat mới: làm theo `MUSE-COMMANDS.md` và `PIPELINE.md` (3 cổng duyệt bằng xlsx). Khi dựng: `tools/word_times.py --auto` → spec → `tools/lint_spec.py` → render → `tools/analyze_video.py` → ghi `LESSONS.md`.

Cam kết khi nộp: đính kèm mp4 + spec.json + qa/report.txt; nói rõ sfx nào còn là placeholder (_TAM).
Nếu môi trường của Muse không chạy được Python/ffmpeg/OpenCV, hãy báo ngay để người dùng biết, đừng tự đổi kỹ thuật.
