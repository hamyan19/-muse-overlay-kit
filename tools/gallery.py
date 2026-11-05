#!/usr/bin/env python3
"""GALLERY — trang HTML xem MỌI dạng design của kit: preset dựng, điểm nhấn theo lời, lớp phủ, chữ & số, biểu đồ,
chuyển động trong ảnh. Mỗi mẫu là một clip ngắn dựng bằng chính overlay_engine trên 3 ảnh style đã duyệt.

  python3 tools/gallery.py                 # -> gallery/index.html + gallery/clips/*.mp4 (~3 phút trên cloud 2 nhân)
  python3 tools/gallery.py --only marker,tag   # dựng lại vài mẫu (giữ clip cũ của các mẫu khác)

Mở gallery/index.html bằng trình duyệt (cần cả thư mục clips/ bên cạnh). Thêm loại phần tử mới vào engine thì thêm
một mục vào DEMOS dưới đây — trang tự cập nhật. Trạng thái "đã chốt / không dùng" lấy theo QUYET-DINH.md.
"""
import argparse, copy, glob, json, os, shutil, subprocess, sys, tempfile
import numpy as np, cv2
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import overlay_engine as O

REFS = sorted(glob.glob(os.path.join(ROOT, "styles", "*", "ref-approved", "*.png")))
BG = {"camp": REFS[0], "hide": REFS[1], "hunt": REFS[2]}    # lửa trại + lều xương | cạo da | thợ săn + tuần lộc
COLORS = {"yellow": [255, 209, 26], "red": [235, 50, 40], "cream": [255, 240, 200], "edge": [230, 225, 200],
          "card": [10, 12, 10], "white": [255, 255, 255], "orange": [232, 110, 20]}
FONTS = {"sans": "fonts/DejaVuSans-Bold.ttf", "mono": "fonts/DejaVuSansMono-Bold.ttf", "serif": "fonts/Lora-Variable.ttf#SemiBold"}

CHOT = "đã chốt dùng"; KHONG = "không dùng (QUYET-DINH)"; THEM = "có sẵn, chưa dùng"
# Nhóm hiển thị trên trang
G_PRESET, G_FOCUS, G_MARK, G_TEXT, G_DATA, G_ATMOS, G_FX = ("Preset dựng", "Điểm nhấn theo lời", "Lớp phủ đánh dấu",
                                                             "Thẻ chữ & số", "Biểu đồ & sơ đồ", "Không khí", "Chuyển động trong ảnh")


def D(id, group, name, use, bg="camp", el=None, fx=None, focus=None, preset="documentary", status=THEM, dur=4.0, cam=None, note=""):
    return dict(id=id, group=group, name=name, use=use, bg=bg, el=el or [], fx=fx or [], focus=focus, preset=preset,
                status=status, dur=dur, cam=cam, note=note)


