# PLAYBOOK — tay nghề dựng (tham chiếu cho bước 7 của `QUY-TRINH.md`)

## Nguyên tắc cốt lõi (rút từ việc chấm từng khung hình bản Hook Koepcke)
1. **Camera không bao giờ đứng yên và không bao giờ giật.** Mỗi cảnh có zoom/pan chậm với easing (`smooth`, `pow:2.2`).
   Giật = lỗi do crop làm tròn pixel; engine đã render 2560x1440 bằng affine + Lanczos rồi `INTER_AREA` xuống khung xuất.
2. **Mốc thời gian lấy từ lời đọc, không đoán.** Mọi dissolve 0.5s nằm TRỌN trong khoảng lặng (`tools/find_gaps.py`).
3. **Cứ ≤ 3.5s phải có một sự kiện thị giác mới** (thẻ hiện, vòng, số nhảy, đổi cảnh, chớp...), trừ cảnh `hold` hoặc chương `calm`.
   Hai cảnh liền nhau không dùng cùng "ngữ pháp" hình ảnh.
4. **Không overlay tĩnh > 3s.** Số chạy có easing; chữ gõ/trượt/pop chứ không "bật" cứng.
5. **Chữ đọc được trên mọi ảnh:** thẻ nền đậm 0.8–0.85, viền kem, chữ có stroke; chữ phụ ≥ 26px. Vàng = điểm nhấn, đỏ = loại bỏ/nguy hiểm.
6. **Grain + vignette + tint lên NỀN trước khi chồng overlay** (overlay giữ sắc nét).
7. **Nhãn trung thực:** cảnh dựng lại có "RECONSTRUCTION"; chỉ đưa lên màn hình số liệu đã kiểm chứng.
8. **Âm thanh:** VO là chuẩn; nhạc nền −21…−25 dB; sfx nhấn −5…−6 dB đúng khung hình; engine tự chuẩn hoá −14 LUFS.

## Thứ tự dựng một chương
1. Lấy gói từ bước 6 (`res/` + `plan/approved_manifest.json`) và style dựng đã duyệt (`STYLES.md`).
2. `tools/word_times.py res/vo/wordts.json --auto` → bảng mệnh đề + gợi ý hiệu ứng.
3. Viết `spec.json` (mẫu: `examples/koepcke_hook.json`): cảnh theo mốc của manifest, camera từng cảnh hướng vào cái người xem phải nhìn,
   hiệu ứng `t_in` = lúc từ khoá bắt đầu ±0.05s. Tham số hiệu ứng: `EFFECTS.md`.
4. `tools/lint_spec.py spec.json --root res` → sửa hết ERR. Xem nhanh vài khung bằng `--frames t1,t2,...`.
5. Render, nghe lại mix, gửi anh.

## Lỗi hay gặp → cách sửa
| Triệu chứng | Nguyên nhân | Sửa |
|---|---|---|
| Nền rung nhẹ khi zoom | crop/resize làm tròn pixel | dùng engine (render 2x + Lanczos) |
| Số đếm "nhảy" | tuyến tính | `power` 2.0–2.4 + pop khi chạm đích |
| Chuyển cảnh "cắt lời" | dissolve đè lên chữ đang đọc | đặt trong khoảng lặng (`find_gaps.py`) |
| Thẻ che chủ thể | đặt toạ độ tay | né vùng chủ thể; dùng `anchored_circle`/`highlight_box` cho thứ bám ảnh |
| Cảnh "chết" 4–7s | chỉ có zoom | thêm `label`, `spotlight`, `timeline`, `strike_cards`... mỗi ≤3.5s |
| Màu mỗi cảnh lệch nhau | không có hậu kỳ chung | `warm`, `vignette`, `grain` global |
| Video quá nặng | CRF thấp | `--crf 24` |
| Hình rung/đứng mà không rõ chỗ | — | `tools/analyze_video.py chuong.mp4 --out qa/` |

## Bàn giao
Mỗi chương: `chuong.mp4` + `spec.json`; nói rõ âm thanh nào còn `_TAM`.
