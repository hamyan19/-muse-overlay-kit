# GỬI MUSE — LÀM NGUYÊN LIỆU BEAT 3 ("Alone in the Green Ocean")
Repo: https://github.com/hamyan19/-muse-overlay-kit (đọc MUSE-COMMANDS.md và PIPELINE.md trước)
Anh đã duyệt TOÀN BỘ 31 dòng (Cổng 1). Làm theo file asset_plan.xlsx đính kèm và MUSE-TODO.md:
1. Sinh 12 ảnh 2560x1440 đúng "TÊN FILE ĐÍCH" (stills/B3_S01A.png … B3_S06B.png), dùng prompt nháp trong sheet SHOTS làm gốc, tự viết prompt cuối.
   - NHÂN VẬT khoá y hệt mọi ảnh: gái 17 tuổi, tóc nâu buộc đuôi ngựa, VÁY NGẮN KHÔNG TAY màu kem nhạt ướt/bẩn, chỉ MỘT chiếc giày, không kính; không thấy rõ mặt; băng ghế 3 chỗ xanh lam hỏng.
   - Không chữ/logo, màu tự nhiên không ám vàng.
2. Tìm/tạo sfx: plane_distant_overhead.wav (máy bay cánh quạt rất xa), low_drone.wav, near_silence.wav (nếu cần); dùng lại từ thư viện kênh: room_tone_footsteps_nhe, rain_heavy, forest_ambience, music_bed, accent_hit.
3. Thu VO Beat 3 (Warm Pebble, chậm trầm, loudnorm -14 LUFS) + wordts.json, đặt vào vo/.
4. Chạy: python3 tools/check_assets.py plan/approved_manifest.json --root res --out plan/ → gửi asset_review.xlsx. DỪNG chờ anh duyệt ảnh.
5. Up cả thư mục (stills, vo, sfx, plan) lên Drive như Beat 2.
