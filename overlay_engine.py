#!/usr/bin/env python3
"""
OVERLAY ENGINE — dựng video "ảnh tĩnh + edit chồng lớp" từ một file JSON.

Cách dùng:
  python3 overlay_engine.py spec.json --out hook.mp4              # dựng đủ hình + tiếng
  python3 overlay_engine.py spec.json --frames 1.0,5.5,9.8        # chỉ lưu vài khung PNG để kiểm tra
  python3 overlay_engine.py spec.json --out hook.mp4 --video-only # chỉ hình
  python3 overlay_engine.py spec.json --out hook.mp4 --jobs 4     # chạy song song

Mọi đường dẫn trong spec tính từ thư mục chứa spec (hoặc --root).
Yêu cầu: python3, numpy, opencv-python-headless, pillow, ffmpeg.
"""
import os, sys, json, math, argparse, subprocess, tempfile
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ------------------------------------------------------------------ tiện ích
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))

def A(t, t0, t1):
    """Tiến độ 0..1 của t trong đoạn [t0,t1]."""
    return clamp((t - t0) / (t1 - t0)) if t1 != t0 else (1.0 if t >= t0 else 0.0)

def ss(x):
    """smoothstep"""
    return x * x * (3 - 2 * x)

def ease(name, u):
    if name == "linear":
        return u
    if name == "smooth":
        return ss(u)
    if name.startswith("pow:"):
        return u ** float(name[4:])
    raise ValueError("ease không hợp lệ: " + name)

def lerp(pair, e):
    return pair[0] + (pair[1] - pair[0]) * e

def col(c):
    return tuple(int(v) for v in c)

class Ctx:
    """Giữ trạng thái đã nạp (ảnh, font, màu) cho một spec."""
    pass

C = Ctx()

def font(kind, size):
    key = (kind, int(size))
    if key not in C.fonts:
        path, _, var = C.font_paths[kind].partition("#")
        f_ = ImageFont.truetype(path, int(size))
        if var:
            f_.set_variation_by_name(var)
        C.fonts[key] = f_
    return C.fonts[key]

def new_layer():
    return Image.new("RGBA", (C.W, C.H), (0, 0, 0, 0))

def apply_alpha(img, f):
    if f >= 0.999:
        return img
    a = img.getchannel("A").point(lambda v: int(v * f))
    img.putalpha(a)
    return img

def text(d, xy, s, kind, size, fill, anchor="mm", stroke=0):
    d.text(xy, s, font=font(kind, size), fill=col(fill) + (255,), anchor=anchor,
           stroke_width=stroke, stroke_fill=(0, 0, 0, 255))

def card(d, box, alpha=0.80, radius=12, width=3):
    d.rounded_rectangle(box, radius=radius,
                        fill=col(C.colors["card"]) + (int(255 * alpha),),
                        outline=col(C.colors["edge"]) + (255,), width=width)

def comp(base, lay):
    return Image.alpha_composite(base, lay)

def vis(t, e, d_in=0.25, d_out=0.3):
    """Độ hiện (0..1) của phần tử theo t_in/t_out, có fade vào/ra."""
    return min(A(t, e["t_in"], e["t_in"] + d_in),
               1 - A(t, e["t_out"], e["t_out"] + d_out)) if "t_out" in e \
        else A(t, e["t_in"], e["t_in"] + d_in)

def color_of(e, key, default):
    v = e.get(key, default)
    return C.colors[v] if isinstance(v, str) else v

# ------------------------------------------------------------------ nền + camera
def load_scene(sc, root):
    if "video" in sc:      # cảnh là clip video (lặp lại nếu ngắn hơn cảnh); ảnh poster tuỳ chọn
        sc["_vpath"] = os.path.join(root, sc["video"])
        return None
    im = cv2.imread(os.path.join(root, sc["image"]), cv2.IMREAD_COLOR)
    if im is None:
        raise FileNotFoundError(sc["image"])
    im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
    if im.shape[1] != 2560 or im.shape[0] != 1440:
        im = cv2.resize(im, (2560, 1440), interpolation=cv2.INTER_LANCZOS4)
    if sc.get("blur"):
        im = cv2.GaussianBlur(im, (0, 0), float(sc["blur"]))
    if sc.get("brightness") is not None:
        im = (im.astype(np.float32) * float(sc["brightness"])).clip(0, 255).astype(np.uint8)
    return im

def cam(sc, t):
    c = sc["camera"]
    u = A(t, c["t0"], c["t1"])
    e = ease(c.get("ease", "linear"), u)
    s = lerp(c["scale"], e)
    cx, cy = lerp(c["cx"], e), lerp(c["cy"], e)
    sh = c.get("shake")          # {"t0","t1","amp","hz"}: rung máy mượt, tắt dần (không giật ngẫu nhiên)
    if sh and sh["t0"] <= t < sh["t1"]:
        dk = (1 - A(t, sh["t0"], sh["t1"])) ** 1.5
        w = 2 * math.pi * sh.get("hz", 9)
        cx += sh["amp"] * dk * (math.sin(w * t) + 0.5 * math.sin(2.3 * w * t + 1.0))
        cy += sh["amp"] * dk * (math.sin(1.7 * w * t + 2.0) + 0.5 * math.sin(2.9 * w * t))
    cx = clamp(cx, 1280 / s, 2560 - 1280 / s)      # không bao giờ lộ viền
    cy = clamp(cy, 720 / s, 1440 - 720 / s)
    return s, cx, cy

def video_frame(path, tl, speed=1.0, loop=True):
    """Khung video tại thời điểm tl (giây) — mở capture riêng cho từng tiến trình, đọc tuần tự khi có thể."""
    key = ("vid", path)
    if key not in C.cache:
        cap = cv2.VideoCapture(path)
        C.cache[key] = [cap, cap.get(cv2.CAP_PROP_FPS) or 30, int(cap.get(cv2.CAP_PROP_FRAME_COUNT)), -2]
    cap, vfps, n, last = C.cache[key]
    idx = int(max(tl, 0) * speed * vfps)
    idx = idx % n if loop else min(idx, n - 1)
    if idx != last + 1:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
    ok, fr = cap.read()
    if not ok:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0); ok, fr = cap.read(); idx = 0
    C.cache[key][3] = idx
    return cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)

def scene_src(sc, t):
    """Ảnh nguồn 2560x1440 của cảnh tại t: ảnh tĩnh hoặc khung video, rồi áp các fx 'chuyển động trong ảnh tĩnh'."""
    if "_vpath" in sc:
        im = video_frame(sc["_vpath"], t - sc["start"], sc.get("speed", 1.0))
        im = cv2.resize(im, (2560, 1440), interpolation=cv2.INTER_CUBIC)
        if sc.get("brightness") is not None:
            im = (im.astype(np.float32) * float(sc["brightness"])).clip(0, 255).astype(np.uint8)
    else:
        im = sc["_img"]
    fxs = sc.get("fx")
    if not fxs:
        return im
    im = im.copy()
    for fx in fxs:
        if t < fx.get("t0", -1e9) or t > fx.get("t1", 1e9):
            continue
        im = FX[fx["type"]](im, fx, t - sc["start"])
    return im

def render_scene(sc, t):
    s, cx, cy = cam(sc, t)
    M = np.float32([[s, 0, 1280 - s * cx], [0, s, 720 - s * cy]])
    big = cv2.warpAffine(scene_src(sc, t), M, (2560, 1440), flags=cv2.INTER_LANCZOS4,
                         borderMode=cv2.BORDER_REPLICATE)          # render ở 2560x1440
    return cv2.resize(big, (C.W, C.H), interpolation=cv2.INTER_AREA).astype(np.float32)

def to_screen(sc, t, x, y):
    """Toạ độ ảnh nguồn -> toạ độ màn hình (để thẻ bám theo camera)."""
    s, cx, cy = cam(sc, t)
    k = C.W / 2560.0
    return (s * x + 1280 - s * cx) * k, (s * y + 720 - s * cy) * k, s * k

def background(t):
    scenes = C.scenes
    k = 0
    for i, sc in enumerate(scenes):
        if t >= sc["start"]:
            k = i
    out = render_scene(scenes[k], t)
    if k > 0 and t < scenes[k]["start"] + C.dissolve:
        prev = render_scene(scenes[k - 1], t)
        a = ss(A(t, scenes[k]["start"], scenes[k]["start"] + C.dissolve))
        out = prev * (1 - a) + out * a
    return out

def finish_bg(img, idx):
    img = img * C.VIG * C.WARM
    g = C.grade
    if g:
        if g.get("bw"):
            gray = (img @ np.array([0.299, 0.587, 0.114], np.float32))[..., None]
            img = img * (1 - g["bw"]) + gray * g["bw"]
        if g.get("tint"):
            img = img * np.array(g["tint"], np.float32)
        if g.get("sat") is not None:   # bão hoà màu: <1 nhạt (hoài niệm), >1 rực (truyện tranh)
            gray = (img @ np.array([0.299, 0.587, 0.114], np.float32))[..., None]
            img = gray + (img - gray) * g["sat"]
        if g.get("contrast"):
            img = (img - 128.0) * g["contrast"] + 128.0
        if g.get("lift"):   # nâng vùng tối -> đen bạc màu như ảnh cũ
            img = img * (1 - g["lift"] / 255.0) + g["lift"]
    if C.flicker > 0:   # nhấp nháy sáng rất nhẹ như phim cũ (tuỳ chọn)
        img = img * (1 + C.flicker * (math.sin(idx * 0.9) + 0.5 * math.sin(idx * 2.3 + 1)))
    if C.grain > 0:
        rng = np.random.default_rng(idx)
        img += rng.normal(0, C.grain, (C.H, C.W, 1)).astype(np.float32)
    return img

