#!/usr/bin/env python3
"""龍蝦學院 實體講座開場版 MV — 16:9 1920×1080 投影機規格。
音軌: V1 49 秒"""
import subprocess, tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

import os
# 素材根目錄：用 LOBSTER_MV_ROOT env 指定，預設 ~/Desktop/龍蝦學院_AI_MV
ROOT = Path(os.environ.get("LOBSTER_MV_ROOT", Path.home() / "Desktop/龍蝦學院_AI_MV"))
PHOTOS = ROOT / "photos"
MUSIC = ROOT / "v2_stage" / "music_stage.wav"
OUT = ROOT / "龍蝦學院_實體講座開場_v1.mp4"

# 16:9 投影規格
W, H = 1920, 1080
FPS = 30
DURATION = 49.0
FONT = "/System/Library/Fonts/Hiragino Sans GB.ttc"
FONT_W6 = 1
LOGO_PATH = str(Path(__file__).resolve().parent.parent / "assets" / "logo.png")
LOGO_IMG = Image.open(LOGO_PATH).convert("RGBA").resize((240, 240))

# 校正歌詞 + Whisper 精準時間軸
LYRICS = [
    (0.0,  2.2,  ""),  # intro yeah, 不上字幕
    (2.2,  3.9,  "打卡上班還在等錢"),
    (3.9,  5.8,  "別人 AI 龍蝦已經連夜"),
    (5.8,  7.4,  "你說太老學不來"),
    (7.4,  9.7,  "六十三歲 Jensen 練到五兆"),
    (9.7,  13.3, "醒醒吧 兄弟姊妹"),
    (13.3, 17.0, "龍蝦學院 為你而開"),
    (17.0, 20.2, "龍蝦學院 24 小時不打烊"),
    (20.2, 24.3, "小爆 小察 小挖 小定 全部上場"),
    (24.3, 27.5, "小辯 小強 小潔 小構 連夜開戰"),
    (27.5, 31.2, "AI 龍蝦軍團 全部歸我管"),
    (31.2, 32.9, "今天你來到這裡"),
    (32.9, 34.6, "就是最棒的決定"),
    (34.6, 36.2, "看看身邊的 8 位戰友"),
    (36.2, 38.9, "你們將是 開國元勳"),
    (38.9, 42.0, "歡迎來到 龍蝦學院"),
    (42.0, 44.2, "熱烈掌聲 給我們的"),
    (44.2, 46.8, "傑森教練 請上台"),
]

# 視覺分鏡 16:9
SHOTS = [
    # 0: Intro reveal — 全名品牌
    (0.0, 2.2, "pil_card", {"title": "AI數字員工\n龍蝦學院", "subtitle": "24 小時不打烊", "size": "huge", "bg": "spotlight"}),

    # 1: Verse 1 痛點
    (2.2,  3.9,  "pil_card", {"title": "打卡 等下班", "subtitle": "你 還在等錢", "bg": "dim"}),
    (3.9,  5.8,  "pil_card", {"title": "別人的 AI", "subtitle": "已經連夜 賺爆了", "bg": "fire"}),
    (5.8,  7.4,  "pil_card", {"title": "「太老學不來」", "subtitle": "這 就是藉口", "bg": "dim"}),
    (7.4,  9.7,  "pil_card", {"title": "Jensen 63 歲", "subtitle": "NVIDIA 練到 5 兆", "highlight": "5 兆", "bg": "spotlight"}),

    # 2: Pre-Chorus
    (9.7,  13.3, "photo", "28482.jpg"),
    (13.3, 17.0, "photo", "28481.jpg"),

    # 3: Chorus
    (17.0, 20.2, "photo", "S__28508192_0.jpg"),
    (20.2, 24.3, "pil_card", {"title": "小爆 小察 小挖 小定", "subtitle": "AI 軍團 全部上場", "highlight": "AI 軍團", "bg": "spotlight"}),
    (24.3, 27.5, "pil_card", {"title": "小辯 小強 小潔 小構", "subtitle": "8 大 數字員工 連夜開戰", "highlight": "8 大", "bg": "spotlight"}),
    (27.5, 31.2, "photo", "S__28409873.jpg"),

    # 4: Verse 2 現場儀式
    (31.2, 32.9, "pil_card", {"title": "今天 你來到這裡", "subtitle": "就是最棒的決定", "highlight": "今天", "bg": "dim"}),
    (32.9, 34.6, "pil_card", {"title": "最棒的決定", "subtitle": "從今天 改變人生", "highlight": "最棒", "bg": "spotlight"}),
    (34.6, 36.2, "pil_card", {"title": "8 位戰友 就在身邊", "subtitle": "看看 左右", "highlight": "8 位戰友", "bg": "dim"}),
    (36.2, 38.9, "photo", "S__28549212.jpg"),

    # 5: Outro 引出傑森
    (38.9, 42.0, "pil_card", {"title": "歡迎來到", "subtitle": "AI數字員工龍蝦學院", "bg": "spotlight"}),
    (42.0, 44.2, "pil_card", {"title": "熱烈 掌聲", "subtitle": "全場 起立", "bg": "fire"}),
    (44.2, 46.8, "pil_card", {"title": "傑森教練", "subtitle": "請 上 台", "highlight": "傑森教練", "bg": "spotlight"}),
    (46.8, 49.0, "pil_card", {"title": "", "subtitle": "AI數字員工龍蝦學院", "bg": "spotlight"}),
]


