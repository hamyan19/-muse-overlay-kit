# HƯỚNG DẪN CHO CLAUDE MỚI — dựng video chương từ gói nguyên liệu

Dành cho một Claude **chưa biết gì về dự án**. Đọc hết file này trước, rồi mới mở file khác.
Vai của bạn là **người dựng** (bước 7 trong `QUY-TRINH.md`): nhận gói nguyên liệu đã duyệt → ra `chuong.mp4`.
Bạn **không** viết script, không thu voice, không tạo ảnh, không tự duyệt thay anh. Những việc đó là của Muse và của anh (chủ dự án).

> Trạng thái file này: viết từ việc đọc mã và nhật ký dựng Ch2 (25/10). Các lệnh bên dưới lấy đúng từ tham số trong mã,
> nhưng **chưa có ai chạy trọn chuỗi lệnh từ đầu tới cuối trên một máy sạch**. Gặp lỗi thì sửa, rồi thêm một dòng vào `LESSONS.md`.

---

## 1. Cài đặt (làm một lần mỗi máy/phiên)

### 1.1 Cần có
| Thứ | Yêu cầu | Kiểm |
|---|---|---|
| Python | 3.10 trở lên | `python3 --version` |
| ffmpeg + ffprobe | trong PATH, có encoder `libx264` và `aac` | `ffmpeg -version`, `ffmpeg -encoders \| grep -E "libx264\|aac"` |
| Thư viện Python | numpy, opencv-python-headless, pillow, matplotlib, openpyxl | `python3 -c "import numpy, cv2, PIL, matplotlib, openpyxl; print(cv2.__version__)"` |
| Repo | đúng **nhánh** (xem 1.2) | `git branch --show-current` |

```bash
git clone https://github.com/hamyan19/-muse-overlay-kit
cd -muse-overlay-kit          # tên thư mục bắt đầu bằng dấu "-": dùng `cd ./-muse-overlay-kit` nếu shell hiểu nhầm là tuỳ chọn
# đang ở nhánh main là đủ công cụ (xem 1.2)
pip install -r requirements.txt   # trên Linux/Claude cloud thêm: --break-system-packages
```

Tuỳ chọn (không bắt buộc để dựng): `tesseract` (để `qc_assets.py` kiểm chữ/logo trong ảnh bằng OCR). Không có thì công cụ ghi "OCR TẮT" và bạn phải kiểm chữ/logo bằng mắt.
`wordts.json`: nếu An chưa đưa thì **tự tạo**, không cần hỏi (căn theo script bằng PocketSphinx, không dùng Whisper, nên chữ trong file là chữ của script, không cần sửa tên riêng/số):
```bash
pip install pocketsphinx
ffmpeg -i chX.mp3 -ar 16000 -ac 1 chX16.wav
python3 tools/align.py chX16.wav chX.txt wordts.json   # chX.txt = script chương (An đưa)
python3 tools/check_wordts.py wordts.json CHX_asset_plan.xlsx --voice chX.mp3
```
Từ lạ (OOV) báo ra thì thêm vào dict `SUB` đầu `tools/align.py` bằng từ phát âm gần giống.

### 1.2 Chọn nhánh nào
- `main` (đã merge 26/10) có đủ công cụ: `mapping_to_spec.py`, `apply_focus.py`, `apply_overlays.py`, camera nhiều mốc, `dissolve` riêng từng cảnh, `image_overlay`. Dựng từ `main`; nhánh `muse/retime-5-11s` chỉ là lịch sử. Nếu anh bảo dùng nhánh khác, theo anh.