DEMOS = [
    # ---------------- preset dựng (cả chương một style; hai chương liền nhau phải khác)
    *[D(f"preset-{p}", G_PRESET, n, u, bg=b, preset=p, status=s, dur=3.5)
      for p, n, u, b, s in [
          ("storybook", "Sách truyện", "Ảnh minh hoạ, kể chậm: tông ấm, màu dịu, vân giấy. Ch2 đã duyệt v3.", "camp", CHOT),
          ("documentary", "Tài liệu sạch", "Màu trung tính, gần như không hạt — bản đồ, số liệu, thẻ tư liệu. Mặc định tạm Ch1/3/5.", "hunt", CHOT),
          ("memory", "Kỷ niệm", "Màu bạc, đen nâng, viền ảnh in kem — hồi ức, đoạn kết (55+).", "hide", THEM),
          ("cinematic", "Điện ảnh", "Ít hạt, màu tự nhiên, hợp phụ đề serif.", "hunt", THEM),
          ("newsreel", "Phim xưa", "Đen trắng ngả nâu, hạt thô, xước phim.", "camp", THEM),
          ("comic", "Truyện tranh", "Màu rực, khung mực quanh ô hình.", "hide", THEM),
          ("kinetic", "Chữ chạy", "Nền tối hơn để chữ to bật theo lời.", "hunt", THEM),
      ]],
    # ---------------- điểm nhấn theo lời (focus.json -> apply_focus.py). 5–7 điểm/chương, mỗi điểm một kiểu
    D("focus-zoom", G_FOCUS, "Zoom tới chi tiết", "Camera trượt tới vật đang được nói, giữ, rồi lùi. Không tối nền.", "camp",
      focus={"t": [1.2, 3.0], "kind": "zoom", "at": [1230, 1060], "zoom": 1.7}, status=CHOT),
    D("focus-cut", G_FOCUS, "Cắt cận cảnh", "Cắt thẳng sang cận cùng ảnh trong đoạn lời, rồi cắt về.", "hide",
      focus={"t": [1.2, 3.0], "kind": "cut", "at": [960, 760], "zoom": 2.0}, status=CHOT),
    D("focus-circle", G_FOCUS, "Khoanh tròn tay", "Nét bút khoanh quanh chi tiết, bám theo camera.", "camp",
      focus={"t": [0.8, 3.4], "kind": "circle", "box": [1000, 930, 1460, 1260]}, status=CHOT),
    D("focus-arrow", G_FOCUS, "Mũi tên tay", "Mũi tên vẽ dần chỉ vào chi tiết, bám camera.", "hunt",
      focus={"t": [0.8, 3.4], "kind": "arrow", "from": [1550, 380], "to": [2120, 760]}, status=CHOT),
    D("focus-spot", G_FOCUS, "Tô sáng vật thể", "Hạ sáng phần còn lại, chừa vùng sáng. Có rào sáng; tối đa 2/chương.", "hide",
      focus={"t": [0.8, 3.4], "kind": "spot", "at": [2060, 520], "r": 420}, status="đã chốt (≤2/chương)"),
    # ---------------- lớp phủ đánh dấu
    D("marker-arrow-label", G_MARK, "Mũi tên + nhãn", "Mũi tên tay có thẻ nhãn ở đuôi (OVERLAYS: to ~40%, cam đậm).", "hunt",
      el=[{"type": "marker", "kind": "arrow", "t_in": 0.5, "t_out": 3.6, "scene": "A", "from": [1500, 330], "to": [2120, 760],
           "label": "REINDEER HERD", "label_src": [1400, 280], "label_card": True, "label_first": True, "color": "orange", "width": 10}],
      status=CHOT, note="sheet OVERLAYS"),
    D("marker-underline", G_MARK, "Gạch chân tay", "Nét bút gạch dưới một chi tiết.", "hide",
      el=[{"type": "marker", "kind": "underline", "t_in": 0.6, "t_out": 3.6, "scene": "A", "from": [1700, 900], "to": [2250, 880], "color": "red"}]),
    D("tag", G_MARK, "Thẻ nhãn", "Thẻ chữ nền tối, đọc được trên giấy sáng lẫn ảnh rậm; bám vật thể.", "hide",
      el=[{"type": "tag", "t_in": 0.5, "t_out": 3.6, "scene": "A", "src": [2060, 900], "text": "DRYING HIDE", "sub": "2–3 days in wind", "size": 30}],
      status=CHOT, note="sheet OVERLAYS"),
    D("route", G_MARK, "Đường đi nét đứt", "Đường đi tự vẽ, chấm mốc + nhãn — hành trình, dấu chân.", "hunt",
      el=[{"type": "route", "t_in": 0.3, "t_out": 3.8, "scene": "A", "points": [[700, 1200], [1200, 1060], [1700, 960], [2150, 860]],
           "labels": ["HUNTERS", "", "", "HERD"], "draw": 2.0}], status=CHOT, note="sheet OVERLAYS"),
    D("image_overlay", G_MARK, "Ảnh nét đứt L01", "Ảnh phủ nét đứt (đồ hiện đại) hiện dần trên vật thể rồi tan; multiply.", "camp",
      el=[{"type": "image_overlay", "t_in": 0.4, "t_out": 3.2, "scene": "A", "file": "stills/G_L01.png", "at": [2180, 1130], "width": 560,
           "strength": 0.8}], status=CHOT, note="sheet OVERLAYS"),
    D("highlight_box", G_MARK, "Khung góc", "Khung góc mở ra quanh vật thể + nhãn.", "hide",
      el=[{"type": "highlight_box", "t_in": 0.4, "t_out": 3.6, "scene": "A", "src_box": [1780, 820, 2380, 1180], "label": "STONE TOOLS"}], status=KHONG),

    D("anchored_circle", G_MARK, "Vòng tròn mốc", "Khoanh một điểm + nhãn, bám camera (kiểu điều tra).", "camp",
      el=[{"type": "anchored_circle", "t_in": 0.3, "t_out": 3.8, "scene": "A", "src": [1240, 1080], "r": 260, "draw": [0.35, 1.1],
           "label": {"t_in": 1.0, "text": "THE ONLY HEAT SOURCE", "half_width": 230}}], status=KHONG),

    D("spotlight", G_MARK, "Đèn rọi", "Phần tử gốc của 'tô sáng vật thể' (dùng qua focus kind spot để có rào sáng).", "camp",
      el=[{"type": "spotlight", "t_in": 0.4, "t_out": 3.6, "scene": "A", "src": [680, 640], "r": 300, "from_mult": 1.7, "dim": 0.35, "soft": 110}]),
    D("photo_pin", G_MARK, "Ảnh polaroid", "Ảnh phụ (hoặc cận từ ảnh nguồn) dán băng keo, thả xuống.", "hunt",
      el=[{"type": "photo_pin", "t_in": 0.3, "t_out": 3.8, "src": "stills/hide.png", "crop": [1700, 100, 2500, 900], "pos": [960, 260],
           "w": 300, "angle": -5, "caption": "the hide, day 2"}]),
    D("sprite", G_MARK, "Vật di chuyển", "Mảnh PNG nền trong suốt bay vào / rơi xuống đúng lời.", "camp",
      el=[{"type": "sprite", "t_in": 0.3, "t_out": 3.8, "scene": "A", "file": "sprites/G_log.png", "from": [1900, 300], "to": [1330, 1040],
           "run": [0.5, 1.8], "ease": "smooth"}]),
    D("panel_reveal", G_MARK, "Lộ dần từng ô", "Ảnh chia ô, mỗi ý mở một ô; ô chưa mở phủ giấy sáng (nhánh cụm ý).", "hunt",
      el=[{"type": "panel_reveal", "t_in": 0.0, "scene": "A", "layout": "3col", "reveal": [0.4, 1.5, 2.6], "t_out": 4.6}], dur=4.2),
    D("redact", G_MARK, "Thanh che", "Thanh đen quét che chữ (hồ sơ mật).", "hide",
      el=[{"type": "typed_card", "t_in": 0.0, "t_out": 4.0, "box": [60, 60, 560, 200], "lines": [
          {"text": "SURVIVAL LOG", "pos": [84, 100], "size": 32, "font": "mono", "color": "cream", "start": 0.0, "cps": 40},
          {"text": "SITE: [CLASSIFIED]", "pos": [84, 150], "size": 26, "font": "mono", "color": "yellow", "start": 0.3, "cps": 40}]},
          {"type": "redact", "t_in": 1.4, "t_out": 4.0, "boxes": [[180, 132, 520, 170]]}]),
    # ---------------- thẻ chữ & số
    D("lower_third", G_TEXT, "Thanh tên", "Thanh tên / chú thích trượt vào.", "hide",
      el=[{"type": "lower_third", "t_in": 0.3, "t_out": 3.6, "title": "HIDE SCRAPING", "sub": "Upper Palaeolithic · reconstruction"}]),
    D("label", G_TEXT, "Tiêu đề nhỏ", "Tiêu đề nhỏ + gạch chân.", "hunt",
      el=[{"type": "label", "t_in": 0.3, "t_out": 3.6, "text": "WINTER · DAY 41", "pos": [640, 110], "size": 34, "underline": [480, 800, 140]}]),
    D("typed_card", G_TEXT, "Thẻ gõ chữ", "Hồ sơ / ngày giờ gõ từng chữ.", "camp",
      el=[{"type": "typed_card", "t_in": 0.1, "t_out": 3.8, "box": [36, 32, 520, 152], "cursor_until": 2.4, "lines": [
          {"text": "MAMMOTH-BONE HUT", "pos": [60, 70], "size": 36, "font": "mono", "color": "cream", "start": 0.25, "cps": 16},
          {"text": "UKRAINE · 15,000 YEARS AGO", "pos": [60, 118], "size": 22, "font": "mono", "color": "yellow", "start": 1.3, "cps": 22}]}], status=KHONG),

    D("badge_pop", G_TEXT, "Số đập vào", "Con số / nhãn đập vào đúng lúc nói.", "hunt",
      el=[{"type": "badge_pop", "t_in": 0.6, "t_out": 3.8, "text": "−40 °C", "pos": [1180, 110], "size": 96, "anchor": "rm",
           "sub": "WINTER NIGHTS", "sub_pos": [1180, 176], "sub_size": 22}]),
    D("stamp", G_TEXT, "Dấu đóng", "Dấu RECONSTRUCTION đập xuống + rung.", "camp",
      el=[{"type": "stamp", "t_in": 0.8, "t_out": 3.8, "text": "RECONSTRUCTION", "pos": [640, 360], "size": 60}]),
    D("speech_box", G_TEXT, "Ô lời dẫn", "Ô lời truyện tranh viền mực, đuôi chỉ vào nhân vật.", "hide",
      el=[{"type": "speech_box", "t_in": 0.4, "t_out": 3.8, "pos": [330, 120], "text": "EVERY SCRAP OF FAT\nIS FUEL", "size": 28, "tail": [470, 330]}]),
    D("clipping", G_TEXT, "Mẩu giấy / báo", "Mẩu báo mép rách hoặc giấy note vàng, thả xuống.", "camp",
      el=[{"type": "clipping", "t_in": 0.3, "t_out": 3.8, "pos": [1000, 180], "w": 360, "headline": "KEEP THE FIRE\nALIVE ALL NIGHT",
           "sub": "RULE ONE", "angle": 3, "size": 28}]),
    D("strike_cards", G_TEXT, "Gạch bỏ đáp án", "\"Không phải X, không phải Y\" — gạch đúng thứ bị phủ định.", "hunt",
      el=[{"type": "strike_cards", "t_in": 0.3, "t_out": 3.9, "cards": [{"text": "THE COLD", "y": 290, "t_in": 0.3, "t_strike": 1.3},
                                                                       {"text": "THE WOLVES", "y": 450, "t_in": 1.6, "t_strike": 2.7}]}], status=KHONG),

    D("question_card", G_TEXT, "Thẻ dấu hỏi", "Thẻ \"?\" nhấp nháy cho câu hỏi mở.", "hunt",
      el=[{"type": "question_card", "t_in": 0.3, "box": [490, 190, 790, 490]}], status=KHONG),

    D("kinetic", G_TEXT, "Chữ bật theo lời", "Từ khoá bật to đúng lúc được nói (wordts.py kinetic sinh danh sách).", "camp",
      el=[{"type": "kinetic", "words": [{"text": "FIRE", "t_in": 0.4, "t_out": 1.7, "pos": [640, 340], "size": 150},
                                        {"text": "OR DEATH", "t_in": 1.9, "t_out": 3.6, "pos": [640, 360], "size": 130, "color": "yellow"}]}], preset="kinetic"),
    D("captions", G_TEXT, "Phụ đề theo lời", "Phụ đề theo mệnh đề, từ đã đọc sáng / chưa đọc mờ.", "hunt",
      el=[{"type": "captions", "wordts": "vo/G_wordts.json", "font": "serif", "size": 44, "y": 600, "karaoke": True}], preset="cinematic"),
    D("ticker", G_TEXT, "Số chạy", "Số chạy tới đích đúng lúc nói (năm, mét, độ). Dòng CON SỐ trong OVERLAYS.", "hunt",
      el=[{"type": "ticker", "t_in": 0.3, "t_out": 3.8, "run": [0.3, 2.4], "from": 0, "to": 15000, "suffix": " YEARS", "pos": [640, 250],
           "size": 100, "label": "AGO"}], status=CHOT),
    D("counter_down", G_TEXT, "Đếm lùi", "Đếm lùi kiểu \"chỉ còn một\", số cuối nổ + chớp. Ghi \"đếm lùi\" ở OVERLAYS.", "camp",
      el=[{"type": "counter_down", "t_in": 0.2, "t_out": 3.9, "run": [0.3, 2.4], "hit": 2.4, "from": 30, "to": 1, "power": 2.0,
           "labels": {"count": "NIGHTS", "end": "OF FUEL LEFT", "sub": "30 NIGHTS"}}], status=CHOT),
    D("day_ticker", G_TEXT, "Đếm ngày", "DAY 1…11 bật lần lượt.", "hunt",
      el=[{"type": "day_ticker", "run": [0.3, 2.6], "from": 1, "to": 11, "x_start": 450, "step": 38, "y": 640}], status=KHONG),
    # ---------------- biểu đồ & sơ đồ
    D("timeline", G_DATA, "Trục thời gian", "Trục vẽ dần, mốc bật theo lời.", "hunt",
      el=[{"type": "timeline", "t_in": 0.2, "t_out": 3.9, "draw": [0.2, 1.3], "x0": 160, "x1": 1120, "y": 600, "events": [
          {"t": 0.5, "pos": 0.0, "label": "AUTUMN", "sub": "hunt"}, {"t": 1.3, "pos": 0.45, "label": "WINTER", "sub": "hut"},
          {"t": 2.1, "pos": 0.9, "label": "SPRING", "sub": "move"}]}]),
    D("bars", G_DATA, "Thanh so sánh", "Thanh mọc ra theo lời.", "camp",
      el=[{"type": "bars", "t_in": 0.3, "t_out": 3.9, "box": [740, 80, 1220, 300], "title": "HEAT LOST PER NIGHT", "max": 100, "items": [
          {"label": "OPEN", "value": 90, "t": 0.5, "text": "90%", "color": "red"}, {"label": "HUT", "value": 35, "t": 1.2, "text": "35%"},
          {"label": "HUT+FIRE", "value": 12, "t": 1.9, "text": "12%", "color": "cream"}]}]),
    D("linechart", G_DATA, "Biểu đồ đường", "Đường tự vẽ (ghi ILLUSTRATIVE nếu không có số thật).", "hunt",
      el=[{"type": "linechart", "t_in": 0.3, "t_out": 3.9, "box": [700, 70, 1230, 330], "run": [0.5, 2.6], "title": "TEMPERATURE (ILLUSTRATIVE)",
           "xlabel": ["OCT", "MAR"], "series": [{"label": "OUTSIDE", "color": "cream", "pts": [[0, 0.7], [0.3, 0.4], [0.6, 0.1], [1, 0.5]]},
                                                {"label": "IN HUT", "color": "yellow", "pts": [[0, 0.85], [0.5, 0.7], [1, 0.8]]}]}]),
    D("gauge", G_DATA, "Thang đo", "Thang đo rơi / leo (nhiệt độ, độ cao).", "hunt",
      el=[{"type": "gauge", "t_in": 0.3, "t_out": 3.9, "x": 1150, "y0": 200, "y1": 600, "max": 40, "ticks": [[40, "0°"], [20, "−20°"], [0, "−40°"]],
           "drop": [0.5, 3.0], "power": 1.6}]),
    D("dimension", G_DATA, "Đường kích thước", "Đường kích thước kiểu bản vẽ, số đổi theo lời.", "camp",
      el=[{"type": "dimension", "t_in": 0.4, "t_out": 3.9, "scene": "A", "a": [180, 560], "b": [1180, 560], "draw": 0.8,
           "texts": [[0.9, "4 M"], [2.2, "4–5 M WIDE"]], "label_off": [0, -60]}]),
    D("flow", G_DATA, "Dòng hạt", "Hạt chạy theo làn — tốc độ là dữ liệu (nhiệt thoát chậm / nhanh).", "camp",
      el=[{"type": "flow", "t_in": 0.2, "t_out": 3.9, "scene": "A", "lanes": [[[1230, 1000], [1300, 300]], [[1150, 1000], [900, 250]]],
           "speed": 140, "spacing": 90, "r": 7, "color": "orange"}]),
    # ---------------- không khí
    D("particles-snow", G_ATMOS, "Tuyết rơi", "Hạt 3 độ sâu: tuyết (OVERLAYS 'tuyết'), bụi, tàn lửa.", "hunt",
      el=[{"type": "particles", "kind": "snow", "t_in": 0, "t_out": 6, "n": 120, "alpha": 0.7, "fade_in": 0.3}], status=CHOT),
    D("particles-embers", G_ATMOS, "Tàn lửa bay", "Tàn lửa bay lên từ đống lửa.", "camp",
      el=[{"type": "particles", "kind": "embers", "t_in": 0, "t_out": 6, "n": 60, "alpha": 0.8, "fade_in": 0.3}]),
    D("particles-dust", G_ATMOS, "Bụi sáng", "Bụi sáng trôi nhẹ trong không khí.", "hide",
      el=[{"type": "particles", "kind": "dust", "t_in": 0, "t_out": 6, "n": 80, "alpha": 0.6, "fade_in": 0.3}]),
    D("mist", G_ATMOS, "Sương trôi", "Sương / khói trôi ngang, 2 lớp thị sai.", "hunt",
      el=[{"type": "mist", "t_in": 0, "t_out": 6, "opacity": 0.22, "y_fade": [300, 720], "speed": 30}]),
    D("rain", G_ATMOS, "Mưa", "Mưa 3 lớp sâu (bão, cảnh u ám).", "hide",
      el=[{"type": "rain", "t_in": 0, "t_out": 6, "density": 300, "alpha": 0.4, "angle": 16, "speed": 1600}]),
    D("video_overlay", G_ATMOS, "Clip sương chồng", "Clip lặp (make_fog_loop.py) chồng 'screen' lên cảnh.", "camp",
      el=[{"type": "video_overlay", "t_in": 0, "t_out": 6, "file": "video/G_fog.mp4", "blend": "screen", "opacity": 0.45}]),
    D("dim", G_ATMOS, "Tối dần", "Tối dần / sáng lại cho nhịp im lặng.", "camp",
      el=[{"type": "dim", "t_in": 0.4, "t_out": 2.6, "alpha": [0.0, 0.55], "fade_out": 0.8}]),
    D("flash", G_ATMOS, "Chớp trắng", "Chớp trắng nhấn cú đập / twist.", "hunt",
      el=[{"type": "flash", "t_in": 1.6, "dur": 0.3}], dur=3.0),
    # ---------------- chuyển động trong ảnh tĩnh (fx của cảnh)
    D("fx-parallax", G_FX, "Thị sai 2.5D", "Máy quay như đi xuyên ảnh (đáy gần, đỉnh xa).", "hunt",
      fx=[{"type": "parallax", "amp": 40, "period": 4, "depth": "auto_ground"}]),
    D("fx-glow", G_FX, "Quầng sáng", "Quầng sáng lửa / nắng, chập chờn.", "camp",
      fx=[{"type": "glow", "pos": [1240, 1060], "r": 520, "color": [255, 170, 80], "strength": 0.55, "pulse": 0.3, "pulse_hz": 0.8, "flicker": 1.0}]),
    D("fx-sway", G_FX, "Đung đưa", "Tấm da, cỏ, cờ lay trong gió (gốc đứng yên).", "hide",
      fx=[{"type": "sway", "box": [1700, 120, 2400, 1000], "amp": 14, "freq": 0.5}]),
    D("fx-ripple", G_FX, "Gợn nước", "Mặt nước gợn, phản chiếu lung linh.", "hide",
      fx=[{"type": "ripple", "box": [600, 560, 1900, 760], "amp": 6, "wavelength": 90, "speed": 0.8, "feather": 60}]),
    D("fx-squash", G_FX, "Nén vùng ảnh", "Nén dọc một vùng về phía đáy (lún, bị ép).", "camp",
      fx=[{"type": "squash", "box": [150, 0, 1300, 1060], "amount": 0.95, "run": [0.6, 2.4]}]),
]


