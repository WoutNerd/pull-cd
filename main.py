import sys
import time
import logging
from pathlib import Path

from config import STACKS_ROOT, setup_logging, load_config
from git import (
    ensure_git_safe_directory,
    ensure_repo,
    update_repo,
    repo_changed,
    get_current_head,
    get_changed_files_between,
)
from stacks import find_stacks, get_changed_stacks
from deploy import deploy_stack
from config import setup_logging, setup_notifications


def deploy_all_stacks(stacks_root: Path, branch: str):
    update_repo(branch)
    stacks = find_stacks(stacks_root)

    logging.info("Found %d stacks", len(stacks))
    for stack in stacks:
        try:
            deploy_stack(stack)
        except Exception:
            logging.exception("Stack %s failed to deploy", stack.name)


def deploy_changed_stacks(branch, stacks_root: Path):
    old_head = get_current_head()
    update_repo(branch)
    new_head = get_current_head()

    changed_files = get_changed_files_between(old_head, new_head)
    stacks = get_changed_stacks(changed_files, stacks_root)

    if not stacks:
        logging.info("No stack changes detected")
        return

    logging.info("Stacks to deploy: %s", ", ".join(s.name for s in stacks))
    for stack in stacks:
        try:
            deploy_stack(stack)
        except Exception:
            logging.exception("Deploy failed for stack: %s", stack.name)


def main():
    setup_logging()
    setup_notifications()
    config = load_config()

    if not config["repo"]:
        logging.error("GIT_REPO is required")
        sys.exit(1)

    ensure_git_safe_directory()
    ensure_repo(config["repo"], config["branch"])

    stacks_root = (
        STACKS_ROOT / config["compose_dir"]
        if config["compose_dir"]
        else STACKS_ROOT
    )

    deploy_all_stacks(stacks_root, config["branch"])

    while True:
        try:
            if repo_changed(config["branch"]):
                logging.info("Repository changes detected")

                if config["force_full_deploy"]:
                    deploy_all_stacks(stacks_root, config["branch"])
                else:
                    deploy_changed_stacks(config["branch"], stacks_root)
            else:
                logging.info("No repository changes")
        except Exception:
            logging.exception("Deploy cycle failed")

        time.sleep(config["interval"])


if __name__ == "__main__":
    main()
