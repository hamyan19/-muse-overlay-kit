# NHẬT KÝ BÀI HỌC (Muse tự cập nhật sau mỗi beat)
Cách dùng: sau khi nộp mỗi beat và nhận phản hồi / so sánh với bản tham chiếu, thêm **một mục** ở đầu danh sách dưới đây
theo đúng khuôn. Mục tiêu: lần sau mắc lỗi cũ thì `lint_spec.py` hoặc quy trình phải chặn được; nếu chưa chặn được, ghi rõ
"cần thêm luật lint nào". Người dùng sẽ commit file này lên repo (hoặc dán vào kho nhớ của Muse).

## Khuôn mục
- **Beat / ngày:** …
- **Lỗi / thiếu sót (có mốc thời gian):** …
- **Nguyên nhân gốc (quy trình, không phải "cẩn thận hơn"):** …
- **Luật mới / công cụ cần có:** …
- **Đã kiểm chứng bằng:** (lint / analyze / xem khung t=…)

---
## 2026-10-22 · Beat 1 "The Last Flight of LANSA" (Muse v1 vs Claude)
- **Thiếu sót:** 10 phần tử / 85s; thẻ tên đứng yên 0–13s; thẻ chuyến bay đứng yên 26–43s; chữ phụ ~10–14px; cảnh 62–72s gần đen; dấu LICENCE REVOKED kẹt sang cảnh im lặng 75–85s; master −17.9 LUFS.
- **Nguyên nhân gốc:** thiết kế theo cảnh (một thẻ cho cả cảnh) thay vì theo mệnh đề lời đọc; không có bước kiểm spec trước render; không chuẩn hoá âm lượng.
- **Luật mới:** (1) mỗi mệnh đề ≥ 1 sự kiện (EDITORIAL-PATTERNS.md); (2) `lint_spec.py` bắt buộc trước khi render; (3) engine tự `loudnorm` −14 LUFS; (4) phủ định → `strike_cards`; số → `ticker`; vật thể → `highlight_box`/`anchored_circle`; trích dẫn → nhãn dẫn + chữ thường.
- **Đã kiểm chứng bằng:** lint trên spec Claude: 0 lỗi; thử bỏ `t_out` → lint báo ERR đúng chỗ.

## Điều Claude v1 cũng làm chưa tốt (đừng bắt chước)
- Hai đoạn đứng yên 66–68,6s và 72,7–74,7s (thẻ "cause of the crash" gõ xong rồi nằm im).
- `highlight_box` PANGUANA nằm yên 8s; nhãn "HER MOTHER'S LAST WORDS" nằm 5,5s.
- Ảnh sân bay dùng hai lần (chỉ đổi góc cắt) vì gói chỉ có 4 ảnh → nên xin thêm ảnh hoặc dùng `blur/brightness` tạo biến thể.
- Chữ phụ badge 20–24px (dưới ngưỡng 26px).

## Beat 2 "The Fall" (cinematic, 58s) — 22/10/2026
- Preset cinematic: ĐÃ BỎ dải đen letterbox (nó cắt mất phần trên/dưới ảnh 16:9 và cắt chữ đặt cao). Full khung 16:9. Phụ đề size 34–38, y ~552, max_width ~1120–1180; nhãn đặt y ≥ 110.
- Đường dẫn thư mục chứa ký tự `#` làm hỏng đọc font (`font.ttf#Variant`) → chép tài nguyên sang thư mục đường dẫn sạch trước khi render.
- Whisper nghe sai ("summary") và tên riêng: dùng `replace` trong captions, key KHÔNG có dấu phẩy.
- Kết quả: jitter P75 0.036 (PASS), −14.9 LUFS, render 0.5s/khung (2 jobs).
- Lỗi nguyên liệu cần bắt sớm: ảnh Beat 2 vẽ áo hoodie olive trong khi kịch bản ghi váy không tay → khoá mô tả nhân vật trong style bible TRƯỚC khi sinh ảnh.

## Dựng cả phim Koepcke 8 chương một lượt (22/10/2026)
- **Lỗi gói phổ biến nhất** (không phải lỗi ảnh): manifest nhiều định dạng (covers dạng chuỗi, thiếu `type`); covers không khớp voice (Beat 3 manifest 70,9s, voice 66,9s; Beat 2 ảnh xếp lệch lời); thiếu file âm thanh mà ghi chú có nhắc (làm hỏng cả lần mix âm). → thêm **Lớp 3 kiểm gói giao** vào QC-ASSETS.md.
- **Whisper nghe sai tên riêng** làm thẻ chữ không tìm được mốc (Tournavista, Pucallpa, Bavarian, "fourteen"). → Muse sửa chữ trong wordts trước khi giao; người dựng kiểm thẻ nào bị bỏ.
- **Âm nền ngắn** (5–12s) phải lặp cho đủ đoạn: engine có `"loop": true` cho track âm thanh; chỗ nối vòng có thể nghe thấy → ưu tiên file nền ≥ 30s.
- **Beat chủ đích thở** (chậm, nặng): đặt `"calm": true` trong spec → lint nới ngưỡng trống sự kiện lên 9s và không đòi ≥2 phần tử/cảnh. Không dùng `calm` cho beat nhịp nhanh.
- **Nhãn từ khóa tự lấp chỗ trống** giúp qua lint nhưng chọn từ theo độ dài, không theo ý nghĩa → người dựng phải xem lại, bỏ nhãn vô nghĩa.
- **Mix từng chương riêng** làm âm lượng chênh khi ghép phim → chạy loudnorm cho bản ghép cuối, thêm khoảng thở/chuyển cảnh giữa các chương.
- **Render trên cloud 2 nhân chậm** (≈10 phút / 1 phút video). Cả phim nên render local.