def make_assets(res, fps):
    os.makedirs(os.path.join(res, "stills"), exist_ok=True); os.makedirs(os.path.join(res, "vo"), exist_ok=True)
    os.makedirs(os.path.join(res, "sprites"), exist_ok=True); os.makedirs(os.path.join(res, "video"), exist_ok=True)
    shutil.copytree(os.path.join(ROOT, "fonts"), os.path.join(res, "fonts"), dirs_exist_ok=True)
    for k, p in BG.items():
        Image.open(p).convert("RGB").resize((2560, 1440), Image.LANCZOS).save(os.path.join(res, "stills", f"{k}.png"))
    # L01: nét đứt đồ hiện đại (một chiếc ghế xếp) — mực tối trên nền trắng, để multiply
    L = Image.new("RGB", (700, 520), (255, 255, 255)); d = ImageDraw.Draw(L)
    def dash(p0, p1, w=16, n=12):
        for i in range(n):
            if i % 2: continue
            a, b = i / n, (i + 1) / n
            d.line((p0[0] + (p1[0] - p0[0]) * a, p0[1] + (p1[1] - p0[1]) * a, p0[0] + (p1[0] - p0[0]) * b, p0[1] + (p1[1] - p0[1]) * b), fill=(30, 30, 30), width=w)
    for seg in [((120, 80), (580, 80)), ((120, 80), (120, 300)), ((580, 80), (580, 300)), ((120, 300), (580, 300)),
                ((150, 300), (90, 500)), ((550, 300), (610, 500)), ((150, 300), (610, 500)), ((550, 300), (90, 500))]:
        dash(*seg)
    L.save(os.path.join(res, "stills", "G_L01.png"))
    # sprite: khúc gỗ (PNG trong suốt)
    S = Image.new("RGBA", (300, 110), (0, 0, 0, 0)); d = ImageDraw.Draw(S)
    d.rounded_rectangle((10, 18, 290, 92), radius=36, fill=(122, 78, 44, 255), outline=(40, 26, 16, 255), width=6)
    d.ellipse((232, 18, 290, 92), fill=(196, 150, 100, 255), outline=(40, 26, 16, 255), width=6)
    d.ellipse((250, 40, 272, 70), outline=(120, 80, 50, 255), width=3)
    S.rotate(-25, expand=True).save(os.path.join(res, "sprites", "G_log.png"))
    # wordts cho phụ đề
    words = "The fire had to burn all night or nobody would see the morning".split()
    W, t = [], 0.3
    for w in words:
        dd = 0.16 + 0.035 * len(w); W.append([round(t, 2), round(t + dd, 2), w]); t += dd + 0.05
    json.dump(W, open(os.path.join(res, "vo", "G_wordts.json"), "w"))
    subprocess.run([sys.executable, os.path.join(ROOT, "tools", "make_fog_loop.py"), "fog", os.path.join(res, "video", "G_fog.mp4"),
                    "--seconds", "6", "--w", "1280", "--h", "720", "--fps", str(fps)], check=True, capture_output=True)


