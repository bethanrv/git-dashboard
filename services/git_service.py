import os
import re
import asyncio
import httpx
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

async def fetch_pr_details(client, item, headers):
    """Fetches Review and CI status for a single PR in parallel."""
    repo_full_name = "/".join(item["repository_url"].split("/")[-2:])
    pr_number = item["number"]
    
    # Define the individual detail calls
    reviews_url = f"https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}/reviews"
    pr_detail_url = f"https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}"
    
    try:
        # Fetch review list and PR details (to get head SHA) concurrently
        res_rev, res_pr = await asyncio.gather(
            client.get(reviews_url, headers=headers, timeout=3),
            client.get(pr_detail_url, headers=headers, timeout=3)
        )

        # Process Review Status
        review_status = "Pending"
        if res_rev.status_code == 200:
            revs = res_rev.json()
            if any(rv["state"] == "APPROVED" for rv in revs): review_status = "Approved"
            elif any(rv["state"] == "CHANGES_REQUESTED" for rv in revs): review_status = "Needs Work"

        # Process CI Status (Requires a second hop to the Status API using the SHA)
        actions_status = "NA"
        if res_pr.status_code == 200:
            head_sha = res_pr.json()["head"]["sha"]
            status_url = f"https://api.github.com/repos/{repo_full_name}/commits/{head_sha}/status"
            res_st = await client.get(status_url, headers=headers, timeout=3)
            if res_st.status_code == 200:
                data = res_st.json()
                state = data.get("state", "None")
                actions_status = state.capitalize() if data.get("total_count", 0) > 0 else "NA"

        return {
            "repo": repo_full_name.split("/")[-1],
            "title": item["title"],
            "review_status": review_status,
            "ci_status": actions_status,
            "url": item["html_url"]
        }
    except Exception as e:
        print(f"Error fetching details for PR {pr_number}: {e}")
        return None

async def fetch_open_prs_async():
    token = AuthService.get_token()
    if not token: return []
    
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    query = "is:open is:pr author:@me"
    search_url = f"https://api.github.com/search/issues?q={query}"
    
    async with httpx.AsyncClient() as client:
        r = await client.get(search_url, headers=headers, timeout=5)
        if r.status_code != 200: return []
        
        items = r.json().get("items", [])
        # Trigger all PR detail fetches at once!
        tasks = [fetch_pr_details(client, item, headers) for item in items]
        results = await asyncio.gather(*tasks)
        
        return [res for res in results if res]

def fetch_open_prs():
    return asyncio.run(fetch_open_prs_async())

async def fetch_review_requests_async():
    token = AuthService.get_token()
    if not token: return []
    
    query = "is:open is:pr review-requested:@me"
    url = f"https://api.github.com/search/issues?q={query}"
    headers = {"Authorization": f"token {token}"}
    
    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers=headers, timeout=5)
        if r.status_code != 200: return []
        return [{
            "repo": i["repository_url"].split("/")[-1],
            "author": i["user"]["login"],
            "title": i["title"],
            "url": i["html_url"]
        } for i in r.json().get("items", [])]

def fetch_review_requests():
    return asyncio.run(fetch_review_requests_async())