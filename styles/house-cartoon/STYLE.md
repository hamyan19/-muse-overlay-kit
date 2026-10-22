# STYLE — House Cartoon (nét cartoon nhà Chapter Studio)

Phong cách ảnh MẶC ĐỊNH đã dùng xuyên các chương Chapter Studio (Amazon, Koepcke test 22/10/2026).
Mọi ảnh theo style này phải đối chiếu 3 ảnh mẫu trong thư mục này (`ref-1-fall.jpg`, `ref-2-seat-jungle.jpg`, `ref-3-stream.jpg`).

## Style block (chép NGUYÊN VĂN vào đầu mọi prompt, không diễn đạt lại)

```
Cartoon illustration, simple clumsy hand-drawn lines, flat colors, friendly storybook look, 16:9 frame.
```

Sau style block là mô tả cảnh cụ thể + khóa nhân vật (từ character sheet của dự án) + cuối prompt luôn có:
`no text, no signage, no words in image`

## Đặc điểm nhận diện
- Nét vẽ tay vụng có chủ đích (clumsy), viền đơn giản, KHÔNG tả thực, không chi tiết rậm.
- Màu phẳng (flat colors), ít chuyển sắc, không ám vàng.
- Cảm giác sách truyện thân thiện (storybook) — kể cả cảnh nguy hiểm vẫn giữ nét này, cảm xúc đến từ bố cục/lời đọc, không từ nét vẽ giật gân.
- Khác hẳn: pulp comic (viền mực đậm, khắc chéo, bão hòa — KHÔNG dùng), painterly điện ảnh (dùng cho lane Koepcke chính), nét phẳng tối giản kiểu icon (quá trơn, dễ mất bộ phận cơ thể).

## Bài học QC riêng cho style này
- Chi tiết ít nên model dễ NUỐT BỘ PHẬN: thiếu chân/tay là lỗi đã gặp thật (22/10) — prompt cảnh có người phải ghi rõ "whole body visible, both legs and feet clearly drawn" khi cần toàn thân, và QC soi giải phẫu kỹ hơn bình thường.
- Dây an toàn dễ bị vẽ thành dây chéo chữ X — ghi "simple lap belt across the waist" nếu cần đúng chuẩn ghế máy bay.
- Giữ đúng số lượng vật thể khóa (vd băng ghế = đúng 3 ghế) — nét đơn giản không phải lý do để sai số.

## Khi nào dùng / không dùng
- Dùng: các chương theo lane Chapter Studio, cảnh kể chuyện thường, cảnh giải thích.
- Không dùng: thumbnail cần độ giật gân (đó là việc của thiết kế thumbnail riêng), cảnh đã khóa style khác trong character sheet của dự án.
- Theo QUY-TRINH.md: mỗi chương một phong cách hình khác chương liền kề — style này là MỘT trong các style luân phiên, không mặc định cho mọi chương liên tiếp.
