#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
龍蝦學院 AI MV 合成引擎（16:9 / 1920×1080）— 已驗證可跑版本。

跟舊的 build_stage_mv.py 差別：路徑全部相對化、分鏡表抽成 JSON、素材缺件先擋下來，
所以換一台機器、換一批素材都不用改程式。

用法：
    # 素材目錄底下要有 ai_images/ photos/ music/
    python3 build_mv_16x9.py --assets ~/Desktop/龍蝦學院_AI_MV

    # 指定音軌與輸出
    python3 build_mv_16x9.py --assets DIR --music DIR/music/take2.mp3 --out ~/Desktop/成片.mp4

    # 自訂分鏡（不給就用內建的品牌招生版）
    python3 build_mv_16x9.py --assets DIR --storyboard my_storyboard.json

管線：PIL 圖卡＋素材整備 → ffmpeg zoompan 運鏡 → concat 重編碼 → 字幕 overlay → 混音

踩雷備忘：
  ・concat 不能 -c copy（timestamp 亂掉 → overlay enable 失效 → 字幕整片消失）
  ・PIL 不支援 emoji → logo 一律用 PNG paste
  ・繁體大字用 Songti TC（SC 版缺繁體字會渲染成空白）
  ・Songti.ttc 在 /System/Library/Fonts/Supplemental/，不在 /System/Library/Fonts/
