# PLAYBOOK — dựng một beat mượt như bản Hook Koepcke

## Nguyên tắc cốt lõi (rút từ việc chấm từng khung hình)
1. **Camera không bao giờ đứng yên và không bao giờ giật.** Mỗi cảnh có zoom/pan chậm với easing (`smooth`, `pow:2.2`).
   Giật = lỗi do crop làm tròn pixel. Cách đúng: render ở 2560x1440 bằng affine + Lanczos rồi `INTER_AREA` xuống 1280x720 (engine đã làm).
2. **Mốc thời gian lấy từ lời đọc, không đoán.** Chạy `find_gaps.py wordts.json` → mọi dissolve 0.5s nằm TRỌN trong khoảng lặng.
3. **Cứ ≤ 3.5s phải có một sự kiện thị giác mới** (thẻ hiện, vòng, số nhảy, đổi cảnh, chớp...). Hai cảnh liền nhau không dùng cùng "ngữ pháp" hình ảnh.
4. **Không overlay tĩnh > 3s.** Số phải chạy có easing (không nhảy tuyến tính); chữ gõ/trượt/pop chứ không "bật" cứng.
5. **Thẻ căn giữa, nền thẻ đậm 0.8–0.85**, viền kem, chữ có stroke đen → đọc được trên mọi ảnh. Vàng = điểm nhấn, đỏ = loại bỏ/nguy hiểm.
6. **Grain + vignette + tint ấm áp lên NỀN trước khi chồng overlay** (overlay giữ sắc nét). Grain seed theo số khung → không nhấp nháy giả.
7. **Nhãn trung thực**: cảnh dựng lại luôn có "RECONSTRUCTION". Số liệu/sự kiện đã fact-check mới được lên màn hình.
8. Âm thanh: VO là chuẩn (~ -15 LUFS); nhạc nền -21…-25 dB; sfx nhấn mạnh -5…-6 dB đúng khung hình nổ. Engine tự `loudnorm` về -14 LUFS (đổi bằng `--lufs`).

## Quy trình 8 bước cho mỗi beat
1. **Lấy tài nguyên**: ảnh 2560x1440 (`stills/`), VO + `wordts.json`, sfx, font.
2. **Chia câu & khoảng lặng**: `python3 tools/find_gaps.py vo/wordts.json`, rồi `python3 tools/word_times.py vo/wordts.json --auto` → bảng mệnh đề + gợi ý hiệu ứng (phủ định/số/tên riêng/trích dẫn). Đọc `EDITORIAL-PATTERNS.md`.
3. **Gán cảnh**: mỗi câu/cụm 3–8s một cảnh; điểm đổi cảnh = đầu khoảng lặng ≥0.5s. Ảnh thiếu → làm mờ/tối ảnh có sẵn (`blur`, `brightness`).
4. **Thiết kế camera** cho từng cảnh (hướng đẩy vào cái người xem phải nhìn; cuối cảnh đẩy mạnh hơn = "punch-in").
5. **Gán hiệu ứng theo lời** (xem `EFFECTS.md`): từ khoá/số/câu hỏi trong VO → phần tử, `t_in` = thời điểm từ đó bắt đầu (từ wordts) ±0.05s.
   Lấp mọi đoạn trống > 3.5s. Twist/cú đập → `flash` hoặc `shake` + sfx cùng khung.
6. **Viết `spec.json` rồi chạy `python3 tools/lint_spec.py spec.json --root res`** — sửa hết ERR và xem xét WARN TRƯỚC khi render (vài giây). Sau đó (copy `examples/koepcke_hook.json`), xem nhanh: `--frames t1,t2,...` ở các mốc (đầu/giữa/cuối mỗi cảnh, đúng lúc mỗi hiệu ứng nổ).
7. **Render**: `--out beat.mp4 --jobs 4`.
8. **Học**: so sánh với bản tham chiếu (nếu có), ghi mục mới vào `LESSONS.md` theo khuôn.
9. **QC bắt buộc**: `python3 tools/analyze_video.py beat.mp4 --out qa/` rồi xem `qa/report.txt`, `qa/energy.png`, `qa/contact.png`.
   Phải PASS jitter; không khung chết > 1.2s (trừ nhịp thở có chủ đích ≤1.5s); không trống sự kiện > 3.5s. Nghe lại mix.

## Lỗi hay gặp → cách sửa
| Triệu chứng | Nguyên nhân | Sửa |
|---|---|---|
| Nền rung nhẹ khi zoom | crop/resize làm tròn pixel, nội suy thấp | render 2x + Lanczos + INTER_AREA (dùng engine) |
| Số đếm "nhảy" khó chịu | tuyến tính / đổi giá trị theo giây | `power` 2.0–2.4 (tăng tốc dần) + pop khi chạm đích |
| Chuyển cảnh nghe bị "cắt lời" | dissolve đè lên chữ đang đọc | đặt trong khoảng lặng theo `find_gaps.py` |
| Thẻ lệch tâm / che mặt chủ thể | đặt toạ độ tay | căn `cx=640`, né vùng chủ thể; dùng `anchored_circle`/`highlight_box` cho thứ bám ảnh |
| Cảnh "chết" 4–7s | chỉ có zoom, không có lớp mới | thêm `label`, `spotlight`, `timeline`, `strike_cards`... mỗi ≤3.5s |
| Màu mỗi cảnh lệch nhau | không có bước hậu kỳ chung | `warm`, `vignette`, `grain` global |
| Video nặng 60MB+ | CRF thấp | `--crf 24` (≈5MB/28s, vẫn nét ở 720p) |

## Bàn giao cho producer
Mỗi beat nộp: `beat.mp4`, `spec.json`, `qa/report.txt`, và ghi chú sfx tạm (`_TAM`) cần thay. Báo rõ chỗ nào còn là placeholder.
