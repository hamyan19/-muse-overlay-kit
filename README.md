# Muse Overlay Kit — dựng video "ảnh tĩnh + edit chồng lớp" mượt như phim

Bộ công cụ + quy trình để Muse và người dựng làm video documentary từ **ảnh tĩnh + giọng đọc**,
với camera mượt, chuyển cảnh trong khoảng lặng, và lớp đồ hoạ chồng theo đúng nhịp lời đọc.

## BẮT ĐẦU Ở ĐÂY
- **Claude/AI được giao DỰNG một chương:** đọc `QUYET-DINH.md` (mọi thứ đã chốt) → cài phần mềm ở mục **Cài đặt** dưới đây → chạy `tools/build_chapter.py` (mục **Dựng một chương**). Chỉ đọc `HUONG-DAN-CLAUDE-MOI.md` khi gặp lỗi lạ.
- **Muse / người lập kế hoạch:** `QUY-TRINH.md` — **Script → Voice → Mapping câu theo voice → Visual plan → Duyệt style → Nguyên liệu → Dựng**. Anh duyệt 2 lần: ở bước Duyệt style và khi xem video chương.

> **AI vào repo:** tải về và xem 3 ảnh mẫu style trong `styles/ice-age-stick-figure/ref-approved/` trước khi làm hình hoặc viết prompt (chi tiết trong `STYLE.md` cùng thư mục).
> **Repo công khai:** không chứa voice, ảnh, script, bảng mapping của dự án. An gửi các file đó trong chat.

## Cài đặt (Claude cài trước khi dựng)

| Phần mềm | Bắt buộc? | Dùng cho | Kiểm đã có chưa |
|---|---|---|---|
| **Python 3.10+** | Có | Chạy mọi công cụ | `python3 --version` |
| **ffmpeg + ffprobe** | Có | Ghép video, trộn tiếng, đo độ dài voice, đổi mp3 → wav | `ffmpeg -version`, `ffprobe -version` |
| `numpy` | Có | Tính toán khung hình | (pip, xem lệnh dưới) |
| `opencv-python-headless` (`cv2`) | Có | Đọc/ghi ảnh, camera, đo độ sáng, lint | |
| `pillow` (`PIL`) | Có | Vẽ chữ, mũi tên, lớp phủ, tấm ghép | |
| `matplotlib` | Có | Biểu đồ trong engine và `analyze_video.py` | |
| `openpyxl` | Có | Đọc/ghi bảng `asset_plan.xlsx` | |
| `pocketsphinx` | Khi phải tự tạo `wordts.json` | `tools/align.py` (căn mốc từng từ theo script) | `python3 -c "import pocketsphinx"` |
| `tesseract` | Không | OCR chữ/logo trong `qc_assets.py`; không có thì kiểm bằng mắt | `tesseract --version` |
| Font | Có sẵn trong `fonts/` | DejaVu, Poppins, Lora — không cần cài | |

Không cần: Whisper, GPU, nhạc nền, tài khoản Drive (Claude cloud không tải được Drive; An gửi file vào chat).

**Linux / Claude cloud (Ubuntu):**
```bash
sudo apt-get install -y ffmpeg            # Claude cloud thường có sẵn; thiếu thì cài
pip install -r requirements.txt --break-system-packages
pip install pocketsphinx --break-system-packages          # chỉ khi An không đưa wordts.json
```
**macOS:** `brew install ffmpeg` rồi `pip3 install -r requirements.txt` (+ `pip3 install pocketsphinx` nếu cần).
**Windows:** xem `HUONG-DAN-WINDOWS.md`.

**Kiểm cài đặt (1 lệnh, phải in "OK"):**
```bash
python3 -c "import numpy, cv2, PIL, matplotlib, openpyxl; print('OK')" && ffmpeg -version | head -1 && ffprobe -version | head -1
```
Phiên bản đã chạy được (26/10): Python 3.13, ffmpeg 6.1, numpy 2.5, opencv 5.0, pillow 12.3, matplotlib 3.11, openpyxl 3.1, pocketsphinx 5.1.