"""
import argparse, json, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter

SKILL_DIR = Path(__file__).resolve().parent.parent
W, H, FPS = 1920, 1080, 30

# 字型候選：macOS 兩個可能位置都試，缺了直接講清楚
FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Songti.ttc",
    "/System/Library/Fonts/Songti.ttc",
]
IDX_TC_BOLD = 2          # Songti TC Bold

GOLD, WHITE, DIM = (232, 183, 74), (255, 255, 255), (184, 189, 199)


def resolve_font():
    for p in FONT_CANDIDATES:
        if Path(p).exists():
            return p
    sys.exit("找不到 Songti.ttc（繁體大字會缺字）。裝了中文字型再跑，或改 FONT_CANDIDATES。")


FONT_TC = None           # main() 裡填


def font(size):
    return ImageFont.truetype(FONT_TC, size, index=IDX_TC_BOLD)


# ───────────────────────── 內建分鏡（品牌招生版 56 秒）─────────────────────────
# 時間軸取自 Whisper 對 music/take2.mp3 的逐句斷點。
# 換歌換素材時複製這段成 JSON 改，別動程式。
DEFAULT_STORYBOARD = {
    "duration": 56.04,
    "cards": {
        "card_open": {"style": "spotlight", "lines": [
            ["AI 數字員工", 62, "GOLD", 0],
            ["龍蝦學院", 190, "WHITE", 26],
            ["每月一班　每班八人", 50, "DIM", 40]]},
        "card_beat": {"style": "fire", "lines": [
            ["龍蝦學院", 168, "WHITE", 0]]},
        "card_army": {"style": "spotlight", "lines": [
            ["AI 龍蝦軍團", 132, "GOLD", 0],
            ["小爆 · 小察 · 小挖 · 小定", 56, "WHITE", 34],
            ["小構 · 小廣 · 小講 · 小辯", 56, "WHITE", 12]]},
        "card_end": {"style": "spotlight", "lines": [
            ["AI 數字員工龍蝦學院", 100, "GOLD", 0],
            ["實戰訓練營　每月一班 · 每班八人", 52, "WHITE", 30],
            ["傑森教練　親自帶班", 46, "DIM", 14],
            ["立即報名　成為開國元勳", 58, "WHITE", 34]]},
    },
    "shots": [
        [0.00,  4.20, "card", "card_open",        "slow"],
        [4.20,  8.00, "ai",   "04_lobster",       "in"],
        [8.00, 11.64, "ai",   "02_ai_army",       "in_right"],
        [11.64, 13.58, "ai",  "01_clock_office",  "in"],
        [13.58, 15.34, "ai",  "06_datastream",    "in_left"],
        [15.34, 17.34, "photo", "p5_audience.jpg", "in"],
        [17.34, 19.54, "photo", "p8_class.jpg",   "out"],
        [19.54, 21.64, "ai",  "03_command",       "in_up"],
        [21.64, 24.60, "photo", "p1_coach.jpg",   "in_right"],
        [24.60, 25.92, "card", "card_beat",       "slow"],
        [25.92, 29.36, "ai",  "05_stage",         "in"],
        [29.36, 33.08, "ai",  "02_ai_army",       "in_down"],
        [33.08, 36.90, "ai",  "06_datastream",    "in"],
        [36.90, 39.88, "card", "card_army",       "slow"],
        [39.88, 42.06, "photo", "p3_room.jpg",    "in_right"],
        [42.06, 44.84, "photo", "p2_hands.jpg",   "in"],
        [44.84, 47.70, "photo", "p4_front.jpg",   "in_left"],
        [47.70, 50.60, "photo", "p6_thumbs.jpg",  "in"],
        [50.60, 51.24, "ai",  "07_gears",         "slow"],
        [51.24, 53.60, "photo", "p7_group.jpg",   "in"],
        [53.60, 56.04, "card", "card_end",        "slow"],
    ],
    "subs": [
        [11.64, 13.58, "天還沒亮　你還在打卡"],
        [13.58, 15.34, "隔壁同行　AI 已經上線"],
        [15.34, 17.34, "你說太老　你說學不來"],
        [17.34, 19.54, "六十歲　一樣可以重開機"],
        [19.54, 21.64, "別再等　別再看"],
        [21.64, 24.50, "龍蝦學院　為你而開"],
        [25.92, 29.36, "龍蝦學院　二十四小時不打烊"],
        [29.36, 33.08, "小爆 小察 小挖 小定　全部上場"],
        [33.08, 36.85, "一句指令　影片文案 網站全開"],
        [39.88, 42.06, "每月一班　每班八人"],
        [42.06, 44.60, "一百講師　開國元勳"],
        [44.84, 47.70, "傑森教練親自帶你　從零做出成果"],
        [47.70, 50.55, "龍蝦學院　等你入列"],
        [51.24, 53.60, "現在就來　當開國元勳"],
    ],
}

COLORS = {"GOLD": GOLD, "WHITE": WHITE, "DIM": DIM}


# ───────────────────────── 字型缺字防呆 ─────────────────────────
def _glyph_bitmap(c, f):
    im = Image.new("L", (160, 160), 0)
    ImageDraw.Draw(im).text((20, 20), c, font=f, fill=255)
    return im.tobytes()


def check_glyphs(text, size=80):
    """繁體缺字防呆：跟私用區字（保證 .notdef）的圖形比對。
    只看有沒有墨水不夠 — 缺字會畫成空心方框，是有墨水的。"""
    f = font(size)
    notdef = _glyph_bitmap("", f)
    bad = [c for c in set(text) if c.strip() and _glyph_bitmap(c, f) == notdef]
    if bad:
        sys.exit(f"字型缺字（會變空白方框）：{bad}　→ 換字型或換符號")


# ───────────────────────── 素材整備 ─────────────────────────
def prep(src: Path, dst: Path):
    """統一成 1920×1080 滿版（手機照先做方向校正），略放大留給運鏡裁切空間。"""
    im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    im = ImageOps.fit(im, (int(W * 1.25), int(H * 1.25)), Image.LANCZOS)
    im.save(dst)
    return dst


def bg_gradient(style="spotlight"):
    """黑紅金三種底：spotlight 品牌／fire 高潮／dim 痛點，統一疊金色斜線紋理。"""
    c_in, c_out = {
        "spotlight": ((138, 24, 24), (26, 10, 10)),
        "fire":      ((204, 69, 40), (60, 15, 10)),
        "dim":       ((76, 80, 142), (26, 30, 40)),
    }[style]
    small = Image.new("RGB", (96, 54))
    d = ImageDraw.Draw(small)
    cx, cy, mx = 48, 27, (48 ** 2 + 27 ** 2) ** 0.5
    for y in range(54):
        for x in range(96):
            t = min(1.0, (((x - cx) ** 2 + (y - cy) ** 2) ** 0.5) / mx)
            d.point((x, y), tuple(int(a + (b - a) * t) for a, b in zip(c_in, c_out)))
    img = small.resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(2))
    d = ImageDraw.Draw(img)
    for i in range(-H, W, 90):                      # 金色斜線紋理 = 品牌質感
        d.line([(i, H), (i + H, 0)], fill=(80, 64, 30), width=2)
    return img


def paste_logo(img, logo_path: Path, size=190, margin=70):
    logo = Image.open(logo_path).convert("RGBA").resize((size, size), Image.LANCZOS)
    base = img.convert("RGBA")
    base.paste(logo, (W - size - margin, H - size - margin), logo)
    return base.convert("RGB")


def centered(d, text, y, f, fill):
    bb = d.textbbox((0, 0), text, font=f)
    d.text(((W - (bb[2] - bb[0])) / 2 - bb[0], y), text, font=f, fill=fill)
    return bb[3] - bb[1]


def card(dst: Path, spec, logo_path: Path):
    """spec: {"style": ..., "lines": [[文字, 字級, 顏色名, 上方留白], ...]}"""
    img = bg_gradient(spec.get("style", "spotlight"))
    d = ImageDraw.Draw(img)
    lines = spec["lines"]
    total = sum(sz * 1.15 + gap for _, sz, _, gap in lines)
    y = (H - total) / 2
    for txt, sz, col, gap in lines:
        check_glyphs(txt)
        y += gap
        centered(d, txt, y, font(sz), COLORS.get(col, WHITE))
        y += sz * 1.15
    img = paste_logo(img, logo_path)
    img.save(dst)
    return dst


def subtitle_png(dst: Path, text):
    """透明字幕層。橫式片壓在畫面高度 80%，白字＋黑描邊＋半透明底條。"""
    check_glyphs(text)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = font(66)
    bb = d.textbbox((0, 0), text, font=f, stroke_width=6)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    x, y = (W - tw) / 2 - bb[0], H * 0.80 - th / 2 - bb[1]
    d.rounded_rectangle([x - 46, y + bb[1] - 26, x + tw + 46, y + bb[1] + th + 26],
                        radius=18, fill=(0, 0, 0, 150))
    d.text((x, y), text, font=f, fill=WHITE, stroke_width=6, stroke_fill=(0, 0, 0))
    img.save(dst)
    return dst


# ───────────────────────── 運鏡 ─────────────────────────
MOTION = {
    "in":       ("1+0.24*on/{N}",    "iw/2-(iw/zoom/2)",        "ih/2-(ih/zoom/2)"),
    "out":      ("1.24-0.24*on/{N}", "iw/2-(iw/zoom/2)",        "ih/2-(ih/zoom/2)"),
    "in_left":  ("1+0.22*on/{N}",    "(iw-iw/zoom)*(1-on/{N})", "ih/2-(ih/zoom/2)"),
    "in_right": ("1+0.22*on/{N}",    "(iw-iw/zoom)*(on/{N})",   "ih/2-(ih/zoom/2)"),
    "in_up":    ("1+0.22*on/{N}",    "iw/2-(iw/zoom/2)",        "(ih-ih/zoom)*(1-on/{N})"),
    "in_down":  ("1+0.22*on/{N}",    "iw/2-(iw/zoom/2)",        "(ih-ih/zoom)*(on/{N})"),
    "slow":     ("1+0.08*on/{N}",    "iw/2-(iw/zoom/2)",        "ih/2-(ih/zoom/2)"),
}


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"FFMPEG FAIL\n{' '.join(str(c) for c in cmd)}\n{r.stderr[-2500:]}")


def make_clip(png: Path, motion: str, dur: float, out: Path):
    n = max(2, round(dur * FPS))
    z, x, y = (e.format(N=n) for e in MOTION[motion])
    vf = f"zoompan=z='{z}':x='{x}':y='{y}':d=1:s={W}x{H}:fps={FPS},setsar=1,format=yuv420p"
    run(["ffmpeg", "-y", "-loop", "1", "-framerate", str(FPS), "-i", str(png),
         "-t", f"{dur}", "-vf", vf, "-frames:v", str(n),
         "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-r", str(FPS), str(out)])


# ───────────────────────── 開跑前先驗素材 ─────────────────────────
def preflight(sb, ai_dir: Path, photo_dir: Path, music: Path, logo: Path):
    """缺什麼一次講完，不要跑到第 15 鏡才爆。"""
    problems = []
    if not music.exists():
        problems.append(f"音軌不存在：{music}")
    if not logo.exists():
        problems.append(f"logo 不存在：{logo}")
    for s, e, kind, payload, motion in sb["shots"]:
        if motion not in MOTION:
            problems.append(f"[{s}-{e}s] 運鏡名稱不存在：{motion}（可用：{', '.join(MOTION)}）")
        if kind == "card":
            if payload not in sb.get("cards", {}):
                problems.append(f"[{s}-{e}s] 分鏡引用了未定義的圖卡：{payload}")
        elif kind == "ai":
            if not (ai_dir / f"{payload}.png").exists():
                problems.append(f"[{s}-{e}s] AI 圖不存在：{ai_dir/(payload + '.png')}")
        elif kind == "photo":
            if not (photo_dir / payload).exists():
                problems.append(f"[{s}-{e}s] 照片不存在：{photo_dir/payload}")
        else:
            problems.append(f"[{s}-{e}s] 不認得的鏡頭類型：{kind}（可用：card / ai / photo）")
    if problems:
        sys.exit("素材檢查沒過：\n  ・" + "\n  ・".join(problems))


def verify_subs(out: Path, sb, work: Path):
    """字幕燒入是 silent failure 高風險區 → 抽幀數底部白字像素驗證。"""
    try:
        import numpy as np
    except ImportError:
        print("   （沒裝 numpy，跳過字幕驗證）")
        return
    checks = [(s + e) / 2 for s, e, _ in sb["subs"][:5]]
    for t in checks:
        png = work / f"_verify_{t:.1f}.png"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{t}", "-i", str(out),
                        "-frames:v", "1", str(png)], capture_output=True)
        if not png.exists():
            continue
        a = np.array(Image.open(png).convert("RGB"))
        band = a[int(H * 0.72):int(H * 0.90), :, :]
        white = int(((band[:, :, 0] > 230) & (band[:, :, 1] > 230) & (band[:, :, 2] > 230)).sum())
        flag = "✅" if white > 3000 else "❌ 字幕疑似沒燒進去"
        print(f"   {t:5.1f}s  白字像素 {white:6d}  {flag}")


def main():
    global FONT_TC
    ap = argparse.ArgumentParser(description="龍蝦學院 AI MV 合成引擎 16:9")
    ap.add_argument("--assets", required=True, type=Path,
                    help="素材目錄，底下要有 ai_images/ photos/ music/")
    ap.add_argument("--music", type=Path, help="音軌檔（預設 <assets>/music/take2.mp3）")
    ap.add_argument("--out", type=Path, help="輸出 mp4（預設 <assets>/龍蝦學院_MV_16x9.mp4）")
    ap.add_argument("--storyboard", type=Path, help="分鏡 JSON（不給就用內建品牌招生版）")
    ap.add_argument("--logo", type=Path, help="logo PNG（預設用 skill 內附的）")
    args = ap.parse_args()

    FONT_TC = resolve_font()

    assets = args.assets.expanduser().resolve()
    ai_dir, photo_dir = assets / "ai_images", assets / "photos"
    music = (args.music or assets / "music" / "take2.mp3").expanduser()
    out = (args.out or assets / "龍蝦學院_MV_16x9.mp4").expanduser()
    logo = (args.logo or SKILL_DIR / "assets" / "logo.png").expanduser()
    sb = json.loads(args.storyboard.read_text()) if args.storyboard else DEFAULT_STORYBOARD

    work = assets / "_work"
    work.mkdir(parents=True, exist_ok=True)

    print(f"素材：{assets}")
    print(f"音軌：{music}")
    print(f"輸出：{out}\n")

    print("⓪ 素材檢查 …", flush=True)
    preflight(sb, ai_dir, photo_dir, music, logo)
    print(f"   ✅ {len(sb['shots'])} 鏡 / {len(sb['subs'])} 字幕 素材齊全")

    print("① 圖卡與素材整備 …", flush=True)
    for name, spec in sb.get("cards", {}).items():
        card(work / f"{name}.png", spec, logo)
    for p in list(photo_dir.glob("*.jpg")) + list(ai_dir.glob("*.png")):
        prep(p, work / f"src_{p.stem}.png")

    print("② 逐鏡頭套運鏡 …", flush=True)
    clips = []
    for i, (s, e, kind, payload, motion) in enumerate(sb["shots"]):
        if kind == "card":
            src = work / f"{payload}.png"
        elif kind == "ai":
            src = work / f"src_{payload}.png"
        else:
            src = work / f"src_{Path(payload).stem}.png"
        clip = work / f"clip{i:02d}.mp4"
        make_clip(src, motion, e - s, clip)
        clips.append(clip)

    print("③ 串接（強制重編碼，不能 -c copy）…", flush=True)
    lst = work / "list.txt"
    lst.write_text("".join(f"file '{c}'\n" for c in clips))
    visual = work / "visual.mp4"
    run(["ffmpeg", "-y", "-fflags", "+genpts", "-f", "concat", "-safe", "0", "-i", str(lst),
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(FPS),
         "-preset", "fast", "-crf", "18", str(visual)])

    print("④ 燒字幕 …", flush=True)
    cmd = ["ffmpeg", "-y", "-i", str(visual)]
    for i, (_, _, txt) in enumerate(sb["subs"]):
        cmd += ["-i", str(subtitle_png(work / f"sub{i:02d}.png", txt))]
    chain, last = [], "[0:v]"
    for i, (s, e, _) in enumerate(sb["subs"]):
        tag = f"[v{i}]"
        chain.append(f"{last}[{i+1}:v]overlay=0:0:enable='between(t,{s},{e})'{tag}")
        last = tag
    subbed = work / "visual_sub.mp4"
    cmd += ["-filter_complex", ";".join(chain), "-map", last,
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast", "-crf", "18",
            str(subbed)]
    run(cmd)

    print("⑤ 混音輸出 …", flush=True)
    run(["ffmpeg", "-y", "-i", str(subbed), "-i", str(music),
         "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-shortest", str(out)])

    print("⑥ 字幕燒入驗證 …", flush=True)
    verify_subs(out, sb, work)

    mb = out.stat().st_size / (1024 * 1024)
    print(f"\n完成：{out}\n   {W}×{H} / {sb['duration']}s / {mb:.1f} MB")


if __name__ == "__main__":
    main()