### 1.3 Môi trường Claude cloud (nếu bạn chạy trong phiên Claude có sandbox)
- Mạng thường chỉ cho phép registry gói (pip/npm) và GitHub. **Không tải được file từ Google Drive** bằng shell. Nếu ảnh/voice nằm trên Drive thì xin anh gửi thẳng vào chat (zip) hoặc đặt vào thư mục đã kết nối. Đừng thử vòng qua chặn.
- Mỗi lệnh chạy nổi bị giới hạn ~10 phút. Render cả chương mất ~10–13 phút (1280×720, 8 tiến trình), nên **render bằng chế độ chạy nền** và chờ thông báo xong.
- Số nhân CPU quyết định tốc độ: `--jobs` mặc định = số nhân. Máy 2 nhân: video 1 phút ≈ 15 phút (số liệu trong `HUONG-DAN-WINDOWS.md`).
- File anh gửi qua chat nằm ở thư mục tải lên; hãy làm việc trên **bản sao** trong `res/`, đừng sửa bản gốc.

---

## 2. Bạn phải được cung cấp những gì (thiếu một thứ là chưa dựng được → hỏi anh)

### 2.1 Gói nguyên liệu của chương
| # | Thứ | Định dạng / quy ước | Ghi chú |
|---|---|---|---|
| 1 | **Voice** | `res/vo/<chương>.mp3` hoặc `.wav` | Phải đúng voice đã dùng để lấy mốc thời gian. Đổi voice ⇒ mốc cũ vô dụng, Muse phải làm lại mapping. |
| 2 | **`wordts.json`** | `res/vo/wordts.json`, mỗi dòng `[bắt đầu, kết thúc, "từ"]` (giây) | Mốc từng từ (An đưa, hoặc tự tạo bằng `tools/align.py`, xem 1.1). Dùng để canh hiệu ứng theo lời. |
| 3 | **Ảnh** | `res/stills/`, PNG/JPG, **2560×1440** (16:9) | Tên đúng cột **TÊN FILE ĐÍCH** của bảng mapping (không dấu, không `#`, không khoảng trắng), hoặc dạng `CH2_S01.png` ứng với mã shot `CH2-S01` khi dùng `--name-from-id`. |
| 4 | **Bảng mapping đã duyệt** | `asset_plan.xlsx` có sheet **SHOTS** (và sheet OVERLAYS nếu có) | Cột bắt buộc trong SHOTS: `ID`, `CẢNH`, `PHỦ THỜI GIAN`, `DÀI (s)`, `CHUYỂN ĐỘNG ĐỀ XUẤT`, `TÊN FILE ĐÍCH`, `DUYỆT`. Chỉ dòng `DUYỆT=OK` được dựng thật. |
| 5 | **Font** | `res/fonts/` | Chép nguyên thư mục `fonts/` của repo sang `res/fonts/`. |
| 6 | **Footage / âm thanh** (nếu bảng có) | `res/video/`, `res/sfx/` | Tên file tạm có đuôi `_TAM` thì báo lại ở lúc bàn giao. |

### 2.2 Quyết định mà bạn không được tự quyết
Nếu anh chưa nói, **hỏi một lần, gọn, trước khi làm** (đừng làm rồi mới hỏi):
- **Style dựng của chương** (chọn trong `STYLES.md`, mục B). Hai chương liền nhau phải **khác** nhau. Biết chương trước dùng style gì.
- **Độ phân giải xuất**: bản xem nhanh 1280×720 (nhẹ, dùng để anh duyệt) hay bản cuối 1920×1080. Bản cuối cần ảnh nguồn đủ lớn, xem 4.2.
- **Có làm lớp phủ/chữ/âm thanh không**, hay chỉ bản xem nhanh camera + nhấn mạnh. (Các bản dựng thử Ch2 chưa có chữ và âm thanh ngoài voice.)
- **Điểm nhấn theo lời** (5–7 điểm/chương): anh có chỉ định sẵn không, hay bạn đề xuất rồi anh gật. Xem 3.5.

### 2.3 Quyền hạn
- Dòng `DUYỆT` còn `CHỜ` thì **không** dựng thật (chỉ được dùng `--include-pending` để thử, và phải nói rõ là bản thử).
- Chương này chưa được anh duyệt video thì **chưa sang chương sau**.
- Không tự thay style hình hay character sheet (đã khoá).

