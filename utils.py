import logging
import subprocess


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
