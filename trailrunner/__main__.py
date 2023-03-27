# Copyright Amethyst Reese
# Licensed under the MIT license

from __future__ import annotations

from pathlib import Path
from typing import Any

import click

try:
    print: Any
    from rich import print as print
except ImportError:
    from pprint import pprint as print

from . import core


@click.group()
def main() -> None:
    pass


@main.command()
@click.argument("path", required=True, type=click.Path(path_type=Path))
def debug(path: Path) -> None:
    """
    Output debug info about the given path
    """
    root = core.project_root(path)
    print(f"root = {root}")
    gitignore = core.gitignore(root)
    print(f"len(gitignore) = {len(gitignore.patterns)}")


@main.command()
@click.argument("path", required=True, type=click.Path(path_type=Path))
def walk(path: Path) -> None:
    """
    Print all paths found when walking
    """
    runner = core.Trailrunner()
    for child in runner.walk(path):
        print(child)

    print()
    for child, reason in runner.EXCLUDED.items():
        print(f"{child} excluded for {reason!r}")


if __name__ == "__main__":
    main()
