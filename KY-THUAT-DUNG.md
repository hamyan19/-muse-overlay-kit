# KỸ THUẬT DỰNG — tách cụm ý, kỹ thuật mới & cũ, tiết kiệm & tăng tốc

> Trạng thái 26/10: **đang thử**, An chưa chốt. Video thử: `examples/demo_cum_y_2_ky_thuat.json` (cần ảnh `stills/hut.png` 16:9 của An).
> Chốt xong thì chuyển các luật sang `QUYET-DINH.md`.

---

## 1. TÁCH CỤM Ý (một ảnh gốc kể nhiều ý)

**Ý tưởng:** trước đây **1 shot = 1 ảnh**. Giờ **1 cụm ý = 1 ảnh gốc rộng**, mỗi shot trong cụm là **một vùng** của ảnh đó (zoom/lia/cắt cận/lộ dần ô).
Một chương ~15 shot còn khoảng **5–7 ảnh**.

### 1.1 Gom vào cùng cụm khi đủ cả 4 điều
1. **Cùng nơi** (cùng trại, cùng bãi, cùng lều).
2. **Cùng lúc** (không nhảy ngày/đêm, mùa).
3. **Cùng nhân vật / đồ vật** đã có mặt trong khung rộng.
4. **Ý nối tiếp nhau** trong lời đọc (liệt kê, mô tả từng phần, các bước của một việc).

### 1.2 Tách cụm mới khi gặp một trong các điều
- Đổi bối cảnh, thời gian, hoặc nhân vật mới chưa có trong ảnh.
- Cần cận **sâu hơn 2×** (chi tiết nhỏ hơn ~1/5 bề ngang) → tạo **ảnh cận riêng**, chuyển bằng cắt cận.
- Cụm đã **quá 40 giây** hoặc **quá 6 shot** (mắt bắt đầu chán bối cảnh dù camera vẫn chạy).
- Cảnh hiện đại, sơ đồ, bản đồ, nhịp "im lặng" → vẫn **1 shot = 1 ảnh**.

### 1.3 Cỡ cụm
| Loại đoạn lời | Số shot/cụm | Kỹ thuật hợp |
|---|---|---|
| Mô tả một nơi/vật gồm nhiều phần | 4–6 | Zoom từng vùng |
| Liệt kê 3–4 việc / 3–4 người làm việc khác nhau | 3–4 | Lộ dần ô (3 cột / 2×2) |
| Kể một hành động liên tục | 2–3 | Zoom + cắt cận |
| Câu then chốt, cảm xúc | 1 (đứng riêng) | Ảnh riêng, camera chậm |

### 1.4 Bảng mapping thêm 3 cột (sheet SHOTS)
| Cột | Ý nghĩa | Ví dụ |
|---|---|---|
| **CỤM** | Mã cụm; các shot cùng mã dùng chung 1 ảnh gốc | `CH3-M02` |
| **VÙNG** | Phần ảnh gốc shot này kể (lời + vị trí; toạ độ điền lúc dựng) | "người phụ nữ kéo da — trái" |
| **CHUYỂN TRONG CỤM** | Từ vùng trước sang vùng này | zoom vào / lia / cắt cận / mở ô 2 / lùi toàn cảnh |
Cột TÊN FILE ĐÍCH: mọi shot trong cụm cùng một tên ảnh gốc (`CH3_M02.png`).

### 1.5 Prompt ảnh gốc của cụm (khác prompt shot lẻ)
- **Một prompt cho cả cụm**, liệt kê đủ các vùng và vị trí: *trái / giữa / phải, trên / dưới*.
- Mỗi chi tiết sẽ zoom tới **chiếm ≥ 1/5 bề ngang**, các chi tiết **không chồng lên nhau**, có khoảng trống giữa chúng.
- Nếu cụm dùng **lộ dần ô**: bố cục chia sẵn 3 cột (hoặc 2×2), **mỗi ô một ý trọn vẹn**, đường ranh giữa các ô rơi vào chỗ trống (trời, đất), không cắt ngang người.
- Ảnh **16:9, độ phân giải cao nhất có thể → upscale lên 3840×2160** (mục 3.3).

### 1.6 Ví dụ (ảnh trại da + xương của An)
| Shot | CỤM | VÙNG | Chuyển |
|---|---|---|---|
| S04 | M02 | toàn cảnh trại | mở, lùi chậm |
| S05 | M02 | người phụ nữ kéo da (trái) | zoom 2× |
| S06 | M02 | chân xương lòi dưới da | lia + khoanh tròn |
| S07 | M02 | chỗ hai tấm da chồng nhau (giữa trên) | lia lên |
| S08 | M02 | vòng đá bếp lửa | mũi tên |
| S09 | M02 | người đàn ông ôm củi (phải) | cắt cận |

---

## 2. KỸ THUẬT DỰNG — cũ và mới

