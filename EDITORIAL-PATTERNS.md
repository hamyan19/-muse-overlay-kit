# NGỮ PHÁP BIÊN TẬP — mệnh đề lời đọc → sự kiện hình
Nguyên tắc: **mỗi mệnh đề của lời đọc (đoạn giữa hai khoảng lặng) có ÍT NHẤT một sự kiện hình riêng**, đặt đúng lúc từ khoá được nói.
Lấy mốc bằng `tools/word_times.py wordts.json --auto`. Bảng dưới là các "motif" đã chứng minh hiệu quả ở Hook/Beat 1.

| Trong lời đọc có... | Dùng | Ví dụ đã làm | Lưu ý |
|---|---|---|---|
| **Phủ định** (not, never, didn't, no, none) | `strike_cards`: thẻ ghi ĐỐI TƯỢNG BỊ PHỦ ĐỊNH, gạch đỏ đúng lúc nói "not" | "A HOUSE" gạch (Home was *not* a house); "TURN BACK" gạch; "OTHER FLIGHTS" gạch + "ALL FULL" | Motif lặp xuyên video → người xem tự học "gạch đỏ = loại bỏ". Dùng nhất quán |
| **Con số / thời lượng** | `ticker` / `counter_down` chạy tới đích đúng lúc từ số được nói; `badge_pop` cho số đứng một mình | 0→40 MIN "AFTER TAKEOFF"; 92→1 | Số phải có easing (power 1.6–2.4), không tuyến tính; đích nổ + pop |
| **Địa điểm / vật thể có trong ảnh** | `highlight_box` (khung góc) bám ảnh + nhãn; `anchored_circle` khoanh điểm | khung ôm hai căn lều "PANGUANA RESEARCH STATION"; vòng quanh tia sét "THE FLASH — RIGHT WING" | Toạ độ `src` theo ảnh gốc 2560x1440 để bám camera; kiểm tra bằng `--frames` |
| **Dữ kiện về người** (tên, quan hệ, nghề) | `lower_third` | "WITH HER MOTHER, MARIA", "HER PARENTS / BOTH ZOOLOGISTS" | Tiêu đề ≤ 24 ký tự, dòng phụ ngắn |
| **Mốc thời gian / ngày** | `stamp` (nền tối) hoặc `timeline`/`day_ticker` | "23 DEC 1971"; DAY 1→11 | Stamp đặt vùng trời/trống, đừng đè chủ thể |
| **Trích dẫn** (last words, "…" ) | `label` dẫn ("HER MOTHER'S LAST WORDS") TRƯỚC, rồi `typed_card` gõ **chữ thường như câu văn**, `dim` nhẹ nền | quote người mẹ | KHÔNG gõ IN HOA cả câu: cứng và "gắt". Nhả `dim` sau khi xong |
| **Phán quyết / văn bản chính thức** | `typed_card` kiểu hồ sơ, dòng nhãn xám + dòng nội dung sáng, chữ nhấn màu vàng | "CAUSE OF THE CRASH: INTENTIONAL FLIGHT INTO HAZARDOUS WEATHER CONDITIONS" | Tốc độ gõ khớp tốc độ nói (tính cps = số ký tự / thời lượng từ wordts) |
| **Cú đập / twist / sét** | `flash` + `shake` camera + sfx CÙNG khung | flash 50.0s + sấm | Không quá 3 flash trong một beat |
| **Câu hỏi** | `question_card` ("?" nhấp nháy) | cuối Hook | |
| **Hệ quả / nhịp kết** | `label` ngắn hiện trên cảnh tối, rồi `dim` đen dần, chữ cuối hiện ma | "NONE OF THAT MATTERED" → fade đen → "SILENCE" | Khi VO ngừng, hình cũng phải ngừng: dọn hết overlay trước |
| **Cảnh tĩnh dài, không từ khoá** | `rain` / `mist` / `spotlight` / camera đổi nhịp | sương trôi cảnh Panguana; mưa bão | Chuyển động trong khung giữ mắt khi không có thông tin mới |

## Quy tắc đi kèm
1. **Đúng lúc từ**: `t_in` = mốc bắt đầu của từ khoá (wordts) − 0 … +0.05s. Không đặt trước lời, không trễ quá 0.2s.
2. **Phần tử phải chết đúng lúc**: luôn có `t_out` (lint sẽ báo lỗi nếu thiếu). Hết ý là rút. Qua điểm đổi cảnh phải có lý do.
3. **Tối đa 2 phần tử đồng thời** trong cùng vùng màn hình; thẻ chữ chính căn giữa/dưới trái, badge góc trên phải.
4. **Cỡ chữ**: chính ≥ 34px, phụ ≥ 26px. Chữ dài thì rút ý, đừng thu nhỏ.
5. **Cảnh tối**: nếu ảnh gốc tối (độ sáng TB < 38) và không phải nhịp "im lặng" thì nâng `brightness` hoặc thêm `spotlight`.
6. **Hai cảnh liền nhau không dùng cùng kiểu**: sau chuỗi lower_third thì chuyển sang strike/ticker/highlight.
7. **Đọc lời trước, thiết kế sau**: nghe/đọc VO, gạch chân từ khoá, rồi mới viết spec.

## Chọn phong cách cho từng video (đa dạng giữa các tập)
Đừng dùng cùng một preset cho mọi tập. Gợi ý: tập về quá khứ/ký ức → `newsreel`; tập cảm xúc, ít dữ kiện → `cinematic`; tập nhiều số liệu/nhịp nhanh → `kinetic` hoặc mặc định. Trong một video dài có thể đổi giữa các beat, nhưng GIỮ MỘT phong cách trong cùng một beat.
