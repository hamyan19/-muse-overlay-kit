# QUYẾT ĐỊNH ĐÃ CHỐT — đọc file này thay vì hỏi lại (An chốt; đổi gì An sẽ sửa ở đây)

Dự án: "Surviving Winter in a House of Mammoth Bones" (Hook, Ch1–Ch9, Ending). Voice: `warm-pebble-speed110`.

| Việc | Quyết định | Nguồn |
|---|---|---|
| Độ dài shot | 5–11s, cắt ở khoảng lặng thật | An 25/10 |
| Style hình | Theo 3 ảnh mẫu `styles/ice-age-stick-figure/ref-approved/` | An 25/10 |
| Style dựng | Ch2 = `storybook` (đã duyệt v3). Hai chương liền nhau phải khác: mặc định tạm Ch1/Ch3/Ch5… `documentary`, Ch4/Ch6… `storybook` cho tới khi An chốt | QUY-TRINH luật cứng |
| Khung hình | Luôn full 16:9, không dải đen | QUY-TRINH |
| Độ phân giải | Bản duyệt: 1280×720 @15fps (`build_chapter.py render --quick`). Bản chính: 1920×1080 @30fps khi An yêu cầu | mặc định tạm |
| Điểm nhấn | **5–7 điểm/chương, mỗi điểm một kiểu**: zoom (không tối nền), cut cận cảnh, khoanh tròn tay, mũi tên tay. Theo từ đang nói | An 25/10 ("ít hiệu ứng…", v3 "ok ổn") |
| Tô sáng vật thể (`spot`) | Được dùng, tối đa 2/chương, có rào sáng (dim ≤0.45, khung sau phủ ≥95/255) | An 26/10 |
| Lớp phủ OVERLAYS | BẬT (mũi tên, nhãn, nét đứt, ảnh L01, tuyết) qua `apply_overlays.py`; phủ xong không được tối mò | An 26/10 |
| Mũi tên OVERLAYS | To hơn mặc định ~40%, cam đậm, vẽ dần | ghi chú trong bảng mapping |
| Số tự đếm (ticker) | Không dùng | mặc định tạm (ít hiệu ứng) |
| Nhạc nền | Không | An |
| Duyệt | Cột DUYỆT giữ CHỜ; người dựng không tự ghi OK | luật cứng |
| Dữ liệu chưa công bố | Voice, ảnh, script, bảng mapping: An gửi trong chat, không đưa lên repo công khai | An 26/10 |
| `wordts.json` | Căn theo script bằng `tools/align.py` (PocketSphinx), không cần Whisper | 26/10 |

| Cụm ý / lộ dần ô / ảnh 4K | **ĐANG THỬ** trên nhánh `muse/cum-y-ky-thuat-moi` — luật trong `KY-THUAT-DUNG.md` | An 26/10 |
| Metaprompt theo cụm | Để sau | An 26/10 |

"Mặc định tạm" = dựng theo đó, ghi rõ trong báo cáo, không dừng chờ.
