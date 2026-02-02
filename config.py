import os
import sys
import logging
from pathlib import Path

from dotenv import load_dotenv

from notifications.handler import NotificationHandler
from notifications.manager import NotificationManager
from notifications.gotify import GotifyNotifier
from notifications.ntfy import NtfyNotifier
from notifications.discord import DiscordNotifier

STACKS_ROOT = Path("/stacks")
SECRETS_ROOT = Path("/secrets")


def setup_notifications():
    manager = load_notifications()

    if not manager.notifiers:
        return

    handler = NotificationHandler(manager)

    handler.setLevel(logging.NOTSET)  # <-- IMPORTANT

    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s",
            "%Y-%m-%d %H:%M:%S",
        )
    )

    root = logging.getLogger()
    root.addHandler(handler)



def load_notifications():
    notifiers = []

    def level(name: str) -> int:
        return getattr(logging, name.upper(), logging.INFO)

    if os.getenv("NOTIFY_GOTIFY") == "true":
        notifiers.append(
            GotifyNotifier(
                os.environ["GOTIFY_URL"],
                os.environ["GOTIFY_TOKEN"],
                level(os.getenv("GOTIFY_LEVEL", "INFO")),
            )
        )

    if os.getenv("NOTIFY_NTFY") == "true":
        notifiers.append(
            NtfyNotifier(
                os.environ["NTFY_TOPIC"],
                level(os.getenv("NTFY_LEVEL", "INFO")),
            )
        )

    if os.getenv("NOTIFY_DISCORD") == "true":
        notifiers.append(
            DiscordNotifier(
                os.environ["DISCORD_WEBHOOK"],
                level(os.getenv("DISCORD_LEVEL", "INFO")),
            )
        )

    return NotificationManager(notifiers)



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
