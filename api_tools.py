import requests, json, os, time
from datetime import datetime

class APIClient:
    """Base client for HTTP/API requests with error handling."""
    
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
    """Get weather from Open-Meteo (free, no API key)."""
    # Geocoding
    geo = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1").json()
    if not geo.get("results"):
        return {"success": False, "error": f"City '{city}' not found"}
    
    lat, lon = geo["results"][0]["latitude"], geo["results"][0]["longitude"]
    
    # Weather
    weather = requests.get(
        f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    ).json()
    
    return {
        "success": True,
        "data": {
            "city": city,
            "temperature": weather["current_weather"]["temperature"],
            "wind_speed": weather["current_weather"]["windspeed"],
            "time": weather["current_weather"]["time"]
        }
    }

def get_crypto_price(symbol="BTC"):
    """Get crypto price from CoinGecko (free, no API key)."""
    response = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={symbol.lower()}&vs_currencies=usd").json()
    if "error" in response:
        return {"success": False, "error": response.get("error", "Unknown error")}
    return {
        "success": True,
        "data": {
            "symbol": symbol.upper(),
            "price_usd": response.get(symbol.lower(), {}).get("usd", 0),
            "timestamp": datetime.now().isoformat()
        }
    }

def get_news(query="technology", max_results=5):
    """Get news from HN Algolia API (free, no API key)."""
    response = requests.get(f"https://hn.algolia.com/api/v1/search?query={query}&hitsPerPage={max_results}").json()
    return {
        "success": True,
        "data": [
            {"title": hit["title"], "url": hit["url"], "points": hit["points"]}
            for hit in response.get("hits", [])
        ]
    }

# ============ PLACEHOLDERS FOR YOUR TOOLS ============

def comfyui_connect(prompt, server="localhost:8188"):
    """
    ComfyUI API integration (placeholder).
    TODO: Implement when ready.
    """
    print(f"🎨 ComfyUI prompt: {prompt}")
    print(f" Server: {server}")
    print("⚠️  Not yet implemented - add ComfyUI API calls here")
    return {"success": False, "error": "Not implemented"}

def whisper_transcribe(audio_path, server="localhost:8188"):
    """
    Whisper API integration (placeholder).
    TODO: Implement when ready.
    """
    print(f"🎙️  Transcribe: {audio_path}")
    print(f"🔌 Server: {server}")
    print("⚠️  Not yet implemented - add Whisper API calls here")
    return {"success": False, "error": "Not implemented"}


if __name__ == "__main__":
    print("🔌 Testing api_tools.py...\n")
    
    # Test 1: Weather
    print("1. Weather API (Tunis):")
    res = get_weather("Tunis")
    if res["success"]:
        print(f"   🌡️  {res['data']['temperature']}°C, 💨 {res['data']['wind_speed']} km/h")
    else:
        print(f"   ❌ {res['error']}")
    
    # Test 2: Crypto
    print("\n2. Crypto API (Bitcoin):")
    res = get_crypto_price("bitcoin")
    if res["success"]:
        print(f"   💰 ${res['data']['price_usd']:,.2f} USD")
    else:
        print(f"   ❌ {res['error']}")
    
    # Test 3: News
    print("\n3. News API (Python):")
    res = get_news("Python programming", max_results=3)
    if res["success"]:
        for i, item in enumerate(res["data"], 1):
            print(f"   {i}. {item['title'][:50]}...")
    
    # Test 4: ComfyUI placeholder
    print("\n4. ComfyUI placeholder:")
    comfyui_connect("a blue square")
    
    # Test 5: Whisper placeholder
    print("\n5. Whisper placeholder:")
    whisper_transcribe("~/Desktop/audio.wav")
    
    print("\n✅ Tests complete!")