## Dựng một chương (3 lệnh, chỉ dừng 2 lần để nhìn)
Cần An gửi: `chX.mp3` (voice), `CHX_asset_plan.xlsx` (bảng mapping), ảnh `CHX_S01.png…` (tên theo ID shot), và `wordts.json` hoặc script `chX.txt`.
```bash
git clone https://github.com/hamyan19/-muse-overlay-kit && cd ./-muse-overlay-kit     # nhánh main
# (chỉ khi chưa có wordts.json) tạo mốc từng từ theo script:
ffmpeg -i chX.mp3 -ar 16000 -ac 1 chX16.wav && python3 tools/align.py chX16.wav chX.txt wordts.json
python3 tools/check_wordts.py wordts.json CHX_asset_plan.xlsx --voice chX.mp3

python3 tools/build_chapter.py plan   --ch X --xlsx CHX_asset_plan.xlsx --vo chX.mp3 --stills anh_chX/ --preset documentary
#   → xem 1 ảnh work/chX/contact.jpg (mọi cảnh, lưới 320px, toạ độ nguồn 2560×1440)
#   → điền work/chX/focus.json (5–7 điểm nhấn, mỗi điểm một kiểu, giây lấy từ wordts) + work/chX/pos.json (lớp phủ)
python3 tools/build_chapter.py check  --ch X       # → xem 1 ảnh work/chX/check.jpg; lệch thì sửa json, chạy lại
python3 tools/build_chapter.py render --ch X --quick   # CHẠY NỀN (~6 phút / 100s video); 1280×720 @15fps để An duyệt
```
Bản chính thức 1920×1080 @30fps: bỏ `--quick` khi An yêu cầu (~2 lần lâu hơn). Lỗi: xem `work/chX/build.log`.
Rào sáng có sẵn: lớp phủ và tô sáng vật thể không được làm khung tối mò (xem `QUYET-DINH.md`).

## Tài liệu (mở ở đúng bước)
| File | Dùng ở bước | Việc |
|---|---|---|
| `HUONG-DAN-CLAUDE-MOI.md` | 7 | **Claude mới vào dựng video: đọc file này trước.** Cài đặt, cần được cung cấp gì, từng lệnh từ gói nguyên liệu tới `mp4`, lỗi đã gặp, mẫu tin nhắn khởi động |
| `QUYET-DINH.md` | — | **Mọi quyết định đã chốt** (style, độ phân giải, điểm nhấn, lớp phủ…). Đọc trước khi hỏi |
| `KY-THUAT-DUNG.md` | 3–7 | **Tách cụm ý** (một ảnh kể nhiều ý), kỹ thuật dựng cũ + mới (zoom từng vùng, lộ dần ô, ảnh 4K), cách tiết kiệm token và tăng tốc. Đang thử |
| `QUY-TRINH.md` | tất cả | **Quy trình duy nhất**: 7 bước, ai làm gì, 5 luật cứng |
| `SCRIPT-NOTES.md` | 1, 4 | Ghi chú chương (loại, âm thanh) + visual plan theo mapping + chống lặp |
| `STYLES.md` | 5 | Menu style hình (cả video) và style dựng (theo chương) |
| `CHARACTER-SHEET.md` | 5 (chương đầu) | Khóa nhân vật, đạo cụ, bối cảnh cho cả video |
| `QC-ASSETS.md` | 6 | Một lần kiểm nguyên liệu: 1 lệnh máy + 5 mục mắt + 4 điều gói giao |
| `SOUND-LIBRARY.md` | 6 | Thư viện âm thanh dùng lại |
| `PLAYBOOK.md` | 7 | Nguyên tắc dựng, thứ tự dựng, bảng lỗi → cách sửa |
| `EFFECTS.md` | 7 | Tham số từng hiệu ứng, preset, lớp chồng |
| `EDITORIAL-PATTERNS.md` | 7 | Ngữ pháp biên tập: mệnh đề lời đọc → sự kiện hình; brief video |
| `VISUAL-IDEA-GUIDE.md` | 4–6 | Cách chọn ý tưởng hình cho từng shot và cách QC (máy làm gì, mắt làm gì) |
| `META-PROMPT-VISUAL.md` | 5 | **Metaprompt mới nhất (25/10)**: AI vào repo mà chưa được giao prompt đầy đủ thì đọc file này và sinh prompt từ bảng mapping |
| `NHAT-KY-DUNG-CH2.md` | 7 | Nhật ký dựng Ch2 từng bước (lệnh, lỗi, cách sửa, nhấn mạnh theo lời) — Muse đọc để học quy trình dựng |
| `LESSONS.md` | đầu dự án | Sổ bài học (nguyên liệu + dựng), thêm một dòng khi có lỗi mới |
| `HUONG-DAN-WINDOWS.md` | — | Chạy kit trên máy Windows không cần AI |

