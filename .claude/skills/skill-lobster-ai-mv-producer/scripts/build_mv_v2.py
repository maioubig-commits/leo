#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MV 合成引擎 v2（16:9 或 9:16）— 從已驗證的 build_mv_16x9.py 移植，管線與踩雷修法照抄。

比 build_mv_16x9.py 多的四件事：
  1. --aspect 切 16x9（1920×1080）/ 9x16（1080×1920）。橫幅素材塞直幅時不硬裁滿版
     （16:9 硬塞 9:16 只剩中間 32% 寬，室內照空間感全失），改成「中央輕裁成 4:3 置中
     ＋同張圖模糊壓暗當底」，只犧牲左右各 12.5%，上下模糊帶正好放標題與字幕。
  2. logo 可選（--no-logo）：不是每條品牌線都有 logo 圖檔，缺圖時純文字排版。
  3. --silent 出純畫面版，音檔還沒到就能先看節奏。
  4. 字幕與圖卡文字過寬自動降字級；素材只整備分鏡真的用到的，不整包 glob。

用法：
    python3 build_mv_v2.py --assets DIR --storyboard sb.json --aspect 16x9 \
        --music DIR/music/x.mp3 --out ~/Desktop/成片.mp4 --no-logo

素材命名契約同 16:9 版：photos/<檔名含副檔名>、ai_images/<檔名不含副檔名>、cards 走 storyboard。

踩雷備忘（沿用，勿改）：
  ・concat 不能 -c copy（timestamp 亂掉 → overlay enable 失效 → 字幕整片消失）
  ・PIL 不支援 emoji → logo 一律用 PNG paste
  ・繁體大字用 Songti TC（SC 版缺繁體字會渲染成空白）
  ・Songti.ttc 在 /System/Library/Fonts/Supplemental/，不在 /System/Library/Fonts/
