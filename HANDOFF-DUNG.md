# HANDOFF DỰNG — dành cho Claude được giao dựng một chương (đọc hết trước khi hỏi bất cứ gì)

Dự án: video "Surviving Winter in a House of Mammoth Bones" (11 phần: Hook, Ch1–Ch9, Ending). Bạn được giao dựng **một chương** từ ảnh + voice.
Mọi thứ cần để dựng nằm trong repo này + **gói dữ liệu** `dung-handoff.zip` (An gửi riêng vì chứa script chưa công bố, không để trong repo công khai).

## 1. Lấy đồ
```bash
git clone -b muse/huong-dan-claude-moi https://github.com/hamyan19/-muse-overlay-kit    # nhánh hướng dẫn + công cụ
cd -muse-overlay-kit && pip install -r requirements.txt     # cần ffmpeg trong PATH; xem HUONG-DAN-WINDOWS.md
```
Repo công khai nên **KHÔNG chứa** voice, ảnh, script. **An tự đưa cho bạn** (đính kèm trong chat): `chX.mp3` (voice), ảnh `CHx_Sxx.png`, script chương, và bảng `CHX_asset_plan.xlsx`. Có đủ 4 thứ này là dựng được; đừng đòi thêm.
**Mốc từng từ `wordts.json`** (`[bắt đầu, kết thúc, "từ"]`): nếu An chưa đưa thì **tự tạo**, không cần hỏi:
```bash
pip install pocketsphinx
ffmpeg -i chX.mp3 -ar 16000 -ac 1 chX16.wav
python3 tools/align.py chX16.wav chX.txt wordts.json     # chX.txt = script chương; căn theo script, không phải Whisper
python3 tools/check_wordts.py wordts.json CHX_asset_plan.xlsx --voice chX.mp3
```
Từ lạ (OOV) báo ra thì thêm vào dict `SUB` đầu `align.py` bằng từ phát âm gần giống.

## 2. KHÔNG hỏi lại những thứ này — đã có sẵn / đã chốt
| Bạn hay hỏi | Trả lời |
|---|---|
| "Gửi wordts.json" | Tự tạo bằng `tools/align.py` (mục 1). Định dạng `[bắt đầu, kết thúc, "từ"]`. Căn **theo script bằng PocketSphinx**, không phải Whisper; chữ trong file là chữ của script nên **không cần sửa tên riêng/số**. Chạy `python3 tools/check_wordts.py wordts.json CHX_asset_plan.xlsx --voice chX.mp3` để kiểm . |
| Có cần Whisper? | Không. Bản căn script đủ để canh điểm nhấn. (Whisper chỉ thêm khả năng phát hiện chỗ voice đọc khác script — không cần ở bước này.) |
| Bảng mapping / lời đọc | `CHX_asset_plan.xlsx` (An đưa), sheet SHOTS. Đã tính mốc 5–11s theo khoảng lặng; không tính lại. |
| Ảnh phải bao nhiêu | Đúng số dòng SHOTS (bỏ dòng CẢNH 0 = lớp phủ). Ảnh gốc có thể 1672×941 → phóng 2560×1440 và báo An. |
| Style dựng | **Mặc định tạm** (An chưa chốt): preset khác chương liền trước. Ch2 dùng `storybook` → Ch3 dùng `documentary`, Ch4 quay lại `storybook`… Dựng bản thử theo mặc định, ghi rõ trong báo cáo "preset X là mặc định tạm". Không dừng chờ. |
| Độ phân giải xuất | Bản thử: 1280×720. Bản chính thức: 1920×1080 khi An yêu cầu. |
| Số tự tăng/giảm (ticker) | Không dùng. An muốn **ít hiệu ứng**. |
| Nhạc nền | Không có nhạc (An chốt). |
| Duyệt | Cột DUYỆT vẫn CHỜ. Dựng bản thử với `--include-pending`; **không ghi OK thay An**. |

## 3. Quy trình (đủ chạy từ đầu đến cuối; log đầy đủ ở `NHAT-KY-DUNG-CH2.md`)
```bash
mkdir -p res/stills res/vo res/fonts && cp -r fonts/* res/fonts/ && cp chX.mp3 res/vo/
# ảnh An gửi → res/stills/CHX_Sxx.png (2560x1440)
python3 tools/mapping_to_spec.py CHX_asset_plan.xlsx --vo chX.mp3 --name-from-id \
    --include-pending --preset documentary --duration <độ dài voice> --calm --out spec.json
# chọn 5–7 điểm nhấn cho cả chương, mỗi điểm một kiểu, canh theo từ đang nói trong wordts → focus.json (mẫu: examples/focus/CH2_focus.json)
python3 tools/apply_focus.py spec.json focus.json --out spec_focus.json
python3 tools/lint_spec.py spec_focus.json --root res --max-gap 12
python3 overlay_engine.py spec_focus.json --root res --frames 12,24,36 --frames-dir chk   # KIỂM TOẠ ĐỘ TRƯỚC khi render
python3 overlay_engine.py spec_focus.json --root res --out chX.mp4 --jobs 8                # chạy nền, ~10–13 phút/chương ở 720p
```
Luật hiệu ứng (An đã duyệt ở Ch2): **5–7 điểm nhấn/chương, mỗi điểm một kiểu** — `zoom` (không tối nền), `cut` (cắt cận), `circle` (khoanh tay), `arrow` (mũi tên tay). Không tô sáng/tối nền hàng loạt. Điểm nhấn đi theo từ đang nói, không theo thứ tự bảng. Đọc toạ độ bằng lưới 320px rồi render khung kiểm.

## 4. Báo cáo khi xong (ngắn)
Số cảnh, độ dài, preset đã dùng (ghi "mặc định tạm"), 5–7 điểm nhấn (giây, kiểu, chi tiết), việc chưa làm (chữ, âm thanh, lớp L01 nét đứt nếu thiếu ảnh), và gửi file `.mp4`. Chỉ hỏi An khi **thiếu ảnh** hoặc ảnh sai tên.

## 5. Luật cứng (từ QUY-TRINH.md)
Không tự duyệt thay An · ảnh bám style đã chốt (3 ảnh mẫu trong `styles/ice-age-stick-figure/ref-approved/`) · hai chương liền nhau khác style dựng · video luôn full 16:9, không dải đen · có lỗi mới ghi một dòng vào `LESSONS.md`.
