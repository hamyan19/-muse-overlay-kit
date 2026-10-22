# QUY TRÌNH MỘT BEAT — 3 CỔNG DUYỆT (anh duyệt ở sheet, Muse không tự duyệt)

```
Kịch bản → VO (Warm Pebble) → wordts.json (Whisper)
      │
      ▼  LỆNH 1  plan_assets.py
 asset_plan.xlsx  ──── CỔNG 1: anh duyệt kế hoạch nguyên liệu (OK / SỬA / BỎ từng dòng)
      │
      ▼  LỆNH 2  apply_approval.py  → MUSE-TODO.md   (còn dòng ảnh CHỜ thì dừng, mã thoát 2)
 Muse sinh ảnh / tìm footage / tìm sfx cho dòng OK + SỬA (đúng tên file đích)
      │
      ▼  LỆNH 3  check_assets.py
 asset_review.xlsx (ảnh thu nhỏ + kiểm tự động) ── CỔNG 2: anh duyệt ảnh thật
      │
      ▼  word_times --auto → spec.json → lint_spec → render → analyze_video → LESSONS.md
 Video beat ──── CỔNG 3: anh duyệt video
```

## Lệnh
```bash
# LỆNH 1 — liệt kê nguyên liệu cần có từ lời đọc, xuất sheet cho anh duyệt
python3 tools/plan_assets.py res/vo/wordts.json --beat B2 --out plan/ \
        --fix "Kupka=Koepcke,Lancer=LANSA,Pucalpa=Pucallpa" --preset newsreel \
        --style-bible "painterly photorealistic, muted natural palette, soft cinematic light"
#   -> plan/asset_plan.xlsx (SHOTS, OVERLAYS, SFX, TONG_QUAN) + csv + asset_manifest.json
#   Gửi asset_plan.xlsx cho anh. DỪNG. Chờ anh trả lại file đã điền cột DUYỆT.

# LỆNH 2 — đọc sheet đã duyệt
python3 tools/apply_approval.py plan/asset_plan.xlsx --out plan/
#   -> plan/MUSE-TODO.md (OK / SỬA kèm ghi chú / BỎ / CHƯA DUYỆT) + approved_manifest.json
#   Mã thoát 2 = còn ảnh CHƯA DUYỆT: không được sinh ảnh cho các dòng đó.

# (Muse sinh ảnh, tìm footage, tìm sfx cho dòng OK + SỬA; ghi đúng "TÊN FILE ĐÍCH" vào res/)

# LỆNH 3 — kiểm nguyên liệu đã giao + sheet duyệt ảnh thật
python3 tools/check_assets.py plan/approved_manifest.json --root res --out plan/
#   -> plan/asset_review.xlsx (thu nhỏ + 2560x1440? + độ sáng + trùng nhau). Gửi anh duyệt. DỪNG.

# DỰNG (sau cổng 2)
python3 tools/word_times.py res/vo/wordts.json --auto      # gợi ý hiệu ứng theo mệnh đề
python3 tools/lint_spec.py spec.json --root res            # sửa hết ERR
python3 overlay_engine.py spec.json --root res --out beat.mp4 --jobs 2
python3 tools/analyze_video.py beat.mp4 --out qa/          # rồi ghi LESSONS.md
```

## Luật cứng
1. **Dòng CHỜ = chưa duyệt.** Không sinh/tìm/dựng cho dòng đó. Không tự đổi CHỜ thành OK.
2. **SỬA = ghi chú của anh thắng** đề xuất của sheet và prompt nháp.
3. **Prompt trong SHOTS chỉ là nháp**; Muse viết prompt cuối, giữ một "style bible" chung cho cả video để ảnh đồng nhất.
4. Ảnh phải 2560x1440 (16:9), không chữ/logo, không thấy rõ khuôn mặt. Footage/AI video 6–10s, dùng làm cảnh `video` hoặc lớp `video_overlay`.
5. Whisper nghe sai tên riêng → dùng `--fix` (và `replace` trong `captions`), đừng để sai chính tả lên màn hình.
6. Giao thiếu hoặc sai kích thước → `check_assets.py` báo; sửa rồi chạy lại trước khi báo anh.
