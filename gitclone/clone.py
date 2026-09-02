"""
Git clone operations
"""

import os
import subprocess
import time
from pathlib import Path
from typing import Optional, List
from concurrent.futures import ThreadPoolExecutor, as_completed

from .logger import log
from .api import GitHubAPI

def run_command(
    cmd: List[str],
    cwd: Optional[str] = None,
    check: bool = True,
    timeout: Optional[int] = None,
    verbose: bool = False
) -> tuple:
    """
    Run a shell command and return output

    Args:
        cmd: Command list
        cwd: Working directory
        check: Raise exception on failure
        timeout: Command timeout
        verbose: Print command output

    Returns:
        (stdout, stderr, returncode)
    """
    if verbose:
        log(f"[CMD] {' '.join(cmd)}", "DEBUG")

    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False
        )

        if verbose and result.stdout:
            log(f"[OUT] {result.stdout.strip()}", "DEBUG")
        if verbose and result.stderr:
            log(f"[ERR] {result.stderr.strip()}", "DEBUG")

        return result.stdout, result.stderr, result.returncode

    except subprocess.TimeoutExpired:
        log(f"[!] Command timed out: {' '.join(cmd)}", "ERROR")
        return "", "Timeout", -1

def clone_repo(
    repo_url: str,
    dest_dir: str,
    branch: str = "main",
    depth: Optional[int] = None,
    mirror: bool = False,
    token: Optional[str] = None,
    retries: int = 3,
    verbose: bool = True
) -> bool:
    """
    Clone a git repository

    Args:
        repo_url: Repository URL
        dest_dir: Destination directory
        branch: Branch to clone
        depth: Shallow clone depth
        mirror: Clone as mirror
        token: GitHub token (for auth)
        retries: Number of retry attempts
        verbose: Verbose output

    Returns:
        True if successful
    """
    # Check if destination already exists
    if Path(dest_dir).exists():
        log(f"[ ] Repository already exists: {dest_dir}", "WARNING")
        return True

    # Build command
    cmd = ["git", "clone"]

    if mirror:
        cmd.append("--mirror")
    else:
        cmd.extend(["--branch", branch])

    if depth:
        cmd.extend(["--depth", str(depth)])

    cmd.append(repo_url)
    cmd.append(dest_dir)

    # Retry loop
    for attempt in range(1, retries + 1):
        log(f"[*] Cloning {repo_url} (attempt {attempt}/{retries})", "INFO")

        stdout, stderr, returncode = run_command(
            cmd,
            verbose=verbose,
            timeout=600  # 10 minutes timeout
        )

        if returncode == 0:
            log(f"[+] Successfully cloned to {dest_dir}", "SUCCESS")
            return True

        if attempt < retries:
            wait_time = 2 ** attempt  # Exponential backoff
            log(f"[!] Clone failed. Retrying in {wait_time}s...", "WARNING")
            time.sleep(wait_time)

    log(f"[!] Failed to clone {repo_url} after {retries} attempts", "ERROR")
    return False