def build_spec(dm, res, fps):
    cam = dm["cam"] or {"t0": 0, "t1": dm["dur"], "ease": "smooth", "scale": [1.0, 1.06], "cx": [1280, 1300], "cy": [720, 720]}
    sc = {"id": "A", "image": f"stills/{dm['bg']}.png", "start": 0.0, "camera": cam}
    if dm["fx"]: sc["fx"] = copy.deepcopy(dm["fx"])
    spec = {"meta": {"width": 1280, "height": 720, "fps": fps, "duration": dm["dur"]}, "colors": COLORS, "fonts": FONTS,
            "preset": dm["preset"], "scenes": [sc], "elements": copy.deepcopy(dm["el"])}
    if dm["focus"]:   # điểm nhấn: đi qua apply_focus.py thật (có rào sáng), đúng như khi dựng chương
        tmp = tempfile.mkdtemp(); sp, fp, op = (os.path.join(tmp, n) for n in ("s.json", "f.json", "o.json"))
        json.dump(spec, open(sp, "w")); json.dump({"A": [dm["focus"]]}, open(fp, "w"))
        subprocess.run([sys.executable, os.path.join(ROOT, "tools", "apply_focus.py"), sp, fp, "--out", op, "--root", res],
                       check=True, capture_output=True)
        spec = json.load(open(op)); shutil.rmtree(tmp)
    return spec


