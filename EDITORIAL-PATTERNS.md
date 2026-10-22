# NGỮ PHÁP BIÊN TẬP — mệnh đề lời đọc → sự kiện hình

> **TẠI SAO phải nhiều cách dựng và nhiều motif khác nhau:** người xem (nhất là khán giả 55+) và thuật toán đều nhận ra khuôn mẫu rất nhanh. Nếu mọi beat cùng một công thức (ảnh mới → zoom → chữ bật → âm nhấn → chuyển cảnh) thì sau vài chục giây video thành slideshow đều tay, retention tụt và kênh giống kênh làm hàng loạt (rủi ro "inauthentic content"). Giữ NHẬN DIỆN (nét vẽ, màu, font) nhưng đổi NHỊP, kiểu hình–chữ–âm theo diễn biến câu chuyện: mỗi lần đổi gắn với một bước ngoặt (thông tin mới, nguy hiểm tăng, nhân vật nhận ra điều gì). Đổi nhịp là công cụ kể chuyện, không phải trang trí.

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

## ĐỔI NHỊP THEO DIỄN BIẾN (chống lặp motif — slideshow đẹp mà đều tay)
Giữ NHẬN DIỆN chung (nét vẽ, màu, font); ĐỔI nhịp theo từng beat. Mỗi lần đổi cách dựng phải gắn với một bước ngoặt của câu chuyện (thông tin mới, nguy hiểm tăng, nhân vật nhận ra điều gì).
**Mỗi beat chọn MỘT motif nhịp riêng (ví dụ):**
| Loại beat | Motif | Cách dựng |
|---|---|---|
| Hook | thiết lập → tiết lộ → khoảng trống | bố cục gọn; chỉ 1–2 thông tin mạnh bật chữ ("92 ABOARD" → "1 SURVIVOR"); sau điểm nhấn GIỮ HÌNH một nhịp cho ngấm |
| Giới thiệu / bối cảnh | quan sát → nhận ra chi tiết → bất an | luân phiên rộng–vừa–cận; có cảnh giữ 5–7s, cảnh khác 2–3s; tiếng mưa/máy bay vào TRƯỚC khi đổi hình; chữ chỉ tên/nơi/ngày |
| Hành động / rơi | tăng tốc → đứt nhịp → yên lại | cắt ngắn dần, xen rộng–chi tiết; âm nhấn tiết chế, MỘT lần thật mạnh ở va chạm, rồi giữ một khung lâu, giảm chuyển động; đoạn yên làm phần hỗn loạn có sức nặng |
| Nhịp trầm / cô độc | chậm, nhiều im lặng | ít chữ, sương, cảnh `hold` dài; chữ chỉ ở cú ngoặt |
**Bốn cách dẫn sự chú ý (xen kẽ, đừng lặp "ảnh mới → zoom → chữ bật → âm nhấn → chuyển cảnh"):**
1. Hình dẫn: lời đọc tiếp tục, hình giữ nguyên cho người xem quan sát.
2. Âm dẫn: nghe tiếng của cảnh sau trước khi thấy cảnh đó.
3. Chi tiết dẫn: cắt từ toàn cảnh vào một vật/cử chỉ có ý nghĩa.
4. Khoảng nghỉ dẫn: sau câu quan trọng, ngưng thêm chữ và hiệu ứng.
**Cảnh `hold`:** thêm `"hold": true` vào cảnh = nhịp để hình tự nói (không chữ/hiệu ứng, tối đa 9s); lint không báo "trống sự kiện" cho cảnh này. Mỗi video >30s nên có ít nhất 1.
**Âm nhấn:** tối đa 3–4 mốc thật sự quan trọng/video, MỘT tiếng mạnh nhất ở cú ngoặt; đừng "đùng" ở mọi con số/phủ định.
**Lượt duyệt chống lặp (trước khi xuất, xem liền các beat):**
- 3 cảnh gần nhau có cùng kiểu zoom, cùng vị trí chữ, cùng âm nhấn không? (lint báo LẶP CAMERA / LẶP VỊ TRÍ CHỮ / ÂM NHẤN)
- Cảnh nào chuyển động chỉ để khỏi bị coi là đứng hình?
- Cao trào có mạnh hơn đoạn trước không, hay cả video căng như nhau?
- Bỏ hiệu ứng này thì ý nghĩa/cảm xúc có giảm không? Không giảm → bỏ.
- Khung đứng có chủ đích vẫn phải giữ; cảnh báo tự động chỉ để tìm chỗ cần xem lại, quyết định cuối theo sức kể.
**Khi lập nguyên liệu:** lên ý đồ nhịp từng beat TRƯỚC, rồi mới hỏi nguyên liệu — đừng mỗi câu một ảnh (đổi độ dài cảnh 2–3s / 5–7s, dùng ảnh cận cắt từ ảnh rộng khi đủ độ phân giải).

