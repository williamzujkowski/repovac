import requests
import os
from datetime import datetime, timezone
import time
import base64
from tqdm import tqdm

PAT = os.environ.get("GITHUB_AUTH_TOKEN")
if not PAT:
    raise ValueError("GITHUB_AUTH_TOKEN environment variable is not set.")

# Prompt for GitHub organization name
ORG_NAME = input("Enter the GitHub organization name: ")
BASE_URL = "https://api.github.com"

PACKAGE_FILES = {
    "Python": ["requirements.txt", "Pipfile.lock"],
    "JavaScript": ["package-lock.json", "yarn.lock"],
    "TypeScript": ["package-lock.json", "yarn.lock"],
    "Java": ["pom.xml", "build.gradle"],
    "Kotlin": ["build.gradle.kts"],
    "Go": ["go.mod"],
    "Ruby": ["Gemfile.lock"],
    "Rust": ["Cargo.lock"],
    "Elixir": ["mix.lock"],
    "PHP": ["composer.lock"],
}


def check_rate_limit(response):
    if "X-RateLimit-Remaining" in response.headers:
        remaining = int(response.headers["X-RateLimit-Remaining"])
        limit = int(response.headers["X-RateLimit-Limit"])
        reset = int(response.headers["X-RateLimit-Reset"])
        reset_time = datetime.fromtimestamp(reset, timezone.utc).strftime(
            "%Y-%m-%d %H-%M-%S UTC"
        )
        if remaining < 10:
            sleep_time = max(reset - time.time(), 0) + 10
            print(
                f"Rate Limit Info - Limit: {limit}, Remaining: {remaining}, Resets: {reset_time}"
            )
            print(f"Approaching rate limit. Sleeping for {sleep_time} seconds.")
            time.sleep(sleep_time)


def get_repos(org_name):
    repos = []
    url = f"{BASE_URL}/orgs/{org_name}/repos"
    headers = {"Authorization": f"token {PAT}"}
    while url:
        response = requests.get(url, headers=headers)
        check_rate_limit(response)
        if response.status_code == 200:
            repos.extend(response.json())
            url = response.links.get("next", {}).get("url", None)
        else:
            break
    return [repo for repo in repos if not repo.get("archived")]


def download_and_save_file(
    repo_name, file_path, success_list, failure_list, non_existent_files
):
    url = f"{BASE_URL}/repos/{repo_name}/contents/{file_path}"
    headers = {"Authorization": f"token {PAT}"}
    response = requests.get(url, headers=headers)
    check_rate_limit(response)
    if response.status_code == 200:
        content = base64.b64decode(response.json()["content"])
        save_path = os.path.join(base_dir, repo_name, file_path)
        os.makedirs(
            os.path.dirname(save_path), exist_ok=True
        )  # Ensure the directory exists
        with open(save_path, "wb") as file:
            file.write(content)
        success_list.append(save_path)
        return True
    elif response.status_code == 404:
        non_existent_files.append(f"{repo_name}/{file_path}")
        return False
    else:
        error_message = response.json().get("message", "No error message available")
        failure_list.append(
            f"{repo_name}/{file_path} - HTTP {response.status_code}: {error_message}"
        )
        return False


def main():
    global base_dir  # Declare base_dir as global to use it in download_and_save_file
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    base_dir = f"./dependencies_{timestamp}"
    os.makedirs(base_dir, exist_ok=True)  # Create the base directory early
    success_list, failure_list, non_existent_files = [], [], []

    repos = get_repos(ORG_NAME)
    print(f"Fetching package files from {len(repos)} repositories...")
    for repo in tqdm(repos, desc="Repositories", unit="repo"):
        repo_name = repo["full_name"]
        for lang, files in tqdm(
            PACKAGE_FILES.items(), desc="Languages", leave=False, unit="lang"
        ):
            for file_name in tqdm(
                files, desc=f"Files in {repo_name}", leave=False, unit="file"
            ):
                download_and_save_file(
                    repo_name, file_name, success_list, failure_list, non_existent_files
                )

    # Write success, failure, and non-existent file lists to files
    with open(os.path.join(base_dir, "success_list.txt"), "w") as f:
        for line in success_list:
            f.write(f"{line}\n")

    with open(os.path.join(base_dir, "failure_list.txt"), "w") as f:
        for line in failure_list:
            f.write(f"{line}\n")

    with open(os.path.join(base_dir, "non_existent_files.txt"), "w") as f:
        for line in non_existent_files:
            f.write(f"{line}\n")


if __name__ == "__main__":
    main()
