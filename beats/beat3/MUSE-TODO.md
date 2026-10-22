# MUSE-TODO (từ asset_plan.xlsx)

Tổng: OK 31 · SỬA 0 · BỎ 0 · CHƯA DUYỆT 0

## LÀM NGAY (đã duyệt OK)
- **B3-S01A** (SHOTS, 0.0–5.4s) → `stills/B3_S01A.png`
- **B3-S01B** (SHOTS, 5.4–10.7s) → `stills/B3_S01B.png`
- **B3-S02A** (SHOTS, 10.2–16.4s) → `stills/B3_S02A.png`
- **B3-S02B** (SHOTS, 16.4–22.5s) → `stills/B3_S02B.png`
- **B3-S03A** (SHOTS, 22.0–28.2s) → `stills/B3_S03A.png`
- **B3-S03B** (SHOTS, 28.2–34.3s) → `stills/B3_S03B.png`
- **B3-S04A** (SHOTS, 33.8–40.6s) → `stills/B3_S04A.png`
- **B3-S04B** (SHOTS, 40.6–47.3s) → `stills/B3_S04B.png`
- **B3-S05A** (SHOTS, 46.8–53.6s) → `stills/B3_S05A.png`
- **B3-S05B** (SHOTS, 53.6–60.5s) → `stills/B3_S05B.png`
- **B3-S06A** (SHOTS, 60.0–65.4s) → `stills/B3_S06A.png`
- **B3-S06B** (SHOTS, 65.4–70.9s) → `stills/B3_S06B.png`
- **B3-EV001** (OVERLAYS, 1.0): strike_cards
- **B3-EV002** (OVERLAYS, 2.8): lower_third
- **B3-EV003** (OVERLAYS, 11.2): dim + label
- **B3-EV004** (OVERLAYS, 14.8): highlight_box
- **B3-EV005** (OVERLAYS, 21.1): badge_pop
- **B3-EV006** (OVERLAYS, 24.5): typed_card
- **B3-EV007** (OVERLAYS, 38.4): label
- **B3-EV008** (OVERLAYS, 43.0): label
- **B3-EV009** (OVERLAYS, 50.3): strike_cards
- **B3-EV010** (OVERLAYS, 55.0): spotlight + label
- **B3-EV011** (OVERLAYS, 61.2): strike_cards
- **B3-EV012** (OVERLAYS, 68.7): lower_third
- **B3-SFX01** (SFX, 0–71s) → `sfx/room_tone_footsteps_nhe.wav`
- **B3-SFX02** (SFX, 0.0–10.7s; 33.8–47.3s) → `sfx/rain_heavy.wav`
- **B3-SFX03** (SFX, 10.2–22.5s) → `sfx/low_drone.wav`
- **B3-SFX04** (SFX, 22.0–71s) → `sfx/forest_ambience.wav`
- **B3-SFX05** (SFX, 43.0–58s) → `sfx/plane_distant_overhead.wav`
- **B3-MUS-01** (SFX, 0–71s) → `sfx/music_bed.wav`
- **B3-ACC-01** (SFX, 1.0s, 11.2s, 21.1s, 50.3s, 61.2s) → `sfx/accent_hit.wav`

## Bước tiếp theo
1. Sinh/tìm nguyên liệu cho OK + SỬA (prompt cuối do Muse viết, theo tên file đích).
2. `python3 tools/check_assets.py plan/approved_manifest.json --root res --out plan/` → asset_review.xlsx để anh duyệt ảnh thật.
3. Sau khi anh duyệt ảnh: viết spec → lint → render → analyze.