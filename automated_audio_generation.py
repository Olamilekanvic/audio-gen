import os
import re
from elevenlabs.client import ElevenLabs
from elevenlabs import save

# CONFIGURATION
API_KEY = "sk_cd0366ef71437f6c899da97dfecce1631a86a536ddb7e4aa"
VOICE_ID = "HaDBcMdLvTIIloqW9jzk" 
MODEL_ID = "eleven_v3"
INPUT_FILE = "compound_int.txt"
MAIN_OUTPUT_FOLDER = "compound_interest_audio"

client = ElevenLabs(api_key=API_KEY)

# 1. LOAD DATA
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    lines = [line.strip() for line in f if line.strip()]

# 2. EMOTION MAPPING (Maps tags to base float values)
def get_base_settings(tag):
    settings = {"stability": 0.5, "similarity_boost": 0.8, "style": 0.2}
    if tag == "seriously": settings.update({"stability": 0.6, "style": 0.45})
    elif tag == "whispers": settings.update({"stability": 0.3, "style": 0.6})
    elif tag == "intensely": settings.update({"stability": 0.4, "style": 0.7})
    elif tag == "instructive": settings.update({"stability": 0.7, "style": 0.1})
    elif tag == "firmly": settings.update({"stability": 0.65, "style": 0.3})
    elif tag == "thoughtfully": settings.update({"stability": 0.45, "style": 0.4})
    elif tag == "determinedly": settings.update({"stability": 0.55, "style": 0.5})
    elif tag == "disbelievingly": settings.update({"stability": 0.35, "style": 0.6})
    elif tag == "energetic": settings.update({"stability": 0.5, "style": 0.75})
    elif tag == "authoritatively": settings.update({"stability": 0.75, "style": 0.25})
    return settings

# 3. GENERATION LOOP
for i, raw_text in enumerate(lines, start=1):
    line_num = str(i).zfill(3)
    
    # Organize by folder: MAIN_FOLDER/Line_034/files.mp3
    line_folder = os.path.join(MAIN_OUTPUT_FOLDER, f"Line_{line_num}")
    if not os.path.exists(line_folder):
        os.makedirs(line_folder)
    
    # Extract tag and clean text for the API call
    tag_match = re.search(r'\[(.*?)\]', raw_text)
    tag = tag_match.group(1).lower() if tag_match else "default"
    clean_text = re.sub(r'\[.*?\]', '', raw_text).strip()
    
    print(f"--- Processing Line {line_num} | Tag: [{tag}] ---")

    # Define 3 specific takes
    base_settings = get_base_settings(tag)
    variations = [
        {"name": "Take_1_Standard", "stab_adj": 0.0, "style_adj": 0.0},
        {"name": "Take_2_Stable", "stab_adj": 0.2, "style_adj": -0.1}, # Very clear, safe bet
        {"name": "Take_3_Expressive", "stab_adj": -0.2, "style_adj": 0.35}, # High emotion/v3 style
    ]

    for v in variations:
        # Enforce 0.0 to 1.0 limits
        final_stab = max(0.0, min(1.0, base_settings["stability"] + v["stab_adj"]))
        final_style = max(0.0, min(1.0, base_settings["style"] + v["style_adj"]))
        
        print(f"  Generating {v['name']}...")
        
        try:
            audio = client.text_to_speech.convert(
                text=clean_text, 
                voice_id=VOICE_ID, 
                model_id=MODEL_ID,
                voice_settings={
                    "stability": final_stab, 
                    "similarity_boost": base_settings["similarity_boost"], 
                    "style": final_style
                }
            )
            
            file_path = os.path.join(line_folder, f"Line_{line_num}_{v['name']}.mp3")
            save(audio, file_path)
        except Exception as e:
            print(f"  ❌ Error on Line {line_num} {v['name']}: {e}")

print(f"\n✅ SUCCESS! Folder '{MAIN_OUTPUT_FOLDER}' is ready for delivery.")