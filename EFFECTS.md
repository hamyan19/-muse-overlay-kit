# Tham chiếu hiệu ứng (type trong `elements`)
Mọi phần tử có `t_in` (giây hiện) và tuỳ chọn `t_out` (giây bắt đầu mờ đi), `fade_in`, `fade_out`.
Toạ độ màn hình 1280x720. Toạ độ "src" = toạ độ trên ảnh nguồn 2560x1440 (bám theo camera).

| type | Dùng khi | Tham số chính |
|---|---|---|
| `typed_card` | Hồ sơ/ngày giờ gõ từng chữ (mở đầu, "FILE") | `box`, `lines[{text,pos,size,font,color,start,cps}]`, `cursor_until` |
| `badge_pop` | Con số/nhãn đập vào (3,000 m) | `text,pos,size,anchor,sub,sub_pos` |
| `gauge` | Thang đo rơi/leo (độ cao, nhiệt độ) | `x,y0,y1,max,ticks,drop[t0,t1],power` |
| `anchored_circle` | Khoanh một điểm trên ảnh, bám camera | `scene,src,r,draw[t0,t1],label{t_in,text}` |
| `counter_down` | Đếm lùi 92→1 kiểu "chỉ một người", số cuối nổ vàng + chớp | `run,hit,from,to,power,labels{count,end,sub}` |
| `ticker` | Số chạy bất kỳ (tiền, năm, mét) | `run,from,to,power,prefix,suffix,pos,size,label` |
| `label` | Tiêu đề nhỏ + gạch chân | `text,pos,size,underline[x0,x1,y]` |
| `strike_cards` | Gạch bỏ các đáp án ("không phải X, không phải Y") | `cards[{text,y,t_in,t_strike}]` |
| `question_card` | Thẻ dấu "?" nhấp nháy | `box,glyph,size,pulse_hz` |
| `day_ticker` | Đếm ngày DAY 1…11 | `run,from,to,x_start,step,y` |
| `timeline` | Trục thời gian vẽ dần + mốc bật theo lời | `x0,x1,y,draw,events[{t,pos,label,sub}]` |
| `spotlight` | Hạ sáng khung, chừa vòng sáng dẫn mắt (bám ảnh). **Rào sáng:** dim ≤0.45, sáng TB sau phủ ≥95/255, ảnh gốc <80 thì đừng dùng; ≤2 lần/chương (qua `apply_focus.py` kind `spot` tự canh) | `scene,src` hoặc `pos`, `r,dim,from_mult,soft` |
| `image_overlay` | Ảnh phủ (L01 nét đứt đồ hiện đại) đặt lên vật thể, hiện dần rồi tan; multiply chỉ phủ nét tối. **Rào sáng:** strength ≤0.85, độ phủ TB ≤10% (engine tự hạ) | `file,scene,at,width,blend,strength,max_cover` (dùng qua `tools/apply_overlays.py`) |
| `panel_reveal` | **Lộ dần từng ô**: ảnh chia 3–4 ô, mỗi ý mở một ô, hết ý là hình hoàn chỉnh; ô chưa mở phủ giấy sáng (không tối) | `scene, layout 3col/4col/3row/2x2 hoặc panels, reveal[t...], order, ghost, fade, line` |
| `highlight_box` | Khung góc mở ra quanh vật thể + nhãn | `scene,src_box,label,color,width` |
| `stamp` | Dấu đóng "RECONSTRUCTION/CLASSIFIED" đập xuống + rung (nền tối mờ cho dễ đọc) | `text,pos,size,angle,color,opacity,fill` |
| `lower_third` | Thanh tên/chú thích trượt vào | `title,sub,y` |
| `flash` | Chớp trắng nhấn twist/cú đập | `dur,alpha,color` |
| `redact` | Thanh đen quét che chữ (hồ sơ mật) | `boxes[[x0,y0,x1,y1]]` |
| `rain` | Mưa rơi thật, 3 lớp sâu (bão, đêm, cảnh u ám) | `density,alpha,angle,speed,length,seed` |
| `mist` | Sương/khói trôi ngang, 2 lớp thị sai | `opacity,speed,floor,gain,y_fade[y0,y1],color` |
| `dim` | Tối dần / sáng lại (nhịp im lặng, tập trung vào thẻ) | `alpha[a0,a1],t_in,t_out,t_end,fade_out` |
| `captions` | Phụ đề điện ảnh theo mệnh đề từ `wordts.json`, từ đã đọc sáng/chưa đọc mờ; `replace` sửa lỗi chính tả Whisper | `wordts,replace,font,size,y,karaoke,max_width` |
| `kinetic` | Từ khoá bật to đúng lúc được nói (`tools/make_kinetic.py` sinh danh sách) | `words[{text,t_in,t_out,pos,size,color}]` |

