#!/usr/bin/env python3
"""
Advanced Usage Examples for GitClonePro
=======================================

This script demonstrates various use cases of GitClonePro including:
- Basic cloning
- Sparse cloning
- Batch cloning
- Mirror cloning
- Private repository cloning
- Custom configuration

Usage:
    python advanced_usage.py
    python advanced_usage.py --example 1
    python advanced_usage.py --all
"""

import os
import sys
import time
from pathlib import Path
from typing import Optional, List, Dict, Any

# Add parent directory to path so we can import gitclone
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from gitclone.core import GitClonePro
    from gitclone.logger import setup_logger, log
    from gitclone.utils import expand_path
except ImportError:
    print("[!] GitClonePro not installed. Please run: pip install -e .")
    sys.exit(1)

# ==================== CONFIGURATION ====================
# Color codes for terminal output
GREEN = '\033[0;32m'
BLUE = '\033[0;34m'
CYAN = '\033[0;36m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
PURPLE = '\033[0;35m'
WHITE = '\033[1;37m'
NC = '\033[0m'  # No Color

# ==================== UTILITY FUNCTIONS ====================

def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{BLUE}╔{'═' * 60}╗{NC}")
    print(f"{BLUE}║{NC} {CYAN}{text:58}{NC} {BLUE}║{NC}")
    print(f"{BLUE}╚{'═' * 60}╝{NC}\n")

def print_section(text: str):
    """Print a section header"""
    print(f"\n{CYAN}▶ {text}{NC}")
    print(f"{CYAN}{'━' * 60}{NC}")

def print_success(text: str):
    """Print success message"""
    print(f"{GREEN}✅ {text}{NC}")

def print_error(text: str):
    """Print error message"""
    print(f"{RED}❌ {text}{NC}")

def print_info(text: str):
    """Print info message"""
    print(f"{BLUE}ℹ️  {text}{NC}")

def print_warning(text: str):
    """Print warning message"""
    print(f"{YELLOW}⚠️  {text}{NC}")

def print_result(key: str, value: str):
    """Print a result pair"""
    print(f"  {WHITE}{key}:{NC} {value}")

def get_token() -> Optional[str]:
    """Get GitHub token from environment or user input"""
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        print_info(f"Using GITHUB_TOKEN from environment: {token[:8]}...")
        return token
    
    print_warning("GITHUB_TOKEN not set in environment")
    response = input("Enter GitHub token (or press Enter to skip): ").strip()
    if response:
        return response
    return None

def create_clone_dir(name: str) -> Path:
    """Create a clone directory"""
    base_dir = Path("./clones_demo")
    base_dir.mkdir(exist_ok=True)
    
    # Create timestamped subdirectory
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    clone_dir = base_dir / f"{name}_{timestamp}"
    clone_dir.mkdir(parents=True, exist_ok=True)
    
    return clone_dir

# ==================== EXAMPLE FUNCTIONS ====================

def example_1_basic_clone():
    """
    Example 1: Basic Repository Clone
    Clones a public repository with default settings
    """
    print_header("Example 1: Basic Repository Clone")
    
    print_info("Cloning a public repository with default settings...")
    print_info("Repository: https://github.com/octocat/Hello-World")
    
    try:
        # Initialize GitClonePro
        core = GitClonePro(verbose=True, quiet=False)
        
        # Create destination directory
        dest_dir = create_clone_dir("basic_clone")
        
        # Clone the repository
        success = core.clone_single(
            url="https://github.com/octocat/Hello-World",
            dest=str(dest_dir / "Hello-World")
        )
        
        if success:
            print_success("Basic clone completed successfully!")
            print_result("Location", str(dest_dir / "Hello-World"))
            
            # Show what was cloned
            clone_path = dest_dir / "Hello-World"
            if clone_path.exists():
                files = list(clone_path.glob("*"))
                print_info(f"Files cloned: {len(files)}")
                for f in files[:5]:
                    print(f"  📁 {f.name}")
                if len(files) > 5:
                    print(f"  ... and {len(files) - 5} more")
        else:
            print_error("Basic clone failed!")
            
    except Exception as e:
        print_error(f"Error: {e}")
        import traceback
        traceback.print_exc()

