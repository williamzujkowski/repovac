# RepoVac: GitHub Repository Dependency File Vacuum

RepoVac is a Python script designed to fetch specified dependency files from all active repositories within a given GitHub organization. It's tailored to retrieve common dependency management files across various programming languages, offering insights into the dependency structure of numerous projects.

## Features

- Dynamically fetches repositories from any specified GitHub organization.
- Supports a wide range of programming languages and their respective dependency files.
- Checks GitHub's API rate limits to prevent exceeding the allotted number of requests.
- Skips archived repositories to focus on active development projects.
- Generates detailed logs of successfully downloaded files, failed attempts, and files that do not exist.
- Retries downloads for files that failed in the initial attempt (excluding files not found).
- Organizes downloaded files into a directory structure based on the repository name, contained within a root folder named with the current date and time for easy identification.

## Supported Files

The script is configured to look for the following dependency files across various programming languages:

- **Python**: `requirements.txt`, `Pipfile.lock`
- **JavaScript/TypeScript**: `package-lock.json`, `yarn.lock`
- **Java**: `pom.xml`, `build.gradle`
- **Kotlin**: `build.gradle.kts`
- **Go**: `go.mod`
- **Ruby**: `Gemfile.lock`
- **Rust**: `Cargo.lock`
- **Elixir**: `mix.lock`
- **PHP**: `composer.lock`

## Usage

Before running the script, ensure you have Python installed on your system and the necessary libraries by running:

```bash
pip install requests tqdm
```
Set up a GitHub Personal Access Token (PAT) and export it as an environment variable:
```
export GITHUB_AUTH_TOKEN='your_personal_access_token_here'
```
To start the script, navigate to the directory containing repovac.py and run:

```
python repovac.py
```

The script will prompt you to enter the GitHub organization name. After inputting the organization name, the script begins processing.


The script outputs the files into a directory structure within the ./dependencies_<timestamp>/ directory, where <timestamp> reflects the run time. Inside this directory, you'll find:
```
success_list.txt: A list of files successfully downloaded.
failure_list.txt: A list of files that failed to download, including the error reason.
non_existent_files.txt: A list of files that were not found (HTTP 404).
```