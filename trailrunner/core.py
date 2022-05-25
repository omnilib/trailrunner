# Copyright 2021 John Reese
# Licensed under the MIT license

import multiprocessing
from concurrent.futures import as_completed, Executor
from pathlib import Path
from typing import (
    Callable,
    Dict,
    Generator,
    Iterable,
    Iterator,
    List,
    Optional,
    Tuple,
    TypeVar,
)

from pathspec import PathSpec, Pattern, RegexPattern
from pathspec.patterns.gitwildmatch import GitWildMatchPattern

from .compat import ProcessPoolExecutor

T = TypeVar("T")
Excludes = Optional[List[str]]


EXECUTOR = None  # deprecated, will be removed by 2.0

INCLUDE_PATTERN: str = r".+\.pyi?$"
"""
Regex pattern used to match against filenames that should be included in results when
recursively walking directories. Any files not matching this regex will be ignored.
"""

ROOT_MARKERS: List[Path] = [Path("pyproject.toml"), Path(".git"), Path(".hg")]
"""
List of :class:`pathlib.Path` objects used to "mark" the root of project. This is used
by :func:`gitignore` for finding and reading a :file:`.gitignore` file from the project
root of a given path or directory.
"""


def project_root(path: Path) -> Path:
    """
    Find the project root, looking upward from the given path.

    Looks through all parent paths until either the root is reached, or a directory
    is found that contains any of :attr:`ROOT_MARKERS`.
    """
    real_path = path.resolve()

    parents = list(real_path.parents)
    if real_path.is_dir():
        parents.insert(0, real_path)

    for parent in parents:
        if any((parent / marker).exists() for marker in ROOT_MARKERS):
            return parent

    return parent


def pathspec(patterns: Excludes, *, style: Pattern = GitWildMatchPattern) -> PathSpec:
    """
    Generate a `PathSpec` object for the given set of paths to include or exclude.

    If None is given, an empty PathSpec is returned.
    """

    if patterns:
        return PathSpec.from_lines(style, patterns)

    return PathSpec([])


def gitignore(path: Path) -> PathSpec:
    """
    Generate a `PathSpec` object for a .gitignore file in the given directory.

    If none is found, an empty PathSpec is returned. If the path is not a directory,
    `ValueError` is raised.
    """
    if not path.is_dir():
        raise ValueError(f"path {path} not a directory")

    gi_path = path / ".gitignore"

    lines: Excludes = None
    if gi_path.is_file():
        lines = gi_path.read_text().splitlines()

    return pathspec(lines, style=GitWildMatchPattern)