def make_background(bg_type):
    """生成豐富背景(亮度+光暈)。"""
    import math
    img = Image.new("RGB", (W, H), (10, 10, 10))
    draw = ImageDraw.Draw(img)
    cx, cy = W // 2, H // 2
    max_r = math.sqrt(cx*cx + cy*cy)

    if bg_type == "spotlight":
        # 龍蝦深紅聚光(品牌色 + 黃字對比強烈)
        for y in range(0, H, 4):
            for x in range(0, W, 4):
                d = math.sqrt((x-cx)**2 + (y-cy)**2)
                t = min(d / max_r, 1)
                # 中心 #8a1818 深紅 → 邊緣 #1a0a0a 黑紅
                r = int(138 * (1-t**1.2) + 26)
                g = int(24 * (1-t**1.2) + 10)
                b = int(24 * (1-t**1.4) + 10)
                draw.rectangle([(x, y), (x+4, y+4)], fill=(r, g, b))
    elif bg_type == "fire":
        # 紅金漸層(更亮)
        for y in range(0, H, 4):
            for x in range(0, W, 4):
                d = math.sqrt((x-cx)**2 + (y-cy)**2)
                t = min(d / max_r, 1)
                r = int(200 * (1-t**1.2) + 60)
                g = int(60 * (1-t**1.2) + 15)
                b = int(20 * (1-t**1.5) + 10)
                draw.rectangle([(x, y), (x+4, y+4)], fill=(r, g, b))
    elif bg_type == "dim":
        # 深藍金漸層(中心藍 → 邊緣深)
        for y in range(0, H, 4):
            for x in range(0, W, 4):
                d = math.sqrt((x-cx)**2 + (y-cy)**2)
                t = min(d / max_r, 1)
                r = int(60 * (1-t**1.2) + 25)
                g = int(80 * (1-t**1.2) + 30)
                b = int(110 * (1-t**1.2) + 40)
                draw.rectangle([(x, y), (x+4, y+4)], fill=(r, g, b))
    else:
        return make_background("spotlight")

    # 加金色斜線紋理(品牌感,提升質感)
    for i in range(0, W+H, 80):
        draw.line([(i, 0), (i - H, H)], fill=(80, 60, 25), width=2)

    return img


def render_pil_card(payload, out_path):
    """16:9 黑金風圖卡 + 豐富背景。"""
    bg = payload.get("bg", "spotlight")
    img = make_background(bg)
    draw = ImageDraw.Draw(img)

    title = payload.get("title", "")
    subtitle = payload.get("subtitle", "")
    highlight = payload.get("highlight")
    size_mode = payload.get("size", "normal")

    # 標題大小(16:9 可以放更大)
    if size_mode == "huge":
        title_size = 150
    elif len(title) <= 6:
        title_size = 160
    elif len(title) <= 12:
        title_size = 130
    else:
        title_size = 100

    title_font = ImageFont.truetype(FONT, title_size, index=FONT_W6)

    # 處理 \n 換行
    title_lines = []
    if "\n" in title:
        for ln in title.split("\n"):
            title_lines.append((ln.strip(), (255, 215, 0)))
    elif highlight and highlight in title and title != highlight:
        parts = title.split(highlight)
        if parts[0].strip():
            title_lines.append((parts[0].strip(), (255, 255, 255)))
        title_lines.append((highlight, (255, 215, 0)))
        if len(parts) > 1 and parts[1].strip():
            title_lines.append((parts[1].strip(), (255, 255, 255)))
    elif title:
        title_lines.append((title, (255, 215, 0) if highlight == title else (255, 255, 255)))

    # 計算總高
    if title_lines:
        line_h = title_size + 30
        total_h = len(title_lines) * line_h
        y0 = H // 2 - total_h // 2 - 60
        for i, (ln, color) in enumerate(title_lines):
            bbox = title_font.getbbox(ln)
            tw = bbox[2] - bbox[0]
            x = (W - tw) // 2
            y = y0 + i * line_h
            draw.text((x, y), ln, font=title_font, fill=color,
                      stroke_width=5, stroke_fill=(0, 0, 0))
        bottom_y = y0 + total_h + 60
    else:
        bottom_y = H // 2

    # 副標
    if subtitle:
        sub_font = ImageFont.truetype(FONT, 70, index=FONT_W6)
        sub_bbox = sub_font.getbbox(subtitle)
        sw = sub_bbox[2] - sub_bbox[0]
        draw.text(((W - sw) // 2, bottom_y), subtitle, font=sub_font,
                  fill=(255, 215, 0), stroke_width=3, stroke_fill=(0, 0, 0))

    # logo 右下(真實 PNG,不用 emoji)
    img_rgba = img.convert("RGBA")
    img_rgba.paste(LOGO_IMG, (W - 280, H - 280), LOGO_IMG)
    img_rgba.convert("RGB").save(out_path)


def make_ken_burns_16_9(photo_path, duration, out_path):
    """16:9 Ken Burns。"""
    frames = max(int(duration * FPS), 25)
    cmd = [
        "ffmpeg", "-y", "-loop", "1", "-i", str(photo_path),
        "-vf", (
            f"scale=2880:1620:force_original_aspect_ratio=increase,"
            f"crop=2880:1620,"
            f"zoompan=z='1.0+0.12*on/{frames}':d=1:s={W}x{H}:fps={FPS}"
        ),
        "-t", f"{duration}",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast", "-r", str(FPS),
        str(out_path)
    ]
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0:
        cmd2 = [
            "ffmpeg", "-y", "-loop", "1", "-i", str(photo_path),
            "-vf", f"scale={W}:-1:force_original_aspect_ratio=increase,crop={W}:{H}",
            "-t", f"{duration}",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast", "-r", str(FPS),
            str(out_path)
        ]
        subprocess.run(cmd2, capture_output=True, check=True)


def make_pil_clip(payload, duration, out_path):
    tmp_png = out_path.with_suffix(".png")
    render_pil_card(payload, tmp_png)
    cmd = [
        "ffmpeg", "-y", "-loop", "1", "-i", str(tmp_png),
        "-t", f"{duration}",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast", "-r", str(FPS),
        str(out_path)
    ]
    subprocess.run(cmd, capture_output=True, check=True)
    tmp_png.unlink()


def render_subtitle_png(text, out_path):
    """16:9 底部字幕。"""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT, 72, index=FONT_W6)
    bbox = font.getbbox(text)
    tw = bbox[2] - bbox[0]
    x = (W - tw) // 2
    y = int(H * 0.88)
    draw.text((x, y), text, font=font, fill=(255, 215, 0, 255),
              stroke_width=8, stroke_fill=(0, 0, 0, 255))
    img.save(out_path)


