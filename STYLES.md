# MENU STYLE — chọn ở bước 5

Mỗi chương chốt 2 thứ: **style hình** (giữ cho cả video) và **style dựng** (đổi theo chương).
Thông số kỹ thuật của từng preset/phần tử nằm ở `EFFECTS.md`; file này chỉ để chọn.

## A. Style hình (giữ nguyên cho cả video)
| Style hình | File chuẩn | Hợp với |
|---|---|---|
| House Cartoon (nét vẽ tay vụng, màu phẳng, sách truyện) | `styles/house-cartoon/STYLE.md` | Kể chuyện thường, giải thích, lane Chapter Studio |
| Painterly điện ảnh (tả thực mềm, màu tự nhiên trầm) | style bible mặc định của `plan_assets.py` | Documentary sinh tồn/điều tra (Koepcke) |

Thêm style hình mới: chép `styles/_MAU/STYLE.md`, điền đủ, có 2–3 ảnh mẫu.

## B. Style dựng (đổi theo chương, hai chương liền nhau không trùng)
| Style dựng | Preset | Lớp chồng chính | Nhịp cảnh · chuyển cảnh | Âm | Hợp với | **Không được đổi** (đổi là thành style khác) |
|---|---|---|---|---|---|---|
| **Hồ sơ điều tra** | (mặc định) | `marker`, `clipping` news, `photo_pin`, `stamp` | 4–6s · dissolve 0.5s | nền tối, nhấn ≤ 4 | Bí ẩn, "chuyện gì thật sự xảy ra" | thẻ tối viền kem, vàng = nhấn, đỏ = loại bỏ |
| **Phim tư liệu xưa** | `newsreel` | thẻ máy chữ, `stamp` | 4–6s · cắt thẳng | tiếng máy chiếu, nhạc cũ | Lịch sử, đời sống quá khứ | đen trắng ngả nâu, hạt thô, xước phim |
| **Điện ảnh** | `cinematic` | `captions` serif, nhãn mono nhỏ | 5–9s, camera chậm · dissolve 0.5s | nền dày, nhạc thấp, nhấn ≤ 3 | Cảm xúc, ít dữ kiện | ít chữ; chữ là phụ đề, không phải thẻ |
| **Chữ theo lời** | `kinetic` | `kinetic`, `badge_pop`, `ticker` | 2–4s · cắt thẳng / flash | nhấn theo nhịp, whoosh | Số liệu, câu chốt, Hook | từ khoá bật đúng lúc nói |
| **Sách truyện** | `storybook` | nhãn serif góc như chú thích tranh | 6–10s, đẩy rất chậm · dissolve 0.8s | piano/đàn dây, nền thưa | Ảnh minh hoạ, kể chậm | vân giấy, màu dịu, rất ít thẻ |
| **Album kỷ niệm** | `memory` | `photo_pin` có ngày tháng, `clipping` note, `lower_third` tên | 6–10s, có `hold` · dissolve dài | nhạc hoài niệm, tiếng phòng/đồng hồ | Hồi ức, gia đình, kết cảm động (55+) | ảnh in viền kem, màu bạc; không badge |
| **Truyện tranh** | `comic` | `speech_box`, `badge_pop`, `strike_cards`, `marker` arrow | 3–5s, pan theo hướng đọc · cắt thẳng | nhấn rõ, sfx hoạt hình nhẹ | Nhịp nhanh/vui, giải thích cơ chế | khung mực, chữ IN HOA đậm |
| **Bản đồ / giải thích** | `documentary` | `route`, `timeline`, `ticker`, `highlight_box` | 4–7s · dissolve 0.3s | nền trung tính, ít nhạc | Hành trình, địa lý, "làm sao mà…" | màu trung tính, đồ hoạ là người kể |

Một video thường dùng 2–4 style dựng (ví dụ: Hook *Chữ theo lời* → kể chuyện *Điện ảnh* → giải thích *Bản đồ* → kết *Album kỷ niệm*).
Trong **một** chương chỉ dùng một style dựng (được mượn 1 phần tử của style khác).

## C. Chỉnh một style cho riêng chương/kênh
Khi anh muốn đổi một style, chia thay đổi làm 3 nhóm:
- **Đổi thoải mái:** màu điểm nhấn, font, vị trí chữ, âm nền cụ thể, độ dài cảnh trong khoảng của style.
- **Đổi là đổi tính cách** (anh phải đồng ý): preset màu, loại lớp chồng chính, kiểu chuyển cảnh, mật độ chữ.
- **Không được đổi:** cột cuối của bảng B. Muốn đổi cột này thì đó là một style mới: thêm một dòng vào bảng B.

Style riêng đã dùng tốt thì thêm dòng vào bảng B để lần sau chọn lại.