---

## 3. Quy trình dựng một chương, từng lệnh

Thư mục dự án (ngoài repo, `--root` trỏ vào `res/`):
```
res/
  vo/        ch2.mp3, wordts.json
  stills/    CH2_S01.png … (2560×1440)
  video/     (nếu có)
  sfx/       (nếu có)
  fonts/     (chép từ repo)
plan/        asset_plan.xlsx
qc/          báo cáo kiểm
```
Mọi đường dẫn bên trong spec tính từ `--root`.

### 3.1 Kiểm đầu vào (3 phút, tránh dựng nhầm cả buổi)
1. Đếm ảnh: số ảnh trong `res/stills/` = số dòng SHOTS được dựng (không tính dòng lớp phủ `CẢNH 0` và dòng thời lượng 0, vì công cụ bỏ chúng). Thiếu ảnh nào thì **báo ngay**, đừng tự thế ảnh khác.
2. Kích thước ảnh: `python3 -c "import glob; from PIL import Image; [print(f, Image.open(f).size) for f in sorted(glob.glob('res/stills/*'))]"`. Nếu không phải 2560×1440 (ví dụ 1672×941 như ảnh Ch2) thì phóng lên 2560×1440 bằng Lanczos, lưu vào `res/stills/`, và **nói với anh** rằng ảnh có thể hơi mềm. Luật cứng số 2 trong `QUY-TRINH.md`: không im lặng.
3. Độ dài voice: `ffprobe -v error -show_entries format=duration -of csv=p=0 res/vo/ch2.mp3`. Ghi lại, dùng cho `--duration` ở bước sau.
4. Kiểm máy (tuỳ chọn): `python3 tools/qc_assets.py --root res --manifest plan/approved_manifest.json --out qc/` (cần `approved_manifest.json`; có từ `apply_approval.py`). FAIL phải sửa hoặc báo.

### 3.2 Bảng mapping → `spec.json`
```bash
python3 tools/mapping_to_spec.py plan/CH2_asset_plan.xlsx --vo vo/ch2.mp3 --name-from-id \
    --preset storybook --duration 101.78 --calm --out spec_ch2.json
```
- Mặc định chỉ lấy dòng `DUYỆT=OK`. Thêm `--include-pending` chỉ để **thử** với dòng CHỜ.
- `--duration` = độ dài file voice (giây). `--calm` khi spec chưa có lớp phủ (không thì lint báo thiếu phần tử).
- `--preset` là style dựng đã chọn (xem `STYLES.md`/`EFFECTS.md`). Bỏ qua nếu anh chưa chốt, nhưng phải hỏi.
- Camera suy từ cột CHUYỂN ĐỘNG ĐỀ XUẤT ("đẩy vào", "lia/dolly", "cố định"…). Lớp phủ trong sheet OVERLAYS không tự thành phần tử: công cụ chỉ ghi vào `meta.overlays_todo`; bật chúng bằng `tools/apply_overlays.py` (mục 3.5b).
- Công cụ này ghi `width=1920, height=1080, fps=30`. Muốn bản xem nhanh 1280×720 thì sửa `meta.width/height` trong spec (engine dùng 1280×720 nếu thiếu). Toạ độ camera và điểm nhấn vẫn tính theo ảnh nguồn **2560×1440**.

### 3.3 Kiểm spec ngay sau khi tạo
```bash
python3 tools/lint_spec.py spec_ch2.json --root res
python3 tools/lint_spec.py spec_ch2.json --root res --max-gap 12   # phong cách tối giản, ít lớp phủ
```
Sửa hết **ERR** trước khi render. (Luật "≤3,5s một sự kiện hình" của PLAYBOOK dành cho chương nhiều hiệu ứng; chương theo kiểu **ít hiệu ứng** như Ch2 dùng `--calm` khi tạo spec và `--max-gap 12` khi lint.) WARN thì đọc rồi quyết định. Tham số mặc định: `--max-gap 3.5` (khoảng tối đa không có sự kiện hình), `--max-static 3.0`, `--min-text 26`.