## Trộn VIDEO với ẢNH TĨNH trong cùng một video (mặc định nên làm)
Mục tiêu: ảnh tĩnh làm xương sống (rẻ, đồng nhất), video chỉ chen vào đúng chỗ cần chuyển động THẬT. Phim "sống" hơn mà không phải làm toàn video.
**Chọn khi nào dùng video thay vì ảnh:**
| Dùng video (6–10s) | Dùng ảnh tĩnh + fx |
|---|---|
| Cảnh đang hành động: rơi, chạy, lội nước, cháy, nổ, máy bay bay | Cảnh tư liệu/bối cảnh, thẻ thông tin, bản đồ, chân dung |
| Cú ngoặt/đỉnh cảm xúc cần "phá nhịp" (thường 1 cảnh / 20–30s) | Nhịp chậm, hồi tưởng, trích dẫn, nhịp im lặng |
| Cảnh mở màn / cảnh cuối cần ấn tượng | Cảnh dài hơn 10s (lặp video dễ lộ) |
**Công thức nhịp:** ảnh, ảnh, VIDEO, ảnh, ảnh, VIDEO… (video ≈ 25–35% thời lượng). Không để 2 video liền nhau; chuyển ảnh↔video bằng dissolve 0.5s trong khoảng lặng như mọi cảnh khác.
**Cách trộn trong spec:**
- Cảnh video: `{"id":"D","video":"video/clip.mp4","start":..,"camera":{..}}` — đi qua cùng camera/grain/vignette/preset màu như ảnh nên đồng nhất. Clip ngắn hơn cảnh tự lặp; tốt nhất cắt clip đúng độ dài cảnh.
- Lớp video chồng lên ảnh (sương, mưa, khói, lửa, tia sáng): `video_overlay` `blend:"screen"` nền đen → trong suốt, opacity 0.2–0.4.
- Âm thanh của clip KHÔNG dùng (chỉ lấy hình); tiếng lấy từ sfx/VO để kiểm soát mix.
**Yêu cầu khi nhờ Muse tìm/sinh video:** cùng style bible với ảnh (cùng màu, cùng nhân vật), 16:9 ≥1280x720, không chữ/logo, camera ổn định (tránh rung tay), 6–10s. Đặt tên `video/<id>.mp4`. Trong `asset_plan.xlsx` cột LOẠI NGUYÊN LIỆU ghi "footage/AI video (tuỳ chọn)" ở cảnh hành động: anh duyệt OK thì Muse làm, BỎ thì dùng ảnh + fx.
**Lint/QC:** `lint_spec.py` và `analyze_video.py` chạy như thường; kiểm clip lặp không bị giật tại điểm nối.

## Chọn phong cách cho từng video (đa dạng giữa các tập)
Đừng dùng cùng một preset cho mọi tập. Gợi ý: tập về quá khứ/ký ức → `newsreel`; tập cảm xúc, ít dữ kiện → `cinematic`; tập nhiều số liệu/nhịp nhanh → `kinetic` hoặc mặc định. Trong một video dài có thể đổi giữa các beat, nhưng GIỮ MỘT phong cách trong cùng một beat.
