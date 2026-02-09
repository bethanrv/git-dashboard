import os
import re
from datetime import datetime
from services.auth_service import AuthService
import requests

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

def get_git_repos(base_path, max_depth=1):
    repos = []
    expanded_root = os.path.expanduser(base_path)
    
    if not os.path.exists(expanded_root):
        return []

    def scan_dir(current_path, current_depth):
        # Base case: don't go deeper than allowed
        if current_depth > max_depth:
            return

        try:
            with os.scandir(current_path) as entries:
                for entry in entries:
                    if not entry.is_dir():
                        continue
                    
                    # Prevent infinite loops with symlinks or scanning .git itself
                    if entry.name.startswith('.') and entry.name != ".git":
                        continue

                    git_dir = os.path.join(entry.path, ".git")
                    
                    if os.path.exists(git_dir):
                        # Found a repo! 
                        msg_file = os.path.join(git_dir, "COMMIT_EDITMSG")
                        mtime = os.path.getmtime(msg_file) if os.path.exists(msg_file) else os.path.getmtime(git_dir)
                        
                        repos.append({
                            "name": entry.name,
                            "path": entry.path,
                            "mtime": mtime,
                            "time_ago": get_time_ago(mtime),
                            "remote_url": extract_git_url(entry.path),
                        })
                        # Usually, repos aren't nested inside repos, 
                        # so we don't scan deeper once a .git is found.
                    else:
                        # Not a repo, search one level deeper
                        scan_dir(entry.path, current_depth + 1)
        except PermissionError:
            pass # Skip folders we can't access

    scan_dir(expanded_root, 1)
    return repos

def fetch_open_prs():
    token = AuthService.get_token()
    if not token:
        return []
    
    # Search for PRs authored by the user that are open
    query = "is:open is:pr author:@me"
    url = f"https://api.github.com/search/issues?q={query}"
    headers = {"Authorization": f"token {token}"}
    
    try:
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code == 200:
            items = r.json().get("items", [])
            return [
                {
                    "repo": i["repository_url"].split("/")[-1],
                    "title": i["title"],
                    "status": "🟢",
                    "url": i["html_url"]
                } for i in items
            ]
    except:
        pass
    return []

def fetch_review_requests():
    token = AuthService.get_token()
    if not token: return []
    
    query = "is:open is:pr review-requested:@me"
    url = f"https://api.github.com/search/issues?q={query}"
    headers = {"Authorization": f"token {token}"}
    
    try:
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code == 200:
            return [{
                "repo": i["repository_url"].split("/")[-1],
                "author": i["user"]["login"],
                "title": i["title"],
                "url": i["html_url"]
            } for i in r.json().get("items", [])]
    except:
        pass
    return []