### 3.4 Xem nhanh vài khung trước khi render cả chương
```bash
python3 overlay_engine.py spec_ch2.json --root res --frames 12.5,23.5,36.8,43 --frames-dir fr
```
Xem ảnh khung ra: không lộ viền/dải đen, chi tiết đúng chỗ, chữ đọc được. Vài chục giây, rẻ hơn nhiều so với render hỏng.

### 3.5 Điểm nhấn theo lời (chỉ 5–7 điểm cho cả chương)
Đây là phần anh phản hồi nhiều nhất, đọc kỹ `NHAT-KY-DUNG-CH2.md` mục 4.
1. Đọc `wordts.json` quanh từng shot, ghi **giây của từ đang nói** tới chi tiết đó (hình đi theo lời, không theo thứ tự bảng).
2. Chọn **5–7 khoảnh khắc** cho cả chương, **mỗi điểm một kiểu khác nhau**: `zoom`, `circle`, `arrow`, `cut`. Có thể dùng `spot` (tô sáng vật thể, hạ sáng nền) tối đa 1–2 lần/chương cho vật thể then chốt; công cụ tự canh độ sáng (dim ≤0.45, khung sau phủ ≥95/255, ảnh gốc tối <80 thì tự đổi sang khoanh tròn). Đọc dòng `spot ... dim ...` in ra và xem khung kiểm trước khi render. Bản v2 dùng spotlight 22 lần bị anh chê lạm dụng.
3. Lấy toạ độ trên ảnh 2560×1440: kẻ lưới 320px lên ảnh thu nhỏ rồi đọc bằng mắt. **Render khung kiểm ngay** (3.4): lần đầu từng đọc lệch cả 200px.
4. Viết `focus.json` (mẫu: `examples/focus/CH2_focus.json`) rồi chạy:
```bash
python3 tools/apply_focus.py spec_ch2.json focus_ch2.json --out spec_ch2_focus.json
```
5. Nếu anh chưa chỉ định điểm nhấn: đề xuất danh sách (giây, kiểu, câu trong lời) rồi **hỏi trước khi làm** (bài học v2: "trả lời trước khi làm").

Kiểu `cut` cần `dissolve: 0` riêng cho cảnh (công cụ tự đặt). Vật sát mép ảnh bị kẹt, không vào giữa khung được (engine không lộ viền).

### 3.5b Lớp phủ trong sheet OVERLAYS (mũi tên, nhãn, nét đứt, ảnh L01, tuyết) — đã BẬT
```bash
python3 tools/apply_overlays.py spec_focus.json plan/CHX_asset_plan.xlsx --template pos.json     # khung điền, mỗi dòng OVERLAYS một mục
# nhìn ảnh (lưới 320px), điền toạ độ ảnh nguồn 2560x1440 vào pos.json (from/to, at, points; L01 cần ảnh + file)
python3 tools/apply_overlays.py spec_focus.json plan/CHX_asset_plan.xlsx --pos pos.json --out spec_ov.json --root res
```
Mục chưa điền toạ độ bị bỏ qua và được liệt kê; tuyết tự bật. **Luôn render khung kiểm** sau khi đọc toạ độ bằng mắt.
**RÀO SÁNG:** lớp ảnh L01 là multiply chỉ phủ nét tối (không tối cả khung), strength ≤0.85, độ phủ TB ≤10%, nền < 80/255 thì không phủ; `spot` (tô sáng vật) dim ≤0.45 và sáng TB sau phủ ≥95/255 (lint cảnh báo nếu vượt). Tối đa 2 phần tử phủ cùng lúc. Phủ xong phải mở khung kiểm xem còn sáng, đừng chỉ tin số.

