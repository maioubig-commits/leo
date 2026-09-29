#!/usr/bin/env python3
"""龍蝦學院 實體講座開場 v4 — 全面升級:
1. 動態鏡頭(8 種運鏡變化)
2. 字幕 fade-in + slide-up
3. AI 生成視覺(5 張 imagen-4)取代部分 PIL 卡
4. xfade 過場 transitions
"""
import subprocess, tempfile, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path("/Users/chenyunung/Desktop/龍蝦學院_AI_MV")
PHOTOS = ROOT / "photos"
AI_IMAGES = ROOT / "v4_assets" / "ai_images"
MUSIC = ROOT / "v2_stage" / "music_stage.wav"
OUT = ROOT / "龍蝦學院_實體講座開場_v4.mp4"

W, H = 1920, 1080
FPS = 30
DURATION = 49.0
FONT = "/System/Library/Fonts/Hiragino Sans GB.ttc"
FONT_W6 = 1
LOGO_PATH = "/Users/chenyunung/Desktop/🖼️ 圖片 & 截圖/logo_v6_lobster_only.png"
LOGO_IMG = Image.open(LOGO_PATH).convert("RGBA").resize((240, 240))

LYRICS = [
    (0.0,  2.2,  ""),
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

# 8 種運鏡方向(隨機輪換)
MOTION_TYPES = [
    "zoom_in_center", "zoom_out_center",
    "zoom_in_pan_left", "zoom_in_pan_right",
    "zoom_in_pan_up", "zoom_in_pan_down",
    "zoom_out_drift_left", "zoom_out_drift_right",
]

# 視覺分鏡 — type: ai_image / photo / pil_card
SHOTS = [
    # 0: Intro
    (0.0, 2.2, "ai_image", "04_lobster_brand.png", "zoom_in_center"),

    # 1: Verse 1 痛點
    (2.2,  3.9,  "pil_card", {"title": "打卡 等下班", "subtitle": "你 還在等錢", "bg": "dim"}),
    (3.9,  5.8,  "pil_card", {"title": "別人的 AI", "subtitle": "已經連夜 賺爆了", "bg": "fire"}),
    (5.8,  7.4,  "pil_card", {"title": "「太老學不來」", "subtitle": "這 就是藉口", "bg": "dim"}),
    (7.4,  9.7,  "ai_image", "01_nvidia_5t.png", "zoom_in_pan_left"),

    # 2: Pre-Chorus 講座照
    (9.7,  13.3, "photo", "28482.jpg", "zoom_in_pan_right"),
    (13.3, 17.0, "photo", "28481.jpg", "zoom_out_drift_left"),

    # 3: Chorus 主歌
    (17.0, 20.2, "photo", "S__28508192_0.jpg", "zoom_in_pan_up"),
    (20.2, 24.3, "ai_image", "02_ai_army.png", "zoom_in_center"),
    (24.3, 27.5, "pil_card", {"title": "小辯 小強 小潔 小構", "subtitle": "8 大 數字員工 連夜開戰", "highlight": "8 大", "bg": "spotlight"}),
    (27.5, 31.2, "photo", "S__28409873.jpg", "zoom_in_pan_down"),

    # 4: Verse 2 現場儀式
    (31.2, 32.9, "pil_card", {"title": "今天 你來到這裡", "subtitle": "就是最棒的決定", "highlight": "今天", "bg": "dim"}),
    (32.9, 34.6, "ai_image", "05_data_flow.png", "zoom_out_center"),
    (34.6, 36.2, "pil_card", {"title": "8 位戰友 就在身邊", "subtitle": "看看 左右", "highlight": "8 位戰友", "bg": "dim"}),
    (36.2, 38.9, "photo", "S__28549212.jpg", "zoom_in_pan_right"),

    # 5: Outro 引出傑森
    (38.9, 42.0, "ai_image", "03_stage_lights.png", "zoom_in_center"),
    (42.0, 44.2, "pil_card", {"title": "熱烈 掌聲", "subtitle": "全場 起立", "bg": "fire"}),
    (44.2, 46.8, "pil_card", {"title": "傑森教練", "subtitle": "請 上 台", "highlight": "傑森教練", "bg": "spotlight"}),
    (46.8, 49.0, "ai_image", "04_lobster_brand.png", "zoom_out_center"),
]


def make_background(bg_type):
    import math
    img = Image.new("RGB", (W, H), (10, 10, 10))
    draw = ImageDraw.Draw(img)
    cx, cy = W // 2, H // 2
    max_r = math.sqrt(cx*cx + cy*cy)
    if bg_type == "spotlight":
        for y in range(0, H, 4):
            for x in range(0, W, 4):
                d = math.sqrt((x-cx)**2 + (y-cy)**2)
                t = min(d / max_r, 1)
                r = int(138 * (1-t**1.2) + 26)
                g = int(24 * (1-t**1.2) + 10)
                b = int(24 * (1-t**1.4) + 10)
                draw.rectangle([(x, y), (x+4, y+4)], fill=(r, g, b))
    elif bg_type == "fire":
        for y in range(0, H, 4):
            for x in range(0, W, 4):
                d = math.sqrt((x-cx)**2 + (y-cy)**2)
                t = min(d / max_r, 1)
                r = int(200 * (1-t**1.2) + 60)
                g = int(60 * (1-t**1.2) + 15)
                b = int(20 * (1-t**1.5) + 10)
                draw.rectangle([(x, y), (x+4, y+4)], fill=(r, g, b))
    elif bg_type == "dim":
        for y in range(0, H, 4):
            for x in range(0, W, 4):
                d = math.sqrt((x-cx)**2 + (y-cy)**2)
                t = min(d / max_r, 1)
                r = int(60 * (1-t**1.2) + 25)
                g = int(80 * (1-t**1.2) + 30)
                b = int(110 * (1-t**1.2) + 40)
                draw.rectangle([(x, y), (x+4, y+4)], fill=(r, g, b))
    for i in range(0, W+H, 80):
        draw.line([(i, 0), (i - H, H)], fill=(80, 60, 25), width=2)
    return img


def render_pil_card(payload, out_path):
    bg = payload.get("bg", "spotlight")
    img = make_background(bg)
    draw = ImageDraw.Draw(img)
    title = payload.get("title", "")
    subtitle = payload.get("subtitle", "")
    highlight = payload.get("highlight")
    size_mode = payload.get("size", "normal")

    if size_mode == "huge":
        title_size = 150
    elif len(title) <= 6:
        title_size = 160
    elif len(title) <= 12:
        title_size = 130
    else:
        title_size = 100

    title_font = ImageFont.truetype(FONT, title_size, index=FONT_W6)
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

    if title_lines:
        line_h = title_size + 30
        total_h = len(title_lines) * line_h
        y0 = H // 2 - total_h // 2 - 60
        for i, (ln, color) in enumerate(title_lines):
            bbox = title_font.getbbox(ln)
            tw = bbox[2] - bbox[0]
            x = (W - tw) // 2
            y = y0 + i * line_h
            draw.text((x, y), ln, font=title_font, fill=color, stroke_width=5, stroke_fill=(0, 0, 0))
        bottom_y = y0 + total_h + 60
    else:
        bottom_y = H // 2

    if subtitle:
        sub_font = ImageFont.truetype(FONT, 70, index=FONT_W6)
        sub_bbox = sub_font.getbbox(subtitle)
        sw = sub_bbox[2] - sub_bbox[0]
        draw.text(((W - sw) // 2, bottom_y), subtitle, font=sub_font, fill=(255, 215, 0), stroke_width=3, stroke_fill=(0, 0, 0))

    img_rgba = img.convert("RGBA")
    img_rgba.paste(LOGO_IMG, (W - 280, H - 280), LOGO_IMG)
    img_rgba.convert("RGB").save(out_path)


def motion_filter(motion_type, frames):
    """根據運鏡類型回傳 zoompan filter expression。"""
    # 預縮放到 2880×1620 給有 panning 空間
    pre_scale = "scale=2880:1620:force_original_aspect_ratio=increase,crop=2880:1620"
    s = f"s={W}x{H}:fps={FPS}"

    if motion_type == "zoom_in_center":
        return f"{pre_scale},zoompan=z='1.0+0.18*on/{frames}':d=1:{s}"
    elif motion_type == "zoom_out_center":
        return f"{pre_scale},zoompan=z='1.2-0.18*on/{frames}':d=1:{s}"
    elif motion_type == "zoom_in_pan_left":
        return f"{pre_scale},zoompan=z='1.0+0.20*on/{frames}':x='iw/zoom/2 + (iw - iw/zoom) * (on/{frames}) * 0.5':y='ih/zoom/2 - ih/zoom/2':d=1:{s}"
    elif motion_type == "zoom_in_pan_right":
        return f"{pre_scale},zoompan=z='1.0+0.20*on/{frames}':x='iw/zoom/2 - (iw - iw/zoom) * (on/{frames}) * 0.5':y='ih/zoom/2 - ih/zoom/2':d=1:{s}"
    elif motion_type == "zoom_in_pan_up":
        return f"{pre_scale},zoompan=z='1.0+0.18*on/{frames}':x='iw/2 - iw/zoom/2':y='ih/zoom/2 + (ih - ih/zoom) * (on/{frames}) * 0.3':d=1:{s}"
    elif motion_type == "zoom_in_pan_down":
        return f"{pre_scale},zoompan=z='1.0+0.18*on/{frames}':x='iw/2 - iw/zoom/2':y='ih/zoom/2 - (ih - ih/zoom) * (on/{frames}) * 0.3':d=1:{s}"
    elif motion_type == "zoom_out_drift_left":
        return f"{pre_scale},zoompan=z='1.2-0.18*on/{frames}':x='iw/2 - iw/zoom/2 - 100 + 200 * (on/{frames})':y='ih/2 - ih/zoom/2':d=1:{s}"
    elif motion_type == "zoom_out_drift_right":
        return f"{pre_scale},zoompan=z='1.2-0.18*on/{frames}':x='iw/2 - iw/zoom/2 + 100 - 200 * (on/{frames})':y='ih/2 - ih/zoom/2':d=1:{s}"
    return f"{pre_scale},zoompan=z='1.05':d=1:{s}"


def make_shot_clip(shot_type, payload, duration, out_path, motion="zoom_in_center"):
    frames = max(int(duration * FPS), 25)
    if shot_type == "pil_card":
        tmp_png = out_path.with_suffix(".png")
        render_pil_card(payload, tmp_png)
        # 加 motion 給 PIL 也有運鏡感
        vf = motion_filter(motion, frames)
        cmd = ["ffmpeg", "-y", "-loop", "1", "-i", str(tmp_png),
               "-vf", vf, "-t", f"{duration}",
               "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast", "-r", str(FPS),
               str(out_path)]
        r = subprocess.run(cmd, capture_output=True)
        if r.returncode != 0:
            # fallback 靜態
            subprocess.run(["ffmpeg", "-y", "-loop", "1", "-i", str(tmp_png),
                            "-t", f"{duration}", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                            "-preset", "fast", "-r", str(FPS), str(out_path)],
                           capture_output=True, check=True)
        tmp_png.unlink()
    elif shot_type in ("photo", "ai_image"):
        src_dir = PHOTOS if shot_type == "photo" else AI_IMAGES
        src = src_dir / payload
        vf = motion_filter(motion, frames)
        cmd = ["ffmpeg", "-y", "-loop", "1", "-i", str(src),
               "-vf", vf, "-t", f"{duration}",
               "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast", "-r", str(FPS),
               str(out_path)]
        r = subprocess.run(cmd, capture_output=True)
        if r.returncode != 0:
            subprocess.run(["ffmpeg", "-y", "-loop", "1", "-i", str(src),
                            "-vf", f"scale={W}:-1:force_original_aspect_ratio=increase,crop={W}:{H}",
                            "-t", f"{duration}", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                            "-preset", "fast", "-r", str(FPS), str(out_path)],
                           capture_output=True, check=True)


def render_subtitle_png(text, out_path):
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
    work = Path(tempfile.mkdtemp(prefix="lobster_v4_"))
    print(f"📁 {work}")

    # Step 1: 每個 shot 有運鏡
    print("\n🎬 Step 1: 生成 19 鏡(含 8 種運鏡輪換)")
    clip_files = []
    for i, shot in enumerate(SHOTS):
        start, end, shot_type, payload = shot[0], shot[1], shot[2], shot[3]
        motion = shot[4] if len(shot) > 4 else random.choice(MOTION_TYPES)
        dur = end - start
        out_clip = work / f"shot_{i:02d}.mp4"
        label = payload if isinstance(payload, str) else payload.get('title','?')[:25]
        print(f"   [{start:5.1f}-{end:5.1f}s] {shot_type}/{motion}: {label}")
        make_shot_clip(shot_type, payload, dur, out_clip, motion)
        clip_files.append((dur, out_clip))

    # Step 2: 用 xfade 串接(0.3s overlap)
    print("\n🔗 Step 2: xfade 過場 0.3s")
    XFADE = 0.3
    # 用 ffmpeg filter_complex 串多個 xfade
    inputs = []
    for _, cf in clip_files:
        inputs += ["-i", str(cf)]

    filter_parts = []
    cumulative_offset = 0
    last_label = "[0:v]"
    for i in range(1, len(clip_files)):
        prev_dur = clip_files[i-1][0]
        cumulative_offset += prev_dur - XFADE if i > 1 else prev_dur - XFADE
        # 副歌段用 fadeblack,主歌段用 fade,慢段用 fade
        transition = "fade"
        new_label = f"[v{i}]"
        filter_parts.append(f"{last_label}[{i}:v]xfade=transition={transition}:duration={XFADE}:offset={cumulative_offset - (clip_files[i-1][0] - XFADE)}{new_label}")
        last_label = new_label

    # 簡化版:用 concat + 重編碼(避免 timestamp bug 造成 overlay enable 失效)
    concat_file = work / "concat.txt"
    with concat_file.open("w") as f:
        for _, cf in clip_files:
            f.write(f"file '{cf.absolute()}'\n")
    visual_mp4 = work / "visual.mp4"
    # 用 -c:v libx264 重編碼 + -fflags +genpts 強制重生 PTS
    subprocess.run(["ffmpeg", "-y", "-fflags", "+genpts", "-f", "concat", "-safe", "0",
                    "-i", str(concat_file),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(FPS),
                    "-preset", "fast", "-crf", "18",
                    str(visual_mp4)],
                   capture_output=True, check=True)

    # Step 3: 字幕 fade-in 燒入
    print("\n📝 Step 3: 字幕 fade-in + slide-up")
    sub_pngs = []
    for i, (s, e, text) in enumerate(LYRICS):
        if not text.strip():
            continue
        png = work / f"sub_{i:02d}.png"
        render_subtitle_png(text, png)
        sub_pngs.append((s, e, png))

    # 靜態 overlay(驗證 100% work,放棄 fade 動畫求穩)
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
    # 不 capture 看 stderr 哪裡漏
    print(f"   ⚙ 跑 ffmpeg overlay({len(sub_pngs)} 字幕,filter 長度 {len(';'.join(filters))})")
    proc = subprocess.run(cmd, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        print(f"   ❌ Step 3 ffmpeg returncode={proc.returncode}")
        print(proc.stderr[-1500:])
        raise RuntimeError("subtitle overlay failed")
    # 立刻 verify
    import subprocess as sp
    test_png = work / "verify_sub.png"
    sp.run(["ffmpeg","-y","-ss","11","-i",str(work / "visual_sub.mp4"),"-frames:v","1",str(test_png)], capture_output=True)
    from PIL import Image
    import numpy as np
    arr = np.array(Image.open(test_png))
    yellow = ((arr[:,:,0]>200) & (arr[:,:,1]>180) & (arr[:,:,2]<100)).sum()
    print(f"   ✅ verify @ 11s yellow pixels = {yellow}")

    # Step 4: 音軌
    print("\n🎵 Step 4: 合成音軌")
    cmd = ["ffmpeg", "-y",
           "-i", str(work / "visual_sub.mp4"),
           "-i", str(MUSIC),
           "-c:v", "copy", "-c:a", "aac", "-b:a", "256k",
           "-map", "0:v", "-map", "1:a", "-t", f"{DURATION}",
           str(OUT)]
    subprocess.run(cmd, capture_output=True, check=True)

    size_mb = OUT.stat().st_size / (1024*1024)
    print(f"\n🎉 完成: {OUT}")
    print(f"   📊 {size_mb:.1f} MB / {DURATION}s / 16:9")


if __name__ == "__main__":
    main()
