def classify(task):
    task = task.lower()
    if any(w in task for w in ["code", "script", "function", "debug", "python", "write", "build"]):
        return "code"
    elif any(w in task for w in ["plan", "design", "strategy", "architecture", "steps", "outline"]):
        return "plan"
    elif any(w in task for w in ["explain", "teach", "summary", "what is", "describe", "how does"]):
        return "explain"
    elif any(w in task for w in ["quick", "fast", "simple", "short", "urgent", "brief"]):
        return "fast"
    else:
        return "general"

if __name__ == "__main__":
    tests = [
        "write a python script",
        "design the system architecture", 
        "explain how recursion works",
        "quick check the syntax",
        "tell me a joke"
    ]
    for t in tests:
        print(f"{t} → {classify(t)}")
