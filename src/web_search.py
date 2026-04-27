from ddgs import DDGS

def search_web(query, max_results=5):
    if not query or not isinstance(query, str):
        return {"success": False, "error": "Invalid query"}
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query.strip(), max_results=max_results))
        if not results:
            return {"success": True, "data": [], "message": "No results found"}
        return {
            "success": True,
            "data": [
                {"title": r.get("title", ""), "url": r.get("href", ""), "snippet": r.get("body", "")}
                for r in results
            ]
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    print("🔍 Testing web_search.py...\n")
    
    print("Test 1: Search 'Python 3.13 new features'")
    res = search_web("Python 3.13 new features", max_results=3)
    print(f"Success: {res['success']}")
    if res["success"]:
        for item in res.get("data", [])[:2]:
            print(f"  • {item['title']}\n    {item['url']}\n")
            
    print("Test 2: Empty query")
    print(search_web(""))
    print("\n✅ Tests complete!")
