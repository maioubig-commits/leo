#!/usr/bin/env python3
"""龍蝦學院 AI MV 生產腳本 — 60 秒 9:16 直幅。
- 音軌: music_v3.wav (54s)
- 視覺: 8 張講座照片 Ken Burns + PIL 黑金圖卡 + 數字人
- 字幕: 校正歌詞燒入(58pt 黃黑)
"""
import os, subprocess, tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path("/Users/chenyunung/Desktop/龍蝦學院_AI_MV")
PHOTOS = ROOT / "photos"
MUSIC = ROOT / "music_v3.wav"
OUT = ROOT / "龍蝦學院_AI_MV_60s.mp4"

W, H = 1080, 1920
FPS = 30
DURATION = 54.0   # V3 mp3 完整時長
FONT = "/System/Library/Fonts/Hiragino Sans GB.ttc"
FONT_W6 = 1  # bold
LOGO_PATH = "/Users/chenyunung/Desktop/🖼️ 圖片 & 截圖/logo_v6_lobster_only.png"
LOGO_IMG = Image.open(LOGO_PATH).convert("RGBA").resize((200, 200))

# ========================================
# 校正後歌詞 + 時間軸(我手動修正錯字)
# ========================================
LYRICS = [
    (0.0,  3.0,  "Yeah"),
    (3.0,  6.8,  "打卡上班還在等錢"),
    (6.8,  9.4,  "別人 AI 已經連夜"),
    (9.4,  11.4, "你說太老學不來 AI"),
    (11.4, 14.6, "六十三歲他練到五兆"),
    (14.6, 17.2, "醒醒吧兄弟姊妹"),
    (18.8, 22.4, "龍蝦學院 為你而開"),
    (22.4, 26.2, "龍蝦學院 24 小時不打烊"),
    (26.2, 30.0, "小爆 小察 小挖 小定 全部上場"),
    (30.0, 33.4, "小辯 小強 小潔 小構 連夜開戰"),
    (33.4, 37.4, "AI 員工軍團 全部歸我管"),
    (37.4, 41.6, "每月一班 每班八人"),
    (41.6, 43.4, "100 講師 開國元勳"),
    (43.4, 45.4, "傑森教練 親自帶你"),
    (45.4, 47.4, "從零到月入百萬"),
    (47.4, 49.4, "龍蝦學院經濟學"),
    (49.4, 50.0, "按訂閱看完整版"),
    (50.0, 53.4, "我們下集見"),
]

# ========================================
# 視覺分鏡:每個鏡頭 (start, end, type, payload)
# type: photo / pil_card / digital_human
# ========================================
SHOTS = [
    # Section 0: Intro (0-3s) — logo reveal
    (0.0, 3.0, "pil_card", {"title": "龍蝦學院", "subtitle": "AI 數字員工 24 小時不打烊", "emoji": "🦞"}),

    # Section 1: Verse 1 痛點 (3-15s)
    (3.0,  6.8,  "pil_card", {"title": "上班族", "subtitle": "打卡 / 等下班 / 等加薪", "bg": "dim"}),
    (6.8,  9.4,  "pil_card", {"title": "別人已經", "subtitle": "用 AI 24 小時自動賺錢", "bg": "fire"}),
    (9.4,  11.4, "pil_card", {"title": "「我太老學不來」", "subtitle": "🚫 錯！", "bg": "dim"}),
    (11.4, 14.6, "pil_card", {"title": "黃仁勳 63 歲", "subtitle": "NVIDIA 市值 5 兆", "highlight": "5 兆"}),

    # Section 2: Pre-Chorus 救贖 (14.6-22.4s)
    (14.6, 18.8, "photo", "28482.jpg"),   # 傑森拿麥克風講課
    (18.8, 22.4, "photo", "28481.jpg"),   # 圍站聽課

    # Section 3: Chorus 主歌 (22.4-37.4s) — peak moment
    (22.4, 26.2, "photo", "S__28508192_0.jpg"),  # 大合照
    (26.2, 30.0, "pil_card", {"title": "小爆 小察 小挖 小定", "subtitle": "AI 員工團隊", "highlight": "小爆"}),
    (30.0, 33.4, "pil_card", {"title": "小辯 小強 小潔 小構", "subtitle": "8 大 AI 員工", "highlight": "8 大"}),
    (33.4, 37.4, "photo", "S__28409873.jpg"),  # 教室坐滿《鈎癮效應》

    # Section 4: Verse 2 招生 (37.4-47.4s)
    (37.4, 41.6, "pil_card", {"title": "每月一班，每班8人", "subtitle": "100位開國元勳"}),
    (41.6, 43.4, "photo", "S__28549212.jpg"),  # 慶生合照
    (43.4, 47.4, "photo", "28478.jpg"),  # 專注聽課

    # Section 5: Outro (47.4-54s)
    (47.4, 50.0, "pil_card", {"title": "龍蝦學院經濟學", "subtitle": "按訂閱看完整版"}),
    (50.0, 54.0, "pil_card", {"title": "我們下集見", "subtitle": "🦞 龍蝦學院", "emoji": "🦞"}),
]