# ------------------------------------------------------------------ các loại phần tử
def el_typed_card(t, e):
    f = vis(t, e, e.get("fade_in", 0.2), e.get("fade_out", 0.4))
    if f <= 0:
        return None
    lay = new_layer(); d = ImageDraw.Draw(lay)
    card(d, e["box"], e.get("alpha", 0.8))
    typing_line, typed_n = None, 0
    for ln in e["lines"]:
        n = int(clamp((t - ln["start"]) * ln.get("cps", 14), 0, len(ln["text"])))
        c = color_of(ln, "color", "cream")
        text(d, ln["pos"], ln["text"][:n], ln.get("font", "mono"), ln["size"], c, "lm")
        if 0 < n < len(ln["text"]) or (n == 0 and t >= ln["start"] - 0.2):
            typing_line, typed_n = ln, n
        elif n == len(ln["text"]) and t < e.get("cursor_until", 0):
            typing_line, typed_n = ln, n
    if typing_line and int(t * 2) % 2 == 0 and t < e.get("cursor_until", 99):
        ln = typing_line
        wch = font(ln.get("font", "mono"), ln["size"]).getlength("0")
        x = ln["pos"][0] + typed_n * wch + 2
        d.rectangle((x, ln["pos"][1] - ln["size"] * 0.45, x + wch * 0.7,
                     ln["pos"][1] + ln["size"] * 0.45), fill=col(C.colors["cream"]) + (255,))
    return apply_alpha(lay, f)

def el_badge_pop(t, e):
    f = vis(t, e, 0.25, e.get("fade_out", 0.4))
    if f <= 0:
        return None
    lay = new_layer(); d = ImageDraw.Draw(lay)
    p = A(t, e["t_in"], e["t_in"] + 0.28)
    size = e["size"] * (1 + 0.30 * (1 - ss(p)))
    text(d, e["pos"], e["text"], "sans", size, color_of(e, "color", "yellow"),
         e.get("anchor", "rm"), stroke=4)
    if e.get("sub"):
        text(d, e["sub_pos"], e["sub"], "sans", e.get("sub_size", 22), C.colors["cream"],
             e.get("anchor", "rm"), stroke=2)
    return apply_alpha(lay, f)

def el_gauge(t, e):
    f = vis(t, e, 0.25, e.get("fade_out", 0.4))
    if f <= 0:
        return None
    lay = new_layer(); d = ImageDraw.Draw(lay)
    gx, y0, y1 = e["x"], e["y0"], e["y1"]
    edge, yel = col(C.colors["edge"]) + (255,), col(C.colors["yellow"]) + (255,)
    d.line((gx, y0, gx, y1), fill=edge, width=4)
    vmax = e["max"]
    for v, label in e["ticks"]:
        yy = y0 + (y1 - y0) * (1 - v / vmax)
        d.line((gx - 22, yy, gx + 4, yy), fill=edge, width=4)
        text(d, (gx - 32, yy), label, "sans", 22, C.colors["cream"], "rm", stroke=2)
    u = A(t, e["drop"][0], e["drop"][1]) ** e.get("power", 1.7)
    my = y0 + (y1 - y0) * u
    d.line((gx, y0, gx, my), fill=yel, width=8)
    d.polygon([(gx + 6, my), (gx + 30, my - 15), (gx + 30, my + 15)], fill=yel)
    text(d, (gx + 36, my), f"{int(round(vmax * (1 - u))):,}", "sans", 22,
         C.colors["yellow"], "lm", stroke=2)
    return apply_alpha(lay, f)

def el_anchored_circle(t, e):
    f = vis(t, e, 0.2, e.get("fade_out", 0.5))
    if f <= 0:
        return None
    sc = C.scene_by_id[e["scene"]]
    sx, sy, k = to_screen(sc, t, e["src"][0], e["src"][1])
    r = e["r"] * k
    lay = new_layer(); d = ImageDraw.Draw(lay)
    p = ss(A(t, e["draw"][0], e["draw"][1]))
    box = (sx - r, sy - r, sx + r, sy + r)
    d.arc((box[0] - 3, box[1] - 3, box[2] + 3, box[3] + 3), -90, -90 + 360 * p,
          fill=(0, 0, 0, 160), width=12)
    d.arc(box, -90, -90 + 360 * p, fill=col(C.colors["yellow"]) + (255,), width=7)
    lb = e.get("label")
    if lb:
        lf = A(t, lb["t_in"], lb["t_in"] + 0.3)
        if lf > 0:
            l2 = new_layer(); d2 = ImageDraw.Draw(l2)
            cy_ = sy + r + 44
            hw = lb.get("half_width", 250)
            card(d2, (sx - hw, cy_ - 24, sx + hw, cy_ + 24), 0.82, 8, 2)
            text(d2, (sx, cy_), lb["text"], "mono", 22, C.colors["cream"])
            lay = comp(lay, apply_alpha(l2, lf))
    return apply_alpha(lay, f)

def el_counter_down(t, e):
    f = vis(t, e, 0.2, e.get("fade_out", 0.5))
    if f <= 0:
        return None
    lay = new_layer(); d = ImageDraw.Draw(lay)
    hit = e["hit"]
    lb = e["labels"]
    if t < hit:
        u = A(t, e["run"][0], hit)
        v = int(round(e["from"] - (e["from"] - e["to"]) * u ** e.get("power", 2.2)))
        text(d, (640, 330), str(v), "sans", 250, C.colors["white"], stroke=6)
        text(d, (640, 490), lb["count"], "sans", 40, C.colors["cream"], stroke=3)
    else:
        p = A(t, hit, hit + 0.30)
        text(d, (640, 335), str(e["to"]), "sans", 300 * (1 + 0.35 * (1 - ss(p))),
             C.colors["yellow"], stroke=7)
        text(d, (640, 500), lb["end"], "sans", 44, C.colors["white"], stroke=3)
        if lb.get("sub"):
            text(d, (640, 560), lb["sub"], "mono", 24, C.colors["edge"])
    lay = apply_alpha(lay, f)
    if e.get("flash", True) and hit <= t < hit + 0.23:
        fl = Image.new("RGBA", (C.W, C.H), (255, 255, 255, int(70 * (1 - A(t, hit, hit + 0.23)))))
        lay = comp(lay, fl)
    return lay

def el_label(t, e):
    f = vis(t, e, e.get("fade_in", 0.3), e.get("fade_out", 0.5))
    if f <= 0:
        return None
    lay = new_layer(); d = ImageDraw.Draw(lay)
    text(d, e["pos"], e["text"], e.get("font", "mono"), e.get("size", 30),
         color_of(e, "color", "yellow"), "mm", stroke=2)
    if e.get("underline"):
        x0, x1, y = e["underline"]
        d.line((x0, y, x1, y), fill=col(color_of(e, "color", "yellow")) + (255,), width=3)
    return apply_alpha(lay, f)

def el_strike_cards(t, e):
    f = vis(t, e, 0.1, e.get("fade_out", 0.55))
    if f <= 0:
        return None
    lay = new_layer(); d = ImageDraw.Draw(lay)
    cx = e.get("cx", 640)
    hw, hh = e.get("half_w", 280), e.get("half_h", 66)
    red = col(C.colors["red"]) + (255,)
    for cd in e["cards"]:
        p = A(t, cd["t_in"], cd["t_in"] + 0.2)
        if p <= 0:
            continue
        cy = cd["y"]; oy = 18 * (1 - ss(p))
        card(d, (cx - hw, cy - hh + oy, cx + hw, cy + hh + oy), 0.82)
        u = A(t, cd["t_strike"], cd["t_strike"] + 0.25)
        text(d, (cx, cy + oy), cd["text"], "sans", e.get("size", 72),
             C.colors["white"] if u <= 0 else (170, 170, 170), stroke=3)
        if u > 0:
            x0 = cx - hw + 35
            x1 = x0 + (cx + hw - 35 - x0) * ss(u)
            d.line((x0, cy + oy, x1, cy + oy), fill=red, width=11)
            if u >= 1:
                ex, ey, w = cx + hw - 30, cy + oy - 40, 14
                d.line((ex - w, ey - w, ex + w, ey + w), fill=red, width=6)
                d.line((ex - w, ey + w, ex + w, ey - w), fill=red, width=6)
    return apply_alpha(lay, f)

def el_question_card(t, e):
    f = vis(t, e, 0.2, e.get("fade_out", 0.1))
    if f <= 0:
        return None
    lay = new_layer(); d = ImageDraw.Draw(lay)
    p = A(t, e["t_in"], e["t_in"] + 0.25)
    x0, y0, x1, y1 = e["box"]
    o = 12 * (1 - ss(p))
    card(d, (x0, y0 - o, x1, y1 - o), 0.85)
    pulse = 0.82 + 0.18 * math.sin(2 * math.pi * e.get("pulse_hz", 1.1) * max(0, t - e["t_in"] - 0.3))
    q = new_layer(); dq = ImageDraw.Draw(q)
    text(dq, ((x0 + x1) / 2, (y0 + y1) / 2 + 5), e.get("glyph", "?"), "sans",
         e.get("size", 240), C.colors["red"], stroke=4)
    return apply_alpha(comp(lay, apply_alpha(q, pulse)), f)