### 2.1 Kỹ thuật đã duyệt (Ch2 v3, "ok ổn")
| Kỹ thuật | Engine / công cụ | Khi dùng |
|---|---|---|
| Camera Ken Burns (đẩy / lùi / lia) | `scenes[].camera` | Mọi cảnh, không bao giờ đứng yên |
| Zoom vào chi tiết (không tối nền) | `apply_focus.py` kind `zoom` (camera nhiều mốc `camera.keys`) | Lời nói tới một chi tiết |
| Cắt cận cảnh | `apply_focus.py` kind `cut` | Nhấn mạnh mạnh, đổi nhịp |
| Khoanh tròn vẽ tay | `apply_focus.py` kind `circle` (`marker`) | Chỉ một vật cụ thể |
| Mũi tên vẽ tay | `apply_focus.py` kind `arrow` (`marker`) | Hướng, dòng chảy, "cái này" |
| Dissolve trong khoảng lặng | `dissolve` riêng từng cảnh | Chuyển cảnh |
Luật: **5–7 điểm nhấn/chương, mỗi điểm một kiểu**, theo từ đang nói.

### 2.2 Bổ sung 26/10 (đã có trong engine, An đã yêu cầu)
| Kỹ thuật | Engine / công cụ | Rào |
|---|---|---|
| Tô sáng vật thể | `apply_focus.py` kind `spot` | ≤2/chương; dim ≤0.45; khung sau phủ ≥95/255; ảnh tối tự đổi sang khoanh |
| Lớp phủ OVERLAYS (mũi tên cam to, nhãn, nét đứt, ảnh L01, tuyết) | `apply_overlays.py` + `image_overlay` | L01 multiply chỉ phủ nét tối, phủ TB ≤10%; nền <80/255 không phủ; ≤2 lớp cùng lúc |

### 2.3 MỚI — đang thử (video `thu_2_ky_thuat.mp4`)
**A. Một ảnh, zoom từng vùng (cụm ý).** Camera đi qua 4–6 vùng của cùng ảnh gốc; xen khoanh / mũi tên / cắt cận cho từng ý; kết bằng lùi ra toàn cảnh.
```json
{"id":"M02","image":"stills/CH3_M02.png","start":40.0,
 "camera":{"keys":[{"t":40.0,"scale":1.0,"cx":1280,"cy":720},{"t":41.5,"scale":2.0,"cx":480,"cy":820},
                   {"t":45.0,"scale":2.0,"cx":480,"cy":820},{"t":46.5,"scale":1.7,"cx":820,"cy":960}], "ease":"smooth",
           "t0":40,"t1":60,"scale":[1,1],"cx":[1280,1280],"cy":[720,720]}}
```
Mỗi cặp mốc = "tới vùng" (mất 1–1,5s) rồi "giữ" (đúng lúc lời nói về vùng đó). Toạ độ theo ảnh nguồn 2560×1440 (ảnh 4K vẫn dùng toạ độ này).

**B. Lộ dần từng ô (`panel_reveal`).** Màn hình chia 3 cột / 4 cột / 3 hàng / 2×2 (hoặc tự đặt ô). Mỗi ý mở một ô; ô cuối mở xong thì nét chia tan, thấy hình hoàn chỉnh.
```json
{"type":"panel_reveal","scene":"M03","layout":"3col","reveal":[62.6,66.4,70.2],"t_in":62,"t_out":73.5,
 "order":[0,1,2], "ghost":0.12, "fade":0.5, "line":6}
```
- Ô chưa mở phủ **giấy sáng** (`cover`, mặc định kem `[244,236,220]`), `ghost` cho thấy lờ mờ hình dưới → **không bao giờ tối**.
- `reveal` = giây của từ bắt đầu ý đó (từ `wordts.json`). Mỗi ô nên mở **≥3s** trước ô sau.
- `order` đổi thứ tự mở (ví dụ phải → trái). `panels` tự đặt ô khi bố cục không chia đều.

**C. Ảnh gốc lớn giữ nguyên độ nét.** Engine giữ ảnh 4K/5K; khi zoom sâu lấy thẳng điểm ảnh từ ảnh gốc (đo: zoom 2,5× ở 1080p nét hơn ~12 lần so với ép về 2560). Spec, toạ độ, công cụ không đổi.

### 2.4 Chọn kỹ thuật nào
| Đoạn lời | Kỹ thuật |
|---|---|
| "Ngôi nhà gồm… khung… da phủ… bếp…" (mô tả các phần) | A — zoom từng vùng |
| "Người thì cắt, người mang, người canh" (liệt kê song song) | B — lộ dần 3 ô |
| "Bốn việc phải làm trước mùa đông…" | B — 2×2 |
| Một chi tiết then chốt | zoom / cắt cận / khoanh (2.1) |
| Một vật quan trọng giữa cảnh rộng | spot (≤2/chương) |
Cả chương vẫn giữ luật **ít hiệu ứng**: mỗi cụm 1 kỹ thuật chính; tổng điểm nhấn 5–7.

---

## 3. TIẾT KIỆM & TĂNG TỐC DỰNG