def render_pil_card(payload: dict, out_path: Path):
    """生成黑金風 PIL 圖卡。"""
    img = Image.new("RGB", (W, H), (10, 10, 10))
    draw = ImageDraw.Draw(img)

    title = payload.get("title", "")
    subtitle = payload.get("subtitle", "")
    highlight = payload.get("highlight")
    bg = payload.get("bg", "black")

    # 背景特效
    if bg == "dim":
        draw.rectangle([(0, 0), (W, H)], fill=(20, 20, 20))
    elif bg == "fire":
        # 紅黑漸層感
        for y in range(H):
            t = y / H
            r = int(30 + 60 * (1-t))
            draw.line([(0, y), (W, y)], fill=(r, 10, 10))

    # 標題(白字 / 高亮黃)
    title_size = 110 if len(title) <= 8 else 86
    title_font = ImageFont.truetype(FONT, title_size, index=FONT_W6)

    # 處理多行
    title_lines = []
    if highlight and highlight in title:
        # 分開渲染
        parts = title.split(highlight)
        title_lines.append(parts[0])
        title_lines.append(highlight)
        if len(parts) > 1 and parts[1]:
            title_lines.append(parts[1])
    else:
        title_lines = [title]

    total_h = len(title_lines) * (title_size + 20)
    y0 = H // 2 - total_h // 2 - 100
    for i, ln in enumerate(title_lines):
        bbox = title_font.getbbox(ln)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2
        y = y0 + i * (title_size + 20)
        color = (255, 215, 0) if ln == highlight else (255, 255, 255)
        # 描邊
        draw.text((x, y), ln, font=title_font, fill=color,
                  stroke_width=4, stroke_fill=(0, 0, 0))

    # 副標(黃字)
    if subtitle:
        sub_font = ImageFont.truetype(FONT, 56, index=FONT_W6)
        sub_bbox = sub_font.getbbox(subtitle)
        sw = sub_bbox[2] - sub_bbox[0]
        sub_y = y0 + total_h + 80
        draw.text(((W - sw) // 2, sub_y), subtitle, font=sub_font,
                  fill=(255, 215, 0), stroke_width=3, stroke_fill=(0, 0, 0))

    # logo 真實 PNG 右下
    img_rgba = img.convert("RGBA")
    img_rgba.paste(LOGO_IMG, (W - 230, H - 280), LOGO_IMG)
    img_rgba.convert("RGB").save(out_path)


def make_ken_burns(photo_path: Path, duration: float, out_path: Path):
    """簡化版:scale 到 1920 高度 → center crop 1080×1920 → 緩推 zoom 1.0→1.10。"""
    frames = max(int(duration * FPS), 25)
    # 先放大到 1620×2880(1.5×),再 zoompan 在這個 canvas 內推進
    cmd = [
        "ffmpeg", "-y", "-loop", "1", "-i", str(photo_path),
        "-vf", (
            f"scale=1620:2880:force_original_aspect_ratio=increase,"
            f"crop=1620:2880,"
            f"zoompan=z='1.0+0.10*on/{frames}':d=1:s={W}x{H}:fps={FPS}"
        ),
        "-t", f"{duration}",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast", "-r", str(FPS),
        str(out_path)
    ]
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0:
        # fallback: 無 zoom,純 center crop
        cmd2 = [
            "ffmpeg", "-y", "-loop", "1", "-i", str(photo_path),
            "-vf", f"scale=-1:1920:force_original_aspect_ratio=increase,crop={W}:{H}",
            "-t", f"{duration}",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast", "-r", str(FPS),
            str(out_path)
        ]
        subprocess.run(cmd2, capture_output=True, check=True)


def make_pil_clip(payload: dict, duration: float, out_path: Path):
    """生成 PIL 圖卡 + 靜態片段。"""
    tmp_png = out_path.with_suffix(".png")
    render_pil_card(payload, tmp_png)
    cmd = [
        "ffmpeg", "-y", "-loop", "1", "-i", str(tmp_png),
        "-t", f"{duration}",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast",
        "-r", str(FPS),
        str(out_path)
    ]
    subprocess.run(cmd, capture_output=True, check=True)
    tmp_png.unlink()


def render_subtitle_png(text: str, out_path: Path):
    """歌詞底部字幕 PNG(58pt 黃黑)。"""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT, 64, index=FONT_W6)
    bbox = font.getbbox(text)
    tw = bbox[2] - bbox[0]
    x = (W - tw) // 2
    y = int(H * 0.82)
    draw.text((x, y), text, font=font, fill=(255, 215, 0, 255),
              stroke_width=7, stroke_fill=(0, 0, 0, 255))
    img.save(out_path)