def el_day_ticker(t, e):
    g = A(t, e["run"][0], e["run"][0] + 0.3)
    if g <= 0:
        return None
    lay = new_layer(); d = ImageDraw.Draw(lay)
    a, b = e["from"], e["to"]
    count = b - a + 1
    n = a + int((count - 1) * A(t, e["run"][0], e["run"][1]))
    xs, step, y = e["x_start"], e["step"], e["y"]
    text(d, (xs - 22, y), e.get("left", f"DAY {a}"), "mono", 28, C.colors["cream"], "rm")
    text(d, (xs + (count - 1) * step + 22, y), e.get("right", f"DAY {b}"), "mono", 28,
         C.colors["cream"], "lm")
    edge = col(C.colors["edge"])
    for i in range(count):
        x = xs + i * step
        d.line((x, y - 9, x, y + 9), fill=edge + ((255 if a + i <= n else 90),), width=3)
    mx = xs + (n - a) * step
    d.ellipse((mx - 8, y - 8, mx + 8, y + 8), fill=col(C.colors["yellow"]) + (255,))
    text(d, (mx, y - 36), f"{e.get('prefix', 'DAY')} {n}", "mono", 26, C.colors["yellow"], stroke=2)
    return apply_alpha(lay, g * 0.8 * (1 - A(t, e.get("t_out", 999), e.get("t_out", 999) + 0.3)))

def _anchor(t, e):
    """Trả về (x, y, k): toạ độ màn hình + hệ số phóng. Có 'scene' thì bám theo camera."""
    if "scene" in e:
        return to_screen(C.scene_by_id[e["scene"]], t, e["src"][0], e["src"][1])
    return e["pos"][0], e["pos"][1], 1.0

def el_spotlight(t, e):
    """Làm tối toàn khung, chỉ chừa một vòng sáng (mềm viền) — dẫn mắt người xem."""
    f = vis(t, e, e.get("fade_in", 0.4), e.get("fade_out", 0.5))
    if f <= 0:
        return None
    sx, sy, k = _anchor(t, e)
    mult = e.get("from_mult", 1.0)
    r = e["r"] * k * (1 + (mult - 1) * (1 - ss(A(t, e["t_in"], e["t_in"] + 0.7))))
    m = np.zeros((C.H, C.W), np.uint8)
    cv2.circle(m, (int(sx), int(sy)), int(r), 255, -1)
    m = cv2.GaussianBlur(m, (0, 0), e.get("soft", 60) / 2.0)
    a = (255 * e.get("dim", 0.65) * f * (1 - m / 255.0)).astype(np.uint8)
    lay = np.zeros((C.H, C.W, 4), np.uint8)
    lay[..., 3] = a
    return Image.fromarray(lay, "RGBA")

def el_highlight_box(t, e):
    """Khung góc (corner brackets) mở rộng từ tâm, bám theo vật thể trong ảnh nguồn."""
    f = vis(t, e, 0.15, e.get("fade_out", 0.4))
    if f <= 0:
        return None
    sc = C.scene_by_id[e["scene"]]
    x0, y0, x1, y1 = e["src_box"]
    ax, ay, k = to_screen(sc, t, x0, y0)
    bx, by, _ = to_screen(sc, t, x1, y1)
    cx, cy = (ax + bx) / 2, (ay + by) / 2
    p = ss(A(t, e["t_in"], e["t_in"] + 0.35))
    hw, hh = (bx - ax) / 2 * p, (by - ay) / 2 * p
    L = min(hw, hh) * 0.45
    lay = new_layer(); d = ImageDraw.Draw(lay)
    c = col(color_of(e, "color", "yellow")) + (255,)
    w = e.get("width", 6)
    for sx_, sy_ in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        px, py = cx + sx_ * hw, cy + sy_ * hh
        d.line((px, py, px - sx_ * L, py), fill=c, width=w)
        d.line((px, py, px, py - sy_ * L), fill=c, width=w)
    if e.get("label") and p > 0.9:
        lf = A(t, e["t_in"] + 0.3, e["t_in"] + 0.6)
        l2 = new_layer(); d2 = ImageDraw.Draw(l2)
        wl = font("mono", 22).getlength(e["label"]) / 2 + 20
        ly = cy - hh - 34
        card(d2, (cx - wl, ly - 20, cx + wl, ly + 20), 0.85, 8, 2)
        text(d2, (cx, ly), e["label"], "mono", 22, C.colors["cream"])
        lay = comp(lay, apply_alpha(l2, lf))
    return apply_alpha(lay, f)

def el_stamp(t, e):
    """Dấu đóng 'RECONSTRUCTION / CLASSIFIED...' đập xuống: phóng to -> thu về + rung nhẹ."""
    f = vis(t, e, 0.04, e.get("fade_out", 0.4))
    if f <= 0:
        return None
    p = A(t, e["t_in"], e["t_in"] + 0.16)
    size = e.get("size", 64)
    fnt = font("sans", size)
    tw = fnt.getlength(e["text"])
    pad = 26
    tmp = Image.new("RGBA", (int(tw + 2 * pad), int(size * 1.25 + 2 * pad)), (0, 0, 0, 0))
    td = ImageDraw.Draw(tmp)
    c = col(color_of(e, "color", "red")) + (255,)
    td.rounded_rectangle((4, 4, tmp.width - 5, tmp.height - 5), radius=10, outline=c, width=8,
                         fill=col(C.colors["card"]) + (int(255 * e.get("fill", 0.6)),))   # nền tối giúp đọc được
    td.text((tmp.width / 2, tmp.height / 2), e["text"], font=fnt, fill=c, anchor="mm")
    sc_ = 1 + 1.1 * (1 - p) ** 2
    tmp = tmp.resize((int(tmp.width * sc_), int(tmp.height * sc_)), Image.BICUBIC)
    tmp = tmp.rotate(e.get("angle", -8), expand=True, resample=Image.BICUBIC)
    tmp = apply_alpha(tmp, e.get("opacity", 0.9) * clamp(p * 2))
    sh = 7 * math.sin((t - e["t_in"]) * 70) * (1 - A(t, e["t_in"] + 0.16, e["t_in"] + 0.45)) if t > e["t_in"] + 0.16 else 0
    lay = new_layer()
    lay.paste(tmp, (int(e["pos"][0] - tmp.width / 2 + sh), int(e["pos"][1] - tmp.height / 2)), tmp)
    return apply_alpha(lay, f)

def el_lower_third(t, e):
    """Thanh tên/chú thích trượt vào từ trái."""
    f = vis(t, e, 0.01, e.get("fade_out", 0.35))
    if f <= 0:
        return None
    p = ss(A(t, e["t_in"], e["t_in"] + 0.4))
    w = max(font("sans", 34).getlength(e["title"]), font("mono", 22).getlength(e.get("sub", ""))) + 90
    x0, y0 = e.get("x", 60) - (1 - p) * (w + 80), e.get("y", 560)
    lay = new_layer(); d = ImageDraw.Draw(lay)
    card(d, (x0, y0, x0 + w, y0 + 92), 0.85, 6, 2)
    d.rectangle((x0, y0, x0 + 9, y0 + 92), fill=col(C.colors["yellow"]) + (255,))
    text(d, (x0 + 28, y0 + 34), e["title"], "sans", 34, C.colors["white"], "lm", stroke=2)
    if e.get("sub"):
        text(d, (x0 + 28, y0 + 71), e["sub"], "mono", 22, C.colors["edge"], "lm")
    return apply_alpha(lay, f)

def el_flash(t, e):
    """Chớp toàn khung (nhấn mạnh cú đập/twist). 'dur' ngắn 0.15–0.3s."""
    dur = e.get("dur", 0.22)
    if not (e["t_in"] <= t < e["t_in"] + dur):
        return None
    a = e.get("alpha", 0.45) * (1 - A(t, e["t_in"], e["t_in"] + dur)) ** 2
    return Image.new("RGBA", (C.W, C.H), col(color_of(e, "color", "white")) + (int(255 * a),))

def el_redact(t, e):
    """Thanh đen quét che chữ/tên (kiểu hồ sơ mật)."""
    f = vis(t, e, 0.01, e.get("fade_out", 0.4))
    if f <= 0:
        return None
    lay = new_layer(); d = ImageDraw.Draw(lay)
    for i, (x0, y0, x1, y1) in enumerate(e["boxes"]):
        p = ss(A(t, e["t_in"] + i * 0.12, e["t_in"] + i * 0.12 + 0.3))
        d.rectangle((x0, y0, x0 + (x1 - x0) * p, y1), fill=(8, 8, 8, 255))
    return apply_alpha(lay, f)

