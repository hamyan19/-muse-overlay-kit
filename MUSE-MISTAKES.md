# SỔ LỖI CỦA MUSE: đọc trước MỖI dự án, ghi thêm sau MỖI lần giao

Mục đích: lỗi đã mắc một lần thì không mắc lại. Đây không phải danh sách việc phải sửa.
Mỗi dòng gồm: **lỗi đã xảy ra → hậu quả khi dựng → luật để lần sau không lặp**.
Muse tự thêm dòng mới (ghi ngày, dự án) mỗi khi anh hoặc Claude chỉ ra lỗi, hoặc Muse tự phát hiện.

## Gói giao (manifest, covers, file)
| # | Lỗi đã xảy ra | Hậu quả khi dựng | Luật |
|---|---|---|---|
| 1 | Manifest mỗi chương một định dạng (covers dạng mảng / chuỗi "0.0–13.5s", có chương thiếu `type`) | Người dựng phải đoán, dễ sai mốc | Dùng đúng một định dạng: `{"id","file":"stills/…","type","covers":[s,e]}` |
| 2 | Covers của gói cũ giữ nguyên sau khi đổi voice (manifest 70,9s, voice 66,9s) | Cảnh lệch lời đọc, phải co tỉ lệ | Đổi voice → tính lại covers từ wordts mới |
| 3 | Xếp ảnh sai câu (ảnh ghế xoay đặt ở câu khác, không ở "spun like a maple seed") | Claude phải tự xếp lại, dùng ảnh 2 lần | Đối chiếu từng ảnh với câu trong wordts trước khi ghi covers |
| 4 | SCRIPT-NOTES nhắc file âm thanh không có trong gói (`music_bed`, `near_silence`) | Lần mix đầu hỏng, bản dựng mất lớp âm | Mọi tên file trong ghi chú phải có trong `sfx/`; kiểm bằng lệnh trước khi giao |
| 5 | Đoạn lời đọc không có ảnh (61–73s Beat 1) mà không báo | Phải dùng lại ảnh cũ | Thiếu ảnh thì ghi rõ "THIẾU ẢNH" + lý do trong SCRIPT-NOTES |
| 6 | Tên thư mục có ký tự `#` (`Koepcke #U2014 …`) | Engine không đọc được font, render lỗi | Tên thư mục/file: chữ không dấu, số, `_`, `-`. Không `#`, không khoảng trắng đầu/cuối |
| 7 | File TẠM không đánh dấu thống nhất (có file `_TAM`, có file chỉ ghi trong README) | Không biết file nào cần thay | File tạm luôn có đuôi `_TAM` VÀ liệt kê trong README |
| 8 | Âm nền quá ngắn (5–12s) cho đoạn 20–40s | Phải lặp, chỗ nối nghe thấy | File nền ≥ 30s; ghi độ dài vào SOUND-LIBRARY |

## Voice / wordts
| # | Lỗi | Hậu quả | Luật |
|---|---|---|---|
| 9 | Không sửa tên riêng Whisper nghe sai (Tournavista, Pucallpa, Bavarian, "fourteen", "Julianne") | Thẻ chữ không bám được mốc → bị bỏ; phụ đề sai chính tả | Sửa CHỮ trong wordts (giữ timing) cho mọi tên riêng và con số trước khi giao |
| 10 | Bản voice Beat 2 khác script đã duyệt mà không hỏi | Không biết bản nào là chuẩn | Voice phải khớp script đã duyệt; lệch thì hỏi anh trước khi thu |

## Hình / nhân vật
| # | Lỗi | Hậu quả | Luật |
|---|---|---|---|
| 11 | Trang phục lệch xuyên chương (hoodie olive vs váy kem không tay) | Nhân vật không nhất quán | Làm CHARACTER-SHEET trước, mọi prompt copy nguyên mô tả nhân vật từ sheet |
| 12 | Giày đảo chân (giày phải thay vì trái), có cảnh còn đủ 2 giày khi đã mất 1 | Lỗi liên tục cảnh | Sheet ghi rõ quy ước trái/phải; QC mắt kiểm riêng mục này |
| 13 | Ghế đơn thừa / số ghế sai | Lệch đạo cụ chuẩn | Sheet ghi số lượng đạo cụ; ảnh lệch thì báo, không tự quyết |
| 14 | Ảnh không đạt 2560×1440 | Ảnh mềm khi xuất 1080p | Ghi kích thước thật trong báo cáo; không phóng lớn rồi gọi là gốc |

## Cách ghi thêm
```
| <số> | <lỗi, cụ thể> | <hậu quả khi dựng> | <luật để không lặp> |   ← ghi ngày + dự án ở cuối ô Lỗi
```
