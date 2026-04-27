import json, os, datetime

MEMORY_FILE = os.path.expanduser("~/.kyoto_memory.json")

def _load_data():
    """Internal: Load memory file or return empty structure."""
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {"tasks": [], "preferences": {}, "stats": {"total": 0, "success": 0}}

def _save_data(data):
    """Internal: Save memory to file."""
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2)

def save_task(task, result, model_used, duration_sec=None):
    data = _load_data()
    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "task": task,
        "result": result,
        "model": model_used,
        "duration_sec": duration_sec
    }
    data["tasks"].append(entry)
    data["stats"]["total"] += 1
    if result == "success":
        data["stats"]["success"] += 1
    _save_data(data)
    return True

def load_preferences(task_type=None):
    """Load learned preferences with FIXED model tracking."""
    data = _load_data()
    prefs = {}
    
    # Track actual model usage per category: {"code": {"qwen2.5-coder:32b": 3}}
    category_models = {}
    
    for t in data.get("tasks", []):
        if t.get("result") != "success": continue
        task_lower = t.get("task", "").lower()
        model = t.get("model")
        if not model: continue
        
        if any(w in task_lower for w in ["code", "script", "function"]): cat = "code"
        elif any(w in task_lower for w in ["plan", "design", "strategy"]): cat = "plan"
        elif any(w in task_lower for w in ["explain", "teach", "summary"]): cat = "explain"
        else: cat = "general"
        
        if task_type and cat != task_type: continue
            
        if cat not in category_models: category_models[cat] = {}
        category_models[cat][model] = category_models[cat].get(model, 0) + 1

    # Pick most successful model per category (min 2 successes)
    for cat, models in category_models.items():
        best_model = max(models.items(), key=lambda x: x[1])
        if best_model[1] >= 2:
            prefs[f"{cat}_model"] = best_model[0]
            
    prefs["stats"] = data.get("stats", {})
    return prefs

def get_recent_tasks(limit=5):
    data = _load_data()
    return data.get("tasks", [])[-limit:]

def clear_memory():
    if os.path.exists(MEMORY_FILE):
        os.remove(MEMORY_FILE)
    return True

if __name__ == "__main__":
    print("🧠 Testing memory.py...\n")
    print("Test 1: Saving tasks")
    save_task("write a python script", "success", "qwen2.5-coder:32b")
    save_task("design the architecture", "success", "deepseek-r1:32b")
    save_task("explain recursion", "success", "phi4:latest")
    save_task("quick fix the bug", "failed", "qwen3:8b")
    print("✅ Tasks saved\n")
    
    print("Test 2: Loading preferences")
    prefs = load_preferences()
    print(f"Preferences: {json.dumps(prefs, indent=2)}\n")
    
    print("Test 3: Recent tasks")
    recent = get_recent_tasks(3)
    for r in recent:
        print(f"  • {r['task']} → {r['result']} ({r['model']})")
    print()
    
    print("Test 4: Stats")
    stats = prefs.get("stats", {})
    print(f"  Total tasks: {stats.get('total', 0)}")
    print(f"  Successful: {stats.get('success', 0)}")
    if stats.get("total"):
        rate = stats["success"] / stats["total"] * 100
        print(f"  Success rate: {rate:.1f}%")
