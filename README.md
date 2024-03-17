# RepoVac

This Python script automates the process of downloading specific dependency files from all active repositories within a specified GitHub organization. It supports a wide range of programming languages and their respective package managers, including Python, JavaScript, TypeScript, Java, Kotlin, Go, Ruby, Rust, Elixir, and PHP.

## Features

- Downloads dependency files for multiple programming languages.
- Skips archived repositories to focus on active projects.
- Handles GitHub API rate limits gracefully.
- Retries downloads for temporary failures.
- Logs successful downloads, temporary failures, and non-existent files.
- User-defined GitHub organization via command-line prompt.

## Prerequisites

- Python 3.6 or newer.
- A GitHub Personal Access Token (PAT) with appropriate permissions to access the organization's repositories.
- The `requests`, `tqdm`, and `base64` Python packages (usually included with Python standard library for `base64`).

## Setup

1. Clone this repository or download the script to your local machine.
2. Ensure you have Python installed on your machine.
3. Install the required Python packages:

    ```bash
    pip install requests tqdm
    ```

4. Set your GitHub Personal Access Token (PAT) as an environment variable:

    - For Linux/macOS:

    ```bash
    export GITHUB_AUTH_TOKEN="your_token_here"
    ```

    - For Windows:

    ```cmd
    set GITHUB_AUTH_TOKEN=your_token_here
    ```

## Usage

To run the script, navigate to the directory where the script is located and execute it with Python:

```bash
python github_dependency_downloader.py