def example_2_sparse_clone():
    """
    Example 2: Sparse Clone
    Clones only specific files/folders from a repository
    """
    print_header("Example 2: Sparse Clone")
    
    print_info("Cloning only specific paths from a repository...")
    print_info("Repository: https://github.com/facebook/react")
    print_info("Paths: src/, README.md")
    
    try:
        core = GitClonePro(verbose=True, quiet=False)
        
        dest_dir = create_clone_dir("sparse_clone")
        
        success = core.clone_single(
            url="https://github.com/facebook/react",
            dest=str(dest_dir / "react-sparse"),
            sparse=["src/", "README.md"],
            depth=1
        )
        
        if success:
            print_success("Sparse clone completed successfully!")
            print_result("Location", str(dest_dir / "react-sparse"))
            
            # Show what was cloned
            clone_path = dest_dir / "react-sparse"
            if clone_path.exists():
                files = list(clone_path.glob("*"))
                print_info(f"Files cloned: {len(files)}")
                for f in files:
                    if f.is_dir():
                        print(f"  📁 {f.name}/")
                    else:
                        print(f"  📄 {f.name}")
        else:
            print_error("Sparse clone failed!")
            
    except Exception as e:
        print_error(f"Error: {e}")

def example_3_batch_clone():
    """
    Example 3: Batch Clone
    Clones all public repositories from a user/organization
    """
    print_header("Example 3: Batch Clone")
    
    owner = "octocat"
    print_info(f"Cloning all public repositories from {owner}...")
    print_warning("This may take a while depending on internet speed")
    
    try:
        core = GitClonePro(verbose=True, quiet=False)
        
        dest_dir = create_clone_dir("batch_clone")
        
        success = core.batch_clone(
            owner=owner,
            dest=str(dest_dir),
            repo_type="public",
            threads=4,
            depth=1
        )
        
        if success:
            print_success(f"Batch clone completed successfully!")
            print_result("Location", str(dest_dir))
            
            # Show what was cloned
            if dest_dir.exists():
                repos = list(dest_dir.glob("*"))
                print_info(f"Repositories cloned: {len(repos)}")
                for repo in repos[:10]:
                    if repo.is_dir():
                        size = sum(f.stat().st_size for f in repo.rglob('*')) / (1024 * 1024)
                        print(f"  📁 {repo.name} ({size:.1f} MB)")
                if len(repos) > 10:
                    print(f"  ... and {len(repos) - 10} more")
        else:
            print_error("Batch clone failed!")
            
    except Exception as e:
        print_error(f"Error: {e}")

def example_4_mirror_clone():
    """
    Example 4: Mirror Clone
    Creates a bare mirror clone for backup purposes
    """
    print_header("Example 4: Mirror Clone (Backup)")
    
    print_info("Creating a mirror (bare) clone for backup...")
    print_info("Repository: https://github.com/torvalds/linux")
    print_warning("This creates a bare repository with all branches and tags")
    
    try:
        core = GitClonePro(verbose=True, quiet=False)
        
        dest_dir = create_clone_dir("mirror_clone")
        
        success = core.clone_single(
            url="https://github.com/torvalds/linux",
            dest=str(dest_dir / "linux-mirror"),
            mirror=True,
            depth=1  # Limit history for demo
        )
        
        if success:
            print_success("Mirror clone completed successfully!")
            print_result("Location", str(dest_dir / "linux-mirror"))
            
            # Show what was cloned
            clone_path = dest_dir / "linux-mirror"
            if clone_path.exists():
                print_info("Mirror contains:")
                for item in clone_path.glob("*"):
                    if item.is_dir():
                        print(f"  📁 {item.name}/")
                    else:
                        print(f"  📄 {item.name}")
        else:
            print_error("Mirror clone failed!")
            
    except Exception as e:
        print_error(f"Error: {e}")

def example_5_private_repo():
    """
    Example 5: Private Repository Clone
    Clones a private repository using GitHub token
    """
    print_header("Example 5: Private Repository Clone")
    
    print_info("Cloning a private repository with token authentication...")
    print_warning("This requires a valid GitHub token with repo scope")
    
    token = get_token()
    if not token:
        print_warning("No token provided. Skipping private repo example.")
        return
    
    repo_url = input("Enter private repository URL (or press Enter to skip): ").strip()
    if not repo_url:
        print_warning("No repository URL provided. Skipping.")
        return
    
    try:
        core = GitClonePro(token=token, verbose=True, quiet=False)
        
        dest_dir = create_clone_dir("private_clone")
        
        success = core.clone_single(
            url=repo_url,
            dest=str(dest_dir / "private-repo"),
            depth=1
        )
        
        if success:
            print_success("Private repository cloned successfully!")
            print_result("Location", str(dest_dir / "private-repo"))
        else:
            print_error("Private repository clone failed!")
            
    except Exception as e:
        print_error(f"Error: {e}")

