import os
import subprocess
import time
import shutil
import sys
import logging
from pathlib import Path

from dotenv import load_dotenv

STACKS_ROOT = Path("/stacks")
SECRETS_ROOT = Path("/secrets")


def get_current_head():
    return run(["git", "rev-parse", "HEAD"], cwd=STACKS_ROOT)

def get_changed_files_between(old, new):
    output = run(
        ["git", "diff", "--name-only", f"{old}..{new}"],
        cwd=STACKS_ROOT,
    )

    if not output:
        return []

    return output.splitlines()


def get_changed_files(branch):
    output = run(
        ["git", "diff", "--name-only", f"HEAD..origin/{branch}"],
        cwd=STACKS_ROOT,
    )

    if not output:
        return []

    return output.splitlines()


def get_changed_stacks(changed_files, stacks_root: Path):
    stacks = set()

    stacks_root_rel = stacks_root.relative_to(STACKS_ROOT)

    for file in changed_files:
        path = Path(file)

        try:
            relative = path.relative_to(stacks_root_rel)
        except ValueError:
            continue  

        if len(relative.parts) == 0:
            continue

        stack_name = relative.parts[0]
        stack_dir = stacks_root / stack_name

        if stack_dir.is_dir():
            stacks.add(stack_dir)

    return sorted(stacks)


def deploy_changed_stacks(branch, stacks_root: Path):
    old_head = get_current_head()

    update_repo(branch)

    new_head = get_current_head()

    changed_files = get_changed_files_between(old_head, new_head)
    changed_stacks = get_changed_stacks(changed_files, stacks_root)

    if not changed_stacks:
        logging.info("No stack changes detected")
    else:
        logging.info(
            "Stacks to deploy: %s",
            ", ".join(s.name for s in changed_stacks),
        )

        for stack in changed_stacks:
            try:
                deploy_stack(stack)
            except Exception:
                logging.exception("Deploy failed for stack: %s", stack.name)



def sync_stack_env(stack_dir: Path):
    secret_file = SECRETS_ROOT / f"{stack_dir.name}.env"
    env_file = stack_dir / ".env"

    if not secret_file.exists():
        logging.debug(
            "No secrets file for stack %s (%s not found)",
            stack_dir.name,
            secret_file
        )
        return False

    shutil.copy(secret_file, env_file)
    logging.debug(
        "Copied secrets for %s: %s -> %s",
        stack_dir.name,
        secret_file,
        env_file
    )
    return True


def setup_logging():
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )


def run(cmd, cwd=None):
    logging.debug("Running: %s (cwd=%s)", " ".join(cmd), cwd)
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)

    if result.returncode != 0:
        logging.error("Command failed: %s", " ".join(cmd))
        logging.error(result.stderr.strip())
        raise RuntimeError("Command failed")

    if result.stdout.strip():
        logging.debug(result.stdout.strip())

    return result.stdout.strip()


def ensure_git_safe_directory():
    run(["git", "config", "--global", "--add", "safe.directory", str(STACKS_ROOT)])


def ensure_repo(repo_url, branch):
    if not (STACKS_ROOT / ".git").exists():
        logging.info("Cloning repo into %s", STACKS_ROOT)
        run(["git", "clone", "-b", branch, repo_url, str(STACKS_ROOT)])
    else:
        logging.debug("Repo already exists")


def repo_changed(branch):
    run(["git", "fetch", "origin"], cwd=STACKS_ROOT)

    local = run(["git", "rev-parse", "HEAD"], cwd=STACKS_ROOT)
    remote = run(["git", "rev-parse", f"origin/{branch}"], cwd=STACKS_ROOT)

    return local != remote


def update_repo(branch):
    logging.info("Pulling latest changes")
    run(["git", "pull", "origin", branch], cwd=STACKS_ROOT)


def find_stacks(stacks_root: Path):
    stacks = []

    for path in stacks_root.iterdir():
        if not path.is_dir():
            continue

        if (path / "docker-compose.yml").exists() or (path / "compose.yaml").exists() or (path / "compose.yml").exists() or (path / "docker-compose.yaml").exists():
            stacks.append(path)

    return stacks


def deploy_stack(path: Path):
    logging.info("Deploying stack: %s", path.name)

    synced = sync_stack_env(path)
    if not synced:
        logging.info(
            "No secrets provided for stack %s, continuing without .env",
            path.name
        )

    run(["docker", "compose", "pull"], cwd=path)
    run(["docker", "compose", "up", "-d"], cwd=path)

    logging.info("Stack %s deployed", path.name)


def deploy_all_stacks(stacks_root: Path, branch: str = os.getenv("BRANCH", "main")):
    update_repo(branch)
    stacks = find_stacks(stacks_root)
    logging.info("Found %d stacks", len(stacks))

    for stack in stacks:
        try:
            deploy_stack(stack)
        except Exception:
            logging.exception("Stack %s failed to deploy", stack.name)


def main():
    load_dotenv()
    setup_logging()
    ensure_git_safe_directory()

    interval = int(os.getenv("CHECK_INTERVAL", 300))
    branch = os.getenv("BRANCH", "main")
    repo = os.getenv("GIT_REPO")
    compose_dir = os.getenv("COMPOSE_DIR", "").strip()

    if not repo:
        logging.error("GIT_REPO is required")
        sys.exit(1)

    stacks_root = (
        STACKS_ROOT / compose_dir
        if compose_dir
        else STACKS_ROOT
    )

    if not stacks_root.exists():
        logging.error("Compose directory does not exist: %s", stacks_root)
        sys.exit(1)

    logging.info("Deploy agent started")
    logging.info("Repo: %s", repo)
    logging.info("Branch: %s", branch)
    logging.info("Interval: %ss", interval)
    logging.info("Stacks root: %s", stacks_root)

    ensure_repo(repo, branch)

    deploy_all_stacks(stacks_root)

    while True:
        try:
            if repo_changed(branch):
                logging.info("Repository changes detected")

                if os.getenv("FORCE_FULL_DEPLOY", "False") == "False":
                    deploy_changed_stacks(branch, stacks_root)
                else:
                    deploy_all_stacks(stacks_root)

            else:
                logging.info("No repository changes")
        except Exception:
            logging.exception("Deploy cycle failed")

        time.sleep(interval)


if __name__ == "__main__":
    main()