### 3.1 Tiết kiệm token (Claude dựng)
| Cách | Làm gì | Lợi |
|---|---|---|
| Skill **dung-chuong-video** + `QUYET-DINH.md` | Claude chỉ đọc 2 file thay vì cả repo (~15 file) | Bớt phần lớn token đầu phiên |
| **Tấm ghép có lưới** `contact.jpg` | Mọi ảnh của chương trong 1 tấm, lưới 320px, số toạ độ | Xem 1 ảnh thay vì 12–15 |
| **Tấm khung kiểm** `check.jpg` | Khung đúng lúc từng điểm nhấn/lớp phủ trong 1 tấm | Xem 1 ảnh thay vì 8–10 |
| `build_chapter.py` in rất ít dòng | Chi tiết ghi vào `build.log`, chỉ mở khi lỗi | Không đổ log vào hội thoại |
| Lọc wordts bằng lệnh | Tìm vài từ khoá thay vì in cả file | Không in 400 từ |
| Cụm ý | Ít ảnh hơn → ít ảnh phải xem | 15 → 5–7 ảnh/chương |

### 3.2 Tăng tốc
| Cách | Lợi |
|---|---|
| `build_chapter.py plan → check → render` | 3 lệnh thay 6–7; chỉ dừng 2 lần để nhìn |
| `render --quick` (1280×720 @15fps) | ~6 phút / 100s video (trước 10–13 phút); bản 1080p @30 chỉ khi An duyệt |
| Render chạy nền | Không bị cắt ở ~10 phút |
| Khung kiểm trước render | Sai toạ độ phát hiện trong ~20s, không phải render lại cả chương |
| `--jobs` = số nhân CPU | Render song song |

### 3.3 Ảnh chất lượng cao (điều kiện để dùng cụm ý)
| Mức zoom (xuất 1080p) | Ảnh gốc cần |
|---|---|
| ≤1,33× | 2560×1440 |
| 2× | **3840×2160 (4K)** |
| 3× | 5760×3240 — nên tạo ảnh cận riêng |
1. Tạo ảnh ở mức lớn nhất công cụ cho phép, 16:9.
2. Upscale ×2–×4 lên 4K: **Upscayl** (app miễn phí, mô hình *digital art / anime*) hoặc **Real-ESRGAN** (dòng lệnh). Tránh upscale "sáng tạo" (Magnific, Krea) — vẽ thêm chi tiết, lệch style.
3. Kiểm nét bằng `tools/qc_assets.py`.
4. Đặt ảnh 4K vào thư mục ảnh; `build_chapter plan` giữ nguyên ảnh lớn, chỉ phóng ảnh nhỏ (và báo).

### 3.4 Công cụ (26/10, nhánh `muse/cum-y-ky-thuat-moi`)
**Cột CỤM trong bảng mapping**
```bash
python3 tools/add_cluster_cols.py CH3_asset_plan.xlsx --set "CH3-M01:S04-S07" "CH3-M02:S10-S12:ô"   # bảng cũ: thêm 3 cột + gán cụm nhanh
```
- `plan_assets.py` tạo bảng mới đã có sẵn 3 cột (Muse điền).
- `mapping_to_spec.py` đọc 3 cột: shot cùng CỤM → cùng ảnh gốc `<CỤM>.png` (vd `CH3_M01.png`), nối liền không dissolve,
  camera đi từ vùng trước sang vùng này (~1,3s) rồi giữ; CHUYỂN có "cắt" = cắt thẳng; có "ô" = `panel_reveal` (3 shot → 3 cột, 4 → 2×2).
- Toạ độ vùng: `work/chX/vung.json` (build_chapter tự tạo khung) hoặc số trong cột VÙNG (`"người kéo da 480,820 x2"`). Thiếu toạ độ → toàn cảnh + cảnh báo.
- `build_chapter.py`: tấm ghép `contact.jpg` hiện **mỗi ảnh gốc 1 lần** (nhãn liệt kê các shot của cụm); `check` tự dựng lại spec khi có `vung.json`.

**Tự upscale (`tools/upscale.py`, `build_chapter.py plan --upscale`)**
- Ảnh nhỏ hơn 4K → 3840×2160 bằng mô hình FSRCNN ×2 (OpenCV, CPU, ~3s/ảnh; cả chương Ch2 14 ảnh ~1,5 phút). Ảnh đã đủ lớn giữ nguyên.
- Đo trên ảnh Ch2: độ nét 57 so với phóng thường 33. Khá hơn rõ, **chưa bằng Real-ESRGAN**. `--model edsr` sắc hơn chút nhưng >10 phút/ảnh trên CPU 2 nhân.
- Cần `pip install opencv-contrib-python-headless`; mô hình tự tải lần đầu (GitHub, ~40 KB).
- Muốn đẹp nhất: An chạy **Upscayl** trên máy (Real-ESRGAN, mô hình digital art/anime) rồi gửi ảnh 4K — `plan` giữ nguyên ảnh lớn.

### 3.5 Còn chưa làm
- Metaprompt: một prompt cho mỗi cụm (mục 1.5) — An để sau.