class Trailrunner:
    """
    Self-contained Trailrunner instance with configurable multiprocessing semantics.

    The basic API functions above are lightweight wrappers calling their respective
    methods on fresh instances of the :class:`Trailrunner` class with no arguments.

    By default, uses a process pool executor with "spawn" child processes, to enforce
    consistent behavior when running functions on Linux, macOS, and Windows. This can
    be overridden for each individual instance by passing an executor factory during
    initialization.
    """

    DEFAULT_EXECUTOR: Optional[Callable[[], Executor]] = None
    """
    Global override for the default executor, used when `executor_factory` is not
    passed to new instances. This is intended primarily for use in unit testing, when
    it is desirable to force using thread pools by default.

    Prefer explicitly passing `executor_factory` when possible to avoid conflicting
    behavior with other packages that also use trailrunner.
    """

    def __init__(
        self,
        *,
        context: Optional[multiprocessing.context.BaseContext] = None,
        executor_factory: Optional[Callable[[], Executor]] = None,
    ):
        """
        :param context: :mod:`multiprocessing` context used by the default process pool
            executor. Ignored if :attr:`DEFAULT_EXECUTOR` is set, or `executor_factory`
            is passed. Not supported in Python 3.6 or older.
        :param executor_factory: Alternative executor factory. Must be a function that
            takes no arguments, and returns an instance
            of :class:`concurrent.futures.Executor`.
        """
        self.context = context or multiprocessing.get_context("spawn")
        self.executor_factory = (
            executor_factory or self.DEFAULT_EXECUTOR or self._default_executor
        )

    def _default_executor(self) -> Executor:
        """
        Default executor factory using a ProcessPoolExecutor.
        """
        if EXECUTOR:  # deprecated
            return EXECUTOR()
        return ProcessPoolExecutor(mp_context=self.context)

    def walk(self, path: Path, *, excludes: Excludes = None) -> Iterator[Path]:
        """
        Generate all significant file paths, starting from the given path.

        Finds the project root and any associated gitignore. Filters any paths that match
        a gitignore pattern. Recurses into subdirectories, and otherwise only includes
        files that match the :attr:`trailrunner.core.INCLUDE_PATTERN` regex.

        Optional `excludes` parameter allows supplying an extra set of paths (or
        gitignore-style patterns) to exclude from the final results.

        Returns a generator that yields each significant file as the tree is walked.
        """
        root = project_root(path)
        ignore = gitignore(root) + pathspec(excludes)
        include = PathSpec([RegexPattern(INCLUDE_PATTERN)])

        def gen(children: Iterable[Path], *, explicit: bool = False) -> Iterator[Path]:
            for child in children:
                if ignore.match_file(child):
                    continue

                if child.is_absolute():
                    relative = child.relative_to(root)
                    if ignore.match_file(relative):
                        continue

                if child.is_file() and (explicit or include.match_file(child)):
                    yield child

                elif child.is_dir():
                    yield from gen(child.iterdir())

        return gen([path], explicit=True)

    def run(self, paths: Iterable[Path], func: Callable[[Path], T]) -> Dict[Path, T]:
        """
        Run a given function once for each path, using an executor for concurrency.

        For each path given, `func` will be called with `path` as the only argument.
        To pass any other positional or keyword arguments, use `functools.partial`.

        Results from each path will be returned as a dictionary mapping path to result.
        """
        paths = list(paths)

        with self.executor_factory() as exe:
            results = list(exe.map(func, paths))

        return dict(zip(paths, results))

    def run_iter(
        self, paths: Iterable[Path], func: Callable[[Path], T]
    ) -> Generator[Tuple[Path, T], None, None]:
        """
        Run a given function once for each path, using an executor for concurrency.

        For each path given, `func` will be called with `path` as the only argument.
        To pass any other positional or keyword arguments, use `functools.partial`.

        Each path, and the function result, will be yielded as they are completed.
        """
        with self.executor_factory() as exe:
            futures = {exe.submit(func, path): path for path in paths}
            for future in as_completed(futures):
                path = futures[future]
                value = future.result()
                yield path, value

    def walk_and_run(
        self,
        paths: Iterable[Path],
        func: Callable[[Path], T],
        *,
        excludes: Excludes = None,
    ) -> Dict[Path, T]:
        """
        Walks each path given, and runs the given function on all gathered paths.

        See :meth:`Trailrunner.walk` for details on how paths are gathered, and
        :meth:`Trailrunner.run` for how functions are run for each gathered path.
        """
        all_paths: List[Path] = []
        for path in paths:
            all_paths.extend(self.walk(path, excludes=excludes))

        return self.run(all_paths, func)


# Maintain basic API with a default TrailRunner instance


def walk(path: Path, *, excludes: Excludes = None) -> Iterator[Path]:
    """
    Generate all significant file paths, starting from the given path.

    Finds the project root and any associated gitignore. Filters any paths that match
    a gitignore pattern. Recurses into subdirectories, and otherwise only includes
    files that match the :attr:`trailrunner.core.INCLUDE_PATTERN` regex.

    Optional `excludes` parameter allows supplying an extra set of paths (or
    gitignore-style patterns) to exclude from the final results.

    Returns a generator that yields each significant file as the tree is walked.
    """
    return Trailrunner().walk(path, excludes=excludes)


def run(paths: Iterable[Path], func: Callable[[Path], T]) -> Dict[Path, T]:
    """
    Run a given function once for each path, using a process pool for concurrency.

    For each path given, `func` will be called with `path` as the only argument.
    To pass any other positional or keyword arguments, use `functools.partial`.

    Results from each path will be returned as a dictionary mapping path to result.

    Uses a process pool with "spawned" processes that share no state with the parent
    process, to enforce consistent behavior on Linux, macOS, and Windows, where forked
    processes are not possible.
    """
    return Trailrunner().run(paths, func)


def run_iter(
    paths: Iterable[Path], func: Callable[[Path], T]
) -> Generator[Tuple[Path, T], None, None]:
    """
    Run a given function once for each path, using a process pool for concurrency.

    For each path given, `func` will be called with `path` as the only argument.
    To pass any other positional or keyword arguments, use `functools.partial`.

    Each path, and the function result, will be yielded as they are completed.

    Uses a process pool with "spawned" processes that share no state with the parent
    process, to enforce consistent behavior on Linux, macOS, and Windows, where forked
    processes are not possible.
    """
    return Trailrunner().run_iter(paths, func)


def walk_and_run(
    paths: Iterable[Path], func: Callable[[Path], T], *, excludes: Excludes = None
) -> Dict[Path, T]:
    """
    Walks each path given, and runs the given function on all gathered paths.

    See :func:`walk` for details on how paths are gathered, and :func:`run` for how
    functions are run for each gathered path.
    """
    return Trailrunner().walk_and_run(paths, func, excludes=excludes)
