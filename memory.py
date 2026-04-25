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
    """
    Log a task execution for learning.
    Args:
        task: str - The original task description
        result: str - "success" or "failed" or error message
        model_used: str - Which model handled it (e.g., "qwen2.5-coder:32b")
        duration_sec: float - Optional execution time
    """
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
    """
    Load learned preferences.
    Args:
        task_type: str - Optional filter (e.g., "code", "plan")
    Returns:
        dict - Preferred model per task type, or overall stats
    """
    data = _load_data()
    prefs = {}
    
    # Count successful model usage per task category
    model_counts = {}
    for t in data.get("tasks", []):
        if t.get("result") != "success":
            continue
        task_lower = t.get("task", "").lower()
        # Simple categorization
        if any(w in task_lower for w in ["code", "script", "function"]):
            cat = "code"
        elif any(w in task_lower for w in ["plan", "design", "strategy"]):
            cat = "plan"
        elif any(w in task_lower for w in ["explain", "teach", "summary"]):
            cat = "explain"
        else:
            cat = "general"
        
        if task_type and cat != task_type:
            continue
            
        model = t.get("model")
        if model:
            key = f"{cat}_model"
            model_counts[key] = model_counts.get(key, 0) + 1
    
    # Pick most-used successful model per category
    for key, count in model_counts.items():
        if count >= 2:  # Only prefer if used successfully at least twice
            prefs[key] = max(model_counts, key=model_counts.get)
    
    # Add overall stats
    prefs["stats"] = data.get("stats", {})
    return prefs

def get_recent_tasks(limit=5):
    """Return the last N tasks for context."""
    data = _load_data()
    return data.get("tasks", [])[-limit:]

def clear_memory():
    """Reset all memory (use with caution)."""
    if os.path.exists(MEMORY_FILE):
        os.remove(MEMORY_FILE)
    return True


if __name__ == "__main__":
    print("🧠 Testing memory.py...\n")
    
    # Test 1: Save some tasks
    print("Test 1: Saving tasks")
    save_task("write a python script", "success", "qwen2.5-coder:32b")
    save_task("design the architecture", "success", "deepseek-r1:32b")
    save_task("explain recursion", "success", "phi4:latest")
    save_task("quick fix the bug", "failed", "qwen3:8b")
    print("✅ Tasks saved\n")
    
    # Test 2: Load preferences
    print("Test 2: Loading preferences")
    prefs = load_preferences()
    print(f"Preferences: {json.dumps(prefs, indent=2)}\n")
    
    # Test 3: Get recent tasks
    print("Test 3: Recent tasks")
    recent = get_recent_tasks(3)
    for r in recent:
        print(f"  • {r['task']} → {r['result']} ({r['model']})")
    print()
    
    # Test 4: Stats
    print("Test 4: Stats")
    stats = prefs.get("stats", {})
    print(f"  Total tasks: {stats.get('total', 0)}")
    print(f"  Successful: {stats.get('success', 0)}")
    if stats.get("total"):
        rate = stats["success"] / stats["total"] * 100
        print(f"  Success rate: {rate:.1f}%")