Cảnh có `"hold": true` = nhịp để hình tự nói (không phần tử mới, ≤9s) — `lint_spec.py` không báo trống sự kiện.

Camera (`scenes[].camera`): `t0,t1,scale[a,b],cx[a,b],cy[a,b],ease` với ease = `linear | smooth | pow:2.2`,
tuỳ chọn `shake{t0,t1,amp,hz}` (rung mượt tắt dần cho cú đập). Cảnh: `blur`, `brightness` để tạo nền mờ/tối từ chính ảnh.
Global: `dissolve`, `grain`, `vignette`, `warm`, `flicker`.

## PRESET PHONG CÁCH (`"preset": "..."` ở đầu spec; mọi khoá trong spec vẫn ghi đè được)
| preset | Cảm giác | Gồm | Hợp với |
|---|---|---|---|
| (mặc định) | Hồ sơ điều tra: tối, thẻ viền kem, vàng/đỏ | — | Documentary căng thẳng |
| `newsreel` | Phim/bản tin xưa | đen trắng ngả nâu, hạt thô, nhấp nháy, bụi + xước phim, full 16:9 (khung 4:3 chỉ khi tự thêm `pillarbox`), màu thẻ ngả giấy cũ | Hoài niệm, lịch sử, đời sống quá khứ (niche 55+) |
| `cinematic` | Điện ảnh tối giản | full khung 16:9 (không dải đen), ít hạt, màu tự nhiên; dùng `captions` font serif thay thẻ | Kể chuyện cảm xúc, ít chữ |
| `kinetic` | Chữ chạy theo lời | nền tối, `kinetic` chữ to bật theo từ | Số liệu, câu chốt, nhịp nhanh |
| `storybook` | Sách truyện | tông ấm, màu dịu (sat 0.92), đen nâng nhẹ, vân giấy | Ảnh minh hoạ hoạt hình, chương kể chậm, hồi ức gia đình |
| `memory` | Ảnh kỷ niệm / hoài niệm | màu bạc (sat 0.78), đen nâng (lift 16), ấm, hạt mịn, nhấp nháy rất nhẹ, **viền ảnh in màu kem** | Hồi ức, "ngày xưa", khán giả 55+, đoạn kết cảm động |
| `comic` | Truyện tranh | màu rực (sat 1.15), tương phản, **khung mực quanh ô hình**, vân giấy | Ảnh hoạt hình nét đậm, chương nhịp nhanh/vui, giải thích cơ chế |
| `documentary` | Tài liệu sạch | màu trung tính, gần như không hạt/vignette | Đoạn bản đồ, số liệu, thẻ tư liệu, mốc thời gian |

**Chọn style dựng (preset + lớp chồng + nhịp + âm) ở `STYLES.md`.** Hai chương liền nhau không dùng cùng style dựng.
Lưu ý: `pillarbox` (tắt mặc định, vì video phải full 16:9) cắt mất 2 bên (≈147px mỗi bên ở 720p) nên đặt thẻ trong vùng giữa (lower_third có tham số `x`). Font thêm: Lora (serif, `fonts/Lora-Variable.ttf#Bold`), Poppins. Dùng `"fonts": {"serif": "..."}`.
Ví dụ: `examples/styles/{newsreel,cinematic,kinetic}.json` (cùng một đoạn 14s của Beat 1 dựng ba kiểu); `examples/styles/preset_grid.jpg` (cùng một ảnh qua 8 preset).

