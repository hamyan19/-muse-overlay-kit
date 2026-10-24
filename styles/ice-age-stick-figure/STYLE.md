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
- **LUẬT MẶT TỐI GIẢN TUYỆT ĐỐI (An chốt 24/10, áp cả cận mặt):** mặt trắng PHẲNG, hai mắt chấm
  đen đặc, lông mày chỉ là nét vẽ đơn, miệng nét phẳng hoặc cong nhỏ, cùng lắm một chấm mũi mờ.
  CẤM: highlight trong mắt, nếp nhăn, răng, tả khối/bóng trên mặt, lông mày nặng tay. Cảm xúc CHỈ
  đổi bằng góc lông mày + hình miệng. Đây chính là lý do dùng style này: KHÔNG cần đồng hóa khuôn
  mặt từng người xuyên các cảnh — chỉ cần cùng "mặt chấm đen" là đủ nhận diện.
- **Tương phản là style:** chi tiết dồn vào THẾ GIỚI, không dồn vào mặt — lông thú, xương, lửa,
  tuyết, nền giấy parchment, màu nước vẽ càng chi tiết càng tốt; người thì tối giản. Thế giới thật,
  người tối giản. Cận cảnh tay/vật thì mặt KHÔNG được chiếm khung thay cho chủ thể (lỗi S04 v1:
  mặt tả chi tiết + chiếm khung thay vì cận tay → gen lại, truyền thẳng 4 ảnh mẫu làm anchor).
  Gen cảnh có mặt: truyền thẳng 4 ẢNH MẪU làm anchor, không chỉ viết prompt bằng chữ.
- Tóc: rối, sợi bay, nâu sẫm/đen; elder tóc bạc búi, mother tóc tết dài, child tóc rối.
- Quần áo: da lông rách, xám-nâu, đường khâu lộ rõ, chân quấn da, tay chân có vết bẩn nhẹ.
- Màu: bảng trầm — nâu đất, xám, xanh lạnh cho băng/đêm; cam lửa là điểm nhấn bão hòa duy nhất.
  Cấm ám vàng/đỏ lên da và ánh sáng (bake warmth vào prompt là lỗi cũ ở The Kind Truth).
- **TƯƠNG PHẢN GIỮA CÁC THÀNH PHẦN LÀ TIÊU CHÍ MÀU (An chốt 24/10):** băng giá lạnh xanh, ánh lửa
  ấm cam, bầu trời dải riêng, quần áo nâu đất PHẢI nổi khỏi nền, đồ vật đọc được ngay. Lỗi chết:
  một dải hue duy nhất phủ cả khung (đo S05 bản ngoài: người 207°, băng 212°, trời 216° — áo lông
  cùng màu băng nên người CHÌM vào cảnh). QC màu = đo/soi hue TỪNG THÀNH PHẦN tách nhau, không
  đo bão hòa trung bình cả khung (Phoenix đã chẩn đoán sai bằng bão hòa TB, An bắt lại).
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

## PHƯƠNG PHÁP PROMPT — CHUẨN NGẮN v3 (An duyệt 24/10, thay mọi prompt dài)

Bài học màu: prompt dài kiểu cũ (style block + đoạn mô tả thời kỳ + negative dài) cho màu
ĐỤC/xấu. Chuẩn đã kiểm chứng qua trọn bộ Hook v3 (19 hình, An duyệt): prompt NGẮN, cấu trúc cố định:

1. Mở đầu nguyên văn: `Using the attached reference images for the drawing style and the simple
   face:` (cảnh không có người thì bỏ đoạn "and the simple face").
2. ĐÍNH THẲNG 4 ẢNH MẪU của thư mục này vào mọi lần gen — anchor bằng hình, không mô tả lại style
   bằng chữ.
3. Thân prompt chỉ gồm: cảnh gì + từng thành phần có màu/ánh sáng riêng (băng xanh lạnh, lửa cam
   ấm, áo lông nâu, trời dải riêng) + nếu có mặt người thì 1 câu luật mặt ("His face stays flat
   white with two solid round dot eyes, two thin single-stroke eyebrows …, and one small flat
   mouth line.").
4. Kết nguyên văn: `Rough Ice Age furs only, no text.` — không negative list dài.
5. Ảnh bám bố cục một ảnh đã duyệt (chuỗi trại S08→S09→S10) thì đính thêm chính ảnh đó.

Bộ prompt mẫu đã duyệt: `PROMPTS-HOOK-v3-short.csv` (cùng thư mục style trên repo).

## Khi nào dùng / không dùng
- **Kích hoạt bằng từ khóa:** khi An nói "làm người que" / "style người que" → dùng ĐÚNG style
  này (4 ảnh mẫu + prompt ngắn v3), không tự chế style người que khác.
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
