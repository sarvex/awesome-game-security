import urllib.request
import re
import json
import sys

# tokens are required because the rate limit for unauthenticated users is only
# 60/h whereas authenticated users get 5000 requests. As of time of writing,
# this repository contains ~1000 links which fits within the budget.
if len(sys.argv) <= 1:
    print(f"Usage: {sys.argv[0]} <github_token>")
    print("You can get a token from https://github.com/settings/tokens")
    exit()

token = sys.argv[1]

if not token.startswith("ghp_"):
    print("Github token should start with 'ghp_', ensure you got your token from https://github.com/settings/tokens.")
    exit()

filename = "../README.md"
repo_regex = r'https:\/\/github.com\/([A-Za-z0-9_.-]+)\/([A-Za-z0-9_.-]+)'

with open(filename,"r") as f:
    readme_content = f.read()
# print(readme_content)

# to give the user an idea how long this takes, print the amount of matches
matchcount = len(re.findall(repo_regex, readme_content))
matches_processed = 0

def get_json(url):
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"token {token}")
    resp = urllib.request.urlopen(req)
    content = json.loads(resp.read())
    resp.close()
    return content

def replace(match):
    global matches_processed
    global matchcount
    matches_processed += 1
    try:
        username = match.group(1)
        project = match.group(2)
        print("checking %s/%s (%i/%i)" % (username, project, matches_processed, matchcount))
        repo_info = get_json(f"https://api.github.com/repos/{username}/{project}")

        if repo_info["fork"]:
            print("\tproject is a fork from %s" % repo_info["parent"]["owner"]["login"])
            stars_fork = repo_info["stargazers_count"]
            stars_orig = repo_info["parent"]["stargazers_count"]
            print("\torig: %s stars, fork: %s stars" % (stars_orig, stars_fork))
            if stars_fork < 5 or stars_fork * 5 < stars_orig:
                print('\tassuming that this fork does not add value, replacing with original')
                return f'https://github.com/{repo_info["parent"]["owner"]["login"]}/{repo_info["parent"]["name"]}'
        else:
            print("\tproject is not a fork")

        return f'https://github.com/{username}/{project}'
    except Exception as e:
        print('\tException occurred!', e)
        return match.group(0)

replaced = re.sub(repo_regex, replace, readme_content)
with open(filename, "w") as f:
    f.write(replaced)
