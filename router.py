def classify(task):
    task = task.lower()
    # Search queries first (before code keywords)
    if any(w in task for w in ["search", "find", "look up", "what is", "who is", "latest", "news"]):
        return "search"
    elif any(w in task for w in ["code", "script", "function", "debug", "write", "build", "create"]):
        return "code"
    elif any(w in task for w in ["plan", "design", "strategy", "architecture", "steps", "outline"]):
        return "plan"
    elif any(w in task for w in ["explain", "teach", "summary", "describe", "how does"]):
        return "explain"
    elif any(w in task for w in ["quick", "fast", "simple", "short", "urgent", "brief"]):
        return "fast"
    elif any(w in task for w in ["file", "read", "write", "pdf", "excel", "doc", "csv"]):
        return "file"
    else:
        return "general"

if __name__ == "__main__":
    tests = [
        "search for Python 3.13 features",
        "write a python script",
        "design the system architecture", 
        "explain how recursion works",
        "quick check the syntax",
        "read my Desktop report.pdf",
        "tell me a joke"
    ]
    for t in tests:
        print(f"{t} → {classify(t)}")
