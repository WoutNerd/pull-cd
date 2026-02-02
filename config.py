import os
import sys
import logging
from pathlib import Path

from dotenv import load_dotenv

STACKS_ROOT = Path("/stacks")
SECRETS_ROOT = Path("/secrets")


def setup_logging():
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )


def load_config():
    load_dotenv()

    return {
        "interval": int(os.getenv("CHECK_INTERVAL", 300)),
        "branch": os.getenv("BRANCH", "main"),
        "repo": os.getenv("GIT_REPO"),
        "compose_dir": os.getenv("COMPOSE_DIR", "").strip(),
        "force_full_deploy": os.getenv("FORCE_FULL_DEPLOY", "False") == "True",
    }