def main():
    work = Path(tempfile.mkdtemp(prefix="lobster_mv_"))
    print(f"📁 工作: {work}")

    # === Step 1: 生成每個視覺鏡頭 ===
    print("\n🎬 Step 1: 生成 16 個視覺鏡頭")
    clip_files = []
    for i, (start, end, shot_type, payload) in enumerate(SHOTS):
        dur = end - start
        out_clip = work / f"shot_{i:02d}.mp4"
        print(f"   [{start:5.1f}-{end:5.1f}s] {shot_type}: {payload if isinstance(payload, str) else payload.get('title','?')[:25]}")
        if shot_type == "photo":
            photo_path = PHOTOS / payload
            if not photo_path.exists():
                print(f"      ⚠ 照片不存在: {photo_path}")
                continue
            make_ken_burns(photo_path, dur, out_clip)
        elif shot_type == "pil_card":
            make_pil_clip(payload, dur, out_clip)
        clip_files.append((start, end, out_clip))

    # === Step 2: 串接所有鏡頭 ===
    print("\n🔗 Step 2: 串接所有鏡頭")
    concat_file = work / "concat.txt"
    with concat_file.open("w") as f:
        for _, _, cf in clip_files:
            f.write(f"file '{cf.absolute()}'\n")

    visual_mp4 = work / "visual.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file),
        "-c", "copy", str(visual_mp4)
    ], capture_output=True, check=True)
    print(f"   ✅ 視覺合成: {visual_mp4}")

    # === Step 3: 生成字幕 PNG 並 overlay ===
    print("\n📝 Step 3: 歌詞字幕燒入")
    sub_pngs = []
    for i, (start, end, text) in enumerate(LYRICS):
        if not text.strip():
            sub_pngs.append((start, end, None))
            continue
        sub_png = work / f"sub_{i:02d}.png"
        render_subtitle_png(text, sub_png)
        sub_pngs.append((start, end, sub_png))

    # ffmpeg overlay all subtitle PNGs
    cmd = ["ffmpeg", "-y", "-i", str(visual_mp4)]
    valid_subs = [(s, e, p) for s, e, p in sub_pngs if p is not None]
    for _, _, p in valid_subs:
        cmd += ["-i", str(p)]

    filters = []
    last = "[0:v]"
    for i, (s, e, p) in enumerate(valid_subs, start=1):
        out_label = f"[v{i}]"
        filters.append(
            f"{last}[{i}:v]overlay=0:0:enable='between(t,{s:.3f},{e:.3f})'{out_label}"
        )
        last = out_label

    cmd += ["-filter_complex", ";".join(filters), "-map", last,
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast", "-crf", "20",
            "-t", f"{DURATION}",
            str(work / "visual_subbed.mp4")]
    subprocess.run(cmd, capture_output=True, check=True)
    print(f"   ✅ 字幕燒入完成")

    # === Step 4: 合成音軌 ===
    print("\n🎵 Step 4: 合成音軌")
    cmd = [
        "ffmpeg", "-y",
        "-i", str(work / "visual_subbed.mp4"),
        "-i", str(MUSIC),
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-map", "0:v", "-map", "1:a",
        "-t", f"{DURATION}",
        str(OUT)
    ]
    subprocess.run(cmd, capture_output=True, check=True)

    size_mb = OUT.stat().st_size / (1024*1024)
    print(f"\n🎉 完成: {OUT}")
    print(f"   📊 大小: {size_mb:.1f} MB / 時長: {DURATION}s / 9:16 1080×1920")


if __name__ == "__main__":
    main()
