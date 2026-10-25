# NHẬT KÝ DỰNG CH2 — để Muse học quy trình dựng (25/10)

Ghi lại đúng những gì đã làm khi dựng Ch2 "The Wall Is a Jar" từ gói ảnh + voice, theo thứ tự thật, kể cả lỗi và cách sửa.
Kết quả: bản xem nhanh 1280×720, 101,8s, có camera + giọng đọc + nhấn mạnh theo lời. Chưa có chữ/mũi tên/âm thanh, các dòng vẫn CHỜ duyệt (bản thử, không phải bản duyệt thật).

## 0. Đầu vào cần có (thiếu một thứ là không dựng được)
| Thứ | Ở đâu | Ghi chú |
|---|---|---|
| Bảng mapping đã chốt | `asset_plan.xlsx` (sheet SHOTS, OVERLAYS) | mã shot, mốc bắt đầu–kết thúc, chuyển động đề xuất |
| Ảnh | zip từ Drive, tên `CH2_S01.png`…`CH2_S12.png` | đủ 12 ảnh theo số shot (không tính dòng lớp phủ) |
| Voice | `ch2-warm-pebble-speed110.mp3` (101,78s) | |
| Mốc từng từ | `wordts.json` (mỗi dòng `[bắt đầu, kết thúc, từ]`) | dùng để canh nhấn mạnh |
| Repo | nhánh `muse/retime-5-11s` | main chưa có các công cụ mới |

## 1. Lấy ảnh
- Folder Drive có 11/12 ảnh (thiếu S11). Máy dựng **không tải được từ Drive** (đường tải bị chặn); công cụ Drive chỉ trả file dạng mã hóa nhét vào hội thoại, ảnh 3 MB không dùng được.
- **Cách đúng:** người dùng gửi ảnh thẳng vào chat (zip). Giải nén vào `res/stills/`.
- Kiểm: đủ 12 ảnh, tên đúng. **Ảnh gốc 1672×941, không phải 2560×1440** → phóng lên 2560×1440 (Lanczos) rồi lưu vào `res/stills/`. Báo cho người dùng biết (ảnh có thể hơi mềm; bản chất lượng cao cần ảnh lớn hơn).
- Tên ảnh ngắn theo mã shot, không theo cột TÊN FILE ĐÍCH → công cụ có cờ `--name-from-id` (CH2-S10 → CH2_S10.png).

## 2. Bảng mapping → spec.json
```bash
python3 tools/mapping_to_spec.py CH2_asset_plan.xlsx --vo vo/ch2.mp3 --name-from-id \
    --include-pending --preset storybook --duration 101.78 --calm --out spec_ch2.json
```
- Mỗi dòng SHOTS thành một cảnh; bỏ dòng CẢNH 0 (lớp phủ) và dòng có thời lượng 0 (cặp dissolve).
- Camera suy từ cột CHUYỂN ĐỘNG ĐỀ XUẤT: "đẩy vào" → zoom vào, "lia/dolly" → pan, "cố định" → gần đứng, còn lại → zoom nhẹ; xen hướng giữa các cảnh.
- `--include-pending` chỉ để thử (dòng CHỜ). Dựng thật phải là dòng OK do An duyệt.
- `--duration` = độ dài file voice; `--calm` vì spec chưa có lớp phủ (không thì lint báo thiếu phần tử).
- Lớp phủ trong sheet OVERLAYS **không** tự thành phần tử; chỉ ghi vào `meta.overlays_todo`.

## 3. Lỗi gặp khi chạy engine lần đầu (đã sửa trong công cụ)
| Lỗi | Nguyên nhân | Cách sửa |
|---|---|---|
| `KeyError: 'colors'` | engine bắt buộc có `colors`, `fonts` | công cụ tự thêm từ `examples/demo_motion.json`; chép thư mục `fonts/` vào `res/` |
| `lint_spec.py` sập `IndexError` | spec chưa có phần tử nào | sửa lint: bỏ qua khi rỗng |
| Render bị cắt ở khung 2200/3053 | lệnh chạy nổi có giới hạn 10 phút | chạy **nền** (`run_in_background`), chờ thông báo xong |
| Lint báo 5 ERR "TRỐNG SỰ KIỆN" | đoạn 9–10s không có gì đổi trên màn hình | đúng với spec chưa có lớp phủ; hết sau khi thêm nhấn mạnh |

Thời gian render: 1280×720, 8 tiến trình, cả chương ~10–13 phút. **Kiểm nhanh trước:** `--frames 36.8,40,... --frames-dir fr` chỉ render vài khung (vài chục giây), xem trước khi render cả chương.

## 4. Nhấn mạnh theo lời (yêu cầu của An: nhấn đúng động tác đang nói, nhưng ÍT hiệu ứng)
**Bản đầu em làm sai:** dùng spotlight (tô sáng vật, làm tối xung quanh) cho 22 điểm → lạm dụng, mọi shot cùng một kiểu. An yêu cầu: ít hiệu ứng, **chỉ 5–7 điểm nhấn cho cả chương**, dùng mũi tên vẽ tay, khoanh tròn, cắt cận cảnh, hoặc chỉ zoom (không tối nền). Phần còn lại giữ camera của mapping.