"""
import argparse, json, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter, ImageEnhance

SKILL_DIR = Path(__file__).resolve().parent.parent
ASPECTS = {"16x9": (1920, 1080), "9x16": (1080, 1920)}
W, H, FPS = 1920, 1080, 30      # main() 依 --aspect 覆寫 W/H
FG_ASPECT = 1.15         # 直幅片：橫幅素材中央裁成這個寬高比再置中（--fg-aspect 可調）。
                         # 4/3 主體只佔畫面 42%、上下黑帶過厚；1.15 撐到約一半，
                         # 代價是左右各多裁 18%，室內廣角照還吃得住。
NO_BLUR = False          # --no-blur：letterbox 底用黑金漸層取代照片模糊
SS = 2                   # 超採樣倍率 — 運鏡抖動的解法，見 make_clip()

FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Songti.ttc",
    "/System/Library/Fonts/Songti.ttc",
]
IDX_TC_BOLD = 2          # Songti TC Bold

GOLD, WHITE, DIM = (232, 183, 74), (255, 255, 255), (184, 189, 199)
COLORS = {"GOLD": GOLD, "WHITE": WHITE, "DIM": DIM}

FONT_TC = None           # main() 裡填


def resolve_font():
    for p in FONT_CANDIDATES:
        if Path(p).exists():
            return p
    sys.exit("找不到 Songti.ttc（繁體大字會缺字）。裝了中文字型再跑，或改 FONT_CANDIDATES。")


def font(size):
    return ImageFont.truetype(FONT_TC, size, index=IDX_TC_BOLD)


# ───────────────────────── 字型缺字防呆 ─────────────────────────
def _glyph_bitmap(c, f):
    im = Image.new("L", (160, 160), 0)
    ImageDraw.Draw(im).text((20, 20), c, font=f, fill=255)
    return im.tobytes()


def check_glyphs(text, size=80):
    """繁體缺字防呆：跟私用區字（保證 .notdef）的圖形比對。"""
    f = font(size)
    notdef = _glyph_bitmap("", f)
    bad = [c for c in set(text) if c.strip() and _glyph_bitmap(c, f) == notdef]
    if bad:
        sys.exit(f"字型缺字（會變空白方框）：{bad}　→ 換字型或換符號")


# ───────────────────────── 素材整備 ─────────────────────────
def prep(src: Path, dst: Path):
    """整成 SS 倍尺寸滿版（手機照先做方向校正），再放大 1.25 倍留給 zoompan 裁切空間。
    存這麼大是因為運鏡在 SS 倍空間跑（見 make_clip），素材不夠大會被放糊。
    直幅片另走 letterbox：橫幅素材硬裁成 9:16 會失去室內空間感，改中央輕裁 4:3 置中，
    同張圖模糊壓暗鋪底。"""
    im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    cw, ch = int(W * SS * 1.25), int(H * SS * 1.25)
    # 素材比例跟畫面夠接近就直接滿版 — 原生直幅素材放進直幅片也走這條，
    # 不然會被當成「橫塞直」裁掉上下再補模糊邊，白白毀掉素材。
    if 0.72 <= (im.width / im.height) / (W / H) <= 1.38:
        ImageOps.fit(im, (cw, ch), Image.LANCZOS).save(dst)
        return dst
    if NO_BLUR:     # Leo 不要直式片霧化：底改用品牌黑金漸層，不拿照片模糊鋪底
        bg = bg_gradient("blackgold").resize((cw, ch), Image.BICUBIC)
    else:
        bg = ImageOps.fit(im, (cw, ch), Image.LANCZOS).filter(ImageFilter.GaussianBlur(48 * SS))
        bg = ImageEnhance.Brightness(bg).enhance(0.40)
    fgh = int(cw / FG_ASPECT)
    fg = ImageOps.fit(im, (cw, fgh), Image.LANCZOS)
    bg.paste(fg, (0, (ch - fgh) // 2))
    bg.save(dst)
    return dst


def bg_gradient(style="spotlight"):
    """三種底：spotlight 品牌／fire 高潮／dim 沉靜，統一疊金色斜線紋理。"""
    c_in, c_out = {
        "spotlight": ((138, 24, 24), (26, 10, 10)),
        "fire":      ((204, 69, 40), (60, 15, 10)),
        "dim":       ((76, 80, 142), (26, 30, 40)),
        "night":     ((28, 52, 74), (10, 14, 20)),
        "blackgold": ((72, 56, 22), (6, 6, 8)),   # 護國神山式黑金：中心暗金聚光、邊緣近全黑
    }[style]
    sw, sh = (96, 54) if W >= H else (54, 96)
    small = Image.new("RGB", (sw, sh))
    d = ImageDraw.Draw(small)
    cx, cy = sw / 2, sh / 2
    mx = (cx ** 2 + cy ** 2) ** 0.5
    for y in range(sh):
        for x in range(sw):
            t = min(1.0, (((x - cx) ** 2 + (y - cy) ** 2) ** 0.5) / mx)
            d.point((x, y), tuple(int(a + (b - a) * t) for a, b in zip(c_in, c_out)))
    cw, ch = W * SS, H * SS                       # 圖卡也畫在 SS 倍空間，跟照片同尺寸進運鏡
    img = small.resize((cw, ch), Image.BICUBIC).filter(ImageFilter.GaussianBlur(2 * SS))
    d = ImageDraw.Draw(img)
    line_col = (128, 102, 44) if style == "blackgold" else (80, 64, 30)
    for i in range(-ch, cw, 90 * SS):
        d.line([(i, ch), (i + ch, 0)], fill=line_col, width=2 * SS)
    return img


def paste_logo(img, logo_path, margin=56):
    if not logo_path:
        return img
    size = (190 if W >= H else 150) * SS
    logo = Image.open(logo_path).convert("RGBA").resize((size, size), Image.LANCZOS)
    base = img.convert("RGBA")
    base.paste(logo, (W * SS - size - margin * SS, H * SS - size - margin * SS), logo)
    return base.convert("RGB")


def centered(d, text, y, f, fill, width):
    bb = d.textbbox((0, 0), text, font=f)
    d.text(((width - (bb[2] - bb[0])) / 2 - bb[0], y), text, font=f, fill=fill)
    return bb[3] - bb[1]


def fit_font(d, text, size, max_w, floor=30):
    """一行塞不下就降級，降到能塞為止。"""
    while size > floor:
        f = font(size)
        bb = d.textbbox((0, 0), text, font=f)
        if bb[2] - bb[0] <= max_w:
            return f
        size -= 3
    return font(floor)


def card(dst: Path, spec, logo_path):
    """spec: {"style": ..., "lines": [[文字, 字級, 顏色名, 上方留白], ...]}
    分鏡 JSON 的字級是以 1920×1080 為基準寫的，這裡統一乘 SS 放到超採樣空間。"""
    img = bg_gradient(spec.get("style", "spotlight"))
    d = ImageDraw.Draw(img)
    lines = [(t, sz * SS, c, g * SS) for t, sz, c, g in spec["lines"]]
    total = sum(sz * 1.15 + gap for _, sz, _, gap in lines)
    y = (H * SS - total) / 2
    for txt, sz, col, gap in lines:
        check_glyphs(txt)
        y += gap
        centered(d, txt, y, fit_font(d, txt, sz, (W - 110) * SS, floor=30 * SS),
                 COLORS.get(col, WHITE), W * SS)
        y += sz * 1.15
    img = paste_logo(img, logo_path)
    img.save(dst)
    return dst


def watermark_png(dst: Path, logo_path: Path):
    """全片常駐浮水印層（右下角）。跟 card 的 logo 不同：card 只蓋在圖卡上，
    照片鏡頭沒有，品牌露出會斷掉；這層是疊在整支片上的。"""
    size = int(W * (0.105 if W >= H else 0.14))
    margin = int(W * 0.028)
    logo = Image.open(logo_path).convert("RGBA").resize((size, size), Image.LANCZOS)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    img.paste(logo, (W - size - margin, H - size - margin), logo)
    img.save(dst)
    return dst


def subtitle_png(dst: Path, text):
    """透明字幕層，壓在畫面高度 80%（直幅片正好落在下方模糊帶）。白字＋黑描邊＋半透明底條。"""
    check_glyphs(text)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = fit_font(d, text, 66 if W >= H else 64, W - 130)
    bb = d.textbbox((0, 0), text, font=f, stroke_width=5)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    x, y = (W - tw) / 2 - bb[0], H * 0.80 - th / 2 - bb[1]
    d.rounded_rectangle([x - 36, y + bb[1] - 22, x + tw + 36, y + bb[1] + th + 22],
                        radius=16, fill=(0, 0, 0, 150))
    d.text((x, y), text, font=f, fill=WHITE, stroke_width=5, stroke_fill=(0, 0, 0))
    img.save(dst)
    return dst


# ───────────────────────── 運鏡 ─────────────────────────
# 幅度刻意壓小、平移只走可移動範圍的中間 60%（不貼邊）：
# 短鏡頭配大幅度會晃，滑順感來自「慢而穩」，不是走得遠。
MOTION = {
    "in":       ("1+0.16*on/{N}",    "iw/2-(iw/zoom/2)",              "ih/2-(ih/zoom/2)"),
    "out":      ("1.16-0.16*on/{N}", "iw/2-(iw/zoom/2)",              "ih/2-(ih/zoom/2)"),
    "in_left":  ("1+0.14*on/{N}",    "(iw-iw/zoom)*(0.8-0.6*on/{N})", "ih/2-(ih/zoom/2)"),
    "in_right": ("1+0.14*on/{N}",    "(iw-iw/zoom)*(0.2+0.6*on/{N})", "ih/2-(ih/zoom/2)"),
    "in_up":    ("1+0.14*on/{N}",    "iw/2-(iw/zoom/2)",              "(ih-ih/zoom)*(0.8-0.6*on/{N})"),
    "in_down":  ("1+0.14*on/{N}",    "iw/2-(iw/zoom/2)",              "(ih-ih/zoom)*(0.2+0.6*on/{N})"),
    "slow":     ("1+0.06*on/{N}",    "iw/2-(iw/zoom/2)",              "ih/2-(ih/zoom/2)"),
}


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"FFMPEG FAIL\n{' '.join(str(c) for c in cmd)}\n{r.stderr[-2500:]}")


def make_clip(png: Path, motion: str, dur: float, out: Path):
    """zoompan 的 x/y 位移會被取整成整數像素，慢速運鏡就一格一格跳；高頻紋理（磨石子、
    格紋壁紙）逐幀縮放還會產生摩爾紋閃爍。兩個問題同一解：在 SS 倍空間跑運鏡，再用
    lanczos 縮回目標尺寸 — 取整誤差變成 1/SS 像素，縮小同時等於做了抗鋸齒超採樣。"""
    n = max(2, round(dur * FPS))
    z, x, y = (e.format(N=n) for e in MOTION[motion])
    vf = (f"zoompan=z='{z}':x='{x}':y='{y}':d=1:s={W*SS}x{H*SS}:fps={FPS},"
          f"scale={W}:{H}:flags=lanczos,setsar=1,format=yuv420p")
    run(["ffmpeg", "-y", "-loop", "1", "-framerate", str(FPS), "-i", str(png),
         "-t", f"{dur}", "-vf", vf, "-frames:v", str(n),
         "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-r", str(FPS), str(out)])


# ───────────────────────── 開跑前先驗素材 ─────────────────────────
def preflight(sb, ai_dir: Path, photo_dir: Path, music, logo):
    """缺什麼一次講完，不要跑到第 15 鏡才爆。"""
    problems = []
    if music and not music.exists():
        problems.append(f"音軌不存在：{music}")
    if logo and not logo.exists():
        problems.append(f"logo 不存在：{logo}（不掛 logo 請加 --no-logo）")
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
    """字幕燒入是 silent failure 高風險區 → 抽幀數底部白字像素驗證。
    字幕是白字＋黑描邊，所以驗白色像素；改字幕顏色要同步改這裡，否則驗證恆假。"""
    try:
        import numpy as np
    except ImportError:
        print("   （沒裝 numpy，跳過字幕驗證）")
        return
    ok = True
    for s, e, _ in sb["subs"][:5]:
        t = (s + e) / 2
        png = work / f"_verify_{t:.1f}.png"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{t}", "-i", str(out),
                        "-frames:v", "1", str(png)], capture_output=True)
        if not png.exists():
            continue
        a = np.array(Image.open(png).convert("RGB"))
        band = a[int(H * 0.72):int(H * 0.90), :, :]
        white = int(((band[:, :, 0] > 230) & (band[:, :, 1] > 230) & (band[:, :, 2] > 230)).sum())
        good = white > 3000
        ok &= good
        print(f"   {t:5.1f}s  白字像素 {white:6d}  {'✅' if good else '❌ 字幕疑似沒燒進去'}")
    return ok


def main():
    global FONT_TC, W, H, FG_ASPECT, NO_BLUR
    ap = argparse.ArgumentParser(description="MV 合成引擎 v2（16:9 / 9:16）")
    ap.add_argument("--assets", required=True, type=Path,
                    help="素材目錄，底下要有 photos/（ai_images/ music/ 視分鏡而定）")
    ap.add_argument("--aspect", default="16x9", choices=list(ASPECTS), help="輸出比例")
    ap.add_argument("--music", type=Path, help="音軌檔；不給且沒 --silent 會找 <assets>/music/take1.mp3")
    ap.add_argument("--silent", action="store_true", help="不混音，輸出純畫面")
    ap.add_argument("--out", type=Path, help="輸出 mp4（預設 <assets>/MV_<aspect>.mp4）")
    ap.add_argument("--storyboard", required=True, type=Path, help="分鏡 JSON")
    ap.add_argument("--logo", type=Path, help="logo PNG")
    ap.add_argument("--no-logo", action="store_true", help="不掛 logo（純文字品牌線）")
    ap.add_argument("--watermark", type=Path,
                    help="全片右下角常駐 logo PNG（去背）。跟 --logo 的差別見 watermark_png()")
    ap.add_argument("--no-blur", action="store_true",
                    help="橫幅素材塞直幅時，底用黑金漸層而不是模糊照片（不要霧化）")
    ap.add_argument("--fg-aspect", type=float, default=FG_ASPECT,
                    help="直幅片主體裁切寬高比：小=主體大但左右裁得多（預設 1.15）")
    args = ap.parse_args()

    FONT_TC = resolve_font()
    FG_ASPECT = args.fg_aspect
    NO_BLUR = args.no_blur
    W, H = ASPECTS[args.aspect]

    assets = args.assets.expanduser().resolve()
    ai_dir, photo_dir = assets / "ai_images", assets / "photos"
    music = None if args.silent else (args.music or assets / "music" / "take1.mp3").expanduser()
    out = (args.out or assets / f"MV_{args.aspect}.mp4").expanduser()
    logo = None if args.no_logo else (args.logo or SKILL_DIR / "assets" / "logo.png").expanduser()
    wm = args.watermark.expanduser() if args.watermark else None
    if wm and not wm.exists():
        sys.exit(f"浮水印檔不存在：{wm}")
    sb = json.loads(args.storyboard.read_text())

    # 兩種比例的中間檔分開放：共用一個 _work 的話，跑完 9:16 會把 16:9 的
    # clip/visual 覆蓋掉，之後只想換字幕或換音軌也得重算整段運鏡。
    work = assets / f"_work_{args.aspect}"
    work.mkdir(parents=True, exist_ok=True)

    print(f"素材：{assets}")
    print(f"音軌：{music or '（無聲版）'}")
    print(f"輸出：{out}\n")

    print("⓪ 素材檢查 …", flush=True)
    preflight(sb, ai_dir, photo_dir, music, logo)
    print(f"   ✅ {len(sb['shots'])} 鏡 / {len(sb['subs'])} 字幕 素材齊全")

    print("① 圖卡與素材整備 …", flush=True)
    for name, spec in sb.get("cards", {}).items():
        card(work / f"{name}.png", spec, logo)
    used = {Path(p).stem for _, _, k, p, _ in sb["shots"] if k in ("photo", "ai")}
    for p in list(photo_dir.glob("*.jpg")) + list(ai_dir.glob("*.png")):
        if p.stem in used:
            prep(p, work / f"src_{p.stem}.png")

    print("② 逐鏡頭套運鏡 …", flush=True)
    clips = []
    for i, (s, e, kind, payload, motion) in enumerate(sb["shots"]):
        src = work / (f"{payload}.png" if kind == "card" else f"src_{Path(payload).stem}.png")
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

    print("④ 燒字幕" + ("＋浮水印 …" if wm else " …"), flush=True)
    cmd = ["ffmpeg", "-y", "-i", str(visual)]
    if wm:
        cmd += ["-i", str(watermark_png(work / "watermark.png", wm))]
    for i, (_, _, txt) in enumerate(sb["subs"]):
        cmd += ["-i", str(subtitle_png(work / f"sub{i:02d}.png", txt))]
    chain, last = [], "[0:v]"
    base = 1
    if wm:                                    # 浮水印全時段疊，不帶 enable
        chain.append(f"{last}[1:v]overlay=0:0[wm]")
        last, base = "[wm]", 2
    for i, (s, e, _) in enumerate(sb["subs"]):
        tag = f"[v{i}]"
        chain.append(f"{last}[{base+i}:v]overlay=0:0:enable='between(t,{s},{e})'{tag}")
        last = tag
    subbed = work / "visual_sub.mp4"
    cmd += ["-filter_complex", ";".join(chain), "-map", last,
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast", "-crf", "18",
            str(subbed)]
    run(cmd)

    if music:
        print("⑤ 混音輸出 …", flush=True)
        run(["ffmpeg", "-y", "-i", str(subbed), "-i", str(music),
             "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-shortest", str(out)])
    else:
        print("⑤ 無聲輸出 …", flush=True)
        run(["ffmpeg", "-y", "-i", str(subbed), "-c:v", "copy", str(out)])

    print("⑥ 字幕燒入驗證 …", flush=True)
    verify_subs(out, sb, work)

    mb = out.stat().st_size / (1024 * 1024)
    print(f"\n完成：{out}\n   {W}×{H} / {sb['duration']}s / {mb:.1f} MB")


if __name__ == "__main__":
    main()
