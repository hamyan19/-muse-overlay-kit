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
| `spotlight` | Tối cả khung, chừa vòng sáng dẫn mắt (có thể bám ảnh) | `scene,src` hoặc `pos`, `r,dim,from_mult,soft` |
| `highlight_box` | Khung góc mở ra quanh vật thể + nhãn | `scene,src_box,label,color,width` |
| `stamp` | Dấu đóng "RECONSTRUCTION/CLASSIFIED" đập xuống + rung (nền tối mờ cho dễ đọc) | `text,pos,size,angle,color,opacity,fill` |
| `lower_third` | Thanh tên/chú thích trượt vào | `title,sub,y` |
| `flash` | Chớp trắng nhấn twist/cú đập | `dur,alpha,color` |
| `redact` | Thanh đen quét che chữ (hồ sơ mật) | `boxes[[x0,y0,x1,y1]]` |
| `rain` | Mưa rơi thật, 3 lớp sâu (bão, đêm, cảnh u ám) | `density,alpha,angle,speed,length,seed` |
| `mist` | Sương/khói trôi ngang, 2 lớp thị sai | `opacity,speed,floor,gain,y_fade[y0,y1],color` |
| `dim` | Tối dần / sáng lại (nhịp im lặng, tập trung vào thẻ) | `alpha[a0,a1],t_in,t_out,t_end,fade_out` |

Camera (`scenes[].camera`): `t0,t1,scale[a,b],cx[a,b],cy[a,b],ease` với ease = `linear | smooth | pow:2.2`,
tuỳ chọn `shake{t0,t1,amp,hz}` (rung mượt tắt dần cho cú đập). Cảnh: `blur`, `brightness` để tạo nền mờ/tối từ chính ảnh.
Global: `dissolve`, `grain`, `vignette`, `warm`, `flicker`.