def el_timeline(t, e):
    """Trục thời gian vẽ dần từ trái sang phải, mỗi mốc bật lên đúng lúc VO nhắc."""
    f = vis(t, e, 0.2, e.get("fade_out", 0.4))
    if f <= 0:
        return None
    lay = new_layer(); d = ImageDraw.Draw(lay)
    x0, x1, y = e["x0"], e["x1"], e["y"]
    p = ss(A(t, e["draw"][0], e["draw"][1]))
    edge = col(C.colors["edge"]) + (255,)
    d.line((x0, y, x0 + (x1 - x0) * p, y), fill=edge, width=5)
    for k, ev in enumerate(e["events"]):
        q = A(t, ev["t"], ev["t"] + 0.25)
        if q <= 0:
            continue
        x = x0 + (x1 - x0) * ev["pos"]
        r = 11 * (1 + 0.6 * (1 - ss(q)))
        d.ellipse((x - r, y - r, x + r, y + r), fill=col(C.colors["yellow"]) + (255,))
        up = (k % 2 == 0)
        ly = y - 50 if up else y + 50
        l2 = new_layer(); d2 = ImageDraw.Draw(l2)
        text(d2, (x, ly), ev["label"], "sans", 28, C.colors["white"], "mm", stroke=2)
        if ev.get("sub"):
            text(d2, (x, ly + (-30 if up else 30)), ev["sub"], "mono", 20, C.colors["edge"], "mm")
        lay = comp(lay, apply_alpha(l2, q))
    return apply_alpha(lay, f)

def el_ticker(t, e):
    """Số chạy lên/xuống tuỳ ý (tiền, năm, mét, người...). Có 'pop' khi chạm đích."""
    f = vis(t, e, 0.2, e.get("fade_out", 0.4))
    if f <= 0:
        return None
    a, b = e["run"]
    u = A(t, a, b) ** e.get("power", 2.0)
    v = e["from"] + (e["to"] - e["from"]) * u
    s = f"{e.get('prefix', '')}{int(round(v)):,}{e.get('suffix', '')}"
    done = t >= b
    size = e["size"] * (1 + 0.25 * (1 - ss(A(t, b, b + 0.25)))) if done else e["size"]
    lay = new_layer(); d = ImageDraw.Draw(lay)
    text(d, e["pos"], s, "sans", size, color_of(e, "end_color", "yellow") if done else color_of(e, "color", "white"),
         e.get("anchor", "mm"), stroke=5)
    if e.get("label"):
        text(d, (e["pos"][0], e["pos"][1] + e["size"] * 0.75), e["label"], "sans", e.get("label_size", 34),
             C.colors["cream"], e.get("anchor", "mm"), stroke=3)
    return apply_alpha(lay, f)

def el_rain(t, e):
    """Mưa rơi thật trong khung: 3 lớp sâu (xa mảnh/chậm, gần dài/nhanh). Vị trí là hàm của t -> không cần lưu trạng thái."""
    f = vis(t, e, e.get("fade_in", 0.6), e.get("fade_out", 0.8))
    if f <= 0:
        return None
    key = ("rain", id(e))
    if key not in C.cache:
        rng = np.random.default_rng(e.get("seed", 7))
        n = int(e.get("density", 220))
        C.cache[key] = (rng.random(n), rng.random(n), rng.integers(0, 3, n))
    rx, ry, dp = C.cache[key]
    ang = math.radians(e.get("angle", 14))
    spd = e.get("speed", 1500)
    lay = np.zeros((C.H, C.W, 4), np.uint8)
    base = e.get("alpha", 0.40)
    pad = 200
    for i in range(len(rx)):
        k = 0.55 + 0.45 * dp[i] / 2.0
        vy, vx = spd * k * math.cos(ang), spd * k * math.sin(ang)
        x = (rx[i] * (C.W + 2 * pad) + vx * t) % (C.W + 2 * pad) - pad
        y = (ry[i] * (C.H + 2 * pad) + vy * t) % (C.H + 2 * pad) - pad
        ln = e.get("length", 70) * k
        x2, y2 = x - ln * math.sin(ang), y - ln * math.cos(ang)
        a = int(255 * base * (0.5 + 0.5 * dp[i] / 2.0))
        cv2.line(lay, (int(x), int(y)), (int(x2), int(y2)), (205, 215, 230, a), 1 + int(dp[i] >= 2), cv2.LINE_AA)
    return apply_alpha(Image.fromarray(lay, "RGBA"), f)

