# SỔ BÀI HỌC — một file cho cả nguyên liệu và dựng

Đọc một lần đầu mỗi dự án. Khi có lỗi MỚI (anh, người dựng hoặc Muse phát hiện), thêm **một dòng** vào đúng bảng:
`ngày · dự án | lỗi đã xảy ra | luật để không lặp`. Không viết báo cáo dài.

## Nguyên liệu & gói giao (Muse)
| Khi | Lỗi đã xảy ra | Luật |
|---|---|---|
| 22/10 · Koepcke | Manifest mỗi chương một định dạng (mốc thời gian dạng chuỗi, thiếu loại) | Dùng manifest do `plan_assets.py` / `apply_approval.py` tạo, không tự viết tay |
| 22/10 · Koepcke | Đổi voice nhưng giữ mốc thời gian cũ (manifest 70,9s, voice 66,9s) | Đổi voice ⇒ chạy lại bước 3 |
| 22/10 · Koepcke | Ảnh đặt sai câu (ảnh ghế xoay không nằm ở "spun like a maple seed") | Visual plan điền trên bảng mapping, mỗi ảnh gắn đúng một dòng |
| 22/10 · Koepcke | Ghi chú nhắc file âm thanh không có trong gói (`music_bed`, `near_silence`) | Mọi tên trong ghi chú phải có trong `sfx/` |
| 22/10 · Koepcke | Đoạn lời đọc 61–73s không có ảnh mà không báo | Ghi "THIẾU ẢNH" trong visual plan |
| 22/10 · Koepcke | Tên thư mục có `#` → engine không đọc được font | Tên file/thư mục không dấu, không `#`, không khoảng trắng |
| 22/10 · Koepcke | File tạm không đánh dấu thống nhất | File tạm luôn có đuôi `_TAM` |
| 22/10 · Koepcke | Âm nền 5–12s cho đoạn 20–40s, nối vòng nghe thấy | File nền ≥ 30s |
| 22/10 · Koepcke | Không sửa tên riêng Whisper nghe sai (Tournavista, Pucallpa, Bavarian, "fourteen") | Sửa chữ trong `wordts.json` trước khi giao (giữ timing) |
| 22/10 · Koepcke | Voice Beat 2 khác script đã duyệt mà không hỏi | Lệch script thì hỏi anh trước khi thu |
| 22/10 · Koepcke | Trang phục lệch xuyên chương (hoodie olive vs váy kem) | Prompt copy nguyên mô tả nhân vật từ character sheet |
| 22/10 · Koepcke | Giày đảo chân; cảnh còn đủ 2 giày khi đã mất 1 | Character sheet ghi rõ trái/phải; mục 1 của kiểm mắt |
| 22/10 · Koepcke | Thừa ghế / sai số ghế | Character sheet ghi số lượng đạo cụ |
| 22/10 · Koepcke | Ảnh không đạt 2560×1440 | Báo kích thước thật, không phóng lớn rồi gọi là gốc |
| 23/10 · Izba Ch2 | `room_tone.wav` gần như im lặng (−70 LUFS); `forest_ambience.wav` 12s nhưng chỉ ~6s có tiếng | Nghe một lượt mỗi file trước khi giao (mục 5 kiểm mắt); file nền ≥ 30s có tiếng thật |
| 23/10 · Izba Ch2 | Manifest ghi chú vào ô `file` ("Ch2_S02.png (tai dung…)") và đường dẫn voice trỏ ra ngoài gói | Ô `file` chỉ chứa tên file có trong gói; ghi chú để ở visual plan |
| 23/10 · Izba Ch3 | Sprite cửa giao dạng ảnh chữ nhật không nền trong suốt, cắt lệch (dính nền + đầu gỗ, mất mép cửa) | Sprite là PNG có kênh alpha, cắt sát đúng vật thể; để trong `sprites/`, không để chung `stills/` |
| 22/10 · Cartoon | Style nét đơn giản làm model nuốt chân/tay | Prompt ghi "whole body visible, both legs and feet clearly drawn" |
| 25/10 · Mammoth Bones | Mapping có shot 2–4s và 13–15s (cắt theo mệnh đề, không theo nhịp ảnh) | Mỗi shot 5–11s; ngắn thì gộp, dài thì cắt ở khoảng lặng; đổi mốc ⇒ viết lại prompt của shot đó, mã shot đánh số lại |
| 25/10 · Mammoth Bones | Prompt viết cho từng cảnh theo bản cũ, sau đó mapping đổi mốc nên prompt lệch ý | Sau khi chốt điểm cắt mới mới sinh prompt; prompt dùng `META-PROMPT-VISUAL.md` (một ảnh = một khoảnh khắc, negative riêng từng shot) |

## Dựng (người dựng)
| Khi | Lỗi đã xảy ra | Luật |
|---|---|---|
| 22/10 · Beat 1 | 10 phần tử / 85s; thẻ đứng yên 0–13s và 26–43s; cảnh 62–72s gần đen; chữ phụ 10–14px; dấu kẹt sang cảnh sau | Thiết kế theo mệnh đề lời đọc (`EDITORIAL-PATTERNS.md`); `lint_spec.py` trước khi render |
| 22/10 · Beat 1 | Master −17.9 LUFS | Engine tự `loudnorm` −14 LUFS |
| 22/10 · Beat 1 | Ảnh sân bay dùng hai lần vì gói chỉ có 4 ảnh | Thiếu ảnh thì xin thêm, hoặc tạo biến thể bằng `blur`/`brightness` |
| 22/10 · Beat 2 | Dải đen letterbox cắt ảnh và chữ đặt cao | Full khung 16:9; preset không tự thêm dải đen |
| 22/10 · Beat 2 | Whisper nghe sai ("summary") | Dùng `replace` trong `captions`, key không có dấu phẩy |
| 22/10 · cả phim | Nhãn từ khoá tự lấp chỗ trống chọn theo độ dài, không theo nghĩa | Người dựng xem lại, bỏ nhãn vô nghĩa |
| 22/10 · cả phim | Mix từng chương riêng → âm lượng chênh khi ghép | Chạy loudnorm cho bản ghép cuối |
| 22/10 · cả phim | Render cloud 2 nhân ≈ 10 phút / 1 phút video | Cả phim nên render trên máy local |
| 23/10 · Izba Ch2 | Ảnh có chi tiết lơ lửng khó hiểu (nắp bình treo xích) | Tách thành `sprite`, vá nền, cho nó chuyển động đúng lời ("sealed" → nắp rơi đóng) |
| 22/10 · cả phim | Chương chủ đích chậm bị lint báo trống sự kiện | Đặt `"calm": true` trong spec (lint nới lên 9s); không dùng cho chương nhịp nhanh |
