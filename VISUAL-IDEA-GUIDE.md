# HƯỚNG DẪN CHỌN Ý TƯỞNG HÌNH VÀ KIỂM (QC) — dành cho Muse

Dùng ở bước 4–6 của `QUY-TRINH.md`. Viết prompt thì đọc `META-PROMPT-VISUAL.md`.
Trước khi làm: tải về và xem 3 ảnh mẫu trong `styles/ice-age-stick-figure/ref-approved/`.

## 1. Cắt shot trước, chọn hình sau
- Điểm cắt chỉ đặt giữa khoảng lặng của giọng đọc (hở ≥0,3s giữa hai từ trong `wordts.json`). Mỗi shot 5–11s.
- Shot không có chỗ ngắt thì để dài tối đa ~11,6s và ghi chú; không cắt giữa câu.
- Chỉ sinh prompt SAU khi điểm cắt đã chốt. Đổi mốc thì kiểm lại cả bảng (prompt, chuyển động, ghi chú, mã).

## 2. Chọn visual idea: một shot, một việc hình ảnh
Với mỗi shot, hỏi theo thứ tự:
1. Câu này đang làm gì? (gợi cảm giác quen thuộc / giải thích cơ chế / kể hành động / chuyển cảnh)
2. Chủ thể nên là người, vật hay sơ đồ? Cơ chế → vật + mặt cắt. Thao tác → cận tay và vật, bỏ mặt. Người chỉ xuất hiện khi hành động của họ là nội dung chính.
3. Hiện đại hay cổ đại? Quyết riêng từng shot. Cảnh hiện đại và cổ đại cùng một vấn đề thì dùng chung góc để người xem tự nối.
4. Một ảnh = một khoảnh khắc. Nhiều động tác nối tiếp → chọn khoảnh khắc rõ nhất cho ảnh, phần còn lại để chuyển động camera (A→B→C).
5. Cần lớp phủ không? Mũi tên, nhãn, nét đứt hiện đại do engine vẽ, không sinh vào ảnh.

## 3. Liên tục và tái sử dụng
- Callback có chủ ý (cửa vào lều Ch5 → Ch9, phòng Hook → Ending). Ghi vào cột ghi chú và bảng đối tượng dùng lại.
- Chương liền kề dùng style dựng khác nhau.
- Mùa: chương còn là mùa thu chuẩn bị thì không tuyết, không bão.
- Mỗi prompt tự đứng được: ghi đặc điểm cần giữ, không viết "giống shot trước".

## 4. Viết spec
- Cấu trúc: STYLE → chủ thể/hành động/khung hình → màu theo thành phần → quy tắc nhân vật → Negative riêng của shot.
- Negative theo bối cảnh: cảnh hiện đại cấm đồ cổ, cảnh cổ đại cấm đồ hiện đại; không dùng một danh sách cấm chung.
- Không nói "đã dùng ảnh tham chiếu" khi ảnh chưa đính. Thông tin ảnh cần đính ghi ở cột "Loại nguyên liệu".
- Không thêm số liệu, nhãn, nguy hiểm, kết luận mà đầu vào không yêu cầu.

## 5. QC — máy làm gì, mắt làm gì
Nguyên tắc: lỗi nào máy bắt được thì để máy bắt; mắt người dành cho ý nghĩa.

**Máy (tự động):**
- Thời lượng mỗi shot nằm trong 5–11s (ngoại lệ có ghi chú; cặp dissolve có thời lượng 0).
- Mốc thời gian trong cột chuyển động nằm trong khoảng của shot.
- Các shot nối liền, không hở, không chồng; cột thời gian khớp cột "dài (s)".
- Từ cấm; rác ký tự trong prompt rút gọn.
- Chỉ số cảnh của lớp phủ tính tự động từ thời điểm từ kích hoạt.

**Mắt, trên mapping và prompt:**
- Đúng một khoảnh khắc? Đúng thời đại? Negative có cấm nhầm vật đang cần vẽ không?
- Có thêm người, đạo cụ, nhãn không được yêu cầu không?
- Cơ chế đúng chiều không? (nhiệt đi từ cơ thể ra môi trường lạnh; lớp đệm làm chậm, không chặn tuyệt đối; gió mang nhiệt đi)
- Trái mùa? Vật neo liên tục (áo đỏ, cửa, nhà xương)?
- Mã shot, tên file đích, ghi chú "dùng lại ở…", bảng đối tượng dùng lại khớp nhau.

**Mắt, trên ảnh đã sinh:**
1. Đếm người, tay chân, vật khóa (một người, một dùi, một đống củi). Soi vật không được có: kim loại, chữ, logo, tuyết trái mùa.
2. Đặt cạnh nhau các ảnh cùng nhân vật hoặc cùng vật neo để soi tóc, áo, góc nhìn.
3. Đối chiếu 3 ảnh mẫu đã duyệt: ảnh quá chi tiết, mặt có bóng, giống ảnh thật thì loại.
4. Logic: lửa trong lều thì không có tuyết rơi lên người trong lều; mặt cắt đúng chiều mũi tên.
5. Ảnh đủ chỗ trống cho camera chạy A→B và cho nhãn/mũi tên do engine vẽ.

## 6. Lỗi đã gặp (xem thêm `LESSONS.md`)
- Đổi mốc cắt nhưng prompt, chuyển động cũ không đổi theo → kiểm lại cả bảng sau mỗi lần đổi mốc.
- Chỉ số cảnh của lớp phủ lệch sau khi tách shot → tính từ thời điểm kích hoạt.
- Chế độ nhịp của `plan_assets.py` từng tạo shot 2s → để tùy chọn, mặc định tắt.
- Prompt rút gọn bị rác ký tự (", ,") → làm sạch trước khi up.
