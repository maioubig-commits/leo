#!/usr/bin/env python3
"""為 v4 MV 生成 5 張 AI 視覺(Gemini imagen-3)。"""
import os, sys, base64
from pathlib import Path
from google import genai
from google.genai import types

# 輸出目錄：第一個參數 > LOBSTER_MV_ROOT env > ~/Desktop/龍蝦學院_AI_MV
# 一律寫進 ai_images_gen/，不覆蓋既有的 ai_images/
ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else \
    Path(os.environ.get("LOBSTER_MV_ROOT", Path.home() / "Desktop/龍蝦學院_AI_MV"))
OUT_DIR = ROOT / "ai_images_gen"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# 金鑰防呆：沒設好就先擋，不要跑到一半才爆
API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or ""
if not API_KEY.startswith("AIza") or len(API_KEY) < 35:
    sys.exit("GEMINI_API_KEY 沒設好（應為 AIza 開頭、約 39 碼），目前長度 = %d\n"
             "  修法：編輯 ~/.zshrc 那行 export GEMINI_API_KEY=\"...\"，存檔後 source ~/.zshrc\n"
             "  拿金鑰：https://aistudio.google.com/apikey" % len(API_KEY))

client = genai.Client(api_key=API_KEY)

# 5 張 AI 視覺(16:9 1920×1080)
IMAGES = [
    ("01_nvidia_5t.png",
     "Dramatic cinematic photo of NVIDIA AI chip glowing red and gold in dark futuristic data center, "
     "Jensen Huang style black leather jacket reflection on glass walls, "
     "neon '$5T' text in background, 16:9 cinematic, deep red and gold color palette, "
     "high contrast, dramatic lighting, epic atmosphere, 8K render"),
    ("02_ai_army.png",
     "Cinematic shot of 8 abstract glowing robot avatars standing in formation in a dark cyberpunk hall, "
     "red and gold neon lighting, lobster red color palette, "
     "futuristic AI workforce, dramatic backlight, 16:9 cinematic, epic atmosphere"),
    ("03_stage_lights.png",
     "Empty stage with dramatic spotlights, red and gold curtains, "
     "audience silhouettes in foreground waiting, anticipation, "
     "TED talk style stage, 16:9 cinematic, deep red and gold lighting, epic atmosphere, "
     "ready for speaker to walk on stage"),
    ("04_lobster_brand.png",
     "Stylized geometric red lobster icon center of frame, "
     "deep black background with subtle red glow, gold particle effects, "
     "luxury brand identity, 16:9 cinematic minimalist, "
     "logo reveal aesthetic, premium feel"),
    ("05_data_flow.png",
     "Abstract red and gold digital data streams flowing through black space, "
     "AI neural network visualization, financial market dashboard glow, "
     "$5 trillion text floating, 16:9 cinematic, deep red gold palette"),
]


import time

def gen_image(filename, prompt):
    out_path = OUT_DIR / filename
    if out_path.exists():
        print(f"⏭  跳過: {filename}")
        return True
    # 優先 fast 版,失敗再 fall back 到 gemini-2.5-flash-image
    for model_name in ["imagen-4.0-fast-generate-001", "imagen-4.0-generate-001"]:
        print(f"🎨 {filename} → {model_name}")
        for attempt in range(3):
            try:
                response = client.models.generate_images(
                    model=model_name,
                    prompt=prompt,
                    config=types.GenerateImagesConfig(
                        number_of_images=1,
                        aspect_ratio="16:9",
                        output_mime_type="image/png",
                    ),
                )
                if response.generated_images:
                    img_bytes = response.generated_images[0].image.image_bytes
                    out_path.write_bytes(img_bytes)
                    size_kb = len(img_bytes) // 1024
                    print(f"   ✅ ({size_kb} KB)")
                    return True
            except Exception as e:
                err = str(e)[:100]
                if "429" in err or "RESOURCE_EXHAUSTED" in err:
                    wait = (attempt + 1) * 15
                    print(f"   ⏳ 429 限流,等 {wait}s 重試 ({attempt+1}/3)")
                    time.sleep(wait)
                    continue
                print(f"   ❌ {type(e).__name__}: {err}")
                break
    return False


def main():
    success = 0
    for fn, prompt in IMAGES:
        if (OUT_DIR / fn).exists():
            print(f"⏭  跳過(已存在): {fn}")
            success += 1
            continue
        if gen_image(fn, prompt):
            success += 1
    print(f"\n🎉 完成 {success}/{len(IMAGES)}")


if __name__ == "__main__":
    main()