### 3.6 Render
```bash
python3 overlay_engine.py spec_ch2_focus.json --root res --out ch2.mp4 --jobs 8 --crf 24 --lufs -14
```
Chạy **nền**, chờ thông báo xong. Tuỳ chọn: `--video-only` (chỉ hình), `--crf` (cao hơn = nhẹ hơn), `--lufs 0` tắt chuẩn hoá âm lượng.
Tiếng: voice là chuẩn; nhạc nền −21…−25 dB, sfx nhấn −5…−6 dB, engine chuẩn hoá master −14 LUFS.

### 3.7 Kiểm sau khi dựng
1. `ffprobe`: đúng độ phân giải đã chốt, `h264` + `aac`, **độ dài khớp voice**.
2. Xem khung tĩnh tại các mốc nhấn mạnh (vài giây trước/sau mỗi điểm).
3. `python3 tools/lint_spec.py spec_ch2_focus.json --root res` → 0 ERR.
4. Chỉ khi thấy hình rung/đứng thì chạy `python3 tools/analyze_video.py ch2.mp4 --out qa/`.

### 3.8 Bàn giao (3–4 dòng, không recap từng bước)
- `ch2.mp4` + `spec_ch2_focus.json` + `focus_ch2.json`.
- Còn thiếu gì (lớp phủ nào chưa làm, chữ, âm thanh, file `_TAM`, ảnh bị phóng).
- Chương này đang ở trạng thái **chờ anh duyệt**. Có lỗi mới thì thêm một dòng vào `LESSONS.md`.

---

## 4. Những điều đã gây lỗi (đọc để khỏi lặp lại)

### 4.1 Lỗi kỹ thuật đã gặp khi dựng Ch2
| Lỗi | Nguyên nhân | Cách xử |
|---|---|---|
| `KeyError: 'colors'` | engine bắt buộc có `colors` và `fonts` trong spec | `mapping_to_spec.py` đã tự thêm; nhớ chép `fonts/` vào `res/` |
| `lint_spec.py` sập `IndexError` | spec chưa có phần tử nào | đã sửa (có trên `main`) |
| Render bị cắt giữa chừng (ví dụ ở khung 2200/3053) | lệnh chạy nổi giới hạn ~10 phút | chạy nền, chờ xong |
| Lint báo "TRỐNG SỰ KIỆN" 5 chỗ | đoạn 9–10s không có gì đổi trên màn hình | đúng với spec chưa có lớp phủ; hết sau khi thêm điểm nhấn, hoặc dùng `--max-gap 12` |
| Không tải được ảnh từ Drive | mạng sandbox chặn | xin anh gửi thẳng vào chat |

### 4.2 Giới hạn hiện tại (nói thẳng với anh, đừng giấu)
- Ảnh Ch2 gốc 1672×941, không phải 2560×1440. Bản **1920×1080 chất lượng cao cần ảnh nguồn lớn hơn**.
- `mapping_to_spec.py` mới thử chuyển đổi trên Ch2, chưa render hết cho các chương khác.
- Lớp phủ (mũi tên, nhãn, nét đứt, ảnh L01) đã có công cụ bật (`apply_overlays.py`, mới thử trên dữ liệu giả, chưa trên bản dựng thật): cần anh đưa ảnh L01 thật; chưa có âm thanh ngoài voice.
- Hook, Ch1, Ch3–Ch9, Ending chưa dựng. Mỗi chương một `focus.json` riêng.

### 4.3 Phản hồi của anh trên các bản Ch2 (để biết "đạt" là gì)
| Bản | Có gì | Phản hồi |
|---|---|---|
| v1 | camera suy từ mapping, không hiệu ứng | "đáng lẽ phải nhấn mạnh bằng cách zoom vào động tác được nói đến" |
| v2 | spotlight 22 điểm, tối nền | "lạm dụng quá… trả lời trước khi làm" |
| v3 | 7 điểm, mỗi điểm một kiểu, không tối nền | "ok ổn" |

---