def _mist_tex(seed, scale):
    rng = np.random.default_rng(seed)
    w = C.W * 2
    small = rng.random((max(4, C.H // scale), max(8, w // scale))).astype(np.float32)
    big = cv2.resize(small, (w, C.H), interpolation=cv2.INTER_CUBIC)
    big = cv2.GaussianBlur(big, (0, 0), scale * 0.6)
    big = (big - big.min()) / (big.max() - big.min() + 1e-6)
    return big

def el_mist(t, e):
    """Sương/khói trôi ngang: 2 lớp nhiễu mịn cuộn ở tốc độ khác nhau (thị sai nhẹ)."""
    f = vis(t, e, e.get("fade_in", 1.0), e.get("fade_out", 1.0))
    if f <= 0:
        return None
    if "mist" not in C.cache:
        C.cache["mist"] = [_mist_tex(11, 90), _mist_tex(23, 45)]
    out = np.zeros((C.H, C.W), np.float32)
    for k, tex in enumerate(C.cache["mist"]):
        off = (e.get("speed", 18) * (1 + 0.8 * k) * t) % C.W
        i0 = int(off); fr = off - i0
        a = tex[:, i0:i0 + C.W]; b = tex[:, i0 + 1:i0 + 1 + C.W]
        if b.shape[1] < C.W:
            b = np.concatenate([b, tex[:, :C.W - b.shape[1]]], 1)
        out += (a * (1 - fr) + b * fr) * (0.6 if k == 0 else 0.4)
    al = np.clip((out - e.get("floor", 0.45)) * e.get("gain", 2.2), 0, 1) * e.get("opacity", 0.30) * f
    if "y_fade" in e:   # chỉ phủ dải ngang (ví dụ gần mặt đất): [y0,y1]
        y0, y1 = e["y_fade"]
        yy = np.arange(C.H, dtype=np.float32)
        al *= np.clip(1 - np.abs((yy - (y0 + y1) / 2) / ((y1 - y0) / 2)), 0, 1)[:, None]
    col_ = color_of(e, "color", [235, 235, 225])
    lay = np.zeros((C.H, C.W, 4), np.uint8)
    lay[..., 0], lay[..., 1], lay[..., 2] = col_
    lay[..., 3] = (al * 255).astype(np.uint8)
    return Image.fromarray(lay, "RGBA")

def el_dim(t, e):
    """Phủ đen tăng/giảm dần (tối dần cho nhịp 'im lặng', hoặc sáng lại). alpha: [a0,a1] giữa t_in và t_out."""
    u = ss(A(t, e["t_in"], e["t_out"]))
    a = lerp(e["alpha"], u)
    if "t_end" in e:   # giữ rồi nhả: sáng lại sau t_end trong fade_out giây
        a *= 1 - ss(A(t, e["t_end"], e["t_end"] + e.get("fade_out", 0.6)))
    if a <= 0.003:
        return None
    return Image.new("RGBA", (C.W, C.H), col(e.get("color", [0, 0, 0])) + (int(255 * a),))

def _clauses(e):
    key = ("cap", id(e))
    if key not in C.cache:
        import re
        W_ = json.load(open(os.path.join(C.root, e["wordts"]), encoding="utf-8"))
        rep = e.get("replace", {})
        gap = e.get("gap", 0.35)
        out, cur = [], []
        for k, (a, b, w) in enumerate(W_):
            w = w.strip()
            base = re.sub(r"[^A-Za-z0-9']", "", w)
            if base in rep:
                w = w.replace(base, rep[base])
            cur.append((w, a, b))
            if k + 1 == len(W_) or W_[k + 1][0] - b >= gap:
                out.append((cur[0][1], cur[-1][2], cur)); cur = []
        C.cache[key] = out
    return C.cache[key]

def el_captions(t, e):
    """Phụ đề điện ảnh theo mệnh đề của lời đọc; từ đã đọc sáng, từ chưa đọc mờ (karaoke nhẹ)."""
    for t0, t1, words in _clauses(e):
        if t0 - 0.08 <= t < t1 + 0.4:
            break
    else:
        return None
    f = min(A(t, t0 - 0.08, t0 + 0.12), 1 - A(t, t1 + 0.1, t1 + 0.4))
    if f <= 0:
        return None
    kind, size = e.get("font", "serif"), e.get("size", 40)
    fnt = font(kind, size)
    maxw = e.get("max_width", 980)
    lines, cur, w = [], [], 0.0
    sp = fnt.getlength(" ")
    for item in words:
        wl = fnt.getlength(item[0])
        if cur and w + sp + wl > maxw:
            lines.append((cur, w)); cur, w = [], 0.0
        w += (sp if cur else 0) + wl; cur.append((item, wl))
    lines.append((cur, w))
    lay = new_layer(); d = ImageDraw.Draw(lay)
    bar = int((C.H - C.W / C.style["letterbox"]) / 2) if C.style.get("letterbox") else 0
    y = e.get("y", C.H - bar - 90) - (len(lines) - 1) * size * 0.6
    for ln, lw in lines:
        x = C.W / 2 - lw / 2
        for (wd, a, b), wl in ln:
            al = 255 if (not e.get("karaoke", True) or t >= a - 0.02) else 120
            d.text((x, y), wd, font=fnt, fill=col(color_of(e, "color", "white")) + (al,), anchor="lm",
                   stroke_width=e.get("stroke", 3), stroke_fill=(0, 0, 0, int(al * 0.9)))
            x += wl + sp
        y += size * 1.2
    return apply_alpha(lay, f)

def el_kinetic(t, e):
    """Từ khoá bật to đúng lúc được nói (scale-pop), tự biến mất. words:[{text,t_in,t_out,pos,size,color}]"""
    lay = None
    for w in e["words"]:
        if not (w["t_in"] <= t < w["t_out"] + 0.2):
            continue
        p = A(t, w["t_in"], w["t_in"] + 0.18)
        f = p * (1 - A(t, w["t_out"], w["t_out"] + 0.2))
        size = w.get("size", e.get("size", 120)) * (1 + 0.55 * (1 - ss(p)) ** 1.5)
        l2 = new_layer(); d2 = ImageDraw.Draw(l2)
        text(d2, w.get("pos", [640, 360]), w["text"], w.get("font", e.get("font", "sans")), size,
             color_of(w, "color", "white"), "mm", stroke=w.get("stroke", 5))
        l2 = apply_alpha(l2, f)
        lay = l2 if lay is None else comp(lay, l2)
    return lay

# ---------- FX: chuyển động BÊN TRONG ảnh tĩnh (áp lên ảnh nguồn 2560x1440 trước camera -> bám đúng ảnh) ----------
def _grid(h, w):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    return xx, yy

def _feather(h, w, fe):
    m = np.zeros((h, w), np.float32)
    fe = int(min(fe, h // 3, w // 3))
    m[fe:h - fe, fe:w - fe] = 1.0
    return cv2.GaussianBlur(m, (0, 0), max(fe / 2.0, 1))

def fx_ripple(im, fx, tl):
    """Mặt nước gợn: ripple ngang + lung linh, mạnh dần về phía gần camera. box=[x0,y0,x1,y1] theo ảnh nguồn."""
    x0, y0, x1, y1 = fx["box"]
    key = ("rip", id(fx))
    if key not in C.cache:
        h, w = y1 - y0, x1 - x0
        xx, yy = _grid(h, w)
        C.cache[key] = (xx, yy, _feather(h, w, fx.get("feather", 60)), 0.35 + 0.65 * yy / h)
    xx, yy, m, pr = C.cache[key]
    amp, wl, sp = fx.get("amp", 5), fx.get("wavelength", 80), fx.get("speed", 1.0)
    dy = amp * pr * np.sin(2 * np.pi * (yy / (wl * pr) - sp * tl))
    dx = 0.6 * amp * pr * np.sin(2 * np.pi * (xx / (1.7 * wl) + 0.7 * sp * tl + yy / (3 * wl)))
    roi = im[y0:y1, x0:x1]
    im[y0:y1, x0:x1] = cv2.remap(roi, xx + dx * m, yy + dy * m, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT101)
    return im

def fx_sway(im, fx, tl):
    """Tán lá/cỏ đung đưa trong gió: vùng box dịch ngang, mạnh dần lên phía trên (gốc đứng yên ở đáy box)."""
    x0, y0, x1, y1 = fx["box"]
    key = ("sway", id(fx))
    if key not in C.cache:
        h, w = y1 - y0, x1 - x0
        xx, yy = _grid(h, w)
        C.cache[key] = (xx, yy, _feather(h, w, fx.get("feather", 80)), ((h - yy) / h) ** 1.5)
    xx, yy, m, wg = C.cache[key]
    amp, f = fx.get("amp", 8), fx.get("freq", 0.35)
    dx = amp * wg * (np.sin(2 * np.pi * f * tl + xx / fx.get("spatial", 260)) +
                     0.5 * np.sin(2 * np.pi * 1.9 * f * tl + xx / 140 + 1.3))
    roi = im[y0:y1, x0:x1]
    im[y0:y1, x0:x1] = cv2.remap(roi, xx - dx * m, yy - 0.25 * dx * m, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT101)
    return im

def fx_glow(im, fx, tl):
    """Quầng sáng cộng thêm (đèn, lửa, nắng, tia sét): nhịp thở pulse_hz + nhấp nháy ngẫu nhiên mượt flicker."""
    cx, cy = fx["pos"]; r = fx.get("r", 220)
    key = ("glow", id(fx))
    if key not in C.cache:
        x0, y0 = int(max(cx - 3 * r, 0)), int(max(cy - 3 * r, 0))
        x1, y1 = int(min(cx + 3 * r, 2560)), int(min(cy + 3 * r, 1440))
        xx, yy = _grid(y1 - y0, x1 - x0)
        d2 = ((xx + x0 - cx) ** 2 + (yy + y0 - cy) ** 2) / (r * r)
        C.cache[key] = (x0, y0, x1, y1, np.exp(-d2)[..., None].astype(np.float32))
    x0, y0, x1, y1, m = C.cache[key]
    k = fx.get("strength", 0.5) * (1 + fx.get("pulse", 0.2) * math.sin(2 * math.pi * fx.get("pulse_hz", 0.5) * tl) +
                                    fx.get("flicker", 0.0) * (math.sin(tl * 13.1) + 0.5 * math.sin(tl * 29.7 + 1)) / 1.5)
    k = max(k, 0.0)
    c = np.array(fx.get("color", [255, 200, 120]), np.float32)
    im[y0:y1, x0:x1] = np.clip(im[y0:y1, x0:x1].astype(np.float32) + m * c * k * 255 / 255.0 * 0.6, 0, 255).astype(np.uint8)
    return im

def fx_parallax(im, fx, tl):
    """Thị sai 2.5D: dịch từng điểm ảnh theo ĐỘ SÂU (gần dịch nhiều, xa dịch ít) -> máy quay như đi xuyên khung.
    depth: 'auto_ground' (đáy ảnh = gần, đỉnh = xa; hợp phong cảnh) hoặc đường dẫn ảnh xám (trắng = gần)."""
    key = ("par", id(fx))
    if key not in C.cache:
        H_, W_ = im.shape[:2]
        xx, yy = _grid(H_, W_)
        dsp = fx.get("depth", "auto_ground")
        if dsp == "auto_ground":
            d = ss_arr(yy / H_)
        else:
            g = cv2.imread(os.path.join(C.root, dsp), cv2.IMREAD_GRAYSCALE)
            d = cv2.resize(g, (W_, H_), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0
            d = cv2.GaussianBlur(d, (0, 0), 6)
        C.cache[key] = (xx, yy, d - fx.get("focus", 0.5))
    xx, yy, d = C.cache[key]
    per = fx.get("period", 9.0)
    s1 = math.sin(2 * math.pi * tl / per)
    s2 = math.sin(2 * math.pi * tl / (per * 1.4) + 1.0)
    a = fx.get("amp", 28)
    return cv2.remap(im, xx + a * d * s1, yy + 0.35 * a * d * s2, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)

def ss_arr(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)

FX = {"ripple": fx_ripple, "sway": fx_sway, "glow": fx_glow, "parallax": fx_parallax}

def el_particles(t, e):
    """Hạt chuyển động trong khung: dust (bụi sáng trôi), embers (tàn lửa bay lên), snow (tuyết/tro rơi). 3 độ sâu."""
    f = vis(t, e, e.get("fade_in", 1.0), e.get("fade_out", 1.0))
    if f <= 0:
        return None
    key = ("prt", id(e))
    n = int(e.get("n", 80))
    if key not in C.cache:
        rng = np.random.default_rng(e.get("seed", 3))
        C.cache[key] = (rng.random(n), rng.random(n), rng.random(n), rng.random(n))
    rx, ry, z, ph = C.cache[key]
    kind = e.get("kind", "dust")
    base = e.get("alpha", 0.55)
    lay = np.zeros((C.H, C.W, 4), np.uint8)
    cr = col(color_of(e, "color", [255, 230, 170] if kind != "embers" else [255, 140, 50]))
    for i in range(n):
        k = 0.4 + 0.6 * z[i]
        if kind == "dust":
            x = (rx[i] * C.W + e.get("speed", 10) * k * t + 14 * math.sin(t * 0.5 + ph[i] * 6.28)) % C.W
            y = (ry[i] * C.H - e.get("rise", 6) * k * t) % C.H
            r = 1.0 + 2.6 * z[i]; a = base * (0.35 + 0.65 * z[i]) * (0.65 + 0.35 * math.sin(t * 0.9 + ph[i] * 6.28))
        elif kind == "embers":
            x = (rx[i] * C.W + 30 * math.sin(t * 1.3 + ph[i] * 6.28) + e.get("drift", 12) * t) % C.W
            y = (ry[i] * C.H - e.get("rise", 70) * k * t) % C.H
            r = 1.0 + 2.2 * z[i]; a = base * (0.5 + 0.5 * math.sin(t * 7 + ph[i] * 20))
        else:   # snow
            x = (rx[i] * C.W + 22 * math.sin(t * 0.9 + ph[i] * 6.28) + e.get("drift", -10) * t) % C.W
            y = (ry[i] * C.H + e.get("fall", 55) * k * t) % C.H
            r = 1.2 + 2.8 * z[i]; a = base * (0.4 + 0.6 * z[i])
        a = max(0.0, min(1.0, a))
        cv2.circle(lay, (int(x), int(y)), int(r * 2.4) + 1, cr + (int(255 * a * 0.22),), -1, cv2.LINE_AA)   # quầng
        cv2.circle(lay, (int(x), int(y)), max(int(r), 1), cr + (int(255 * a),), -1, cv2.LINE_AA)
    return apply_alpha(Image.fromarray(lay, "RGBA"), f)

def el_video_overlay(t, e):
    """Chồng một clip video (sương, khói, mưa, bụi...) lên khung. blend: screen (nền đen->trong suốt) | normal."""
    f = vis(t, e, e.get("fade_in", 0.8), e.get("fade_out", 0.8))
    if f <= 0:
        return None
    fr = video_frame(os.path.join(C.root, e["file"]), t - e["t_in"], e.get("speed", 1.0))
    fr = cv2.resize(fr, (C.W, C.H), interpolation=cv2.INTER_LINEAR)
    op = e.get("opacity", 0.5)
    if e.get("blend", "screen") == "screen":
        al = fr.max(axis=2).astype(np.float32) / 255.0 * op
    else:
        al = np.full((C.H, C.W), op, np.float32)
    lay = np.dstack([fr, (al * 255).astype(np.uint8)])
    return apply_alpha(Image.fromarray(lay, "RGBA"), f)


# ------------------------------------------------------------------ NHÓM CHỒNG LỚP "SỔ TAY / TƯ LIỆU / TRUYỆN TRANH"
_IMG_CACHE = {}
def _rgba_img(path, crop=None):
    key = (path, tuple(crop) if crop else None)
    if key not in _IMG_CACHE:
        im = Image.open(os.path.join(C.root, path)).convert("RGBA")
        if crop:
            sx, sy = im.width / 2560.0, im.height / 1440.0   # crop theo toạ độ nguồn 2560x1440
            im = im.crop((int(crop[0] * sx), int(crop[1] * sy), int(crop[2] * sx), int(crop[3] * sy)))
        _IMG_CACHE[key] = im
    return _IMG_CACHE[key]

def _place(lay, piece, cx, cy, angle=0.0, alpha=1.0, scale=1.0, shadow=True):
    """Dán một mảnh RGBA (đã vẽ sẵn) vào layer: xoay, co giãn, đổ bóng mềm."""
    if scale != 1.0:
        piece = piece.resize((max(1, int(piece.width * scale)), max(1, int(piece.height * scale))), Image.LANCZOS)
    if angle:
        piece = piece.rotate(angle, resample=Image.BICUBIC, expand=True)
    if shadow:
        sh = Image.new("RGBA", piece.size, (0, 0, 0, 0))
        sh.putalpha(piece.getchannel("A").point(lambda v: int(v * 0.45)))
        sh = sh.filter(ImageFilter.GaussianBlur(7))
        lay.alpha_composite(apply_alpha(sh, alpha), (int(cx - piece.width / 2 + 6), int(cy - piece.height / 2 + 9)))
    lay.alpha_composite(apply_alpha(piece, alpha), (int(cx - piece.width / 2), int(cy - piece.height / 2)))
    return lay

def _drop(t, e, d=0.45):
    """hiệu ứng thả xuống bàn: to hơn + nghiêng hơn rồi đặt xuống."""
    p = ss(A(t, e["t_in"], e["t_in"] + d))
    return p, 1.0 + 0.18 * (1 - p), e.get("angle", -4) + 6 * (1 - p)

def el_photo_pin(t, e):
    """Ảnh in (polaroid) ghim/dán băng keo lên khung: ảnh khác hoặc crop cận từ ảnh nguồn.
    {src, crop?[x0,y0,x1,y1 nguồn 2560x1440], pos[x,y], w, angle, caption?, tape?:true}"""
    f = vis(t, e, 0.2, e.get("fade_out", 0.4))
    if f <= 0:
        return None
    im = _rgba_img(e["src"], e.get("crop"))
    w = int(e.get("w", 360)); h = int(w * im.height / im.width)
    m, mb = int(w * 0.05), int(w * (0.20 if e.get("caption") else 0.05))
    pc = Image.new("RGBA", (w + 2 * m, h + m + mb), (246, 242, 232, 255))
    pc.alpha_composite(im.resize((w, h), Image.LANCZOS), (m, m))
    d = ImageDraw.Draw(pc)
    if e.get("caption"):
        text(d, (pc.width / 2, h + m + mb / 2), e["caption"], e.get("font", "serif"), int(mb * 0.42), (60, 52, 44))
    if e.get("tape", True):
        tp = Image.new("RGBA", (int(w * 0.32), int(w * 0.09)), (232, 222, 190, 190))
        pc2 = Image.new("RGBA", (pc.width, pc.height + tp.height // 2), (0, 0, 0, 0))
        pc2.alpha_composite(pc, (0, tp.height // 2)); pc2.alpha_composite(tp, (pc.width // 2 - tp.width // 2, 0))
        pc = pc2
    p, sc_, ang = _drop(t, e)
    return _place(new_layer(), pc, *e["pos"], angle=ang, alpha=f * p, scale=sc_)

def _wobble_ellipse(cx, cy, rx, ry, n=90, turns=1.12, seed=3):
    rng = np.random.default_rng(seed); pts = []
    for i in range(n + 1):
        a = -math.pi / 2 + 2 * math.pi * turns * i / n
        r = 1 + 0.035 * math.sin(i * 0.31 + seed) + 0.02 * rng.normal()
        pts.append((cx + rx * r * math.cos(a), cy + ry * r * math.sin(a)))
    return pts

def el_marker(t, e):
    """Nét bút dạ vẽ tay tự hiện ra: kind circle | arrow | underline.
    circle: {box[x0,y0,x1,y1]}; arrow: {from[x,y], to[x,y]}; underline: {from, to}. Toạ độ màn hình 1280x720,
    hoặc thêm "scene" để toạ độ là ảnh nguồn (bám camera)."""
    f = vis(t, e, 0.05, e.get("fade_out", 0.4))
    if f <= 0:
        return None
    p = ss(A(t, e["t_in"], e["t_in"] + e.get("draw", 0.6)))
    def S(x, y):
        if e.get("scene"):
            a, b, _ = to_screen(C.scene_by_id[e["scene"]], t, x, y); return a, b
        return x, y
    c = col(color_of(e, "color", "red")) + (235,)
    w = int(e.get("width", 7))
    lay = new_layer(); d = ImageDraw.Draw(lay)
    k = e.get("kind", "circle")
    if k == "circle":
        x0, y0 = S(*e["box"][:2]); x1, y1 = S(*e["box"][2:])
        pts = _wobble_ellipse((x0 + x1) / 2, (y0 + y1) / 2, abs(x1 - x0) / 2 * 1.12, abs(y1 - y0) / 2 * 1.18, seed=e.get("seed", 3))
        pts = pts[:max(2, int(len(pts) * p))]
    else:
        (ax, ay), (bx, by) = S(*e["from"]), S(*e["to"])
        n = 40; bend = e.get("bend", 0.12 if k == "arrow" else 0.02)
        nx, ny = -(by - ay) * bend, (bx - ax) * bend
        pts = [(ax + (bx - ax) * i / n + nx * math.sin(math.pi * i / n), ay + (by - ay) * i / n + ny * math.sin(math.pi * i / n)) for i in range(n + 1)]
        pts = pts[:max(2, int(len(pts) * p))]
    d.line(pts, fill=c, width=w, joint="curve")
    if k == "arrow" and p > 0.97:
        (x1, y1), (x0, y0) = pts[-1], pts[-4]
        ang = math.atan2(y1 - y0, x1 - x0); L = w * 4.2
        for s_ in (2.55, -2.55):
            d.line((x1, y1, x1 + L * math.cos(ang + s_), y1 + L * math.sin(ang + s_)), fill=c, width=w)
    if e.get("label") and p > 0.9:
        lx, ly = e.get("label_pos", pts[-1])
        text(d, (lx, ly), e["label"], e.get("font", "sans"), e.get("size", 30), color_of(e, "color", "red"), "mm", stroke=3)
    return apply_alpha(lay, f)

def _torn(w, h, seed=5, jag=5):
    rng = np.random.default_rng(seed); pts = []
    for x in range(0, w + 1, 9): pts.append((x, rng.integers(0, jag)))
    for y in range(0, h + 1, 9): pts.append((w - rng.integers(0, jag), y))
    for x in range(w, -1, -9): pts.append((x, h - rng.integers(0, jag)))
    for y in range(h, -1, -9): pts.append((rng.integers(0, jag), y))
    return [(int(a), int(b)) for a, b in pts]

def el_clipping(t, e):
    """Mẩu báo cắt / giấy tư liệu mép rách: {pos, w, headline, sub?, lines?(số dòng chữ giả), angle, kind: news|note}"""
    f = vis(t, e, 0.2, e.get("fade_out", 0.4))
    if f <= 0:
        return None
    w = int(e.get("w", 420)); kind = e.get("kind", "news")
    hs = int(e.get("size", 34)); lines = e.get("lines", 4 if kind == "news" else 0)
    hl = e["headline"].split("\n")
    h = int(24 + len(hl) * hs * 1.15 + (30 if e.get("sub") else 0) + lines * 15 + 24)
    paper = (240, 234, 216, 255) if kind == "news" else (252, 236, 140, 255)
    pc = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(pc)
    d.polygon(_torn(w, h, e.get("seed", 5)), fill=paper)
    y = 18
    for ln in hl:
        text(d, (w / 2, y + hs * 0.55), ln, e.get("font", "serif"), hs, (30, 26, 22)); y += hs * 1.15
    if e.get("sub"):
        text(d, (w / 2, y + 14), e["sub"], "mono", 18, (95, 85, 70)); y += 30
    if kind == "news":
        d.line((22, y + 4, w - 22, y + 4), fill=(60, 52, 44, 255), width=2); y += 14
        rng = np.random.default_rng(e.get("seed", 5))
        for i in range(lines):
            ww = w - 44 - (rng.integers(0, w // 3) if i == lines - 1 else 0)
            d.rectangle((22, y, 22 + ww, y + 6), fill=(150, 140, 125, 255)); y += 15
    p, sc_, ang = _drop(t, e)
    return _place(new_layer(), pc, *e["pos"], angle=ang, alpha=f * p, scale=sc_)

def el_speech_box(t, e):
    """Ô lời dẫn kiểu truyện tranh: khung mực đen, nền vàng nhạt, chữ IN HOA; tail?[x,y] chỉ vào nhân vật."""
    f = vis(t, e, 0.12, e.get("fade_out", 0.3))
    if f <= 0:
        return None
    size = int(e.get("size", 30)); fnt = font(e.get("font", "sans"), size)
    lines = e["text"].split("\n"); tw = max(fnt.getlength(l) for l in lines)
    pad = 18; w, h = int(tw + 2 * pad), int(len(lines) * size * 1.2 + 2 * pad)
    x, y = e["pos"]; x0, y0 = x - w / 2, y - h / 2
    lay = new_layer(); d = ImageDraw.Draw(lay)
    p = ss(A(t, e["t_in"], e["t_in"] + 0.2)); sc_ = 0.85 + 0.15 * p
    bw, bh = w * sc_, h * sc_; x0, y0 = x - bw / 2, y - bh / 2
    fill = tuple(e.get("fill", [255, 244, 190])) + (255,); ink = (18, 16, 14, 255)
    if e.get("tail"):
        tx, ty = e["tail"]
        d.polygon([(x - bw * 0.12, y + bh / 2 - 2), (x + bw * 0.06, y + bh / 2 - 2), (tx, ty)], fill=fill, outline=ink)
    d.rectangle((x0, y0, x0 + bw, y0 + bh), fill=fill, outline=ink, width=4)
    if e.get("tail"):
        d.line((x - bw * 0.12 + 3, y + bh / 2 - 2, x + bw * 0.06 - 3, y + bh / 2 - 2), fill=fill, width=5)
    for i, l in enumerate(lines):
        text(d, (x, y0 + pad * sc_ + (i + 0.5) * size * 1.2 * sc_), l, e.get("font", "sans"), int(size * sc_), (18, 16, 14))
    return apply_alpha(lay, f * p)

def el_route(t, e):
    """Đường đi trên bản đồ/ảnh tự vẽ ra (nét đứt) + chấm mốc + nhãn. {points[[x,y],...], labels?[...], scene?, draw}"""
    f = vis(t, e, 0.1, e.get("fade_out", 0.5))
    if f <= 0:
        return None
    P = e["points"]
    if e.get("scene"):
        P = [to_screen(C.scene_by_id[e["scene"]], t, x, y)[:2] for x, y in P]
    seg = [math.dist(P[i], P[i + 1]) for i in range(len(P) - 1)]; tot = sum(seg) or 1
    p = ss(A(t, e["t_in"], e["t_in"] + e.get("draw", 1.6))) * tot
    lay = new_layer(); d = ImageDraw.Draw(lay)
    c = col(color_of(e, "color", "yellow")) + (255,); w = int(e.get("width", 5)); dash = 16
    run = 0.0
    for i, L in enumerate(seg):
        (ax, ay), (bx, by) = P[i], P[i + 1]
        k = 0.0
        while k < L and run + k < p:
            k2 = min(k + dash, L, p - run)
            d.line((ax + (bx - ax) * k / L, ay + (by - ay) * k / L, ax + (bx - ax) * k2 / L, ay + (by - ay) * k2 / L), fill=c, width=w)
            k += dash * 1.7
        run += L
    run = 0.0
    labels = e.get("labels", [])
    for i, (x, y) in enumerate(P):
        if p + 0.5 >= run:
            d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=c, outline=(20, 18, 16, 255), width=3)
            if i < len(labels) and labels[i]:
                text(d, (x, y - 26), labels[i], "mono", 22, C.colors["cream"], "mm", stroke=3)
        if i < len(seg): run += seg[i]
    return apply_alpha(lay, f)

TYPES = {
    "photo_pin": el_photo_pin, "marker": el_marker, "clipping": el_clipping,
    "speech_box": el_speech_box, "route": el_route,
    "particles": el_particles, "video_overlay": el_video_overlay,
    "captions": el_captions, "kinetic": el_kinetic,
    "rain": el_rain, "mist": el_mist, "dim": el_dim,
    "spotlight": el_spotlight, "highlight_box": el_highlight_box, "stamp": el_stamp,
    "lower_third": el_lower_third, "flash": el_flash, "redact": el_redact,
    "timeline": el_timeline, "ticker": el_ticker,
    "typed_card": el_typed_card, "badge_pop": el_badge_pop, "gauge": el_gauge,
    "anchored_circle": el_anchored_circle, "counter_down": el_counter_down,
    "label": el_label, "strike_cards": el_strike_cards,
    "question_card": el_question_card, "day_ticker": el_day_ticker,
}

# ------------------------------------------------------------------ khung hình
def post(arr, idx):
    """Hậu kỳ toàn khung (sau overlay): bụi/xước phim, dải đen letterbox, khung 4:3 pillarbox."""
    st = C.style
    if not st:
        return arr
    arr = np.array(arr)
    if st.get("scratches"):
        rng = np.random.default_rng(10_000 + idx // 2)     # đổi mỗi 2 khung -> cảm giác 15fps của phim cũ
        for _ in range(int(rng.poisson(5))):
            x, y, r = int(rng.integers(0, C.W)), int(rng.integers(0, C.H)), int(rng.integers(1, 3))
            cv2.circle(arr, (x, y), r, (25, 22, 18) if rng.random() < 0.6 else (225, 218, 200), -1, cv2.LINE_AA)
        if rng.random() < 0.28:
            ov = arr.copy(); x = int(rng.integers(0, C.W)); y0 = int(rng.integers(0, C.H // 2)); y1 = y0 + int(rng.integers(120, C.H // 2))
            cv2.line(ov, (x, y0), (x + int(rng.integers(-3, 4)), y1), (235, 230, 215), 1, cv2.LINE_AA)
            arr = cv2.addWeighted(ov, 0.45, arr, 0.55, 0)
    if st.get("paper"):   # vân giấy tĩnh (tạo 1 lần), nhân vào khung -> cảm giác tranh in
        if getattr(C, "_paper", None) is None or C._paper.shape[:2] != (C.H, C.W):
            rng = np.random.default_rng(7)
            n = rng.normal(0, 1, (C.H // 2, C.W // 2)).astype(np.float32)
            n = cv2.GaussianBlur(n, (0, 0), 1.2) + 0.6 * cv2.GaussianBlur(rng.normal(0, 1, (C.H // 2, C.W // 2)).astype(np.float32), (0, 0), 9)
            n = cv2.resize(n, (C.W, C.H)); n = n / (np.abs(n).max() + 1e-6)
            C._paper = (1 + st["paper"] * n)[..., None]
        arr = np.clip(arr.astype(np.float32) * C._paper, 0, 255).astype(np.uint8)
    if st.get("border"):   # viền ảnh in (kiểu ảnh kỷ niệm): {"w": px, "color": [r,g,b]}
        b = st["border"]; w = int(b.get("w", 18)); col = tuple(int(c) for c in b.get("color", [240, 232, 214]))
        arr[:w] = col; arr[-w:] = col; arr[:, :w] = col; arr[:, -w:] = col
        if b.get("shadow", True):
            ov = arr.copy(); cv2.rectangle(ov, (w, w), (C.W - w - 1, C.H - w - 1), (60, 50, 40), 2, cv2.LINE_AA)
            arr = cv2.addWeighted(ov, 0.35, arr, 0.65, 0)
    if st.get("ink_frame"):   # khung mực kiểu ô truyện tranh: {"w": độ dày nét, "margin": lề}
        f = st["ink_frame"]; m = int(f.get("margin", 14)); th = int(f.get("w", 5))
        arr[:m] = 245; arr[-m:] = 245; arr[:, :m] = 245; arr[:, -m:] = 245
        cv2.rectangle(arr, (m, m), (C.W - m - 1, C.H - m - 1), (18, 16, 14), th, cv2.LINE_AA)
    if st.get("letterbox"):
        h = int((C.H - C.W / st["letterbox"]) / 2)
        if h > 0:
            arr[:h] = 0; arr[-h:] = 0
    if st.get("pillarbox"):
        w = int((C.W - C.H * st["pillarbox"]) / 2)
        if w > 0:
            arr[:, :w] = 0; arr[:, -w:] = 0
    return arr

def frame(i):
    t = i / C.FPS
    bg = finish_bg(background(t), i)
    base = Image.fromarray(bg.clip(0, 255).astype(np.uint8), "RGB").convert("RGBA")
    for e in C.elements:
        lay = TYPES[e["type"]](t, e)
        if lay is not None:
            base = comp(base, lay)
    return post(np.asarray(base.convert("RGB")), i)

PRESETS = {
    # phim cũ / bản tin xưa: đen trắng ngả nâu, hạt thô, nhấp nháy, vết xước; full 16:9
    # (muốn khung 4:3 thì tự thêm "style": {"pillarbox": 1.37} vào spec — mặc định tắt vì video phải full 16:9)
    "newsreel": {"grain": 6.0, "vignette": 0.55, "warm": [1.0, 1.0, 1.0], "flicker": 0.03,
                 "grade": {"bw": 1.0, "tint": [1.12, 0.98, 0.78], "contrast": 1.15},
                 "style": {"scratches": True},
                 "colors": {"yellow": [236, 214, 160], "red": [170, 60, 50], "cream": [240, 228, 200],
                            "edge": [210, 198, 165], "card": [24, 20, 14]}},
    # điện ảnh tối giản: full khung 16:9 (KHÔNG dải đen), phụ đề serif, ít hạt, màu gần tự nhiên
    # (muốn dải đen thì tự thêm "style": {"letterbox": 2.39} vào spec — mặc định tắt)
    "cinematic": {"grain": 2.4, "vignette": 0.32, "warm": [1.02, 1.0, 0.98], "flicker": 0.0,
                  "grade": {"contrast": 1.08}},
    # chữ chạy theo lời: nền tối hơn, chữ to bật lên đúng từ khoá
    "kinetic": {"grain": 3.0, "vignette": 0.5, "grade": {"contrast": 1.1}},
    # sách truyện: tông ấm, màu dịu, vân giấy nhẹ — hợp ảnh minh hoạ hoạt hình, kể chuyện chậm
    "storybook": {"grain": 0.8, "vignette": 0.22, "warm": [1.03, 1.0, 0.95], "flicker": 0.0,
                  "grade": {"sat": 0.92, "contrast": 1.04, "lift": 6}, "style": {"paper": 0.06}},
    # kỷ niệm / hoài niệm (khán giả 55+): màu bạc nhẹ, đen nâng, hạt mịn, viền ảnh in màu kem
    "memory": {"grain": 2.6, "vignette": 0.35, "warm": [1.06, 1.0, 0.9], "flicker": 0.008,
               "grade": {"sat": 0.78, "contrast": 0.98, "lift": 16},
               "style": {"border": {"w": 18, "color": [238, 230, 212]}}},
    # truyện tranh: màu rực hơn, tương phản, khung mực quanh ô hình, vân giấy
    "comic": {"grain": 0.6, "vignette": 0.12, "flicker": 0.0,
              "grade": {"sat": 1.15, "contrast": 1.12}, "style": {"ink_frame": {"w": 5, "margin": 14}, "paper": 0.04}},
    # tài liệu sạch: màu trung tính, gần như không hạt/vignette — để thẻ tư liệu, bản đồ, số liệu nói
    "documentary": {"grain": 0.4, "vignette": 0.15, "warm": [1.0, 1.0, 1.0], "flicker": 0.0,
                    "grade": {"sat": 0.96, "contrast": 1.03}},
}

def apply_preset(spec):
    p = PRESETS.get(spec.get("preset"), {})
    for k, v in p.items():
        if isinstance(v, dict):
            spec[k] = {**v, **spec.get(k, {})}
        else:
            spec.setdefault(k, v)
    return spec

def setup(spec, root):
    spec = apply_preset(spec)
    C.grade = spec.get("grade", {})
    C.style = spec.get("style", {})
    m = spec["meta"]
    C.W, C.H, C.FPS = m.get("width", 1280), m.get("height", 720), m.get("fps", 30)
    C.DUR = m["duration"]
    C.N = int(round(C.DUR * C.FPS))
    C.colors = {k: tuple(v) for k, v in spec["colors"].items()}
    C.font_paths = {k: os.path.join(root, v) for k, v in spec["fonts"].items()}
    C.root = root
    C.fonts = {}
    C.dissolve = spec.get("dissolve", 0.5)
    C.grain = spec.get("grain", 3.2)
    C.flicker = spec.get("flicker", 0.0)
    C.cache = {}
    yy, xx = np.mgrid[0:C.H, 0:C.W].astype(np.float32)
    rr = np.sqrt(((xx - C.W / 2) / (C.W / 2)) ** 2 + ((yy - C.H / 2) / (C.H / 2)) ** 2) / 1.414
    C.VIG = (1.0 - spec.get("vignette", 0.38) * np.clip(rr, 0, 1) ** 2.2)[..., None]
    C.WARM = np.array(spec.get("warm", [1.035, 1.0, 0.955]), np.float32)
    C.scenes = spec["scenes"]
    for sc in C.scenes:
        sc["_img"] = load_scene(sc, root)
    C.scene_by_id = {sc["id"]: sc for sc in C.scenes}
    C.elements = spec["elements"]

# ------------------------------------------------------------------ âm thanh
def build_audio(spec, root, out_wav):
    a = spec["audio"]
    total = a.get("total", spec["meta"]["duration"])
    inputs = [os.path.join(root, a["vo"]["file"])]
    loops = [False]   # track có "loop": true → lặp file ngắn cho đủ trim_end (nền dài)
    chains = [f"[0]aresample=48000,apad=whole_dur={total},atrim=0:{total},"
              f"volume={a['vo'].get('volume_db', 0)}dB[a0]"]
    for k, tr in enumerate(a["tracks"], start=1):
        inputs.append(os.path.join(root, tr["file"]))
        loops.append(bool(tr.get("loop")))
        ch = []
        if tr.get("trim_end"):
            ch.append(f"atrim=0:{tr['trim_end']}")
        if tr.get("fade_in"):
            ch.append(f"afade=t=in:st=0:d={tr['fade_in']}")
        if tr.get("fade_out"):
            ch.append(f"afade=t=out:st={tr['fade_out'][0]}:d={tr['fade_out'][1]}")
        ch.append(f"volume={tr.get('volume_db', 0)}dB")
        ch.append(f"adelay={int(round(tr['start'] * 1000))}:all=1")
        chains.append(f"[{k}]" + ",".join(ch) + f"[a{k}]")
    n = len(inputs)
    mix = "".join(f"[a{k}]" for k in range(n))
    chains.append(f"{mix}amix=inputs={n}:normalize=0:duration=longest,"
                  f"alimiter=limit=0.95,atrim=0:{total}[out]")
    cmd = ["ffmpeg", "-v", "error", "-y"]
    for p, lp in zip(inputs, loops):
        cmd += (["-stream_loop", "-1"] if lp else []) + ["-i", p]
    cmd += ["-filter_complex", ";".join(chains), "-map", "[out]", "-ar", "48000", "-ac", "1", out_wav]
    subprocess.run(cmd, check=True)

# ------------------------------------------------------------------ chính
def render_video(out_mp4, crf, jobs):
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{C.W}x{C.H}", "-r", str(C.FPS), "-i", "-", "-c:v", "libx264",
           "-preset", "medium", "-crf", str(crf), "-pix_fmt", "yuv420p", out_mp4]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    if jobs > 1:
        import multiprocessing as mp
        with mp.get_context("fork").Pool(jobs) as pool:
            for i, arr in enumerate(pool.imap(_frame_bytes, range(C.N), chunksize=4)):
                pr.stdin.write(arr)
                if i % 100 == 0:
                    print(f"frame {i}/{C.N}", flush=True)
    else:
        for i in range(C.N):
            pr.stdin.write(frame(i).tobytes())
            if i % 100 == 0:
                print(f"frame {i}/{C.N}", flush=True)
    pr.stdin.close()
    pr.wait()

def _frame_bytes(i):
    return frame(i).tobytes()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--out")
    ap.add_argument("--root")
    ap.add_argument("--frames", help="danh sách giây, ví dụ 1.0,5.5,9.8")
    ap.add_argument("--frames-dir", default=".")
    ap.add_argument("--video-only", action="store_true")
    ap.add_argument("--jobs", type=int, default=os.cpu_count() or 1)
    ap.add_argument("--crf", type=int, default=24)
    ap.add_argument("--lufs", type=float, default=-14.0, help="chuẩn hoá âm lượng master (0 = tắt)")
    a = ap.parse_args()
    root = a.root or os.path.dirname(os.path.abspath(a.spec))
    spec = json.load(open(a.spec, encoding="utf-8"))
    setup(spec, root)
    if a.frames:
        for ts in a.frames.split(","):
            arr = frame(int(round(float(ts) * C.FPS)))
            p = os.path.join(a.frames_dir, f"chk_{ts}.png")
            Image.fromarray(arr).save(p)
            print("saved", p)
        return
    if not a.out:
        ap.error("cần --out hoặc --frames")
    tmp = tempfile.mkdtemp()
    vid = os.path.join(tmp, "video.mp4")
    render_video(vid, a.crf, a.jobs)
    if a.video_only or "audio" not in spec:
        os.replace(vid, a.out)
    else:
        wav = os.path.join(tmp, "mix.wav")
        build_audio(spec, root, wav)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vid, "-i", wav, "-map", "0:v",
                        "-map", "1:a", "-c:v", "copy"] + (["-af", f"loudnorm=I={a.lufs}:TP=-1.5:LRA=11"] if a.lufs else []) + ["-c:a", "aac", "-b:a", "160k",
                        "-movflags", "+faststart", "-t", str(C.DUR), a.out], check=True)
    print("xong:", a.out)

if __name__ == "__main__":
    main()
