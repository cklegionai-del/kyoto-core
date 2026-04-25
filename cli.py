python
with open('/Users/hichem/Desktop/cli.py', 'r') as f:
    content = f.read()
github_push(repo='kyoto-core', file='cli.py', content=content)