## BỘ CHỒNG LỚP THEO PHONG CÁCH (style edit = cách CHỒNG LỚP, không phải màu)
Preset ở trên chỉ đổi màu/khung. **Phong cách dựng thật sự nằm ở loại lớp chồng.** 5 phần tử mới + 4 bộ phong cách:

| Phần tử | Là gì | Tham số chính |
|---|---|---|
| `photo_pin` | Ảnh in kiểu polaroid dán băng keo, thả xuống khung (ảnh khác hoặc crop cận từ ảnh nguồn) | `src`, `crop?[x0,y0,x1,y1 nguồn]`, `pos`, `w`, `angle`, `caption?`, `tape` |
| `marker` | Nét bút dạ vẽ tay tự hiện: `kind` circle / arrow / underline | `box` (circle) hoặc `from`,`to`; `color`, `width`, `draw`, `label?`, `scene?` (bám camera) |
| `clipping` | Mẩu báo cắt mép rách (`kind: news`) hoặc giấy note vàng (`kind: note`), thả xuống | `pos`, `w`, `headline` (xuống dòng bằng `\n`), `sub?`, `lines`, `angle`, `size` |
| `speech_box` | Ô lời dẫn truyện tranh, viền mực, có đuôi chỉ vào nhân vật | `pos`, `text`, `size`, `tail?[x,y]`, `fill` |
| `route` | Đường đi nét đứt tự vẽ trên bản đồ/ảnh, chấm mốc + nhãn | `points`, `labels?`, `draw`, `color`, `scene?` |

| Bộ phong cách | Lớp chồng dùng | Hợp với |
|---|---|---|
| **Sổ tay điều tra** | `marker` circle/arrow khoanh chi tiết, `clipping` news, `photo_pin` ảnh phụ, `stamp` | Bí ẩn, điều tra, "chuyện gì thật sự đã xảy ra" |
| **Album kỷ niệm** | `photo_pin` có caption ngày tháng, `clipping` note, `lower_third` tên người; preset `memory` | Hồi ức, gia đình, đoạn kết cảm động (55+) |
| **Truyện tranh** | `speech_box` lời dẫn, `badge_pop`, `strike_cards`, `marker` arrow; preset `comic` | Ảnh hoạt hình, nhịp nhanh, giải thích cơ chế |
| **Bản đồ / giải thích** | `route`, `marker` arrow + label, `ticker` số, `timeline`, `clipping` note quy tắc; preset `documentary` | Hành trình, địa lý, số liệu, "làm sao mà…" |

**Luật:** mỗi chương chọn MỘT bộ chính (có thể mượn 1 phần tử của bộ khác); hai chương liền nhau không dùng cùng bộ. Mỗi cảnh tối đa 2 lớp chồng cùng lúc + phụ đề.
Demo: `examples/demo_overlay_styles.json` + `examples/styles/overlay_styles_grid.jpg` (Beat 4 Koepcke: album, bản đồ, truyện tranh, note).

## BỘ SƠ ĐỒ & SỐ LIỆU (style dựng "Bản đồ / giải thích" — dùng thật ở Ch2 "The Wall Is a Jar")
Mọi phần tử có `scene` thì toạ độ là ảnh nguồn 2560x1440 và bám theo camera; không có `scene` thì là toạ độ màn hình 1280x720.

| type | Dùng khi | Tham số chính |
|---|---|---|
| `tag` | Thẻ chữ có nền tối (đọc được trên giấy sáng lẫn ảnh rậm) | `text, pos` hoặc `scene+src, size, color, font, sub?` |
| `marker` + `label_card` | Mũi tên tay chỉ vào chi tiết, nhãn ở đuôi mũi tên bám camera | `kind:"arrow", scene, from, to, label, label_src, label_card:true, label_first:true` |
| `dimension` | Đường kích thước kiểu bản vẽ, số đổi theo lời ("25" → "25–30 CM") | `scene, a, b, draw, texts[[t,"…"]], label_off` |
| `bars` | Thanh so sánh mọc ra theo lời | `box, title, max, items[{label,value,t,text,color}]` |
| `flow` | Dòng hạt chạy theo làn — **tốc độ là dữ liệu** (nhiệt qua gỗ chậm, qua gạch nhanh gấp 5) | `scene, lanes[[[x,y],[x,y]]], speed, spacing, r, color` |
| `linechart` | Biểu đồ đường mini tự vẽ (ghi "ILLUSTRATIVE" nếu không có số thật) | `box, run, title, xlabel[a,b], series[{label,color,pts}]` |
| `sprite` | Một mảnh PNG nền trong suốt di chuyển (nắp rơi xuống đóng bình, vật bay vào) | `file, scene, from, to, run, ease` |
| fx `squash` | Nén dọc một vùng ảnh về phía đáy (tường lún, vật bị ép) | `box, amount (vd 0.955), run[t0,t1] tính từ đầu cảnh` |

