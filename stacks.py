import logging
from pathlib import Path

from config import STACKS_ROOT


def find_stacks(stacks_root: Path):
    stacks = []

    for path in stacks_root.iterdir():
        if not path.is_dir():
            continue

        if any(
            (path / name).exists()
            for name in (
                "docker-compose.yml",
                "docker-compose.yaml",
                "compose.yml",
                "compose.yaml",
            )
        ):
            stacks.append(path)

    return stacks


def get_changed_stacks(changed_files, stacks_root: Path):
    stacks = set()
    stacks_root_rel = stacks_root.relative_to(STACKS_ROOT)

    for file in changed_files:
        path = Path(file)

        try:
            relative = path.relative_to(stacks_root_rel)
        except ValueError:
            continue

        if not relative.parts:
            continue

        stack_dir = stacks_root / relative.parts[0]
        if stack_dir.is_dir():
            stacks.add(stack_dir)

    return sorted(stacks)
