# QC CỨNG nguyên liệu (ảnh · video · âm thanh) — Muse làm TRƯỚC khi gửi anh duyệt
Mục tiêu: anh chỉ phải duyệt nguyên liệu đã sạch lỗi. Làm đúng 2 lớp: **tự động** rồi **bằng mắt**. Không được báo "xong" khi còn FAIL.

## Lớp 1 — chạy máy (bắt buộc)
```bash
python3 tools/qc_assets.py --root res --manifest plan/approved_manifest.json --out qc/     # FAIL phải bằng 0
python3 tools/check_assets.py plan/approved_manifest.json --root res --out plan/            # sheet duyệt ảnh thu nhỏ
```
Sửa/gen lại mọi file FAIL, đọc từng WARN và ghi lý do giữ/sửa. Nếu báo "OCR/nhận diện mặt TẮT" thì phần đó phải kiểm bằng mắt.

## Lớp 2 — kiểm bằng mắt từng ảnh/clip (điền bảng, gửi kèm `qc/QC-REPORT.md`)
Mỗi ảnh/clip một dòng: `ID | đạt/không | ghi chú`. Mở ảnh 100% (zoom vào tay, chân, mép, nền), xem clip từ đầu đến cuối.

| # | Kiểm | Không đạt khi |
|---|---|---|
| 1 | **Nhân vật nhất quán** (so với ảnh chuẩn đầu tiên của bộ) | đổi tuổi/tóc/trang phục/giày/kính; xuất hiện 2 người; đổi bên ngồi |
| 2 | **Giải phẫu** | tay/ngón thừa-thiếu, chân méo, giày sai số lượng, mắt/da lạ; vật thể nhập vào nhau |
| 3 | **Vật thể khoá** (vd băng ghế 3 chỗ xanh lam, đúng số ghế) | thừa/thiếu ghế, đổi màu, ghế bay lơ lửng sai logic |
| 4 | **Đúng thời đại/bối cảnh** | đạo cụ hiện đại (điện thoại, ba lô, đồ nhựa mới), máy bay sai loại, cây/thú sai vùng |
| 5 | **Không chữ/logo/watermark** (kể cả biển hiệu mờ, số hiệu máy bay) | bất kỳ ký tự đọc được |
| 6 | **Không thấy rõ mặt** (quay lưng/silhouette/khuất) | thấy rõ mắt-mũi-miệng |
| 7 | **Không gore/hình thi thể** (cảnh tang thương chỉ gợi ý, tôn trọng) | máu, thi thể, cảnh phản cảm |
| 8 | **Màu/ánh sáng tự nhiên, cùng style bible** (không ám vàng, cùng độ tương phản cả bộ) | lệch tông giữa các ảnh liền kề |
| 9 | **Bố cục chừa chỗ cho chữ & camera** (chủ thể không sát mép, còn khoảng trống ~1/3) | chủ thể ở mép bị cắt khi zoom 1.3× |
| 10 | **Đủ nét 2560x1440** (zoom 100%: không bệt, không nhiễu, không viền răng cưa) | mờ, artifact AI, vân lạ |
| 11 | **Khác nhau giữa các cảnh liền nhau** | hai ảnh liền gần như cùng một khung |
| 12 | **Khớp lời đọc/ý đồ cảnh** (đọc dòng "HÌNH GỢI Ý" và lời) | hình nói điều khác lời |

### Riêng VIDEO (thêm) — chỉ kiểm clip có BRIEF (xem "BRIEF VIDEO" trong EDITORIAL-PATTERNS.md); clip không có brief = không làm
| # | Kiểm | Không đạt khi |
|---|---|---|
| V1 | Một cảnh liền 6–10s, không cắt ngầm | có cắt/đổi bối cảnh giữa chừng |
| V2 | Chuyển động **tự nhiên, có chủ đích** | vật thể biến dạng/trôi chảy, người tan chảy, "morph" |
| V3 | Camera ổn định (trừ rung chủ đích) | rung tay, giật, đổi tốc độ đột ngột |
| V4 | Nhân vật/vật thể **giữ nguyên hình** từ khung đầu đến cuối | đổi mặt/quần áo/số lượng giữa clip |
| V5 | Khung đầu & cuối dùng được để dissolve (không đen/trắng/nhảy) | khung đen, flash, hạt nhiễu |
| V6 | Cùng độ phân giải/tone với ảnh | khác hẳn màu/độ sáng so với ảnh liền kề |

### Riêng ÂM THANH (thêm)
| # | Kiểm | Không đạt khi |
|---|---|---|
| A1 | Nghe cả file qua tai nghe | méo, rè, có tiếng lạ/giọng người không mong muốn |
| A2 | Đúng mô tả (vd "máy bay cánh quạt rất xa", "mưa rừng") | nghe ra thứ khác |
| A3 | Vòng lặp liền mạch với nền dài (không "cục" ở chỗ nối) | click/nhảy âm lượng |
| A4 | Ghi rõ file nào là **TEMP/tổng hợp tạm** | giấu bản tạm |
| A5 | Có thật hay giả: nguồn/giấy phép nếu lấy từ thư viện | không rõ nguồn |

## Lớp 3: kiểm GÓI GIAO trước khi gửi (bắt buộc, bài học từ dựng cả phim Koepcke)
Lỗi gói làm bản dựng thiếu hoặc lệch, dù từng ảnh đều đạt. Kiểm 7 mục trước khi gửi:
1. **Manifest một định dạng:** `{"id", "file": "stills/<tên>.png", "type": "image|video", "covers": [bắt_đầu, kết_thúc]}`. `covers` là SỐ GIÂY dạng mảng, không phải chuỗi "0.0–13.5s".
2. **Covers khớp wordts THẬT** của voice đang giao. Đổi voice thì cập nhật covers. Không có khoảng hở hay chồng nhau, và cảnh cuối kết thúc đúng thời lượng voice.
3. **Mỗi đoạn lời đọc có hình.** Đoạn nào chưa có ảnh riêng thì ghi rõ trong SCRIPT-NOTES là "giữ cảnh X" hay "thiếu ảnh". Không để trống mà không báo.
4. **Đủ mọi file âm thanh mà SCRIPT-NOTES nhắc tới.** Tên trong ghi chú phải trùng tên file trong `sfx/`. Thiếu file thì bản dựng mất lớp âm đó.
5. **Sửa tên riêng trong `wordts.json`** (giữ timing, sửa chữ): Koepcke, LANSA, Pucallpa, Tournavista, Panguana, Bavarian... Whisper nghe sai thì thẻ chữ không bám được mốc và phụ đề sai chính tả.
6. **Đường dẫn sạch:** tên thư mục/file không có `#`, không dấu tiếng Việt, không khoảng trắng đầu/cuối. Ký tự `#` làm hỏng đọc font.
7. **File TẠM ghi rõ:** đuôi `_TAM` hoặc liệt kê trong README. Chương nào còn file TẠM thì báo trong báo cáo.

## Báo cáo cho anh (bắt buộc cuối mỗi lần giao)
1. Kết quả `qc/QC-REPORT.md` (FAIL=0; liệt kê WARN đã xử lý/giữ vì sao).
2. Bảng kiểm mắt đã điền (cả 12 mục cho từng ảnh; V1–V6 cho clip; A1–A5 cho âm thanh).
3. Danh sách file **TEMP**, file **gen lại mấy lần** và lý do, file **còn nghi ngờ** (nói thẳng, không giấu).
4. Mục tiêu: anh xem `asset_review.xlsx` chỉ để chốt gu, không phải bắt lỗi kỹ thuật.
