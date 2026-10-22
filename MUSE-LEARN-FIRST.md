# GỬI MUSE — ĐỌC TRƯỚC KHI DỰNG BẤT KỲ BEAT NÀO

Đây là bộ công cụ + quy trình để dựng video ảnh tĩnh + overlay **mượt đúng chuẩn bản Hook Koepcke đã duyệt**.
Bản pilot v2 trước đó bị chấm từng khung hình và có lỗi: nền rung (jitter), cảnh trống 7–8s không có sự kiện mới,
đoạn tĩnh dài. Từ nay mọi beat phải qua máy chấm `tools/analyze_video.py` TRƯỚC khi nộp.

Thứ tự học (≈10 phút):
1. `PLAYBOOK.md` — 8 nguyên tắc + quy trình 8 bước + bảng lỗi.
2. `EFFECTS.md` — 17 hiệu ứng có sẵn, tham số và khi nào dùng.
3. `examples/koepcke_hook.json` — spec mẫu hoàn chỉnh (28s); `examples/demo_effects.json` — hiệu ứng mới.
4. Chạy thử: `pip install -r requirements.txt` rồi
   `python3 overlay_engine.py examples/koepcke_hook.json --root <thư mục res> --frames 1.0,9.8,15.4`
   (res = thư mục có stills/ vo/ sfx/ fonts/ của Hook Resources).
5. Với beat mới: `tools/find_gaps.py` → viết spec → render → `tools/analyze_video.py` → sửa tới khi PASS.

Cam kết khi nộp: đính kèm mp4 + spec.json + qa/report.txt; nói rõ sfx nào còn là placeholder (_TAM).
Nếu môi trường của Muse không chạy được Python/ffmpeg/OpenCV, hãy báo ngay để người dùng biết, đừng tự đổi kỹ thuật.
