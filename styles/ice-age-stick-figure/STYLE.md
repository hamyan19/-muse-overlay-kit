# STYLE — Ice Age Stick Figure (style người que, video Ice Age Winter)

Style hình đã khóa cho video "The Price of Surviving One Winter" (tên làm việc, chưa khóa).
An duyệt 24/10/2026 từ 4 ảnh mẫu anh gửi. Mọi ảnh của video này phải đối chiếu 4 ảnh mẫu
trong thư mục này trước khi gen, và gen xong phải soi THEO BỘ (liên tục nhân vật/đạo cụ
xuyên các tấm), không soi lẻ từng tấm.

## Ảnh mẫu
- `ref-1-wide-glacier-sunset.webp` — toàn cảnh: đồng bằng tuyết, tường băng xanh ở chân trời,
  hoàng hôn cam, lều xương + 3 người nhỏ quanh lửa. Chuẩn cho cảnh ngoài trời, tông lạnh.
- `ref-2-family-fire-hut.webp` — trong lều xương: 4 người quanh lửa (elder tóc bạc, hunter cầm giáo,
  mother tóc tết, child), dụng cụ đá + túi da trên nền đất, khung xương/ngà voi. Chuẩn cho cảnh
  trong nhà, tông ấm, và khóa "4 người quanh lửa".
- `ref-3-child-breath-closeup.webp` — cận mặt child: hơi thở trắng, tuyết bám áo lông, lông mày
  lo lắng, nền xương mờ. Chuẩn cho cận cảm xúc.
- `ref-4-diagram-firepit-cutaway.webp` — sơ đồ cắt lớp hố lửa: nền giấy parchment, mũi tên mực,
  hộp nhãn TRỐNG (không chữ), cô gái đang cào tro. Chuẩn cho lớp sơ đồ giải thích, KHÁC với
  cảnh kể chuyện (nền parchment chỉ dùng cho sơ đồ, không dùng cho cảnh thường).

## Style block (chép NGUYÊN VĂN vào đầu mọi prompt, không diễn đạt lại)

```
Hand-drawn ink sketch with soft watercolor wash, sketchy black ink lines and hatching, muted earth tones, pale round faces with two black dot eyes and minimal features, tattered fur and hide clothing with visible stitching, detailed natural textures, 16:9 frame.
```

Sau style block là mô tả cảnh cụ thể + cuối prompt luôn có:
`no text, no signage, no words in image`

Riêng cảnh sơ đồ thì thêm: `empty blank label boxes with thin ink arrows, no letters or numbers in the boxes`
— hộp nhãn để TRỐNG, chữ gắn ở hậu kỳ, cấm nướng chữ vào hình.

## Đặc điểm nhận diện
- Nét: mực đen vẽ tay, nét phác hơi run, gạch chéo (hatching) tạo khối, không phải vector sạch,
  không tả thực, không 3D.
- Mặt người que: mặt tròn/oval gần như trắng, chỉ 2 mắt chấm đen, miệng nhỏ, gần như không có mũi;
  cảm xúc chỉ qua lông mày (vạch ngắn) và miệng. Đây chính là lý do dùng style này: KHÔNG cần
  đồng hóa khuôn mặt từng người xuyên các cảnh — chỉ cần cùng "mặt chấm đen" là đủ nhận diện.
- Tóc: rối, sợi bay, nâu sẫm/đen; elder tóc bạc búi, mother tóc tết dài, child tóc rối.
- Quần áo: da lông rách, xám-nâu, đường khâu lộ rõ, chân quấn da, tay chân có vết bẩn nhẹ.
- Màu: bảng trầm — nâu đất, xám, xanh lạnh cho băng/đêm; cam lửa là điểm nhấn bão hòa duy nhất.
  Cấm ám vàng/đỏ lên da và ánh sáng (bake warmth vào prompt là lỗi cũ ở The Kind Truth).
- Bối cảnh: chi tiết thật, không phẳng trơn — tuyết, đá, xương, ngà voi, cỏ khô, gỗ, da khâu đều
  có vân. Vật liệu phải đúng thời kỳ: đá, xương, gỗ, da, lửa — cấm kim loại, vải hiện đại, đồ nhựa.
- Ánh sáng: lửa ấm trong nhà, hoàng hôn cam + xanh lạnh ngoài trời, đêm sao. Nguồn sáng phải
  nhất quán trong một cảnh (lửa thì sáng từ dưới lên, hoàng hôn thì sáng từ chân trời).

## Khóa nhân vật / đạo cụ (áp mọi prompt có người)
- Elder: tóc bạc, búi, áo lông dày. Hunter: râu, tóc rối sẫm, cầm giáo gỗ mũi đá. Mother: tóc tết
  dài, áo da. Child: nhỏ nhất, tóc rối, áo lông trùm.
- Giáo = cán gỗ + mũi đá nhọn, buộc dây; không giáo kim loại. Lều xương = khung xương/ngà voi
  + da phủ, không lều vải hiện đại.
- Cảnh có người toàn thân phải ghi rõ "whole body visible, both legs and feet clearly drawn"
  (nét này model cũng dễ nuốt chân như style cartoon nhà).

## Khi nào dùng / không dùng
- Dùng: toàn bộ video Ice Age Winter, cả cảnh kể chuyện lẫn sơ đồ (sơ đồ chỉ đổi nền parchment
  + hộp nhãn trống, giữ nguyên ngôn ngữ mực).
- Không dùng: thumbnail cần độ giật gân (việc riêng của thumbnail), và không mang sang dự án khác
  khi chưa có lệnh — đây là style riêng của video này, khác style cartoon nhà (house-cartoon).

## Bài học QC riêng cho style này (ghi khi gặp, đừng đợi cuối dự án)
- Soi bộ: cùng một người/đạo cụ xuất hiện nhiều tấm thì đặt các tấm cạnh nhau mà soi (tóc, áo,
  độ bẩn, giáo, túi da) — bài học Koepcke Beat 3.
- Đếm: đếm người, đếm tay/chân, đếm vật khóa; soi cả vật KHÔNG ĐƯỢC CÓ (kim loại, chữ, logo).
- Logic trước style: thuyền có máy thì không chèo; ở đây: người trong lều xương thì không đội mũ
  lông ngoài trời, lửa trong nhà thì không có tuyết rơi lên người trong nhà.
