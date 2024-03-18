import requests
from datetime import datetime
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import os

PAT = os.environ.get("GITHUB_AUTH_TOKEN")
if not PAT:
    raise ValueError("GITHUB_AUTH_TOKEN environment variable is not set.")
ORG_NAME = input("Enter the GitHub organization name: ")
BASE_URL = "https://api.github.com"

session = requests.Session()
session.headers.update({"Authorization": f"token {PAT}"})

DEPENDENCY_FILES = [
    "requirements.txt",
    "Pipfile.lock",
    "pyproject.toml",
    "Gemfile.lock",
    "package-lock.json",
    "yarn.lock",
    "npm-shrinkwrap.json",
    "composer.lock",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "go.mod",
    "Cargo.lock",
    "mix.lock",
    "Podfile.lock",
    "Cartfile.resolved",
]


def check_rate_limit():
    rate_limit_url = f"{BASE_URL}/rate_limit"
    response = session.get(rate_limit_url)
    rate_limit_data = response.json()
    remaining = rate_limit_data["rate"]["remaining"]
    reset_time = rate_limit_data["rate"]["reset"]
    current_time = time.time()

    if remaining < 5:  # Ensure we have buffer of 5 requests
        sleep_time = reset_time - current_time + 1  # Adding 1 second buffer
        print(f"Approaching rate limit. Sleeping for {sleep_time:.2f} seconds.")
        time.sleep(sleep_time)


def fetch_repos(org_name):
    check_rate_limit()
    repos = []
    url = f"{BASE_URL}/orgs/{org_name}/repos?per_page=100"
    while url:
        response = session.get(url)
        response.raise_for_status()
        repos.extend([repo for repo in response.json() if not repo.get("archived")])
        url = response.links.get("next", {}).get("url")
    return repos


def download_file(args):
    repo_name, file_name, save_path = args
    check_rate_limit()
    file_url = f"{BASE_URL}/repos/{repo_name}/contents/{file_name}"
    response = session.get(file_url)
    if response.status_code == 200:
        with open(save_path, "wb") as f:
            f.write(response.content)
        return f"Success: {repo_name}/{file_name}"
    return f"Failed: {repo_name}/{file_name} - {response.status_code}"


def main():
    base_dir = f"dependencies_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
    os.makedirs(base_dir, exist_ok=True)

    repos = fetch_repos(ORG_NAME)

    tasks = []
    for repo in repos:
        repo_name = repo["full_name"]
        for file_name in DEPENDENCY_FILES:
            save_path = os.path.join(base_dir, repo_name, file_name)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            tasks.append((repo_name, file_name, save_path))

    results = []
    with ThreadPoolExecutor(
        max_workers=4
    ) as executor:  # Adjust max_workers based on your needs and GitHub's rate limit
        future_to_task = {executor.submit(download_file, task): task for task in tasks}
        for future in tqdm(
            as_completed(future_to_task), total=len(tasks), desc="Downloading"
        ):
            result = future.result()
            results.append(result)

    # Log the results
    with open(os.path.join(base_dir, "download_log.txt"), "w") as log_file:
        for result in results:
            log_file.write(f"{result}\n")


if __name__ == "__main__":
    main()
