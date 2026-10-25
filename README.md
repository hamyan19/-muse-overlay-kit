# Muse Overlay Kit — dựng video "ảnh tĩnh + edit chồng lớp" mượt như phim

Bộ công cụ + quy trình để Muse và người dựng làm video documentary từ **ảnh tĩnh + giọng đọc**,
với camera mượt, chuyển cảnh trong khoảng lặng, và lớp đồ hoạ chồng theo đúng nhịp lời đọc.

## BẮT ĐẦU Ở ĐÂY → `QUY-TRINH.md`
**Script → Voice → Mapping câu theo voice → Visual plan → Duyệt style → Nguyên liệu → Dựng**
Anh duyệt 2 lần: ở bước Duyệt style (kế hoạch hình + style) và khi xem video chương.

> **AI vào repo:** tải về và xem 3 ảnh mẫu style trong `styles/ice-age-stick-figure/ref-approved/` trước khi làm hình hoặc viết prompt (chi tiết trong `STYLE.md` cùng thư mục).

## Tài liệu (mở ở đúng bước)
| File | Dùng ở bước | Việc |
|---|---|---|
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
| `HANDOFF-DUNG.md` | 7 | **Giao một chương cho Claude khác dựng**: lấy đồ ở đâu, câu hay hỏi đã trả lời sẵn, lệnh chạy, cách báo cáo |
| `NHAT-KY-DUNG-CH2.md` | 7 | Nhật ký dựng Ch2 từng bước (lệnh, lỗi, cách sửa, nhấn mạnh theo lời) — Muse đọc để học quy trình dựng |
| `LESSONS.md` | đầu dự án | Sổ bài học (nguyên liệu + dựng), thêm một dòng khi có lỗi mới |
| `HUONG-DAN-WINDOWS.md` | — | Chạy kit trên máy Windows không cần AI |

## Công cụ
| Công cụ | Bước | Việc |
|---|---|---|
| `tools/plan_assets.py` | 3 | `wordts.json` → `asset_plan.xlsx`: mapping câu ↔ mốc thời gian, gợi ý hình, overlay, âm thanh; cột DUYỆT |
| `tools/mapping_to_spec.py` | 7 | `asset_plan.xlsx` (dòng DUYỆT=OK) → `spec.json` cho engine: ảnh, mốc bắt đầu, camera, giọng đọc. Chưa gồm lớp phủ và âm thanh (ghi vào `meta.overlays_todo`). Mới thử chuyển đổi, chưa render |
| `tools/apply_approval.py` | 6 | Sheet đã duyệt → `MUSE-TODO.md` (danh sách nguyên liệu) + `approved_manifest.json` |
| `tools/qc_assets.py` | 6 | Kiểm máy nguyên liệu (thiếu file, kích thước, nét, mặt, chữ, video, LUFS...) |
| `tools/check_assets.py` | 6 (tuỳ chọn) | Sheet ảnh thu nhỏ khi anh muốn xem nguyên liệu trước khi dựng |
| `tools/word_times.py`, `tools/find_gaps.py` | 7 | Mốc cụm từ, gợi ý hiệu ứng theo mệnh đề; khoảng lặng để đặt điểm cắt |
| `tools/lint_spec.py` | 7 | Kiểm spec trước render (trống sự kiện, overlay tĩnh, thiếu t_out, chữ nhỏ...) |
| `overlay_engine.py` | 7 | Engine: `spec.json` → MP4 (hình + mix tiếng); 35 loại phần tử, 8 preset |
| `tools/analyze_video.py` | 7 (khi cần) | Chấm từng khung: jitter, khung chết, khoảng trống sự kiện |
| `tools/make_fog_loop.py`, `tools/make_kinetic.py` | 7 | Tạo clip sương chồng lớp, chữ kinetic |
| `examples/` | 7 | Spec mẫu (Hook Koepcke 28s), demo hiệu ứng, demo preset và lớp chồng |

## Chạy nhanh
```bash
pip install -r requirements.txt
python3 overlay_engine.py examples/koepcke_hook.json --root ../res --frames 1.0,9.8,15.4   # xem vài khung
python3 overlay_engine.py examples/koepcke_hook.json --root ../res --out hook.mp4 --jobs 4  # render đầy đủ
```
`--root` = thư mục chứa `stills/ vo/ sfx/ fonts/` (đường dẫn trong spec tính từ đây).
Repo này chỉ chứa quy trình và công cụ; file riêng của từng dự án/chương để ở thư mục dự án.
