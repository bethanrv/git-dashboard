import os
import re
from datetime import datetime

def get_time_ago(timestamp):
    if timestamp == 0: return "Never"
    diff = datetime.now() - datetime.fromtimestamp(timestamp)
    s = diff.total_seconds()
    if s < 60: return f"{int(s)}s ago"
    if s < 3600: return f"{int(s // 60)}m ago"
    if s < 86400: return f"{int(s // 3600)}h ago"
    return f"{int(s // 86400)}d ago"

def extract_git_url(repo_path):
    config_path = os.path.join(repo_path, ".git", "config")
    if not os.path.exists(config_path): return None
    try:
        with open(config_path, "r") as f:
            content = f.read()
            match = re.search(r'\[remote "origin"\][^\[]*url = ([^\s\n]+)', content)
            if match:
                url = match.group(1)
                if url.startswith("git@"):
                    url = url.replace(":", "/").replace("git@", "https://").replace(".git", "")
                return url
    except: return None
    return None

def get_git_repos(path):
    repos = []
    expanded_path = os.path.expanduser(path)
    if not os.path.exists(expanded_path): return []
    with os.scandir(expanded_path) as entries:
        for entry in entries:
            git_dir = os.path.join(entry.path, ".git")
            if entry.is_dir() and os.path.exists(git_dir):
                msg_file = os.path.join(git_dir, "COMMIT_EDITMSG")
                mtime = os.path.getmtime(msg_file) if os.path.exists(msg_file) else os.path.getmtime(git_dir)
                repos.append({
                    "name": entry.name,
                    "path": entry.path,
                    "mtime": mtime,
                    "time_ago": get_time_ago(mtime),
                    "remote_url": extract_git_url(entry.path),
                })
    return repos
