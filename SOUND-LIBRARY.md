# Thư viện âm thanh (dùng lại giữa các chương / video)

Muse cập nhật file này MỖI KHI tạo hoặc tìm được âm thanh mới. Lần sau tra ở đây trước, chưa có mới tạo.
Âm thanh phải đạt QC (`tools/qc_assets.py`): đúng LUFS, không clipping, không tên TEMP, ghi nguồn/giấy phép.

| ID | Loại (bed / one-shot / nhạc / im) | Mô tả | Hợp với | Độ dài | File | Nguồn/giấy phép | Đã dùng ở |
|---|---|---|---|---|---|---|---|
| (ví dụ) BED-RAIN-01 | bed | mưa rừng nhẹ, loop mượt | chương chậm, rừng | 60s | sfx/bed_rain_01.wav | tự tạo | Beat 3 |

Quy tắc dùng lại (chống bị quét "nội dung lặp"):
- Tái dùng được ở NHIỀU chương nhưng không để cùng một bed/nhạc lặp ở hai chương liền nhau.
- Đổi cao độ/độ dài/lớp chồng khi dùng lại; ghi vào cột "Đã dùng ở".
- Mỗi video có ít nhất vài âm thanh MỚI; không dùng nguyên một bộ cho cả video.
- Chỉ ghi vào thư viện âm thanh đã QC xong. Tên chuẩn: `<loại>_<mô_tả>_<số>`.
