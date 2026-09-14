import os
import json
import requests
import base64

GITHUB_TOKEN = os.environ.get("GH_TOKEN")
WAKATIME_API_KEY = os.environ.get("WAKATIME_API_KEY")

def get_github_data():
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

    response = requests.get("https://api.github.com/user", headers=headers)
    response.raise_for_status()
    data = response.json()

    followers = data["followers"]
    public_repos = data["public_repos"]
    private_repos = data["total_private_repos"]
    total_repos = public_repos + private_repos

    stars = 0
    top_repo = None
    page = 1

    while True:
        repos_resp = requests.get(
            "https://api.github.com/user/repos",
            headers=headers,
            params={"per_page": 100, "page": page, "visibility": "public"}
        )
        repos_resp.raise_for_status()
        repos_data = repos_resp.json()
        if not repos_data:
            break

        for repo in repos_data:
            stars += repo["stargazers_count"]
            if top_repo is None or repo["stargazers_count"] > top_repo["stars"]:
                top_repo = {
                    "name": repo["name"],
                    "url": repo["html_url"],
                    "stars": repo["stargazers_count"],
                    "description": repo["description"],
                }

        page += 1

    return {
        "stars": stars,
        "followers": followers,
        "total_repos": total_repos,
        "public_repos": public_repos,
        "private_repos": private_repos,
        "top_repo": top_repo
    }

def get_wakatime_data():
    encoded_key = base64.b64encode(WAKATIME_API_KEY.encode()).decode()
    headers = {"Authorization": f"Basic {encoded_key}"}

    response = requests.get(
    "https://wakatime.com/api/v1/users/current/stats/last_7_days",
        headers=headers
    )
    response.raise_for_status()
    body = response.json()
    data = body["data"]

    return {
        "total_time": data["human_readable_total"],
        "daily_average": data["human_readable_daily_average"],
        "top_languages": [
            {"name": lang["name"], "percent": lang["percent"]}
            for lang in data["languages"][:5]
        ],
        "top_editors": [
            {"name": ed["name"], "percent": ed["percent"]}
            for ed in data["editors"][:3]
        ],
    }

def main():
    github = get_github_data()
    wakatime = get_wakatime_data()

    output = {
        "github": github,
        "wakatime": wakatime
    }

    with open("public/thirt_party.json", "w", encoding="utf-8") as file:
        json.dump(output, file, ensure_ascii=False, indent=4)

    print(json.dumps(output, ensure_ascii=False, indent=4))

if __name__ == "__main__":
    main()