## 5. Luật cứng (rút từ `QUY-TRINH.md`; file đó thắng nếu mâu thuẫn)
1. Không tự duyệt thay anh. Không làm dòng CHỜ. Chương chưa duyệt thì chưa sang chương sau.
2. Ảnh không đủ 2560×1440 thì **báo thẳng**.
3. Style dựng của hai chương liền nhau phải khác nhau.
4. Video luôn full khung 16:9, không dải đen.
5. Có lỗi mới thì ghi **một dòng** vào `LESSONS.md`; có âm thanh mới thì ghi vào `SOUND-LIBRARY.md`.

Thêm cho người dựng: **cứ ≤ 3,5s phải có một sự kiện hình mới** (trừ cảnh `hold` hoặc chương `calm`); camera không bao giờ đứng yên và không giật; dissolve nằm trọn trong khoảng lặng của giọng đọc. Chi tiết: `PLAYBOOK.md`.

---

## 6. Đọc gì khi nào (đừng đọc hết)
| Việc | Mở file |
|---|---|
| Quy trình tổng, ai làm gì | `QUY-TRINH.md` |
| Chọn style dựng | `STYLES.md` (mục B) |
| Tham số từng hiệu ứng, preset | `EFFECTS.md` |
| Nguyên tắc dựng, bảng lỗi → sửa | `PLAYBOOK.md` |
| Mệnh đề lời đọc → hiệu ứng | `EDITORIAL-PATTERNS.md`, `python3 tools/word_times.py res/vo/wordts.json --auto` |
| Ví dụ dựng thật một chương | `NHAT-KY-DUNG-CH2.md`, `examples/CH2_spec_approved_v3.json`, `examples/focus/CH2_focus.json` |
| Máy Windows, không có AI | `HUONG-DAN-WINDOWS.md` |
| Kiểm nguyên liệu | `QC-ASSETS.md` |

(Không cần đọc `META-PROMPT-VISUAL.md` và `VISUAL-IDEA-GUIDE.md` nếu bạn chỉ dựng: đó là việc của Muse khi sinh prompt ảnh.)

---

## 7. Mẫu tin nhắn anh gửi để khởi động một Claude mới

> Đọc repo `hamyan19/-muse-overlay-kit`, nhánh `<tên nhánh>`, file `HUONG-DAN-CLAUDE-MOI.md`. Bạn là người dựng.
> Chương: `<Ch2>`. Style dựng: `<storybook>` (chương trước dùng `<…>`). Độ phân giải: `<1280×720 xem nhanh / 1920×1080>`.
> Đính kèm: voice `<file>`, `wordts.json`, `asset_plan.xlsx`, zip ảnh `<CH2_S01…S12>`.
> Làm tới bước `<bản xem nhanh có điểm nhấn>`; hỏi tôi danh sách điểm nhấn trước khi làm. Chưa có lớp phủ/chữ/âm thanh thì cứ để trống.

Nếu tin nhắn thiếu mục nào trong phần 2, hỏi đúng mục đó rồi dừng chờ.

---

## 8. Mặc định tạm khi An chưa chốt (đừng dừng chờ, dựng rồi ghi rõ "mặc định tạm" trong báo cáo)

| Việc | Mặc định |
|---|---|
| Style dựng | Khác chương liền trước (Ch2 = `storybook` → Ch3 `documentary`, Ch4 lại `storybook`…) |
| Độ phân giải | Bản thử 1280×720; bản chính thức 1920×1080 khi An yêu cầu |
| Số tự đếm (ticker) | Không dùng (An muốn ít hiệu ứng) |
| Nhạc nền | Không có |
| Cột DUYỆT | Vẫn CHỜ; dựng bản thử với `--include-pending`, không ghi OK thay An |
| Ảnh 1672×941 | Phóng Lanczos lên 2560×1440 và báo An |

Voice, ảnh, script, bảng mapping An tự đưa trong chat; repo công khai không chứa chúng. Chỉ hỏi An khi **thiếu ảnh** hoặc ảnh sai tên.
