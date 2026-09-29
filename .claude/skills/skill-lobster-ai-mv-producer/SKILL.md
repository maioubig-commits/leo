---
name: skill-lobster-ai-mv-producer
description: 龍蝦學院 AI MV 製作 SOP — 用 Suno V5.5 生洗腦中文 EDM 主題曲 + Gemini Imagen-4 生 AI 視覺 + PIL 黑紅金圖卡 + 講座照片 Ken Burns + ffmpeg 動態合成,輸出 16:9 實體講座開場(投影機/大螢幕)或 9:16 招生 Shorts(YT/IG/TikTok)。對標《護國神山》12 萬觀看 AI MV 公式。**觸發詞**:「AI MV」、「龍蝦 MV」、「主題曲」、「品牌曲」、「Suno MV」、「護國神山風」、「招生 MV」、「實體講座開場」、「實體開場曲」、「龍蝦學院主題曲」、「製作 MV」、「品牌音樂」。本 skill 用於商業招生資產(訓練營開場 / FB 廣告 / 招生頁主視覺)— 100% 商業權(Suno Pro 訂閱)。
---

# 龍蝦學院 AI MV 製作 SOP

## 戰略意義

龍蝦學院實體訓練營**每月開班 1 場 / 100 講師認證**核心商業目標,需要強品牌儀式感資產。AI MV 一次製作可重複使用:

- ✅ **實體講座開場**:每月 1 場 × 12 個月 = **12 次曝光**(投影機大螢幕)
- ✅ **招生頁 hero 視覺**:用截圖當網站主視覺(常態使用)
- ✅ **FB/IG 廣告素材**:60 秒精華版 / 15 秒 hook 版(月月跑)
- ✅ **儀式典禮**:認證學員頒獎、年度盛會
- ✅ **YT Shorts**:衝流量(雖然轉化率不如書本精讀)

**對標案例**:房叔《護國神山》(12 萬觀看)— AI 生歌 + 黑金科技視覺 + 洗腦 hook + 中文 Rap

**成本** vs **外包**:
- 外包請音樂人寫主題曲:NT$ 20,000-50,000
- 本 skill 全自動:Suno Pro $10/月 + 我的時間,**單次 ~NT$ 320**(60 倍便宜)

---

## 完整 5 步驟 SOP

### Step 1:寫歌詞 + 選曲風

**歌詞結構模板**(對標《護國神山》Verse-Chorus-Bridge 公式):

```
[Verse 1] — 痛點(4 句,共 ~8 秒)
打卡上班還在等錢
別人 AI 龍蝦已經連夜
你說太老學不來
六十三歲 Jensen 練到五兆

[Pre-Chorus] — 反轉(2 句,~5 秒)
醒醒吧 兄弟姊妹
龍蝦學院 為你而開

[Chorus] — 主歌洗腦(4 句,~15 秒)
龍蝦學院 24 小時不打烊
小爆 小察 小挖 小定 全部上場
小辯 小強 小潔 小構 連夜開戰
AI 龍蝦軍團 全部歸我管

[Verse 2] — 情境(4 句,~10 秒)
[依用途調整]
- 實體開場版:今天你來到這裡 / 就是最棒的決定 / 看看身邊的 8 位戰友 / 你們將是 開國元勳
- 招生 Shorts 版:每月一班 每班八人 / 100 講師 開國元勳 / 傑森教練 親自帶你 / 從零到月入百萬

[Outro] — CTA(2-3 句,~5 秒)
[依用途調整]
- 實體開場版:歡迎來到 龍蝦學院 / 熱烈掌聲 給我們的 / 傑森教練 請上台
- 招生 Shorts 版:龍蝦學院經濟學 / 按訂閱看完整版 / 我們下集見
```

**Suno style prompt 鎖定**:

```
實體開場版(燃 + 儀式感):
Mandarin EDM with Rap verses, anthem opening, stadium atmosphere, build-up intro, viral pop, 130 BPM, energetic, Taiwanese male vocal, hype crowd

招生 Shorts 版(viral + hook):
Mandarin EDM with Rap verses, catchy hook, viral pop, 130 BPM, energetic, Taiwanese male vocal
```

### Step 2:Suno V5.5 生歌(用戶手動)

1. https://suno.com/create
2. 確認帳號是 **Pro $10/月**(才有商業權 + 完整 v5.5)
3. **先進的** + **v5.5** 模式
4. 歌詞 + style prompt 貼上
5. 創造 → 等 40-90 秒 → 拿 2 首
6. 用 Whisper 篩選:選**完整無 bug + 「Jensen / 傑森教練」發音清楚**那首
7. 下載 WAV(高品質)

**常見踩雷**:
- ⚠️ Suno TTS 把「拚」唱成「pàn」→ 一律用「拼」(同 skill-jason-digital-human)
- ⚠️ 「Jensen」英文名會唱成「真森」→ 可接受 / 或改寫「黃仁勳」
- ⚠️ 末段「Jayson 教練」死循環 bug → 兩首 A/B test,丟出有 bug 那首

### Step 3:Gemini Imagen-4 生 AI 視覺

腳本:`scripts/gen_ai_images.py`

5 張預設視覺 prompts(對標《護國神山》深紅金科技風):
1. **NVIDIA 5T 紅金晶片**:cinematic NVIDIA AI chip glowing red and gold
2. **8 大 AI 軍團**:8 abstract glowing robot avatars in red cyberpunk hall
3. **舞台聚光燈**:empty stage with dramatic spotlights, red and gold curtains
4. **龍蝦品牌**:stylized geometric red lobster icon, gold particles
5. **數據流**:abstract red and gold digital data streams, $5T text

**模型**:`imagen-4.0-fast-generate-001`(預設 imagen-4.0-generate-001 會限流 429)
**aspect**:`16:9`
**成本**:Gemini API 免費額度內

**ENV 需求**:
```bash
export GEMINI_API_KEY="..."  # ~/.zshrc
```

跑法:
```bash
source ~/.zshrc && /usr/bin/python3 gen_ai_images.py
```

### Step 4:Ken Burns 動態鏡頭 + PIL 圖卡

**8 種運鏡輪換**(每張照片/AI 圖隨機選一種):
```python
MOTION_TYPES = [
    "zoom_in_center", "zoom_out_center",
    "zoom_in_pan_left", "zoom_in_pan_right",
    "zoom_in_pan_up", "zoom_in_pan_down",
    "zoom_out_drift_left", "zoom_out_drift_right",
]
```

**PIL 黑紅金圖卡** 3 種背景樣式:
| 背景 | 顏色 | 用途 |
|---|---|---|
| `spotlight` | 中心深紅 #8a1818 → 邊緣 #1a0a0a | 品牌/高潮鏡頭(黃字超對比) |
| `fire` | 中心橘紅 #cc4528 → 邊緣 #3c0f0a | 熱烈/激動段 |
| `dim` | 中心藍 #4c508e → 邊緣 #1a1e28 | 痛點/沉思段 |