def sparse_clone(
    repo_url: str,
    dest_dir: str,
    paths: List[str],
    branch: str = "main",
    depth: Optional[int] = None,
    token: Optional[str] = None,
    retries: int = 3,
    verbose: bool = True
) -> bool:
    """
    Clone only specific paths using sparse-checkout

    Args:
        repo_url: Repository URL
        dest_dir: Destination directory
        paths: List of paths to clone
        branch: Branch to clone
        depth: Shallow clone depth
        token: GitHub token
        retries: Number of retry attempts
        verbose: Verbose output

    Returns:
        True if successful
    """
    if Path(dest_dir).exists():
        log(f"[ ] Sparse directory already exists: {dest_dir}", "WARNING")
        return True

    os.makedirs(dest_dir, exist_ok=True)

    # Git init
    cmd_init = ["git", "init"]
    run_command(cmd_init, cwd=dest_dir, verbose=verbose)

    # Add remote
    cmd_remote = ["git", "remote", "add", "origin", repo_url]
    run_command(cmd_remote, cwd=dest_dir, verbose=verbose)

    # Fetch with depth if specified
    cmd_fetch = ["git", "fetch"]
    if depth:
        cmd_fetch.extend(["--depth", str(depth)])
    cmd_fetch.extend(["origin", branch])

    for attempt in range(1, retries + 1):
        log(f"[*] Sparse fetching {repo_url} (attempt {attempt}/{retries})", "INFO")

        _, _, returncode = run_command(cmd_fetch, cwd=dest_dir, verbose=verbose)

        if returncode == 0:
            break

        if attempt < retries:
            wait_time = 2 ** attempt
            log(f"[!] Fetch failed. Retrying in {wait_time}s...", "WARNING")
            time.sleep(wait_time)
    else:
        log(f"[!] Failed to fetch after {retries} attempts", "ERROR")
        return False

    # Setup sparse-checkout
    cmd_sparse = ["git", "sparse-checkout", "init", "--cone"]
    run_command(cmd_sparse, cwd=dest_dir, verbose=verbose)

    # Add paths
    for path in paths:
        cmd_add = ["git", "sparse-checkout", "add", path]
        run_command(cmd_add, cwd=dest_dir, verbose=verbose)

    # Checkout
    cmd_checkout = ["git", "checkout", branch]
    _, _, returncode = run_command(cmd_checkout, cwd=dest_dir, verbose=verbose)

    if returncode == 0:
        log(f"[+] Sparse clone successful: {', '.join(paths)}", "SUCCESS")
        return True

    log(f"[!] Sparse checkout failed", "ERROR")
    return False

def batch_clone(
    owner: str,
    dest_dir: str,
    repo_type: str = "all",
    include_forks: bool = False,
    token: Optional[str] = None,
    threads: int = 4,
    depth: Optional[int] = None,
    mirror: bool = False,
    branch: str = "main",
    exclude: Optional[List[str]] = None,
    use_ssh: bool = False,
    retries: int = 3
) -> bool:
    """
    Clone all repositories from a user or organization

    Args:
        owner: GitHub username or organization
        dest_dir: Destination directory
        repo_type: Repository type filter
        include_forks: Include forks
        token: GitHub token
        threads: Number of parallel threads
        depth: Shallow clone depth
        mirror: Clone as mirror
        branch: Branch to clone
        exclude: List of repos to exclude
        use_ssh: Use SSH instead of HTTPS
        retries: Retry attempts

    Returns:
        True if all successful
    """
    # Get repositories from GitHub API
    api = GitHubAPI(token=token)
    repos = api.get_repos(owner, repo_type, include_forks)

    if not repos:
        log(f"[!] No repositories found for {owner}", "ERROR")
        return False

    # Apply excludes
    if exclude:
        repos = [r for r in repos if r.get("name") not in exclude]

    log(f"[*] Cloning {len(repos)} repositories to {dest_dir}", "INFO")

    os.makedirs(dest_dir, exist_ok=True)

    # Clone function for thread pool
    def clone_worker(repo):
        name = repo["name"]
        clone_url = repo["clone_url"]

        # Use SSH if requested
        if use_ssh:
            clone_url = repo.get("ssh_url", clone_url)

        # Embed token for HTTPS
        if token and "https://" in clone_url and "@" not in clone_url:
            clone_url = clone_url.replace("https://", f"https://{token}@")

        target = Path(dest_dir) / name

        # Skip if exists
        if target.exists():
            log(f"[ ] {name} already exists, skipping", "INFO")
            return True

        log(f"[*] Cloning {name}...", "INFO")

        return clone_repo(
            repo_url=clone_url,
            dest_dir=str(target),
            branch=branch,
            depth=depth,
            mirror=mirror,
            retries=retries,
            verbose=False  # Reduce noise for batch
        )

    # Execute in parallel
    success_count = 0
    failure_count = 0

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {
            executor.submit(clone_worker, repo): repo["name"]
            for repo in repos
        }

        for future in as_completed(futures):
            name = futures[future]
            try:
                if future.result():
                    success_count += 1
                else:
                    failure_count += 1
                    log(f"[!] Failed to clone {name}", "ERROR")
            except Exception as e:
                failure_count += 1
                log(f"[!] Error cloning {name}: {e}", "ERROR")

    log(f"[+] Batch complete: {success_count} succeeded, {failure_count} failed", "INFO")
    return failure_count == 0