def example_6_custom_config():
    """
    Example 6: Custom Configuration
    Uses custom configuration settings
    """
    print_header("Example 6: Custom Configuration")
    
    print_info("Using custom configuration for clone...")
    
    try:
        # Create in-memory configuration
        config = {
            "clone_dir": "./custom_clones",
            "default_branch": "develop",
            "retries": 5,
            "threads": 8,
            "verbose": True,
        }
        
        # Note: GitClonePro expects config file path, not dict
        # Instead, we'll use environment variables
        os.environ["GITCLONE_BRANCH"] = "develop"
        os.environ["GITCLONE_RETRIES"] = "5"
        
        core = GitClonePro(verbose=True, quiet=False)
        
        dest_dir = create_clone_dir("custom_config")
        
        success = core.clone_single(
            url="https://github.com/facebook/react",
            dest=str(dest_dir / "react-custom"),
            branch="main",  # Using main instead of develop for demo
            depth=1
        )
        
        if success:
            print_success("Custom configuration clone completed!")
            print_result("Location", str(dest_dir / "react-custom"))
            
            # Show config used
            print_info("Configuration used:")
            for key, value in config.items():
                print(f"  {key}: {value}")
        else:
            print_error("Custom configuration clone failed!")
            
    except Exception as e:
        print_error(f"Error: {e}")

def example_7_shallow_clone():
    """
    Example 7: Shallow Clone
    Clones only the latest commit for speed
    """
    print_header("Example 7: Shallow Clone (Latest Commit Only)")
    
    print_info("Cloning with minimal history for speed...")
    print_info("Repository: https://github.com/angular/angular")
    print_info("Depth: 1 (only latest commit)")
    
    try:
        core = GitClonePro(verbose=True, quiet=False)
        
        dest_dir = create_clone_dir("shallow_clone")
        
        success = core.clone_single(
            url="https://github.com/angular/angular",
            dest=str(dest_dir / "angular-shallow"),
            depth=1
        )
        
        if success:
            print_success("Shallow clone completed successfully!")
            print_result("Location", str(dest_dir / "angular-shallow"))
            
            # Check git log
            clone_path = dest_dir / "angular-shallow"
            if clone_path.exists():
                os.chdir(clone_path)
                import subprocess
                result = subprocess.run(
                    ["git", "log", "--oneline", "-n", "3"],
                    capture_output=True,
                    text=True
                )
                print_info("Latest commits:")
                for line in result.stdout.strip().split("\n"):
                    if line:
                        print(f"  {line}")
        else:
            print_error("Shallow clone failed!")
            
    except Exception as e:
        print_error(f"Error: {e}")

def example_8_branch_clone():
    """
    Example 8: Specific Branch Clone
    Clones a specific branch from a repository
    """
    print_header("Example 8: Specific Branch Clone")
    
    print_info("Cloning a specific branch...")
    print_info("Repository: https://github.com/kubernetes/kubernetes")
    print_info("Branch: release-1.28")
    
    try:
        core = GitClonePro(verbose=True, quiet=False)
        
        dest_dir = create_clone_dir("branch_clone")
        
        success = core.clone_single(
            url="https://github.com/kubernetes/kubernetes",
            dest=str(dest_dir / "kubernetes-branch"),
            branch="release-1.28",
            depth=1
        )
        
        if success:
            print_success("Branch clone completed successfully!")
            print_result("Location", str(dest_dir / "kubernetes-branch"))
            print_result("Branch", "release-1.28")
        else:
            print_error("Branch clone failed!")
            
    except Exception as e:
        print_error(f"Error: {e}")

def example_9_ssh_clone():
    """
    Example 9: SSH Clone
    Clones using SSH instead of HTTPS
    """
    print_header("Example 9: SSH Clone")
    
    print_info("Cloning using SSH authentication...")
    print_info("Repository: git@github.com:octocat/Hello-World.git")
    print_warning("This requires SSH keys configured with GitHub")
    
    try:
        core = GitClonePro(use_ssh=True, verbose=True, quiet=False)
        
        dest_dir = create_clone_dir("ssh_clone")
        
        success = core.clone_single(
            url="git@github.com:octocat/Hello-World.git",
            dest=str(dest_dir / "hello-world-ssh"),
            depth=1
        )
        
        if success:
            print_success("SSH clone completed successfully!")
            print_result("Location", str(dest_dir / "hello-world-ssh"))
        else:
            print_error("SSH clone failed!")
            
    except Exception as e:
        print_error(f"Error: {e}")

def example_10_exclude_files():
    """
    Example 10: Clone with Exclusions
    Clones a repository while excluding certain files/folders
    """
    print_header("Example 10: Clone with Exclusions")
    
    print_info("Cloning with file/folder exclusions...")
    print_info("Repository: https://github.com/django/django")
    print_info("Excluding: tests/, docs/")
    
    try:
        core = GitClonePro(verbose=True, quiet=False)
        
        dest_dir = create_clone_dir("exclude_clone")
        
        success = core.clone_single(
            url="https://github.com/django/django",
            dest=str(dest_dir / "django-exclude"),
            exclude=["tests/", "docs/"],
            depth=1
        )
        
        if success:
            print_success("Clone with exclusions completed!")
            print_result("Location", str(dest_dir / "django-exclude"))
            
            # Show what was excluded
            clone_path = dest_dir / "django-exclude"
            if clone_path.exists():
                print_info("Excluded paths:")
                print("  📁 tests/ (excluded)")
                print("  📁 docs/ (excluded)")
                print_info("All other files were cloned normally")
        else:
            print_error("Clone with exclusions failed!")
            
    except Exception as e:
        print_error(f"Error: {e}")

