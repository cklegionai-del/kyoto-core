python
import subprocess
import signal

def run_code_in_sandbox(code):
    def handler(signum, frame):
        raise TimeoutError("Execution timed out")

    # Set the signal handler and a 30-second alarm
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(30)

    try:
        # Write code to a temporary file
        with open('temp_code.py', 'w') as file:
            file.write(code)

        # Run the code in a subprocess
        result = subprocess.run(['python', 'temp_code.py'], capture_output=True, text=True)
        return result.stdout

    except TimeoutError as e:
        return str(e)

    finally:
        # Disable the alarm
        signal.alarm(0)

def github_push(repo='kyoto-core', file='executor.py', content=''):
    import requests

    url = f'https://api.github.com/repos/{repo}/contents/{file}'
    token = 'YOUR_GITHUB_TOKEN'  # Replace with your GitHub token

    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json',
    }

    response = requests.get(url, headers=headers)
    sha = response.json().get('sha', None) if response.status_code == 200 else None

    data = {
        'message': 'Add executor.py with sandbox code',
        'content': content,
        'sha': sha
    }

    response = requests.put(url, headers=headers, json=data)
    return response.json()

# Example usage
if __name__ == '__main__':
    code_to_run = 'print("Hello from the sandbox!")'
    output = run_code_in_sandbox(code_to_run)
    print(output)

    # Push to GitHub
    with open('executor.py', 'r') as file:
        content = file.read()

    push_response = github_push(file='executor.py', content=content.encode('base64').decode('utf-8'))
    print(push_response)
