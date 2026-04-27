#!/usr/bin/env python3
import sys, os, json
sys.path.insert(0, os.path.expanduser("~/Desktop"))
from router import classify
from executor import run_code
from memory import save_task, load_preferences
from file_tools import read_text, read_pdf, read_docx, read_excel, read_csv
from web_search import search_web
from api_tools import comfyui_generate, whisper_transcribe, get_weather, get_crypto_price, get_news

def print_header():
    print("\n" + "="*50)
    print("🧠 KYOTO CLI v2.0 — Local AI Factory")
    print("="*50 + "\n")

def show_help():
    print("""📖 COMMANDS:
  • generate image <prompt>       → ComfyUI Flux generation
  • transcribe <audio_path>       → Whisper speech-to-text
  • weather <city>                → Live weather data
  • crypto <symbol>               → BTC, ETH, SOL prices
  • news <topic>                  → Latest tech/news headlines
  • read <file_path>              → Extract text (PDF/DOCX/CSV/TXT)
  • run <python_code>             → Safe code execution
  • search <query>                → DuckDuckGo web search
  • stats                         → View usage memory
  • help                          → Show this menu
  • exit / quit                   → Close Kyoto
""")

def main():
    print_header()
    prefs = load_preferences()
    stats = prefs.get("stats", {})
    print(f"📊 Ready. Tasks logged: {stats.get('total', 0)} | Success: {stats.get('success', 0)}\n")
    while True:
        try:
            cmd = input("🔹 Kyoto> ").strip()
            if not cmd: continue
            if cmd.lower() in ["exit", "quit", "q"]:
                print("👋 Kyoto shutting down. Goodbye!"); break
            if cmd.lower() == "help": show_help(); continue
            if cmd.lower() == "stats": print(json.dumps(prefs, indent=2)); continue
            if cmd.lower().startswith("generate image"):
                prompt = cmd[14:].strip()
                if not prompt: print("❌ Usage: generate image <prompt>"); continue
                print("🎨 Generating via ComfyUI...")
                res = comfyui_generate(prompt)
                if res["success"]: print(f"✅ Saved: {res['data']['image_path']}"); os.system(f"open '{res['data']['image_path']}'"); save_task(cmd, "success", "comfyui")
                else: print(f"❌ {res['error']}"); save_task(cmd, "failed", "comfyui")
            elif cmd.lower().startswith("transcribe"):
                path = cmd[10:].strip().replace("~", os.path.expanduser("~"))
                if not os.path.exists(path): print(f"❌ File not found: {path}"); continue
                print("🎙️  Transcribing..."); res = whisper_transcribe(path)
                if res["success"]: print(f"✅ Text: {res['data']['text'][:200]}..."); print(f"💾 Saved: {res['data']['transcript_file']}"); save_task(cmd, "success", "whisper")
                else: print(f"❌ {res['error']}"); save_task(cmd, "failed", "whisper")
            elif cmd.lower().startswith("weather"):
                city = cmd[7:].strip() or "Tunis"
                print(f"🌤️  Weather for {city}..."); res = get_weather(city)
                if res["success"]: d=res["data"]; print(f"✅ {d['city']}: {d['temperature']}°C | Wind: {d['wind_speed']} km/h | {d['time']}"); save_task(cmd, "success", "weather_api")
                else: print(f"❌ {res['error']}")
            elif cmd.lower().startswith("crypto"):
                sym = cmd[6:].strip().upper() or "BTC"
                print(f"💰 Fetching {sym}..."); res = get_crypto_price(sym.lower())
                if res["success"]: print(f"✅ {res['data']['symbol']}: ${res['data']['price_usd']:,} USD"); save_task(cmd, "success", "crypto_api")
                else: print(f"❌ {res['error']}")
            elif cmd.lower().startswith("news"):
                q = cmd[4:].strip() or "technology"
                print(f"📰 News: '{q}'..."); res = get_news(q, max_results=5)
                if res["success"]:
                    for i, item in enumerate(res["data"], 1): print(f"{i}. {item['title']}\n   🔗 {item['url']}")
                    save_task(cmd, "success", "news_api")
                else: print(f"❌ {res['error']}")
            elif cmd.lower().startswith("read"):
                path = cmd[4:].strip().replace("~", os.path.expanduser("~"))
                if not os.path.exists(path): print(f"❌ File not found: {path}"); continue
                print(f"📄 Reading {path}...")
                try:
                    if path.endswith(".pdf"): text = read_pdf(path)
                    elif path.endswith(".docx"): text = read_docx(path)
                    elif path.endswith(".csv"): text = str(read_csv(path)[:5])
                    elif path.endswith(".xlsx"): text = str(read_excel(path)[:5])
                    else: text = read_text(path)
                    print(f"✅ Preview:\n{text[:500]}..."); save_task(cmd, "success", "file_tools")
                except Exception as e: print(f"❌ Read error: {e}"); save_task(cmd, f"error: {e}", "file_tools")
            elif cmd.lower().startswith("run"):
                code = cmd[3:].strip()
                if not code: print("❌ Usage: run <python code>"); continue
                print("💻 Executing..."); res = run_code(code)
                print(f"{'✅' if res['success'] else '❌'} Output: {res['output'][:500]}"); save_task(cmd, "success" if res["success"] else "failed", "executor")
            elif cmd.lower().startswith("search"):
                q = cmd[6:].strip()
                if not q: print("❌ Usage: search <query>"); continue
                print("🔍 Searching..."); res = search_web(q, max_results=5)
                if res["success"]:
                    for i, item in enumerate(res["data"], 1): print(f"{i}. {item['title']}\n   🔗 {item['url']}")
                    save_task(cmd, "success", "web_search")
                else: print(f"❌ {res['error']}")
            else:
                cat = classify(cmd); print(f"🔍 Routing: '{cmd}' → {cat}"); save_task(cmd, "routed", cat); print("💡 Type 'help' to see commands.")
        except KeyboardInterrupt: print("\n⚠️  Interrupted. Type 'exit' to quit cleanly.")
        except Exception as e: print(f"❌ Unexpected error: {e}"); save_task(cmd, f"error: {e}", "cli")

if __name__ == "__main__": main()