# ==================== RUN ALL EXAMPLES ====================

def run_all_examples():
    """Run all examples sequentially"""
    print_header("Running All Examples")
    
    print_info("Starting all examples...")
    print_warning("This will take some time and bandwidth")
    print("")
    
    examples = [
        ("Basic Clone", example_1_basic_clone),
        ("Sparse Clone", example_2_sparse_clone),
        ("Batch Clone", example_3_batch_clone),
        ("Mirror Clone", example_4_mirror_clone),
        ("Private Repo", example_5_private_repo),
        ("Custom Config", example_6_custom_config),
        ("Shallow Clone", example_7_shallow_clone),
        ("Branch Clone", example_8_branch_clone),
        ("SSH Clone", example_9_ssh_clone),
        ("Exclude Files", example_10_exclude_files),
    ]
    
    for i, (name, func) in enumerate(examples, 1):
        print(f"\n{CYAN}{'=' * 60}{NC}")
        print(f"{CYAN}Running Example {i}/{len(examples)}: {name}{NC}")
        print(f"{CYAN}{'=' * 60}{NC}")
        
        try:
            func()
        except Exception as e:
            print_error(f"Example {i} failed: {e}")
        
        if i < len(examples):
            print("\n" + "-" * 40)
            input("Press Enter to continue to next example...")

def show_menu():
    """Show interactive menu"""
    print_header("GitClonePro - Advanced Usage Examples")
    
    print("Available examples:")
    print("  1)  Basic Clone - Clone a public repository")
    print("  2)  Sparse Clone - Clone only specific files/folders")
    print("  3)  Batch Clone - Clone all repos from a user/org")
    print("  4)  Mirror Clone - Create a bare mirror backup")
    print("  5)  Private Repo - Clone a private repository with token")
    print("  6)  Custom Config - Use custom configuration")
    print("  7)  Shallow Clone - Clone only the latest commit")
    print("  8)  Branch Clone - Clone a specific branch")
    print("  9)  SSH Clone - Clone using SSH authentication")
    print("  10) Exclude Files - Clone with exclusions")
    print("  a)  Run All Examples")
    print("  q)  Quit")
    print("")
    
    choice = input("Select an option: ").strip().lower()
    
    examples = {
        "1": example_1_basic_clone,
        "2": example_2_sparse_clone,
        "3": example_3_batch_clone,
        "4": example_4_mirror_clone,
        "5": example_5_private_repo,
        "6": example_6_custom_config,
        "7": example_7_shallow_clone,
        "8": example_8_branch_clone,
        "9": example_9_ssh_clone,
        "10": example_10_exclude_files,
    }
    
    if choice == "a":
        run_all_examples()
    elif choice == "q":
        print_info("Exiting...")
        sys.exit(0)
    elif choice in examples:
        print_info(f"Running example {choice}...")
        examples[choice]()
    else:
        print_error(f"Invalid choice: {choice}")
        print_info("Please select 1-10, 'a', or 'q'")

# ==================== MAIN ====================

def main():
    """Main entry point"""
    # Parse command line arguments
    import argparse
    
    parser = argparse.ArgumentParser(
        description="GitClonePro Advanced Usage Examples",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--example", "-e",
        type=int,
        choices=range(1, 11),
        help="Run specific example (1-10)"
    )
    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Run all examples"
    )
    parser.add_argument(
        "--menu", "-m",
        action="store_true",
        help="Show interactive menu"
    )
    
    args = parser.parse_args()
    
    # Create clones directory
    Path("./clones_demo").mkdir(exist_ok=True)
    
    # Run based on arguments
    if args.all:
        run_all_examples()
    elif args.example:
        examples = {
            1: example_1_basic_clone,
            2: example_2_sparse_clone,
            3: example_3_batch_clone,
            4: example_4_mirror_clone,
            5: example_5_private_repo,
            6: example_6_custom_config,
            7: example_7_shallow_clone,
            8: example_8_branch_clone,
            9: example_9_ssh_clone,
            10: example_10_exclude_files,
        }
        print_info(f"Running example {args.example}...")
        examples[args.example]()
    else:
        # Default: show menu
        show_menu()

if __name__ == "__main__":
    main()