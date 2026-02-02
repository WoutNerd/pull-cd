import logging
import shutil
from pathlib import Path

from config import SECRETS_ROOT
from utils import run


def sync_stack_env(stack_dir: Path):
    secret_file = SECRETS_ROOT / f"{stack_dir.name}.env"
    env_file = stack_dir / ".env"

    if not secret_file.exists():
        logging.debug("No secrets file for stack %s", stack_dir.name)
        return False

    shutil.copy(secret_file, env_file)
    logging.debug("Copied secrets for %s", stack_dir.name)
    return True


def deploy_stack(path: Path):
    logging.info("Deploying stack: %s", path.name)

    if not sync_stack_env(path):
        logging.info("No secrets for stack %s, continuing", path.name)

    run(["docker", "compose", "pull"], cwd=path)
    run(["docker", "compose", "up", "-d"], cwd=path)

    logging.info("Stack %s deployed", path.name)
