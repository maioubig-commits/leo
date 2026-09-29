# 龍蝦學院 Skill 全export（34 個）

匯出日期：2026-09-29　｜　來源：Leo 的 `~/.claude/skills/`

## 安裝

把底下所有資料夾複製到 `~/.claude/skills/`：

```bash
cp -R */ ~/.claude/skills/
```

重開 Claude Code，直接叫名字就會上工（例如打「小安」「小劇」「gogo」）。

## 清單

| 資料夾 | 角色 | 做什麼 |
|---|---|---|
| `skill-ai-lobster-brand` | AI數字員工龍蝦學院 | 只有「確實為龍蝦學院製作」的產出（上課作業、繳交給傑森教練的素材、學 |
| `skill-knowledge-ip-coach` | 知識 IP | 把個人技能/經驗/熱情變成可變現的知識 IP 與完整商業模式 |
| `skill-lobster-ai-mv-producer` | AI MV | 用 Suno V5.5 生洗腦中文 EDM 主題曲 + Gemini |
| `skill-market-insight-analyst` | 市場洞察分析師 | 頂級市場研究與用戶畫像專家 |
| `skill-ugc-script-decoder` | UGC 拆解 | UGC 帶貨腳本拆解專家 |
| `skill-user-needs-miner` | 用戶需求挖掘 | 深度訪談型心理分析師 |
| `skill-viral-script-decoder` | 爆款腳本 | 本 skill 為通用敘事拆解 |
| `skill-xiao-an` | 小安 | Leo專屬房仲員工SOP執行官 |
| `skill-xiao-bao` | 小爆 | 短影音爆款 / UGC 帶貨腳本專員 |
| `skill-xiao-bian` | 小辯 | 首席律師（直屬 Leo） |
| `skill-xiao-cha` | 小察 | 市場洞察分析師 / 用戶畫像產出官 |
| `skill-xiao-ding` | 小定 | 知識 IP 定位與商業模式首席教練 |
| `skill-xiao-gou` | 小構 | 爆款腳本架構師 / 通用敘事拆解專員 |
| `skill-xiao-guang` | 小廣 | FB／IG 廣告投放與「實體講座招生漏斗」＋ TikTok/YouT |
| `skill-xiao-jiang` | 小講 | 線上直播 / 實體講座的簡報內容與排程專員 |
| `skill-xiao-jie` | 小潔 | 行銷總監（部門主管 |
| `skill-xiao-ju` | 小劇 | AI 短劇製作專員 |
| `skill-xiao-kai` | 小開 | 建物謄本建檔專員 |
| `skill-xiao-ke` | 小客 | LINE 客服自動回覆專員 |
| `skill-xiao-kong` | 小空 | 空間設計與客戶互動專員（室內設計／裝修／商業空間） |
| `skill-xiao-mei` | 小美 | 平面視覺設計專員（雜誌編輯設計／海報 DM／原住民族活動主視覺／包裝 |
| `skill-xiao-qiang` | 小強 | 製造部經理（電子書批量生產與上架） |
| `skill-xiao-shu` | 小書 | 作業說明書撰寫 ＋ 郵件收信摘要專員 |
| `skill-xiao-sou` | 小搜 | SEO／搜尋流量專員 |
| `skill-xiao-ting` | 小聽 | 影音逐字稿與字幕生成專員 |
| `skill-xiao-wa` | 小挖 | 用戶需求挖掘專員 / 內容選題彈藥庫產出官 |
| `skill-xiao-wang` | 小網 | 網站建立與維護專員 |
| `skill-xiao-wei` | 小維 | 客戶網站維運專員（Website Maintenance） |
| `skill-xiao-wen` | 小文 | 行銷文案專員（Copywriter） |
| `skill-xiao-xi` | 小析 | 台股分析師 / 個股健檢與盤勢解讀專員 |
| `skill-xiao-yi` | 小譯 | 日文在地化翻譯專員 / 影片字幕與腳本本地化 |
| `skill-xiao-yun` | 小運 | 短影音文案運營專員 |
| `skill-xiao-zhang` | 小帳 | AI 會計 / 記帳與財務報表專員 |
| `skill-xiao-zhao` | 小招 | 課程招生與開班行政專員 |

## 需要金鑰或外部服務的

| Skill | 需要 |
|---|---|
| `skill-xiao-ju`（小劇） | `GEMINI_API_KEY`、`ELEVENLABS_API_KEY`、`FAL_KEY`、`fal-client` 套件 |
| `skill-lobster-ai-mv-producer` | `GEMINI_API_KEY`、ffmpeg、Pillow |
| `skill-xiao-ting`（小聽） | whisper.cpp（`whisper-cli`）＋ 語音模型檔 |
| `skill-xiao-guang`（小廣） | `google-api-python-client`（YouTube 上傳用） |
| `skill-xiao-mei`（小美） | `fonttools`（缺字檢查） |

## ⚠️ 這包已做過的本機客製（給別人前請先確認）

1. **品牌預設不掛龍蝦學院**：`skill-ai-lobster-brand` 的「適用範圍」、16 個 SKILL.md 的品牌句、
   13 支腳本改讀環境變數 `LOBSTER_BRAND`（預設空＝不掛）。還原工具：
   `skill-ai-lobster-brand/scripts/reapply_local_brand.py`
2. **直屬主管寫 Leo**（母版寫傑森教練）：小定、小辯、小潔、小強、小析、小帳、小書。
3. **小帳、小書裡指稱使用者的「教練」已改成 Leo**。
4. **小聽（`skill-xiao-ting`）是本機自建**：逐字稿與字幕。母版的「小譯」是日文翻譯，兩者不同。
5. **小安是房仲版**（母版的小安是保險行銷專員），內含 Leo 的門市電話、手機與 email，
   對外分享前請先移除 `skill-xiao-an/references/listing-content.md` 的聯絡資訊。

