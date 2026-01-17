#!/usr/bin/env python3
"""
Download SWE-bench repositories to local cache

This script downloads repositories used in SWE-bench Lite to a local cache directory.
The cached repositories can then be mounted into Docker containers for faster access.
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Optional

# SWE-bench Lite repositories
REPOSITORIES = [
    "astropy/astropy",
    # Add more repositories as needed:
    # "django/django",
    # "sympy/sympy",
    # "matplotlib/matplotlib",
    # "scikit-learn/scikit-learn",
    # "pytest-dev/pytest",
    # "sphinx-doc/sphinx",
    # "psf/requests",
    # "pylint-dev/pylint",
    # "pydata/xarray",
    # "mwaskom/seaborn",
    # "pallets/flask",
]

CACHE_DIR = Path("./cache/repos")


def clone_repository(repo: str, cache_dir: Path, force: bool = False) -> bool:
    """
    Clone a repository to the cache directory.
    
    Args:
        repo: Repository name in format "owner/name"
        cache_dir: Cache directory path
        force: If True, remove existing clone and re-clone
    
    Returns:
        True if successful, False otherwise
    """
    repo_path = cache_dir / repo.replace("/", "_")
    repo_url = f"https://github.com/{repo}.git"
    
    if repo_path.exists():
        if force:
            print(f"Removing existing clone: {repo_path}")
            import shutil
            shutil.rmtree(repo_path)
        else:
            print(f"Repository already exists: {repo_path}")
            print(f"  To re-clone, use --force flag")
            return True
    
    print(f"Cloning {repo} to {repo_path}...")
    try:
        subprocess.run(
            ["git", "clone", repo_url, str(repo_path)],
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✓ Successfully cloned {repo}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to clone {repo}: {e.stderr}")
        return False


def update_repository(repo: str, cache_dir: Path) -> bool:
    """
    Update an existing repository in cache.
    
    Args:
        repo: Repository name in format "owner/name"
        cache_dir: Cache directory path
    
    Returns:
        True if successful, False otherwise
    """
    repo_path = cache_dir / repo.replace("/", "_")
    
    if not repo_path.exists():
        print(f"Repository not found: {repo_path}")
        return False
    
    print(f"Updating {repo}...")
    try:
        subprocess.run(
            ["git", "fetch", "origin"],
            cwd=repo_path,
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✓ Successfully updated {repo}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to update {repo}: {e.stderr}")
        return False


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Download SWE-bench repositories to local cache"
    )
    parser.add_argument(
        "--repos",
        nargs="+",
        help="Specific repositories to download (default: all)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-clone existing repositories"
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Update existing repositories instead of cloning"
    )
    parser.add_argument(
        "--cache-dir",
        type=str,
        default="./cache/repos",
        help="Cache directory path (default: ./cache/repos)"
    )
    
    args = parser.parse_args()
    
    cache_dir = Path(args.cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    repos_to_download = args.repos if args.repos else REPOSITORIES
    
    print(f"Cache directory: {cache_dir.absolute()}")
    print(f"Repositories to process: {len(repos_to_download)}\n")
    
    success_count = 0
    for repo in repos_to_download:
        if args.update:
            success = update_repository(repo, cache_dir)
        else:
            success = clone_repository(repo, cache_dir, force=args.force)
        
        if success:
            success_count += 1
        print()
    
    print(f"{'='*60}")
    print(f"Summary: {success_count}/{len(repos_to_download)} repositories processed successfully")
    print(f"Cache location: {cache_dir.absolute()}")
    
    if success_count < len(repos_to_download):
        sys.exit(1)


if __name__ == "__main__":
    main()
