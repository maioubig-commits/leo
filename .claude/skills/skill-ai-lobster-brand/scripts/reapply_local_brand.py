#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 9 隻員工腳本裡寫死的「AI數字員工龍蝦學院」改成環境變數控制。

規則：預設空字串＝不掛品牌；要掛時 export LOBSTER_BRAND="AI數字員工龍蝦學院"。
"""
import re, sys
from pathlib import Path

# 目標資料夾：第一個參數，預設本機 skills（方便先對副本試跑）
SK = Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else Path.home() / ".claude/skills"

BLOCK = '''
# ── 品牌（本機規則：預設不掛）─────────────────────────────
# 對外產出預設不掛任何品牌。要掛龍蝦學院品牌時：
#     export LOBSTER_BRAND="AI數字員工龍蝦學院"
# 判斷準則見 skill-ai-lobster-brand 的「適用範圍」。
BRAND = os.environ.get("LOBSTER_BRAND", "")
'''.rstrip("\n")

# (檔案, [(舊字串, 新字串), ...], 是否需要插入 BLOCK)
JOBS = [
 ("skill-xiao-shu/scripts/sopdoc.py", [
   # 母版原有 bug：f-string 表達式內含反斜線，Python 3.11 以下 SyntaxError
   ('                items.append(f"<li>{inline(re.sub(r\'^\\s*\\d+\\.\\s+\', \'\', lines[i]))}</li>"); i += 1',
    '                # 先算好再插值：f-string 表達式內不能含反斜線（Python 3.11 以下會 SyntaxError）\n'
    '                item = inline(re.sub(r"^\\s*\\d+\\.\\s+", "", lines[i]))\n'
    '                items.append(f"<li>{item}</li>"); i += 1'),
   ('    hdr = make_header_png("AI數字員工龍蝦學院", os.path.join(outdir, ".header.png"))\n    stamp_pdf(pdf_path, hdr)',
    '    if BRAND:\n'
    '        hdr = make_header_png(BRAND, os.path.join(outdir, ".header.png"))\n'
    '        stamp_pdf(pdf_path, hdr)'),
   # 先算好再插值：f-string 內不能再用同種引號（Python 3.11 以下 SyntaxError）
   ('    print(f"✓ PDF → {pdf_path}（{n} 頁，每頁已掛 logo）")',
    '    brand_note = f"，每頁已掛 {BRAND}" if BRAND else "，未掛品牌"\n'
    '    print(f"✓ PDF → {pdf_path}（{n} 頁{brand_note}）")'),
 ], True),

 ("skill-xiao-shu/scripts/mailbrief.py", [
   ('L.append("整理：小書（Xiao Shu）｜**AI數字員工龍蝦學院**")',
    'L.append("整理：小書（Xiao Shu）" + (f"｜**{BRAND}**" if BRAND else ""))'),
 ], True),

 ("skill-xiao-zhao/scripts/zhao.py", [
   ('BRAND = "AI數字員工龍蝦學院"',
    '# 品牌：預設不掛。要掛時 export LOBSTER_BRAND="AI數字員工龍蝦學院"\n'
    'BRAND = os.environ.get("LOBSTER_BRAND", "")'),
   ('DISCLAIMER = ("本文件由「AI數字員工龍蝦學院」AI 員工小招協助整理草擬，僅供單位內部作業參考。"',
    'DISCLAIMER = ("本文件由" + (f"「{BRAND}」" if BRAND else "") + "AI 員工小招協助整理草擬，僅供單位內部作業參考。"'),
 ], False),

 ("skill-xiao-sou/scripts/blogen.py", [
   # 母版這支沒有 import os，BRAND 讀環境變數前要先補（漏了會 NameError，編譯檢查抓不到）
   ('import json\nimport re\n', 'import json\nimport os\nimport re\n'),
   ('BRAND = "AI數字員工龍蝦學院"\nBRAND_SHORT = "龍蝦學院"',
    '# 品牌：預設不掛。要掛時 export LOBSTER_BRAND / LOBSTER_BRAND_SHORT\n'
    'BRAND = os.environ.get("LOBSTER_BRAND", "")\n'
    'BRAND_SHORT = os.environ.get("LOBSTER_BRAND_SHORT", BRAND)'),
   ('    "brand": "AI數字員工龍蝦學院",', '    "brand": BRAND,'),
 ], False),

 ("skill-xiao-sou/scripts/lecture_pages.py", [
   # 母版這支沒有 import os，BRAND 讀環境變數前要先補（漏了會 NameError，編譯檢查抓不到）
   ('import json\nimport re\n', 'import json\nimport os\nimport re\n'),
   ('BRAND = "AI數字員工龍蝦學院"\nBRAND_SHORT = "龍蝦學院"',
    '# 品牌：預設不掛。要掛時 export LOBSTER_BRAND / LOBSTER_BRAND_SHORT\n'
    'BRAND = os.environ.get("LOBSTER_BRAND", "")\n'
    'BRAND_SHORT = os.environ.get("LOBSTER_BRAND_SHORT", BRAND)'),
 ], False),

 ("skill-xiao-sou/scripts/seocheck.py", [
   ('L.append(f"> 檢測日期：{today}　·　檢測員：小搜（AI 數字員工龍蝦學院）\\n")',
    'L.append(f"> 檢測日期：{today}　·　檢測員：小搜" + (f"（{BRAND}）" if BRAND else "") + "\\n")'),
 ], True),

 ("skill-xiao-wei/scripts/webcheck.py", [
   ('L += ["", "---", "🦞 AI數字員工龍蝦學院｜維運專員 小維"]',
    'L += ["", "---", (f"🦞 {BRAND}｜維運專員 小維" if BRAND else "維運專員 小維")]'),
 ], True),

 ("skill-xiao-mei/scripts/poster.py", [
   ('                  "**AI數字員工龍蝦學院**　🦞　小美 Xiao Mei"]',
    '                  (f"**{BRAND}**　🦞　小美 Xiao Mei" if BRAND else "小美 Xiao Mei")]'),
 ], True),

 ("skill-xiao-mei/scripts/preflight.py", [
   ('out.append("**AI數字員工龍蝦學院**　🦞　小美 Xiao Mei")',
    'out.append(f"**{BRAND}**　🦞　小美 Xiao Mei" if BRAND else "小美 Xiao Mei")'),
 ], True),

 ("skill-xiao-kong/scripts/spacemgr.py", [
   ('L.append("**AI數字員工龍蝦學院**　🦞　由小空 Xiao Kong 協助整理")',
    'L.append(f"**{BRAND}**　🦞　由小空 Xiao Kong 協助整理" if BRAND else "由小空 Xiao Kong 協助整理")'),
 ], True),

 ("skill-xiao-zhang/scripts/bookkeeper.py", [
   ('L.append("＿AI數字員工龍蝦學院 🦞 財務部・小帳＿")',
    'L.append(f"＿{BRAND} 🦞 財務部・小帳＿" if BRAND else "＿財務部・小帳＿")'),
 ], True),

 ("skill-xiao-jiang/scripts/deck_kit.py", [
   ('[("AI數字員工龍蝦學院 ▎ LIVE", 18, GOLD, True)], align=PP_ALIGN.CENTER)',
    '[((f"{BRAND} ▎ LIVE" if BRAND else "LIVE"), 18, GOLD, True)], align=PP_ALIGN.CENTER)'),
 ], True),

 ("skill-xiao-yun/scripts/gen_copy_pack.py", [
   ('A("> 出品：AI數字員工龍蝦學院 · 內容部小運  ")',
    'A(f"> 出品：{BRAND} · 內容部小運  " if BRAND else "> 出品：內容部小運  ")'),
   # 用 + 明確串接：隱式字串相接後面接括號會被當成函式呼叫
   ('    A("> 下列項目仍須人工確認：貨對板（標題承諾片中真的有）、"\n'
    '      "YouTube AI 內容營利新規（非套版幻燈片／非情緒操弄／AI 人格不談健康金融法律政治）、"\n'
    '      "對外交付物已掛「AI數字員工龍蝦學院」品牌 + logo。")',
    '    brand_note = (f"對外交付物已掛「{BRAND}」品牌 + logo。" if BRAND\n'
    '                  else "對外交付物品牌：依 skill-ai-lobster-brand「適用範圍」判斷，本機預設不掛。")\n'
    '    A("> 下列項目仍須人工確認：貨對板（標題承諾片中真的有）、"\n'
    '      "YouTube AI 內容營利新規（非套版幻燈片／非情緒操弄／AI 人格不談健康金融法律政治）、"\n'
    '      + brand_note)'),
 ], True),
]


def ensure_block(text: str) -> str:
    """在最後一行 import 之後插入 BRAND 定義（含必要的 import os）。"""
    lines = text.split("\n")
    last = -1
    for i, l in enumerate(lines[:80]):
        if re.match(r'^(import |from )\S', l):
            last = i
    if last < 0:
        raise RuntimeError("找不到 import 區塊")
    block = BLOCK
    if not re.search(r'^(import os\b|import os,|from os import)', text, re.M) \
       and not re.search(r'^import .*\bos\b', text, re.M):
        block = "import os\n" + block
    lines.insert(last + 1, block)
    return "\n".join(lines)


ok = fail = 0
for rel, subs, need_block in JOBS:
    p = SK / rel
    if not p.exists():
        print(f"—  {rel}（檔案不存在，略過）")
        continue
    t = orig = p.read_text(errors='replace')
    # 每個替換後的新字串都已存在＝之前套用過，直接略過（可重複執行）
    if all(n in t for _, n in subs):
        print(f"⏭  {rel}（已套用，略過）")
        ok += 1
        continue
    problems = []
    for old, new in subs:
        if old not in t:
            problems.append(old[:60])
            continue
        t = t.replace(old, new, 1)
    if problems:
        print(f"❌ {rel}\n   找不到：{problems}")
        fail += 1
        continue
    if need_block:
        t = ensure_block(t)
    p.write_text(t)
    print(f"✅ {rel}（{len(subs)} 處）")
    ok += 1

print(f"\n程式碼層：完成 {ok} 個檔案，失敗 {fail} 個")

# ── 第二部分：直屬主管改成 Leo ─────────────────────────────
# 母版寫「直屬傑森教練（CEO）」，本機老闆是 Leo。只改同時含「直屬」和「傑森」的那一行，
# 「由傑森教練創辦」「創建人」這類歷史事實不動。
REPORT_FILES = ["skill-xiao-ding", "skill-xiao-bian", "skill-xiao-jie", "skill-xiao-qiang",
                "skill-xiao-xi", "skill-xiao-zhang", "skill-xiao-shu"]

def fix_report_line(l):
    l = l.replace("傑森教練（CEO）", "Leo").replace("傑森教練 CEO", "Leo").replace("傑森教練", "Leo")
    return re.sub(r"直屬Leo", "直屬 Leo", l)

print("\n── 直屬主管 → Leo ──")
for d in REPORT_FILES:
    p = SK / d / "SKILL.md"
    if not p.exists():
        print(f"—  {d}/SKILL.md（檔案不存在，略過）")
        continue
    lines = p.read_text(errors="replace").split("\n")
    n = 0
    for i, l in enumerate(lines):
        if "直屬" in l and "傑森" in l:
            new = fix_report_line(l)
            if new != l:
                lines[i] = new; n += 1
    if n:
        p.write_text("\n".join(lines)); print(f"✅ {d}/SKILL.md（{n} 處）")
    else:
        print(f"⏭  {d}/SKILL.md（已套用，略過）")


# ── 第三部分：小帳、小書裡指稱使用者的「教練」→ Leo ────────────
# 母版把使用者稱為「教練」（指傑森教練），會印在財務報表、郵件草稿、SOP 草稿上。
COACH_SKILLS = ["skill-xiao-zhang", "skill-xiao-shu"]
TEXT_EXT = {".md", ".py", ".json", ".csv", ".txt"}

def fix_coach_line(l):
    l = l.replace("傑森教練", "Leo").replace("教練", "Leo")
    l = re.sub(r"(?<=[一-鿿])Leo", " Leo", l)
    l = re.sub(r"Leo(?=[一-鿿])", "Leo ", l)
    return l

print("\n── 小帳／小書：「教練」→ Leo ──")
for d in COACH_SKILLS:
    root = SK / d
    if not root.exists():
        print(f"—  {d}（不存在，略過）")
        continue
    n_total = 0
    for f in sorted(root.rglob("*")):
        if not f.is_file() or f.suffix not in TEXT_EXT or "__pycache__" in f.parts:
            continue
        lines = f.read_text(errors="replace").split("\n")
        n = 0
        for i, l in enumerate(lines):
            if "教練" in l:
                new = fix_coach_line(l)
                if new != l:
                    lines[i] = new; n += 1
        if n:
            f.write_text("\n".join(lines)); n_total += n
    print(f"✅ {d}（{n_total} 處）" if n_total else f"⏭  {d}（已套用，略過）")


# ── 第四部分：小辯、小定裡指稱老闆的「傑森教練」→ Leo ──────────
# 只換下面這幾句；「創建人：傑森教練」「為傑森教練教學素材提供案例」是事實／學院專屬，不動。
BOSS_SUBS = [
    ("skill-xiao-bian/SKILL.md",            "給傑森教練或客戶看",              "給 Leo 或客戶看"),
    ("skill-xiao-bian/SKILL.md",            "對 **傑森教練** 或 **客戶本人**", "對 **Leo** 或 **客戶本人**"),
    ("skill-xiao-bian/output_templates.md", "給傑森教練或客戶看",              "給 Leo 或客戶看"),
    ("skill-xiao-ding/SKILL.md",            "[傑森教練 / 客戶創辦人]",         "[Leo / 客戶創辦人]"),
]
print("\n── 小辯／小定：指稱老闆的「傑森教練」→ Leo ──")
for rel, old, new in BOSS_SUBS:
    p = SK / rel
    if not p.exists():
        print(f"—  {rel}（不存在，略過）")
        continue
    t = p.read_text(errors="replace")
    if old in t:
        p.write_text(t.replace(old, new)); print(f"✅ {rel}：{new}")
    elif new in t:
        print(f"⏭  {rel}（已套用，略過）")
    else:
        print(f"❌ {rel}：找不到原文（母版可能改版）"); fail += 1

sys.exit(1 if fail else 0)
