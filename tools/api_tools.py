import requests, json, os, time, uuid, urllib.parse
from datetime import datetime

class APIClient:
    def __init__(self, base_url=None, headers=None, timeout=30):
        self.base_url = base_url or ""
        self.headers = headers or {}
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def get(self, endpoint, params=None):
        url = f"{self.base_url}/{endpoint}" if endpoint.startswith("http") else f"{self.base_url}/{endpoint}"
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return {"success": True, "data": response.json() if "application/json" in response.headers.get("Content-Type", "") else response.text}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def post(self, endpoint, data=None, json_data=None):
        url = f"{self.base_url}/{endpoint}" if endpoint.startswith("http") else f"{self.base_url}/{endpoint}"
        try:
            response = self.session.post(url, json=json_data, data=data, timeout=self.timeout)
            response.raise_for_status()
            return {"success": True, "data": response.json() if "application/json" in response.headers.get("Content-Type", "") else response.text}
        except Exception as e:
            return {"success": False, "error": str(e)}

# ============ FREE PUBLIC APIS ============
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

# ============ COMFYUI INTEGRATION (TEMPLATE-BASED) ============

def comfyui_generate(prompt, output_dir=None, server="http://127.0.0.1:8188", template_path=None, steps=20, seed=None):
    """
    Generate image using ComfyUI with user-provided workflow template.
    Falls back to minimal workflow if template not found.
    """
    # 1. Check server
    try:
        requests.get(f"{server}/", timeout=5)
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "ComfyUI not running at " + server}
    
    # 2. Load or build workflow
    workflow = None
    if template_path and os.path.exists(template_path):
        with open(template_path, "r") as f:
            workflow = json.load(f)
    
    if not workflow:
        # Minimal fallback workflow (adjust node IDs if needed)
        workflow = {
            "4": {"inputs": {"ckpt_name": "v1-5-pruned-emaonly.ckpt"}, "class_type": "CheckpointLoaderSimple"},
            "6": {"inputs": {"text": prompt, "clip": ["4", 1]}, "class_type": "CLIPTextEncode"},
            "7": {"inputs": {"text": "blurry, low quality", "clip": ["4", 1]}, "class_type": "CLIPTextEncode"},
            "3": {"inputs": {"seed": seed or 0, "steps": steps, "cfg": 7.5, "sampler_name": "euler", "scheduler": "normal", "denoise": 1, "model": ["4", 0], "positive": ["6", 0], "negative": ["7", 0], "latent_image": ["5", 0]}, "class_type": "KSampler"},
            "5": {"inputs": {"width": 512, "height": 512, "batch_size": 1}, "class_type": "EmptyLatentImage"},
            "8": {"inputs": {"samples": ["3", 0], "vae": ["4", 2]}, "class_type": "VAEDecode"},
            "9": {"inputs": {"filename_prefix": "kyoto_", "images": ["8", 0]}, "class_type": "SaveImage"}
        }
        # Update prompt in fallback
        for node in workflow.values():
            if node.get("class_type") == "CLIPTextEncode" and "positive" in node.get("inputs", {}).get("text", "").lower():
                node["inputs"]["text"] = prompt
    
    # 3. Queue prompt
    try:
        client_id = str(uuid.uuid4())
        resp = requests.post(f"{server}/prompt", json={"prompt": workflow, "client_id": client_id}, timeout=10)
        resp.raise_for_status()
        prompt_id = resp.json().get("prompt_id")
    except Exception as e:
        return {"success": False, "error": f"Queue failed: {str(e)}"}
    
    # 4. Poll for completion
    for _ in range(120):
        try:
            hist = requests.get(f"{server}/history/{prompt_id}", timeout=5).json()
            if prompt_id in hist:
                outputs = hist[prompt_id].get("outputs", {})
                # Find any SaveImage output
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

def whisper_transcribe(audio_path, server="localhost:8188"):
    return {"success": False, "error": "Not implemented"}

if __name__ == "__main__":
    print("🔌 Testing api_tools.py...\n")
    print("1. Weather:", get_weather("Tunis")["data"]["temperature"])
    print("2. Crypto:", get_crypto_price("bitcoin")["data"]["price_usd"])
    print("3. ComfyUI Test:")
    # Try with template first, then fallback
    res = comfyui_generate("a blue circle", template_path="~/Desktop/comfy_template.json", steps=10)
    if res["success"]:
        print(f"✅ Generated: {res['data']['image_path']}")
        os.system(f"open '{res['data']['image_path']}'")
    else:
        print(f"❌ {res['error']}")
        print("💡 Tip: Create a workflow in ComfyUI, click 'Save (API Format)', save as comfy_template.json")
