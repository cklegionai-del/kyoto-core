python
import os
from collections import defaultdict

def count_files_by_type(directory):
    file_count = defaultdict(int)
    for filename in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, filename)):
            _, ext = os.path.splitext(filename)
            file_count[ext] += 1
    return file_count

def github_push(repo='kyoto-core', file='file_counter.py', content=''):
    # Placeholder function to simulate pushing to GitHub
    print(f"Pushing {file} to {repo}")
    print(content)

if __name__ == "__main__":
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    summary = count_files_by_type(desktop_path)
    
    summary_text = "\n".join([f"{ext}: {count}" for ext, count in summary.items()])
    print(summary_text)
    
    github_push(file='file_counter.py', content=summary_text)
