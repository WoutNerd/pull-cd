import logging
from pathlib import Path

from config import STACKS_ROOT
from utils import run


def ensure_git_safe_directory():
    run(["git", "config", "--global", "--add", "safe.directory", str(STACKS_ROOT)])


def ensure_repo(repo_url, branch):
    if not (STACKS_ROOT / ".git").exists():
        logging.info("Cloning repo into %s", STACKS_ROOT)
        run(["git", "clone", "-b", branch, repo_url, str(STACKS_ROOT)])
    else:
        logging.debug("Repo already exists")


def update_repo(branch):
    logging.info("Pulling latest changes")
    run(["git", "pull", "origin", branch], cwd=STACKS_ROOT)


def repo_changed(branch):
    run(["git", "fetch", "origin"], cwd=STACKS_ROOT)

    local = run(["git", "rev-parse", "HEAD"], cwd=STACKS_ROOT)
    remote = run(["git", "rev-parse", f"origin/{branch}"], cwd=STACKS_ROOT)

    return local != remote


def get_current_head():
    return run(["git", "rev-parse", "HEAD"], cwd=STACKS_ROOT)


def get_changed_files_between(old, new):
    output = run(
        ["git", "diff", "--name-only", f"{old}..{new}"],
        cwd=STACKS_ROOT,
    )
    return output.splitlines() if output else []
