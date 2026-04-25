import requests, json, os, time, uuid, urllib.parse, copy
from datetime import datetime

# ============ COMFYUI INTEGRATION (YOUR FLUX WORKFLOW) ============

def comfyui_generate(prompt, output_dir=None, server="http://127.0.0.1:8188", template_path="~/Desktop/comfy_template.json", steps=None):
    """
    Generate image using YOUR ComfyUI Flux workflow.
    Loads template, injects prompt into Node 4, updates steps in Node 7, queues, polls, downloads.
    """
    # 1. Check server
    try:
        requests.get(f"{server}/", timeout=5)
    except:
        return {"success": False, "error": "ComfyUI not running at " + server}
    
    # 2. Load YOUR template
    tpl_path = os.path.expanduser(template_path)
    if not os.path.exists(tpl_path):
        return {"success": False, "error": f"Template not found: {tpl_path}. Please save your workflow as API JSON there."}
    
    with open(tpl_path, "r") as f:
        workflow = json.load(f)
    
    # Deep copy to avoid modifying original
    work_copy = copy.deepcopy(workflow)
    
    # 3. Inject prompt into Node 4 (Positive CLIP Text Encode)
    if "4" in work_copy and "inputs" in work_copy["4"]:
        work_copy["4"]["inputs"]["text"] = prompt
    
    # 4. Update steps in Node 7 (KSamplerAdvanced) if provided
    if steps is not None and "7" in work_copy:
        work_copy["7"]["inputs"]["steps"] = steps
        work_copy["7"]["inputs"]["end_at_step"] = steps  # Flux Advanced Sampler needs this
    
    # 5. Queue the prompt
    try:
        client_id = str(uuid.uuid4())
        resp = requests.post(f"{server}/prompt", json={"prompt": work_copy, "client_id": client_id}, timeout=10)
        resp.raise_for_status()
        prompt_id = resp.json().get("prompt_id")
    except Exception as e:
        return {"success": False, "error": f"Queue failed: {str(e)}"}
    
    print(f"⏳ Generating... (Prompt ID: {prompt_id[:8]}...)")
    
    # 6. Poll for completion (Max 5 mins for Flux Upscale)
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

# ============ OTHER APIS (Weather, Crypto, News) ============
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

if __name__ == "__main__":
    print("🔌 Testing api_tools.py (Flux Integration)...\n")
    print("1. Weather:", get_weather("Tunis")["data"]["temperature"])
    print("2. Crypto:", get_crypto_price("bitcoin")["data"]["price_usd"])
    print("\n3. ComfyUI Flux Test:")
    print("   ⚠️  This will take ~30-60 seconds (Flux + Upscaling)")
    res = comfyui_generate("a futuristic cyberpunk cat wearing sunglasses, neon lights, 8k, detailed", steps=20)
    if res["success"]:
        print(f"✅ SUCCESS! Generated: {res['data']['image_path']}")
        os.system(f"open '{res['data']['image_path']}'")
    else:
        print(f"❌ FAILED: {res['error']}")
    print("\n✅ Tests complete!")
