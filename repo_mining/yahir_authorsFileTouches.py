import requests
import json
import csv
import os
from datetime import datetime

repo = "scottyab/rootbeer"
lstTokens = [""]

if not os.path.exists("data"):
    os.makedirs("data")

# --------------------------------------------------
# GitHub auth
# --------------------------------------------------

def github_auth(url, tokens, ct):
    ct = ct % len(tokens)
    headers = {"Authorization": f"Bearer {tokens[ct]}"}
    r = requests.get(url, headers=headers)
    return json.loads(r.content), ct + 1

# --------------------------------------------------
# Get GitHub-classified source files
# --------------------------------------------------

def get_github_language_files(repo, tokens):
    ct = 0

    # Get default branch
    repo_url = f"https://api.github.com/repos/{repo}"
    repo_data, ct = github_auth(repo_url, tokens, ct)
    branch = repo_data["default_branch"]

    # Get full tree
    tree_url = f"https://api.github.com/repos/{repo}/git/trees/{branch}?recursive=1"
    tree_data, ct = github_auth(tree_url, tokens, ct)

    files = set()

    for item in tree_data["tree"]:
        if item["type"] != "blob":
            continue

        path = item["path"]

        if path.endswith(".java"):
            files.add(path)
        elif path.endswith(".kt"):
            files.add(path)
        elif path.endswith(".c") or path.endswith(".h"):
            files.add(path)
        elif path.endswith(".cpp"):
            files.add(path)
        elif path.endswith("CMakeLists.txt"):
            files.add(path)

    return files

# --------------------------------------------------
# Collect author/date touches
# --------------------------------------------------

def collect_author_touches(repo, tokens, valid_files):
    ct = 0
    page = 1
    fileTouches = {f: [] for f in valid_files}

    while True:
        commits_url = (
            f"https://api.github.com/repos/{repo}/commits"
            f"?page={page}&per_page=100"
        )
        commits, ct = github_auth(commits_url, tokens, ct)

        if not commits:
            break

        for commit in commits:
            sha = commit["sha"]
            commit_url = f"https://api.github.com/repos/{repo}/commits/{sha}"
            details, ct = github_auth(commit_url, tokens, ct)

            author = details["commit"]["author"]["name"]
            date = details["commit"]["author"]["date"]
            date = datetime.strptime(
                date, "%Y-%m-%dT%H:%M:%SZ"
            ).date().isoformat()

            for f in details.get("files", []):
                fname = f["filename"]
                if fname in valid_files:
                    fileTouches[fname].append((author, date))

        page += 1

    return fileTouches

# --------------------------------------------------
# Run
# --------------------------------------------------

valid_files = get_github_language_files(repo, lstTokens)

print(f"\nGitHub-language source files detected: {len(valid_files)}")
for f in sorted(valid_files):
    print(f)

print("\nGenerating CSV, please wait...")

fileTouches = collect_author_touches(repo, lstTokens, valid_files)

# --------------------------------------------------
# Write CSV
# --------------------------------------------------

outfile = f"data/authors_file_touches_{repo.split('/')[1]}.csv"

with open(outfile, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Filename", "Author", "Date"])
    for file, touches in fileTouches.items():
        for author, date in touches:
            writer.writerow([file, author, date])

print(f"\nCSV written to {outfile}")