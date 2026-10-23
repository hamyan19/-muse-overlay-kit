# KIỂM NGUYÊN LIỆU — một lần, trước khi giao (bước 6)

Chỉ một lần kiểm, hai phần: máy kiểm cái đo được, mắt kiểm cái máy không thấy. FAIL = 0 mới giao.

## Phần 1 — một lệnh máy
```bash
python3 tools/qc_assets.py --root res --manifest plan/approved_manifest.json --out qc/
```
Máy kiểm: thiếu file so với danh sách đã duyệt, ảnh đủ 2560×1440, nét, cháy/đen, ám màu, mặt rõ, chữ/logo, ảnh trùng;
video 6–10s, đứng hình, cắt ngầm, rung; âm thanh méo, LUFS, im lặng thừa.
Sửa mọi FAIL. WARN thì xem qua, giữ hay sửa tuỳ mắt.

## Phần 2 — 5 mục nhìn bằng mắt (xem nhanh cả bộ, mở 100% khi nghi)
| # | Kiểm | Không đạt khi |
|---|---|---|
| 1 | **Khớp character sheet** | đổi tóc/trang phục/giày, sai số lượng đạo cụ, đổi bên trái/phải |
| 2 | **Giải phẫu & vật thể** | thừa/thiếu tay chân ngón, vật thể nhập nhau; video: người/vật biến dạng giữa clip |
| 3 | **Đúng thời đại, không phản cảm** | đồ vật hiện đại lạc thời; máu, thi thể |
| 4 | **Khớp ý dòng visual plan** | hình nói điều khác lời; hai ảnh liền nhau gần như một khung |
| 5 | **Âm thanh nghe một lượt** | nghe ra thứ khác mô tả, chỗ nối vòng bị cục |

Nếu báo cáo máy ghi "OCR/nhận diện mặt TẮT" thì kiểm thêm chữ/logo và mặt bằng mắt.

## Phần 3 — gói giao (4 điều, lỗi hay gặp nhất khi dựng)
1. Tên file đúng cột **TÊN FILE ĐÍCH**; không dấu, không `#`, không khoảng trắng.
2. Mốc thời gian khớp voice **đang giao** (đổi voice thì chạy lại bước 3).
3. Tên riêng và con số trong `wordts.json` đã sửa đúng chính tả.
4. File tạm có đuôi `_TAM`.

## Báo cáo khi giao (3 dòng)
- `qc/QC-REPORT.md`: FAIL 0, WARN còn giữ và vì sao.
- 5 mục mắt: đạt, hoặc dòng nào còn nghi.
- Danh sách file `_TAM` (nếu có).
