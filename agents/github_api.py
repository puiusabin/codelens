import re

import requests


def parse_pr_url(pr_url: str) -> tuple[str, str, int]:
    """Extracts (owner, repo, pr_number) from a GitHub PR URL."""
    pattern = r"github\.com/([^/]+)/([^/]+)/pull/(\d+)"
    match = re.search(pattern, pr_url)
    if not match:
        raise ValueError(f"Invalid GitHub PR URL: {pr_url}")
    owner, repo, number = match.groups()
    return owner, repo, int(number)


def fetch_pr_diff(pr_url: str, token: str | None = None) -> str:
    """Fetches the unified diff for a GitHub Pull Request."""
    owner, repo, pr_number = parse_pr_url(pr_url)
    headers = {"Accept": "application/vnd.github.v3.diff"}
    if token:
        headers["Authorization"] = f"token {token}"
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text