**全部背景**疊金色斜線紋理(#50401e width=2)= 品牌質感
**Logo**:右下角 PNG paste(`assets/logo.png`,240×240)
**字色**:標題白/highlight 黃 #FFD700 / subtitle 黃 #FFD700
**字體**:Hiragino Sans GB W6(index=1)

### Step 5:ffmpeg 合成(關鍵踩雷修法在此!)

**首選腳本**:`scripts/build_mv_16x9.py` — 路徑全相對化、分鏡抽成 JSON、開跑前先驗素材。
2026-08-12 在 Leo 的機器完整跑通(21 鏡 / 14 字幕 / 56 秒 / 53 秒建置)。

```bash
# 素材目錄底下要有 ai_images/ photos/ music/
/usr/bin/python3 scripts/build_mv_16x9.py --assets ~/Desktop/龍蝦學院_AI_MV

# 換分鏡:複製 DEFAULT_STORYBOARD 成 JSON 改,不要動程式
/usr/bin/python3 scripts/build_mv_16x9.py --assets DIR --storyboard my.json
```

**素材命名契約**(preflight 會擋):
- `ai_images/<名>.png` — 分鏡表寫 `["ai", "04_lobster", ...]`(不含副檔名)
- `photos/<名>.jpg` — 分鏡表寫 `["photo", "p1_coach.jpg", ...]`(含副檔名)
- 圖卡寫 `["card", "card_open", ...]`,對應 storyboard 的 `cards` 區塊

**完整 pipeline**(4 sub-steps):
1. 為每個鏡頭生 mp4(套用 Ken Burns motion)
2. concat 所有鏡頭 → visual.mp4
3. overlay 字幕 PNG → visual_sub.mp4
4. 合成音軌 → 最終 mp4

**踩雷 #1**(必修):**concat 不能用 `-c copy`**!
```python
# ❌ 錯(timestamp 亂掉 → overlay enable 失效 → 字幕變空)
subprocess.run(["ffmpeg", "-f", "concat", "-i", "list.txt", "-c", "copy", "out.mp4"])

# ✅ 對(強制重編碼 + 重生 PTS)
subprocess.run(["ffmpeg", "-fflags", "+genpts", "-f", "concat", "-safe", "0",
                "-i", "list.txt",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30",
                "-preset", "fast", "-crf", "18",
                "out.mp4"])
```

**踩雷 #2**:字幕 fade-in 動畫太複雜會壞 → 改靜態 overlay 才穩
```python
# ✅ 穩定靜態 overlay
filters.append(f"{last}[{i}:v]overlay=0:0:enable='between(t,{s},{e})'[v{i}]")
```

**踩雷 #3**:PIL 不支援 emoji(🦞 變 X 框)→ 用 Image.paste(logo PNG)
```python
# ❌ 錯
draw.text((x, y), "🦞", font=font, fill=red)  # 變 X

# ✅ 對
LOGO_IMG = Image.open(LOGO_PATH).convert("RGBA").resize((240, 240))
img_rgba.paste(LOGO_IMG, (x, y), LOGO_IMG)  # 第 3 個參數 = mask
```

---

## 兩個版本規格

### 16:9 實體講座開場版

- **解析度**:1920×1080(投影機 / 大螢幕)
- **時長**:Suno 生出多少就多少(通常 45-60 秒)
- **音檔**:歌詞 outro 用「歡迎傑森教練上台」
- **字體**:66-72pt(字幕)/ 100-190pt(PIL 標題),繁體用 Songti TC index=2
- **腳本**:`scripts/build_mv_16x9.py`(**首選,已驗證**)/ `scripts/build_stage_mv.py`(舊版,分鏡表寫死)

### 9:16 招生 Shorts 版

- **解析度**:1080×1920(YT Shorts / IG Reels / TikTok)
- **時長**:54 秒(Shorts 最佳)
- **音檔**:歌詞 outro 用「按訂閱看完整版」
- **字體**:64pt(字幕)/ 86-110pt(PIL 標題)
- **腳本**:`scripts/build_shorts_mv.py`

---

## 標準工作目錄結構

`build_mv_16x9.py` 吃 `--assets` 指到這個目錄即可,腳本本身留在 skill 裡不用複製。

```
~/Desktop/龍蝦學院_AI_MV/          # ← --assets 指這裡
├── ai_images/                     # 分鏡用的 AI 圖(檔名要對上分鏡表)
│   ├── 01_clock_office.png
│   ├── 02_ai_army.png
│   ├── 03_command.png
│   ├── 04_lobster.png
│   ├── 05_stage.png
│   ├── 06_datastream.png
│   └── 07_gears.png
├── photos/                        # 講座實拍照 p1_coach.jpg … p8_class.jpg
├── music/                         # take1/2/3.mp3 + Whisper 逐字 json
├── ai_images_gen/                 # gen_ai_images.py 輸出(不覆蓋上面的)
├── _work/                         # 中間檔,可整個砍掉重跑
└── 龍蝦學院_MV_16x9.mp4           # 成品
```

---

## 觸發後執行流程(典型 60 分鐘)

1. **使用者輸入**:「幫我做 [實體開場 / 招生 Shorts] MV」
2. **Claude 確認**:歌詞主題 / 講座照片來源 / 想對標的 viral MV(可選)
3. **Claude 輸出歌詞**(2-3 個版本給用戶選),含 Suno style prompt
4. **用戶手動到 Suno**:生歌 + 下載 WAV(10-15 分鐘)
5. **用戶丟 WAV 給 Claude**
6. **Claude 跑 Whisper** 拿精準時間軸 + 篩出最佳版本
7. **Claude 跑 Gemini Imagen-4** 生 5 張 AI 視覺(2 分鐘)
8. **Claude 跑 build_*.py** 合成 MV(3-5 分鐘)
9. **Claude QuickTime 開啟預覽** + 等用戶 verdict
10. **回饋修改循環**:字幕位置/背景/運鏡/AI 圖

---

## 已知踩雷紀錄(複用避免)

1. ⚠️ **HeyGen TTS 用「拚」字會唱「pàn」** → 一律用「拼」(skill-jason-digital-human 已記)
2. ⚠️ **Suno Free 沒商業權** → 必須 Pro $10/月(月底退訂仍保留下載過的 mp3 license)
3. ⚠️ **ffmpeg concat -c copy 壞 timestamp** → 重編碼 + `-fflags +genpts`
4. ⚠️ **PIL 不支援 emoji** → logo 用 PNG paste,移除所有 🦞👏🎤
5. ⚠️ **黃背景 + 黃字看不見** → spotlight 改深紅龍蝦色
6. ⚠️ **PIL 黑背景全黑太空洞** → spotlight/fire/dim 3 樣式輪換,加金色斜線紋理
7. ⚠️ **imagen-3.0 已停**,改 `imagen-4.0-fast-generate-001`
8. ⚠️ **imagen-4.0-generate-001 限流 429** → 用 fast 版 + 3 次 retry 等 15-45 秒
9. ⚠️ **字幕燒入失敗 silent error** → 每次 build 完用 numpy 檢測底部 yellow 像素數驗證(>100 才算通過)
10. ⚠️ **Suno 節慶賀詞口吻會被誤判「copyrighted material」** → 做端午/中秋/過年等節慶 MV 時,賀歌套語(端午快樂/恭喜發財/祝福你…)整體太像版權節慶歌會被擋。**改寫成原創嘻哈口吻、節慶只當場景描述、刪掉賀詞套語+高風險四字成語**(如「黃金萬兩」「站上浪頭」)。仍擋→精簡 style 欄到 `Mandarin EDM rap, 128 BPM, energetic, Taiwanese male vocal`(移除 `festival anthem`/`viral pop hook`/`celebratory`);診斷招:歌詞框只打「啦啦啦 測試」能不能生,分辨是歌詞還是 style 問題。(2026-06-19 端午 MV 實證)
11. ⚠️ **Veo I2V 真實動態 hero** → `imagen-4.0` 靜圖+Ken Burns 不夠時,用 `client.models.generate_videos(veo-3.0-generate-001, image=..., aspect_ratio="9:16")` 把主視覺圖變 8s 真實動態(如划龍舟槳手划動),放開場前 10s 衝 retention。**必加 8 分鐘 polling 超時 + 多模型 fallback**(veo-3.0-fast 常 429→自動退 veo-3.0)。Veo 吃共用額度,只做 1-2 顆 hero。腳本:`端午節/gen_veo_dragonboat.py`
12. ⚠️ **腳本寫死原作者機器路徑** → 2026-08-12 已修:`build_mv_16x9.py` 用 `--assets` 參數;三支舊腳本改吃 `LOBSTER_MV_ROOT` env(預設 `~/Desktop/龍蝦學院_AI_MV`),logo 一律指向 skill 自帶的 `assets/logo.png`。原始版本留在 `scripts/_legacy_原機器路徑版/`
13. ⚠️ **Songti.ttc 不在 `/System/Library/Fonts/`** → 實際在 `/System/Library/Fonts/Supplemental/Songti.ttc`。`build_mv_16x9.py` 兩個位置都試。**繁體必用 Songti TC(index=2)**,SC 版缺繁體字會渲染成空白方框
14. ⚠️ **字幕顏色與驗證門檻要對齊** → SKILL.md 舊版寫「驗證底部**黃**色像素 > 100」,但 `build_mv_16x9.py` 的字幕是**白字 + 黑描邊 + 半透明底條**,要驗**白**色像素(實測 6,500-28,000,門檻設 3,000)。改字幕顏色時記得同步改驗證條件,否則驗證恆假
15. ⚠️ **Gemini 生圖與現有分鏡素材不同組** → `gen_ai_images.py` 內建 5 個 prompt(NVIDIA 晶片/AI 軍團/舞台燈/龍蝦品牌/數據流)產出 `01_nvidia_5t.png` 等檔名,跟品牌招生版分鏡用的 `01_clock_office.png` 等**不相通**。輸出一律進 `ai_images_gen/` 不覆蓋既有素材;要接進分鏡得改 prompt 或改分鏡表

---

## 商業應用(非招生用途別走這條)

| 場景 | 變現邏輯 |
|---|---|
| **學員福利**(認證學員可學 AI MV 製作) | 加值課程 NT$3,000 |
| **企業客戶 OEM**(幫其他講師做主題曲) | NT$10,000-30,000 / 支 |
| **YouTube/IG 廣告素材** | 提升 ROAS(影音廣告 > 靜態圖) |
| **訓練營實體儀式感** | 學員 NPS 直接 +30(從上課變成體驗) |

---

## 後續開發 backlog(未做)

- [ ] 9:16 招生 Shorts 也套 v4 動畫升級(目前只 16:9 升級了)
- [ ] 加入 Veo 3 視頻(取代部分 Imagen 靜態圖,真實動態場景)
- [ ] 加 ffmpeg xfade transitions(目前 concat 是 hard cut)
- [ ] 字幕 fade-in 動畫(已 deprecated,因為跟 enable 衝突)
- [ ] 多版本批量生產:60s + 30s + 15s + 6s(4 個廣告長度)
- [ ] 自動偵測歌詞時間軸(Whisper)+ 自動切歌詞段

---

## 參考連結

- Suno:https://suno.com
- Gemini Imagen-4:https://ai.google.dev/gemini-api/docs/image-generation
- 對標 MV:https://youtu.be/u2vZPAC4tAU(房叔《護國神山》)
- 對標頻道:房叔unclehouse 自媒體短影音

---

## 觸發後 main agent 必做檢查清單

- [ ] 確認 Suno Pro 訂閱還有效(用戶手動 check)
- [ ] **只有要生新 AI 圖才需要** `GEMINI_API_KEY`;純合成不需要金鑰。檢查值必須 `AIza` 開頭約 39 碼 — **不能只看 env 有沒有值**,佔位符也是值
- [ ] 確認素材目錄底下有 `ai_images/` `photos/` `music/`,且檔名對上分鏡表(`build_mv_16x9.py` 的 preflight 會一次列出所有缺件)
- [ ] logo 用 skill 自帶的 `assets/logo.png`,不要指向使用者桌面
- [ ] 跑 build 後**用 numpy 驗證字幕像素**:白字版驗底部白色像素 > 3000(`build_mv_16x9.py` 已內建 Step ⑥ 自動驗)。**改過字幕顏色就要同步改驗證條件**
- [ ] QuickTime 預覽後問用戶 4 件事:字幕對嗎 / 運鏡順嗎 / AI 圖搶戲嗎 / 整體節奏燃嗎