Nguyên tắc: hình đi theo **từ đang được nói**, không theo thứ tự trong bảng mapping.
1. Đọc `wordts.json` quanh từng shot, ghi giây của từ nói ra chi tiết (ví dụ S05: "sharp edge… open" 35,9–37,6 → rạch; "point… holes" 42,0 → đục lỗ).
2. Chọn **5–7 khoảnh khắc đáng nhấn nhất** của cả chương (câu then chốt, chi tiết dễ bỏ qua). Mỗi khoảnh khắc một kiểu khác nhau, không lặp kiểu liền nhau.
3. Lấy toạ độ chi tiết trên ảnh 2560×1440: vẽ **lưới mỗi 320px** lên ảnh thu nhỏ rồi đọc bằng mắt. **Sau đó render vài khung để kiểm** — lần đầu em đọc sai toạ độ khối đá vỡ ở S03 (đặt lệch cả 200px), chỉ nhìn ảnh khung mới thấy.
4. Viết `focus.json` (`examples/focus/CH2_focus.json`), mỗi beat có `t`, `kind`:
   - `zoom` {at, zoom}: camera trượt vào chi tiết, không tối nền.
   - `circle` {box}: khoanh tròn vẽ tay (bám camera).
   - `arrow` {from, to}: mũi tên vẽ tay.
   - `cut` {at, zoom}: cắt thẳng sang cận cảnh (crop cùng ảnh) rồi cắt lại, camera cũ chạy tiếp.
   - `spot` {at, r}: tô sáng/tối nền — chỉ khi thật sự cần, 1–2 lần/chương.
5. Chạy: `python3 tools/apply_focus.py spec_ch2.json CH2_focus.json --out spec_ch2_focus.json`
6. Ch2 dùng 7 điểm: S02 cắt cận mảnh dăm bật ra (12,2s); S03 khoanh khối đá vỡ (22,8s); S05 zoom bàn tay rạch da (35,3s) và mũi tên vào lỗ vừa đục (42,0s); S06 zoom khung nhà (45,1s); S07 khoanh vết rách (54,9s); S10 mũi tên vào đường khâu (78,8s).
7. Khi lời đọc và bảng mapping ngược thứ tự (S06: lời nói khung nhà trước, mapping ghi mảnh đá trước) → theo lời đọc.
8. Vật sát mép ảnh bị kẹt không vào giữa khung được (engine không lộ viền): vẫn đúng chỗ, chỉ lệch tâm.
- Cắt thẳng cần `dissolve: 0` riêng cho cảnh (engine đã hỗ trợ); khoanh/mũi tên bám camera nên không trôi khi camera chạy.
- Lint `--max-gap 12` khi spec ít lớp phủ (mặc định 9s hay báo "trống sự kiện" cho phong cách tối giản).

## 5. Kiểm sau khi dựng
- `tools/lint_spec.py spec.json --root res` → 0 lỗi (còn cảnh báo: toàn spotlight, camera S12 gần đứng, S01–S03 cùng đẩy vào).
- Xem 8 khung tĩnh tại các mốc nhấn mạnh (36.8, 40, 43, 46.5, 49.5, 55.5, 58.5, 62.5): vòng sáng đúng chi tiết, không lộ viền, không dải đen.
- `ffprobe`: 1280×720, h264 + aac, dài 101,78s khớp voice.

## 6. Chưa làm / việc còn lại
- Lớp nét đứt áo rách (CH2-EV001 lúc 50,6s): thiếu ảnh L01 trong gói.
- Chữ nhãn, mũi tên, âm thanh ngoài giọng đọc.
- Bản chất lượng cao 1920×1080 (cần ảnh gốc lớn hơn 1672×941).
- Chọn style dựng cho chương (hai chương liền nhau phải khác nhau) và duyệt các dòng CHỜ.
- Làm lại cho Hook, Ch1, Ch3–Ch9, Ending: cùng quy trình, mỗi chương một `focus.json`.

## 7. Bài học (thêm vào LESSONS.md nếu cần)
1. Ảnh không đủ 2560×1440 thì báo ngay (luật cứng số 2), đừng im lặng phóng lên.
2. Tải ảnh qua Drive không được → xin người dùng gửi thẳng vào chat.
3. Render dài thì chạy nền và kiểm trước bằng vài khung.
4. Nhấn mạnh theo từ đang nói (wordts), không theo thứ tự bảng; **chỉ 5–7 điểm/chương, mỗi điểm một kiểu**, đừng dùng một hiệu ứng cho mọi shot (bài học bản đầu dùng spotlight 22 lần).
5. Đọc toạ độ bằng mắt thì render khung kiểm ngay, đừng tin toạ độ ước lượng.
6. Chạy lint ngay sau khi tạo spec, trước khi render.
