# Copyright 2021 John Reese
# Licensed under the MIT license

from concurrent.futures import ProcessPoolExecutor, Executor
from multiprocessing import get_context
from pathlib import Path
from typing import Iterable, Iterator, Callable, TypeVar, List, Dict, Type

from pathspec import PathSpec, RegexPattern
from pathspec.patterns.gitwildmatch import GitWildMatchPattern

T = TypeVar("T")

CONTEXT = get_context("spawn")
EXECUTOR: Type[Executor] = ProcessPoolExecutor
INCLUDE_PATTERN = r".+\.pyi?$"
ROOT_MARKERS = [Path("pyproject.toml"), Path(".git"), Path(".hg")]


def project_root(path: Path) -> Path:
    real_path = path.resolve()

    parents = list(real_path.parents)
    if real_path.is_dir():
        parents.insert(0, real_path)

    for parent in parents:
        if any((parent / marker).exists() for marker in ROOT_MARKERS):
            return parent

    return parent


def gitignore(path: Path) -> PathSpec:
    if not path.is_dir():
        raise ValueError(f"path {path} not a directory")

    gi_path = path / ".gitignore"

    if gi_path.is_file():
        lines = gi_path.read_text().splitlines()
        return PathSpec.from_lines(GitWildMatchPattern, lines)

    return PathSpec([])


def walk(path: Path) -> Iterator[Path]:
    root = project_root(path)
    ignore = gitignore(root)
    include = PathSpec([RegexPattern(INCLUDE_PATTERN)])

    def gen(children: Iterable[Path]) -> Iterator[Path]:
        for child in children:

            if ignore.match_file(child):
                continue

            if child.is_file() and include.match_file(child):
                yield child

            elif child.is_dir():
                yield from gen(child.iterdir())

    return gen([path])


def run(paths: Iterable[Path], func: Callable[[Path], T]) -> Dict[Path, T]:
    paths = list(paths)

    with EXECUTOR() as exe:
        results = list(exe.map(func, paths))

    return dict(zip(paths, results))


def walk_and_run(paths: Iterable[Path], func: Callable[[Path], T]) -> Dict[Path, T]:
    all_paths: List[Path] = []
    for path in paths:
        all_paths.extend(walk(path))

    return run(all_paths, func)