## Công cụ
| Công cụ | Bước | Việc |
|---|---|---|
| `tools/plan_assets.py` | 3 | `wordts.json` → `asset_plan.xlsx`: mapping câu ↔ mốc thời gian, gợi ý hình, overlay, âm thanh; cột DUYỆT |
| `tools/build_chapter.py` | 7 | **Một lệnh cho cả chương**: `plan` (spec + tấm ghép có lưới) → `check` (điểm nhấn + lớp phủ + lint + tấm khung kiểm) → `render --quick` |
| `tools/apply_overlays.py` | 7 | Bật sheet OVERLAYS (mũi tên, nhãn, nét đứt, ảnh L01, tuyết) lên đúng vật thể từ `pos.json`, có rào độ sáng |
| `tools/mapping_to_spec.py` | 7 | `asset_plan.xlsx` → `spec.json` cho engine: ảnh, mốc bắt đầu, camera, giọng đọc (lớp phủ ghi vào `meta.overlays_todo`, bật bằng `apply_overlays.py`). Đã render Ch2 |
| `tools/apply_focus.py` | 7 | `focus.json` → điểm nhấn theo lời: zoom, cut cận, khoanh tròn, mũi tên, spot (có rào sáng) |
| `tools/align.py`, `tools/check_wordts.py` | 2, 7 | Tạo `wordts.json` từ voice + script (PocketSphinx); kiểm mốc từ khớp voice và bảng mapping |
| `tools/apply_approval.py` | 6 | Sheet đã duyệt → `MUSE-TODO.md` (danh sách nguyên liệu) + `approved_manifest.json` |
| `tools/qc_assets.py` | 6 | Kiểm máy nguyên liệu (thiếu file, kích thước, nét, mặt, chữ, video, LUFS...) |
| `tools/check_assets.py` | 6 (tuỳ chọn) | Sheet ảnh thu nhỏ khi anh muốn xem nguyên liệu trước khi dựng |
| `tools/word_times.py`, `tools/find_gaps.py` | 7 | Mốc cụm từ, gợi ý hiệu ứng theo mệnh đề; khoảng lặng để đặt điểm cắt |
| `tools/lint_spec.py` | 7 | Kiểm spec trước render (trống sự kiện, overlay tĩnh, thiếu t_out, chữ nhỏ...) |
| `overlay_engine.py` | 7 | Engine: `spec.json` → MP4 (hình + mix tiếng); 35 loại phần tử, 8 preset |
| `tools/analyze_video.py` | 7 (khi cần) | Chấm từng khung: jitter, khung chết, khoảng trống sự kiện |
| `tools/make_fog_loop.py`, `tools/make_kinetic.py` | 7 | Tạo clip sương chồng lớp, chữ kinetic |
| `examples/` | 7 | Spec mẫu (Hook Koepcke 28s), demo hiệu ứng, demo preset và lớp chồng |

## Chạy thử engine với spec mẫu
```bash
pip install -r requirements.txt
python3 overlay_engine.py examples/koepcke_hook.json --root ../res --frames 1.0,9.8,15.4   # xem vài khung
python3 overlay_engine.py examples/koepcke_hook.json --root ../res --out hook.mp4 --jobs 4  # render đầy đủ
```
`--root` = thư mục chứa `stills/ vo/ sfx/ fonts/` (đường dẫn trong spec tính từ đây).
Repo này chỉ chứa quy trình và công cụ; file riêng của từng dự án/chương để ở thư mục dự án.
