import subprocess, os, time

def run_code(code, timeout=30, cwd=None):
    """
    Run Python code safely with timeout.
    Returns: {"success": bool, "output": str}
    """
    if cwd is None:
        cwd = os.getcwd()
    
    # Write code to temp file
    temp_file = os.path.join(cwd, "temp_exec.py")
    with open(temp_file, "w") as f:
        f.write(code)
    
    try:
        # Run with timeout
        result = subprocess.run(
            ["python3", temp_file],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd
        )
        output = result.stdout if result.stdout else result.stderr
        return {"success": result.returncode == 0, "output": output.strip()}
    
    except subprocess.TimeoutExpired:
        return {"success": False, "output": f"⏱️ Timeout after {timeout} seconds"}
    
    except Exception as e:
        return {"success": False, "output": f"❌ Error: {str(e)}"}
    
    finally:
        # Clean up temp file
        if os.path.exists(temp_file):
            os.remove(temp_file)


if __name__ == "__main__":
    # Test 1: Simple print
    print("Test 1: Simple print")
    result = run_code('print("Hello from executor!")')
    print(f"Success: {result['success']}\nOutput: {result['output']}\n")
    
    # Test 2: Math operation
    print("Test 2: Math operation")
    result = run_code('print(2 + 2 * 3)')
    print(f"Success: {result['success']}\nOutput: {result['output']}\n")
    
    # Test 3: Timeout test (should fail)
    print("Test 3: Timeout test (2s timeout, code sleeps 5s)")
    result = run_code('import time; time.sleep(5)', timeout=2)
    print(f"Success: {result['success']}\nOutput: {result['output']}\n")
    
    # Test 4: Error handling
    print("Test 4: Error handling (division by zero)")
    result = run_code('print(10 / 0)')
    print(f"Success: {result['success']}\nOutput: {result['output']}")