Mẹo: ảnh có chi tiết "treo lơ lửng" hoặc thừa thì tách ra làm `sprite` + xoá khỏi nền (vá bằng mảng giấy/nền cạnh đó) — biến điểm yếu thành chuyển động có nghĩa.

## CHUYỂN ĐỘNG BÊN TRONG ẢNH TĨNH ("nhìn như phim mà không cần cảnh quay")
Ba lớp kỹ thuật, dùng chồng lên nhau trên cùng một ảnh:

**1) `scenes[].fx` — biến dạng chính ảnh nguồn (toạ độ ảnh 2560x1440, bám camera).** Mỗi fx có thể có `t0/t1` (giây tuyệt đối).
| fx | Dùng cho | Tham số |
|---|---|---|
| `ripple` | Mặt nước gợn, phản chiếu lung linh (sông, hồ, vũng nước) | `box,amp,wavelength,speed,feather` |
| `sway` | Tán lá, cỏ, rèm, cờ đung đưa trong gió (gốc đứng yên, ngọn lay) | `box,amp,freq,spatial,feather` |
| `glow` | Quầng sáng: nắng, đèn, lửa, tia sét, ánh ma quái. `flicker` = chập chờn, `pulse_hz` = nhịp thở | `pos,r,color,strength,pulse,pulse_hz,flicker` |
| `parallax` | Thị sai 2.5D — máy quay như "đi xuyên" ảnh. `depth:"auto_ground"` (đáy gần, đỉnh xa) hoặc ảnh xám độ sâu | `amp,period,depth,focus` |

**2) Phần tử hạt/clip chồng lên:** `particles` (`kind: dust | embers | snow`, 3 độ sâu), `rain`, `mist`, `video_overlay` (clip sương/khói/mưa, `blend:"screen"` nền đen → trong suốt).

**3) Cảnh là video:** `{"id":"D","video":"video/clip.mp4","start":14.0,"camera":{...}}` — clip đi qua cùng camera, grain, vignette, preset màu như ảnh tĩnh nên ảnh và video trộn đồng nhất. Clip ngắn hơn cảnh sẽ tự lặp.
Chưa có footage? `python3 tools/make_fog_loop.py fog out.mp4` sinh clip sương lặp liền mạch (hoặc `smoke`).

### Công thức theo loại ảnh
| Ảnh | Gợi ý |
|---|---|
| Phong cảnh có nước | `parallax` nhẹ (amp 25–35) + `ripple` ở vùng nước + `sway` tán lá + `glow` nắng + `particles dust` |
| Bão / cửa sổ máy bay | `rain` + `glow` màu xanh lạnh `flicker≥1` tại tia sét + `flash`/`shake` đúng khung sấm |
| Rừng đêm / hang tối | `particles embers`/`dust` xanh + `glow` ma quái `pulse_hz≈0.3` + `sway` nhẹ |
| Phòng / chân dung cũ | `glow` đèn `flicker 0.3` + `particles dust` + preset `newsreel` |
| Bản đồ / sơ đồ | `parallax` rất nhẹ + `highlight_box`, `timeline` |
Chuyển động trong khung nên NHẸ (biên độ nhỏ, tốc độ chậm): mục tiêu là người xem "cảm" thấy sống động chứ không nhận ra hiệu ứng. Chạy `tools/analyze_video.py` để chắc chắn nền vẫn mượt.
Ví dụ: `examples/demo_motion.json`.
