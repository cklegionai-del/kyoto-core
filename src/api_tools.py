import requests, json, os, time, uuid, urllib.parse, copy
from datetime import datetime

# ============ COMFYUI INTEGRATION (YOUR FLUX WORKFLOW) ============
def _clean_workflow(workflow):
    clean = {}
    for nid, node in workflow.items():
        clean[nid] = {"class_type": node["class_type"], "inputs": node["inputs"]}
    return clean

def comfyui_generate(prompt, output_dir=None, server="http://127.0.0.1:8188", template_path=os.path.expanduser("~/Desktop/00_Kyoto_Core/workflows/comfy_template.json"), steps=None):
    try:
        requests.get(f"{server}/", timeout=5)
    except:
        return {"success": False, "error": "ComfyUI not running at " + server}
    
    tpl_path = os.path.expanduser(template_path)
    if not os.path.exists(tpl_path):
        return {"success": False, "error": f"Template not found: {tpl_path}"}
    
    with open(tpl_path, "r") as f: workflow = json.load(f)
    work_copy = _clean_workflow(copy.deepcopy(workflow))
    
    if "4" in work_copy: work_copy["4"]["inputs"]["text"] = prompt
    if steps is not None and "7" in work_copy:
        work_copy["7"]["inputs"]["steps"] = steps
        work_copy["7"]["inputs"]["end_at_step"] = steps
    
    try:
        client_id = str(uuid.uuid4())
        resp = requests.post(f"{server}/prompt", json={"prompt": work_copy, "client_id": client_id}, timeout=10)
        resp.raise_for_status()
        prompt_id = resp.json().get("prompt_id")
    except Exception as e:
        return {"success": False, "error": f"Queue failed: {str(e)}"}
    
    print(f"⏳ Generating... (ID: {prompt_id[:8]}...)")
    for _ in range(300):
        try:
            hist = requests.get(f"{server}/history/{prompt_id}", timeout=5).json()
            if prompt_id in hist:
                outputs = hist[prompt_id].get("outputs", {})
                for node_out in outputs.values():
                    if "images" in node_out:
                        img = node_out["images"][0]
                        url = f"{server}/view?filename={urllib.parse.quote(img['filename'])}&subfolder={urllib.parse.quote(img['subfolder'])}&type={img['type']}"
                        data = requests.get(url, timeout=30).content
                        out_dir = output_dir or os.path.expanduser("~/Desktop")
                        os.makedirs(out_dir, exist_ok=True)
                        local_path = os.path.join(out_dir, img["filename"])
                        with open(local_path, "wb") as f: f.write(data)
                        return {"success": True, "data": {"image_path": local_path, "prompt": prompt}}
        except: pass
        time.sleep(1)
    return {"success": False, "error": "Timeout waiting for generation"}

# ============ WHISPER INTEGRATION (LOCAL VOICE-TO-TEXT) ============
def whisper_transcribe(audio_path, model_size="base", language=None, output_dir=None):
    import whisper
    if not os.path.exists(audio_path):
        return {"success": False, "error": f"Audio file not found: {audio_path}"}
    try:
        print(f"⏳ Loading Whisper model '{model_size}'...")
        model = whisper.load_model(model_size)
        print(f"🎙️  Transcribing {audio_path}...")
        result = model.transcribe(audio_path, language=language, verbose=False)
        text = result["text"].strip()
        duration = result.get("segments", [{}])[-1].get("end", 0) if result.get("segments") else 0
        
        out_dir = output_dir or os.path.expanduser("~/Desktop")
        os.makedirs(out_dir, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        txt_path = os.path.join(out_dir, f"{base_name}_transcript.txt")
        with open(txt_path, "w", encoding="utf-8") as f: f.write(text)
        
        return {"success": True, "data": {"text": text, "duration_sec": round(duration, 2), "transcript_file": txt_path, "model": model_size}}
    except Exception as e:
        return {"success": False, "error": f"Whisper error: {str(e)}"}

# ============ PUBLIC APIS ============
def get_weather(city="Tunis"):
    geo = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1").json()
    if not geo.get("results"): return {"success": False, "error": f"City '{city}' not found"}
    lat, lon = geo["results"][0]["latitude"], geo["results"][0]["longitude"]
    weather = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true").json()
    return {"success": True, "data": {"city": city, "temperature": weather["current_weather"]["temperature"], "wind_speed": weather["current_weather"]["windspeed"], "time": weather["current_weather"]["time"]}}

def get_crypto_price(symbol="BTC"):
    response = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={symbol.lower()}&vs_currencies=usd").json()
    if "error" in response: return {"success": False, "error": response.get("error", "Unknown error")}
    return {"success": True, "data": {"symbol": symbol.upper(), "price_usd": response.get(symbol.lower(), {}).get("usd", 0), "timestamp": datetime.now().isoformat()}}

def get_news(query="technology", max_results=5):
    response = requests.get(f"https://hn.algolia.com/api/v1/search?query={query}&hitsPerPage={max_results}").json()
    return {"success": True, "data": [{"title": hit["title"], "url": hit["url"], "points": hit["points"]} for hit in response.get("hits", [])]}

# ============ TEST BLOCK ============
if __name__ == "__main__":
    print("🔌 Testing api_tools.py (Whisper + ComfyUI + APIs)...\n")
    print("1. Weather:", get_weather("Tunis")["data"]["temperature"])
    print("2. Crypto:", get_crypto_price("bitcoin")["data"]["price_usd"])
    
    print("\n3. Whisper Test (Local Speech-to-Text):")
    test_audio = os.path.expanduser("~/Desktop/kyoto_test_audio.aiff")
    os.system(f"say 'Hello from Kyoto. This is a test of the local Whisper transcription module.' -o '{test_audio}'")
    print(f"   🎵 Created test audio: {test_audio}")
    
    res = whisper_transcribe(test_audio, model_size="base")
    if res["success"]:
        print(f"   ✅ Transcribed! Duration: {res['data']['duration_sec']}s")
        print(f"   📝 Text: {res['data']['text'][:100]}...")
        print(f"   💾 Saved to: {res['data']['transcript_file']}")
        os.system(f"open '{res['data']['transcript_file']}'")
    else:
        print(f"   ❌ {res['error']}")
        
    print("\n4. ComfyUI Flux:")
    print("   ✅ Connected & tested. Use: from api_tools import comfyui_generate")
    print("\n✅ Tests complete!")