def render(spec, res, out_mp4, poster):
    O.setup(spec, res)
    n = O.C.N
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1280x720", "-r", str(O.C.FPS),
                           "-i", "-", "-vf", "scale=640:360:flags=area", "-c:v", "libx264", "-preset", "veryfast", "-crf", "27",
                           "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", out_mp4], stdin=subprocess.PIPE)
    for i in range(n):
        fr = O.frame(i); ff.stdin.write(fr.tobytes())
        if i == int(n * 0.6): Image.fromarray(fr).resize((640, 360), Image.LANCZOS).save(poster, quality=80)
    ff.stdin.close(); ff.wait()


def sample_json(dm):
    if dm["focus"]: return {"focus.json": {"<ID cảnh>": [dm["focus"]]}}
    if dm["group"] == G_PRESET: return {"spec": {"preset": dm["preset"]}, "build_chapter": f"--preset {dm['preset']}"}
    if dm["fx"]: return {"cảnh": {"fx": dm["fx"]}}
    return {"elements": dm["el"]}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default=os.path.join(ROOT, "gallery"))
    ap.add_argument("--only", default=""); ap.add_argument("--fps", type=int, default=15)
    a = ap.parse_args()
    clips = os.path.join(a.out, "clips"); os.makedirs(clips, exist_ok=True)
    res = tempfile.mkdtemp(); make_assets(res, a.fps)
    only = set(x for x in a.only.split(",") if x)
    for dm in DEMOS:
        if only and dm["id"] not in only and not (dm["el"] and dm["el"][0]["type"] in only): continue
        spec = build_spec(dm, res, a.fps)
        render(spec, res, os.path.join(clips, dm["id"] + ".mp4"), os.path.join(clips, dm["id"] + ".jpg"))
        print("ok", dm["id"], flush=True)
    shutil.rmtree(res)
    missing = sorted(set(O.TYPES) - {e["type"] for dm in DEMOS for e in dm["el"]})
    data = [{"id": dm["id"], "group": dm["group"], "name": dm["name"], "use": dm["use"], "status": dm["status"], "note": dm["note"],
             "type": (dm["el"][0]["type"] if dm["el"] and dm["group"] not in (G_PRESET,) else (dm["fx"][0]["type"] if dm["fx"] else
                     ("focus:" + dm["focus"]["kind"] if dm["focus"] else "preset:" + dm["preset"]))),
             "json": json.dumps(sample_json(dm), ensure_ascii=False, indent=1)} for dm in DEMOS]
    groups = [G_PRESET, G_FOCUS, G_MARK, G_TEXT, G_DATA, G_ATMOS, G_FX]
    tpl = open(os.path.join(ROOT, "tools", "gallery_template.html"), encoding="utf-8").read()
    html = tpl.replace("/*DATA*/[]", json.dumps(data, ensure_ascii=False)).replace("/*GROUPS*/[]", json.dumps(groups, ensure_ascii=False))
    open(os.path.join(a.out, "fragment.html"), "w", encoding="utf-8").write(html)        # bản không khung (để đăng artifact)
    open(os.path.join(a.out, "index.html"), "w", encoding="utf-8").write(
        '<!doctype html>\n<html lang="vi"><head><meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n</head><body>\n' + html + "\n</body></html>\n")
    print(f"{len(DEMOS)} mẫu -> {a.out}/index.html" + (f" | loại phần tử chưa có mẫu: {missing}" if missing else ""))


if __name__ == "__main__":
    main()
