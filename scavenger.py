import os
import requests
import time
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
    print(f"--- Connecting to ElevenLabs History (Workspace: {WORKSPACE_ID}) ---")
    url = "https://api.us.elevenlabs.io/v1/history"
    params = {"page_size": 1000}
    
    try:
        response = session.get(url, params=params, timeout=30)
        if response.status_code == 200:
            items = response.json().get("history", []) 
            print(f"✅ Retrieved {len(items)} items.")
            return items
        return []
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return []

def run_scavenger():
    if not os.path.exists(SCRIPT_FILENAME):
        print(f"❌ Error: {SCRIPT_FILENAME} not found.")
        return

    with open(SCRIPT_FILENAME, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip()]
    
    history = fetch_history()
    if not history:
        print("⚠️ No history found.")
        return

    # 1. Find the Markers
    start_idx, end_idx = -1, -1
    for i, item in enumerate(history):
        txt = get_item_text(item).lower().strip()
        if END_SENTINEL.lower() in txt and end_idx == -1:
            end_idx = i
        if START_SENTINEL.lower() in txt:
            start_idx = i
            if end_idx != -1: break

    if start_idx == -1 or end_idx == -1:
        print("❌ Markers Not Found.")
        return

    # 2. Isolate the items between markers
    # items are newest to oldest, so end_idx (newer) comes before start_idx (older)
    project_items = history[end_idx+1 : start_idx]
    print(f"📦 Found {len(project_items)} audio takes between markers.")

    output_base = f"Output_{PROJECT_NAME}"
    if not os.path.exists(output_base):
        os.makedirs(output_base)

    # 3. Match and Save
    # We iterate through each line of your text file
    for i, line_text in enumerate(lines, 1):
        folder_name = f"Line_{str(i).zfill(3)}"
        folder_path = os.path.join(output_base, folder_name)
        
        # Find all history items that match the start of this line
        match_segment = line_text[:15].lower().strip() # Use 15 chars for safer matching
        takes = [item for item in project_items if match_segment in get_item_text(item).lower()]

        if takes:
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            
            # Reverse because history is newest-first, we want Take 1 to be the oldest
            takes.reverse() 
            
            for t_idx, take in enumerate(takes, 1):
                f_name = f"Take_{t_idx}.mp3"
                dl_url = f"https://api.elevenlabs.io/v1/history/{take['history_item_id']}/audio"
                audio_res = session.get(dl_url, timeout=30)
                
                if audio_res.status_code == 200:
                    with open(os.path.join(folder_path, f_name), "wb") as f:
                        f.write(audio_res.content)
                    print(f"💾 Saved: {folder_name}/{f_name}")
                time.sleep(0.2) # Avoid rate limits

    print(f"\n✅ All done! The folder is at: {os.path.abspath(output_base)}")

if __name__ == "__main__":
    run_scavenger()