def main():
    work = Path(tempfile.mkdtemp(prefix="lobster_stage_"))
    print(f"📁 工作: {work}")

    print("\n🎬 Step 1: 生成 19 個視覺鏡頭(16:9 1920×1080)")
    clip_files = []
    for i, (start, end, shot_type, payload) in enumerate(SHOTS):
        dur = end - start
        out_clip = work / f"shot_{i:02d}.mp4"
        label = payload if isinstance(payload, str) else payload.get('title','?')[:30]
        print(f"   [{start:5.1f}-{end:5.1f}s] {shot_type}: {label}")
        if shot_type == "photo":
            make_ken_burns_16_9(PHOTOS / payload, dur, out_clip)
        else:
            make_pil_clip(payload, dur, out_clip)
        clip_files.append(out_clip)

    print("\n🔗 Step 2: 串接所有鏡頭")
    concat_file = work / "concat.txt"
    with concat_file.open("w") as f:
        for cf in clip_files:
            f.write(f"file '{cf.absolute()}'\n")
    visual_mp4 = work / "visual.mp4"
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0",
                    "-i", str(concat_file), "-c", "copy", str(visual_mp4)],
                   capture_output=True, check=True)

    print("\n📝 Step 3: 字幕燒入")
    sub_pngs = []
    for i, (s, e, text) in enumerate(LYRICS):
        if not text.strip():
            continue
        png = work / f"sub_{i:02d}.png"
        render_subtitle_png(text, png)
        sub_pngs.append((s, e, png))

    cmd = ["ffmpeg", "-y", "-i", str(visual_mp4)]
    for _, _, p in sub_pngs:
        cmd += ["-i", str(p)]
    filters = []
    last = "[0:v]"
    for i, (s, e, _) in enumerate(sub_pngs, start=1):
        out_label = f"[v{i}]"
        filters.append(f"{last}[{i}:v]overlay=0:0:enable='between(t,{s:.3f},{e:.3f})'{out_label}")
        last = out_label
    cmd += ["-filter_complex", ";".join(filters), "-map", last,
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast", "-crf", "18",
            "-t", f"{DURATION}", str(work / "visual_sub.mp4")]
    subprocess.run(cmd, capture_output=True, check=True)

    print("\n🎵 Step 4: 合成音軌")
    cmd = [
        "ffmpeg", "-y",
        "-i", str(work / "visual_sub.mp4"),
        "-i", str(MUSIC),
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "256k",
        "-map", "0:v", "-map", "1:a",
        "-t", f"{DURATION}",
        str(OUT)
    ]
    subprocess.run(cmd, capture_output=True, check=True)

    size_mb = OUT.stat().st_size / (1024*1024)
    print(f"\n🎉 完成: {OUT}")
    print(f"   📊 {size_mb:.1f} MB / {DURATION}s / 16:9 {W}×{H}")


if __name__ == "__main__":
    main()
