import os
import requests
import time
import re  # Added for ID extraction
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ==========================================
# 🛠️ USER SETTINGS
# ==========================================
PROJECT_NAME    = "CBN" 
SCRIPT_FILENAME = "dry_run.txt" 
START_SENTINEL  = f"Starting {PROJECT_NAME}"
END_SENTINEL    = f"Ending {PROJECT_NAME}"
API_KEY         = "sk_0c87648eedf19fe4fe6f34046ed014656f7b4f382b781722"
WORKSPACE_ID    = "0054c1e491c244f0ac1922d6052aa20a"
# ==========================================

session = requests.Session()
retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))

HEADERS = {
    "xi-api-key": API_KEY,
    "xi-workspace-id": WORKSPACE_ID,
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}
session.headers.update(HEADERS)

def get_item_text(item):
    dialogue_list = item.get("dialogue", [])
    if dialogue_list:
        return " ".join([d.get("text", "") for d in dialogue_list])
    return item.get("text") or ""

def fetch_history():
    print(f"--- Connecting to ElevenLabs History ---")
    url = "https://api.elevenlabs.io/v1/history"
    params = {"page_size": 1000}
    
    try:
        response = session.get(url, params=params, timeout=30)
        if response.status_code == 200:
            items = response.json().get("history", []) 
            return items
        return []
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return []

def run_scavenger():
    history = fetch_history()
    if not history: return

    # 1. Map history items by their ID tags
    # This creates a dictionary where the key is the ID number (e.g., "18")
    history_map = {}
    for item in history:
        text = get_item_text(item)
        # Look for the pattern [ID:number] or simply [number] at the end
        match = re.search(r'\[(?:ID:)?(\d+)\]', text)
        if match:
            line_id = match.group(1)
            if line_id not in history_map:
                history_map[line_id] = []
            history_map[line_id].append(item)

    output_base = f"Output_{PROJECT_NAME}"
    if not os.path.exists(output_base): os.makedirs(output_base)

    # 2. Match based on the Line Number
    # We now ignore the text entirely and just look for the folder index in history_map
    for i in range(1, 81): # Adjust this range based on your script length
        line_num_str = str(i)
        folder_name = f"Line_{line_num_str.zfill(3)}"
        folder_path = os.path.join(output_base, folder_name)
        
        takes = history_map.get(line_num_str, [])

        if takes:
            if not os.path.exists(folder_path): os.makedirs(folder_path)
            takes.reverse() # Oldest take first
            
            for t_idx, take in enumerate(takes, 1):
                f_name = f"Take_{t_idx}.mp3"
                dl_url = f"https://api.elevenlabs.io/v1/history/{take['history_item_id']}/audio"
                audio_res = session.get(dl_url, timeout=30)
                
                if audio_res.status_code == 200:
                    with open(os.path.join(folder_path, f_name), "wb") as f:
                        f.write(audio_res.content)
                    print(f"💾 Match Found! Saved: {folder_name}/{f_name}")
                time.sleep(0.1)

    print(f"\n✅ All done! Accurate sync complete.")

if __name__ == "__main__":
    run_scavenger()