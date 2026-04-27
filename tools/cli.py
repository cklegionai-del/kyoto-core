#!/usr/bin/env python3
import sys, os, json

# Add Desktop to path so we can import Kyoto modules
sys.path.insert(0, os.path.expanduser("~/Desktop"))

from router import classify
from executor import run_code
from memory import save_task, load_preferences, get_recent_tasks
from file_tools import read_text, write_text, read_csv, read_pdf, read_docx, read_excel
from web_search import search_web

def print_banner():
    print("\n" + "="*50)
    print("🧠 KYOTO CLI v0.1 — Your Local AI Factory")
    print("="*50 + "\n")

def main_loop():
    print_banner()
    prefs = load_preferences()
    print(f"📊 Stats: {prefs.get('stats', {})}\n")
    
    while True:
        try:
            task = input("🔹 Kyoto> ").strip()
            if task.lower() in ["exit", "quit", "q"]:
                print("👋 Goodbye! Kyoto is always ready.")
                break
            if not task:
                continue
                
            # Route the task
            category = classify(task)
            print(f"🔍 Routing: '{task}' → category: {category}")
            
            # Handle by category
            if category == "code":
                print("💻 Generating code...")
                # In real usage: call an LLM here
                code = f'print("Code for: {task}")'
                result = run_code(code)
                print(f"✅ Output: {result['output']}")
                save_task(task, "success" if result["success"] else "failed", "local_exec")
                
            elif category == "search":
                print("🔍 Searching web...")
                res = search_web(task, max_results=3)
                if res["success"]:
                    for i, item in enumerate(res["data"], 1):
                        print(f"{i}. {item['title']}\n   {item['url']}\n")
                    save_task(task, "success", "web_search")
                    
            elif category == "file":
                print("📁 File operation detected")
                # Simple demo: read a file if path is mentioned
                if "/Desktop/" in task and ".txt" in task:
                    path = task.split("/Desktop/")[-1].split()[0]
                    full_path = os.path.expanduser(f"~/Desktop/{path}")
                    if os.path.exists(full_path):
                        content = read_text(full_path)[:200]
                        print(f"📄 Preview: {content}...")
                        save_task(task, "success", "file_tools")
                        
            else:
                print(f"🤔 General task: '{task}'")
                save_task(task, "pending", "cli")
                
        except KeyboardInterrupt:
            print("\n⚠️  Interrupted. Type 'exit' to quit cleanly.")
        except Exception as e:
            print(f"❌ Error: {e}")
            save_task(task, f"error: {e}", "cli")

if __name__ == "__main__":
    main_loop()
