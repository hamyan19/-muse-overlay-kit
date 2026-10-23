# QUY TRÌNH — file duy nhất cần đọc trước

Mọi file khác trong repo là **tham chiếu**, chỉ mở ở đúng bước được nhắc tên bên dưới.
Nếu file tham chiếu nói khác file này, **file này thắng**.

## Ai làm gì
- **Muse:** script, voice, mapping, visual plan, nguyên liệu (hình, footage, âm thanh).
- **Người dựng:** anh chọn cho từng dự án (Claude, Muse hoặc GPT). Dùng `overlay_engine.py`.
- **Anh:** duyệt 2 lần: kế hoạch hình + style (trước khi tạo nguyên liệu) và video chương.

## 7 bước — làm tuần tự từng chương (xong chương này mới sang chương sau)

| # | Bước | Ai | Ra cái gì | Tham chiếu |
|---|---|---|---|---|
| 1 | **Script** | Muse | Lời đọc + ghi chú chương: BÌNH THƯỜNG hay SÔI NỔI, âm thanh phụ trợ | `SCRIPT-NOTES.md` mục 1 |
| 2 | **Voice** | Muse | `vo/<chương>.wav` + `vo/wordts.json` (mốc từng từ), đã sửa tên riêng | — |
| 3 | **Mapping câu theo voice** | Muse | Bảng câu/cụm câu ↔ mốc thời gian thật, cắt ở khoảng lặng | `tools/plan_assets.py` |
| 4 | **Visual plan** | Muse | Mỗi dòng của bảng mapping một ý tưởng hình, không lặp | `SCRIPT-NOTES.md` mục 2 |
| 5 | **Duyệt style dựng** | **Anh duyệt** | Chốt kế hoạch hình (bước 4) + style hình + style dựng của chương | `STYLES.md` |
| 6 | **Nguyên liệu cần có** | Muse | Danh sách → sản xuất → 1 lần kiểm → giao gói | `QC-ASSETS.md` |
| 7 | **Dựng** | Người dựng | Video chương → **anh xem**, nhận xét thì sửa | `PLAYBOOK.md`, `EFFECTS.md`, `EDITORIAL-PATTERNS.md` |

### Bước 1 — Script
Viết lời đọc của chương và ghi chú ngắn theo `SCRIPT-NOTES.md` mục 1 (loại chương + âm thanh phụ trợ).
Chưa viết ý tưởng hình ở bước này: hình được lên kế hoạch theo voice thật ở bước 4.

### Bước 2 — Voice
- Voice phải khớp script. Lệch thì hỏi anh trước khi thu lại.
- Chạy Whisper ra `wordts.json`, rồi **sửa chữ các tên riêng và con số** (giữ nguyên mốc thời gian).
- Đổi voice ⇒ làm lại bước 3 (mốc thời gian cũ không còn đúng).

### Bước 3 — Mapping câu theo voice
```bash
python3 tools/plan_assets.py res/vo/wordts.json --beat B3 --out plan/ --fix "Kupka=Koepcke"
```
Ra `plan/asset_plan.xlsx`. Sheet **SHOTS** là bảng mapping: mỗi dòng = một khoảng thời gian thật + lời đọc của khoảng đó,
điểm cắt nằm trong khoảng lặng. Muse đọc lại, gộp/tách dòng nếu ý nghĩa bị cắt sai chỗ.

### Bước 4 — Visual plan
Muse điền cột **HÌNH GỢI Ý** của sheet SHOTS cho từng dòng (thay đề xuất tự động nếu chưa hay), theo luật chống lặp trong
`SCRIPT-NOTES.md` mục 2. Dòng nào cần footage/AI video thì viết brief (mục "BRIEF VIDEO" trong `EDITORIAL-PATTERNS.md`);
không có brief thì là ảnh tĩnh.

### Bước 5 — Duyệt style (lần duyệt 1 của anh)
Muse gửi anh `asset_plan.xlsx` kèm đề xuất style của chương (chọn từ `STYLES.md`):
- **Style hình** — giữ nguyên cho cả video (chương đầu tiên: kèm character sheet theo `CHARACTER-SHEET.md`).
- **Style dựng** — preset + bộ chồng lớp, **khác chương liền trước**.

Anh điền cột DUYỆT (OK / SỬA / BỎ) và xác nhận hoặc đổi style. Dòng còn CHỜ thì chưa được làm. **Dừng chờ anh.**

### Bước 6 — Nguyên liệu cần có
```bash
python3 tools/apply_approval.py plan/asset_plan.xlsx --out plan/      # -> plan/MUSE-TODO.md = danh sách cần làm
```
1. Muse làm đúng danh sách OK/SỬA: ảnh, footage có brief, âm thanh (tra `SOUND-LIBRARY.md` trước, thiếu mới tạo).
2. **Một lần kiểm** theo `QC-ASSETS.md` (một lệnh máy + 5 mục nhìn bằng mắt). FAIL = 0 mới giao.
3. Giao gói cho người dựng. Anh **không** phải duyệt ảnh lần nữa (muốn xem trước thì chạy `tools/check_assets.py`).

### Bước 7 — Dựng
```bash
python3 tools/word_times.py res/vo/wordts.json --auto          # gợi ý hiệu ứng theo mệnh đề
python3 tools/lint_spec.py spec.json --root res                # kiểm spec, sửa hết ERR (vài giây)
python3 overlay_engine.py spec.json --root res --out chuong.mp4
```
Dựng theo style đã duyệt ở bước 5. Gửi anh video chương (lần duyệt 2). `tools/analyze_video.py` chỉ chạy khi thấy hình rung/đứng.

## Luật cứng (chỉ 5 điều)
1. Không tự duyệt thay anh; không làm dòng CHỜ; chương này chưa duyệt thì chưa sang chương sau.
2. Mọi ảnh bám style hình + character sheet đã khóa; ảnh không đủ 2560×1440 thì báo thẳng.
3. Style dựng của hai chương liền nhau phải khác nhau (chống bị quét nội dung lặp).
4. Video luôn full khung 16:9, không dải đen.
5. Có lỗi mới thì ghi **một dòng** vào `LESSONS.md`. Có âm thanh mới thì ghi vào `SOUND-LIBRARY.md`.

## Thư mục một dự án (không đưa lên repo này)
```
res/
  vo/        <chương>.wav, wordts.json
  stills/    ảnh 2560x1440 (tên file theo cột TÊN FILE ĐÍCH)
  video/     footage có brief
  sfx/       âm thanh
  fonts/     (chép từ repo)
plan/        asset_plan.xlsx, MUSE-TODO.md, approved_manifest.json
qc/          QC-REPORT.md
```
