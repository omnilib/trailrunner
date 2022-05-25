# Copyright 2021 John Reese
# Licensed under the MIT license

import multiprocessing
import os
from concurrent.futures.thread import ThreadPoolExecutor
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Generator, Iterator
from unittest import TestCase
from unittest.mock import patch

from pathspec import PathSpec
from pathspec.patterns.gitwildmatch import GitWildMatchPattern

from trailrunner import core
from ..compat import ProcessPoolExecutor


@contextmanager
def cd(path: Path) -> Iterator[None]:
    try:
        cwd = Path.cwd()
        os.chdir(path)
        yield
    finally:
        os.chdir(cwd)


def getpid(path: Path) -> int:
    return os.getpid()


@patch.object(core.Trailrunner, "DEFAULT_EXECUTOR", ThreadPoolExecutor)
class CoreTest(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.temp_dir = TemporaryDirectory()
        self.td = Path(self.temp_dir.name).resolve()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_executor(self) -> None:
        def spawn_factory() -> ProcessPoolExecutor:
            return ProcessPoolExecutor(mp_context=multiprocessing.get_context("spawn"))

        parent = os.getpid()
        inputs = [Path()]
        expected = {
            Path(): parent,
        }

        with self.subTest("explicit thread pool"):
            result = core.Trailrunner(executor_factory=ThreadPoolExecutor).run(
                inputs, getpid
            )
            self.assertEqual(expected, result)

        with self.subTest("explicit spawn factory"):
            parent = os.getpid()
            results = core.Trailrunner(executor_factory=spawn_factory).run(
                inputs, getpid
            )
            self.assertNotEqual(expected, results)

        with self.subTest("patched thread pool"):
            result = core.Trailrunner().run(inputs, getpid)
            self.assertEqual(expected, result)

        with self.subTest("patched default is none"):
            with patch.object(core.Trailrunner, "DEFAULT_EXECUTOR", None):
                result = core.Trailrunner().run(inputs, getpid)
                self.assertNotEqual(expected, result)  # spawned process

                with self.subTest("deprecated EXECUTOR"):
                    with patch("trailrunner.core.EXECUTOR") as mock_exe:
                        core.Trailrunner().run(inputs, getpid)
                        mock_exe.assert_called_with()

    def test_project_root_empty(self) -> None:
        result = core.project_root(self.td)
        self.assertTrue(self.td.relative_to(result))

    def test_project_root_basic(self) -> None:
        (self.td / ".git").mkdir()
        (self.td / "foo.py").write_text("\n")
        (self.td / "frob").mkdir()
        (self.td / "frob" / "berry.py").write_text("\n")

        with self.subTest("root"):
            result = core.project_root(self.td)
            self.assertEqual(self.td, result)

        with self.subTest("root file"):
            result = core.project_root(self.td / "foo.py")
            self.assertEqual(self.td, result)

        with self.subTest("subdir"):
            result = core.project_root(self.td / "frob")
            self.assertEqual(self.td, result)

        with self.subTest("subdir file"):
            result = core.project_root(self.td / "frob/berry.py")
            self.assertEqual(self.td, result)

        with self.subTest("local root"):
            with cd(self.td):
                result = core.project_root(Path("frob"))
                self.assertEqual(self.td, result)

        with self.subTest("local subdir"):
            with cd(self.td / "frob"):
                result = core.project_root(Path("berry.py"))
                self.assertEqual(self.td, result)

    def test_project_root_multilevel(self) -> None:
        (self.td / ".hg").mkdir()
        inner = self.td / "foo" / "bar"
        inner.mkdir(parents=True)
        (inner / "pyproject.toml").write_text("\n")
        (inner / "fuzz").mkdir()
        (inner / "fuzz" / "ball.py").write_text("\n")

        with self.subTest("root"):
            result = core.project_root(self.td)
            self.assertEqual(self.td, result)

        with self.subTest("subdir"):
            result = core.project_root(self.td / "foo")
            self.assertEqual(self.td, result)

        with self.subTest("inner root"):
            result = core.project_root(inner)
            self.assertEqual(inner, result)

        with self.subTest("inner file"):
            result = core.project_root(inner / "fuzz" / "ball.py")
            self.assertEqual(inner, result)

    def test_gitignore(self) -> None:
        with self.subTest("no .gitignore"):
            result = core.gitignore(self.td)
            self.assertIsInstance(result, PathSpec)
            self.assertListEqual([], result.patterns)

        (self.td / "foo.py").write_text("\n")

        with self.subTest("path is file"):
            with self.assertRaisesRegex(ValueError, "path .+ not a directory"):
                core.gitignore(self.td / "foo.py")

        (self.td / ".gitignore").write_text("foo/\n*.c\n")

        with self.subTest("valid file"):
            result = core.gitignore(self.td)
            self.assertIsInstance(result, PathSpec)
            self.assertTrue(result.patterns)
            for pattern in result.patterns:
                self.assertIsInstance(pattern, GitWildMatchPattern)

    def test_walk(self) -> None:
        (self.td / ".git").mkdir()
        inner = self.td / "inner" / "subproject"
        inner.mkdir(parents=True)
        (inner / "pyproject.toml").write_text("\n")
        (inner / "requirements.txt").write_text("\n")
        (inner / "fuzz").mkdir()
        (inner / "fuzz" / "ball.py").write_text("\n")
        (inner / "fuzz" / "data.txt").write_text("\n")
        (self.td / "foo" / "bar").mkdir(parents=True)
        (self.td / "foo" / "a.py").write_text("\n")
        (self.td / "foo" / "bar" / "b.py").write_text("\n")
        (self.td / "foo" / "bar" / "c.pyi").write_text("\n")
        (self.td / "foo" / "d.cpp").write_text("\n")
        (self.td / "vendor" / "useful").mkdir(parents=True)
        (self.td / "vendor" / "useful" / "old.py").write_text("\n")

        with self.subTest("explicit txt files"):
            result = sorted(core.walk(inner / "requirements.txt"))
            expected = [inner / "requirements.txt"]
            self.assertListEqual(expected, result)

        with self.subTest("absolute root no gitignore"):
            result = sorted(core.walk(self.td))
            expected = [
                self.td / "foo" / "a.py",
                self.td / "foo" / "bar" / "b.py",
                self.td / "foo" / "bar" / "c.pyi",
                self.td / "inner" / "subproject" / "fuzz" / "ball.py",
                self.td / "vendor" / "useful" / "old.py",
            ]
            self.assertListEqual(expected, result)

        with self.subTest("absolute subdir no gitignore"):
            result = sorted(core.walk(self.td / "foo"))
            expected = [
                self.td / "foo" / "a.py",
                self.td / "foo" / "bar" / "b.py",
                self.td / "foo" / "bar" / "c.pyi",
            ]
            self.assertListEqual(expected, result)

        with self.subTest("absolute subdir no gitignore with excludes"):
            result = sorted(core.walk(self.td / "foo", excludes=["foo/bar/", "b.py"]))
            expected = [
                self.td / "foo" / "a.py",
            ]
            self.assertListEqual(expected, result)

        with self.subTest("local root no gitignore"):
            with cd(self.td):
                result = sorted(core.walk(Path(".")))
                expected = [
                    Path("foo") / "a.py",
                    Path("foo") / "bar" / "b.py",
                    Path("foo") / "bar" / "c.pyi",
                    Path("inner") / "subproject" / "fuzz" / "ball.py",
                    Path("vendor") / "useful" / "old.py",
                ]
                self.assertListEqual(expected, result)

        with self.subTest("local subdir no gitignore"):
            with cd(self.td):
                result = sorted(core.walk(Path("foo")))
                expected = [
                    Path("foo") / "a.py",
                    Path("foo") / "bar" / "b.py",
                    Path("foo") / "bar" / "c.pyi",
                ]
                self.assertListEqual(expected, result)

        with self.subTest("local subdir no gitignore with excludes"):
            with cd(self.td):
                result = sorted(core.walk(Path("foo"), excludes=["foo/bar/"]))
                expected = [
                    Path("foo") / "a.py",
                ]
                self.assertListEqual(expected, result)

        (self.td / ".gitignore").write_text("vendor/\n*.pyi")

        with self.subTest("absolute root with gitignore"):
            result = sorted(core.walk(self.td))
            expected = [
                self.td / "foo" / "a.py",
                self.td / "foo" / "bar" / "b.py",
                self.td / "inner" / "subproject" / "fuzz" / "ball.py",
            ]
            self.assertListEqual(expected, result)

        with self.subTest("absolute subdir with gitignore"):
            result = sorted(core.walk(self.td / "foo"))
            expected = [
                self.td / "foo" / "a.py",
                self.td / "foo" / "bar" / "b.py",
            ]
            self.assertListEqual(expected, result)

        with self.subTest("absolute subdir with gitignore and excludes"):
            result = sorted(core.walk(self.td / "foo", excludes=["a.py"]))
            expected = [
                self.td / "foo" / "bar" / "b.py",
            ]
            self.assertListEqual(expected, result)

        with self.subTest("local root with gitignore"):
            with cd(self.td):
                result = sorted(core.walk(Path(".")))
                expected = [
                    Path("foo") / "a.py",
                    Path("foo") / "bar" / "b.py",
                    Path("inner") / "subproject" / "fuzz" / "ball.py",
                ]
                self.assertListEqual(expected, result)

        with self.subTest("local subdir with gitignore"):
            with cd(self.td):
                result = sorted(core.walk(Path("foo")))
                expected = [
                    Path("foo") / "a.py",
                    Path("foo") / "bar" / "b.py",
                ]
                self.assertListEqual(expected, result)

        with self.subTest("inner project snubs gitignore"):
            with cd(inner):
                result = sorted(core.walk(Path(".")))
                expected = [
                    Path("fuzz") / "ball.py",
                ]
                self.assertListEqual(expected, result)

    def test_run(self) -> None:
        def get_posix(path: Path) -> str:
            return path.as_posix()

        paths = [
            Path("foo") / "bar" / "baz.py",
            Path("bingo.py"),
            Path("/frob/glob.pyi"),
        ]
        expected = {p: p.as_posix() for p in paths}
        result = core.run(paths, get_posix)
        self.assertDictEqual(expected, result)

    def test_run_iter(self) -> None:
        def get_posix(path: Path) -> str:
            return path.as_posix()

        paths = [
            Path("foo") / "bar" / "baz.py",
            Path("bingo.py"),
            Path("/frob/glob.pyi"),
        ]
        expected = {p: p.as_posix() for p in paths}

        gen = core.run_iter(paths, get_posix)
        self.assertIsInstance(gen, Generator)

        result = {}
        for path, value in gen:
            self.assertIn(path, paths)
            result[path] = value

        self.assertDictEqual(expected, result)

    def test_walk_then_run(self) -> None:
        (self.td / "pyproject.toml").write_text("\n")
        (self.td / "foo").mkdir()
        (self.td / "foo" / "foo.py").write_text("\n")
        (self.td / "foo" / "bar.py").write_text("\n")
        (self.td / "foo" / "car.py").write_text("\n")
        (self.td / "foo" / "car.pyi").write_text("\n")
        (self.td / "foo" / "data.dat").write_text("\n")
        (self.td / "vendor").mkdir()
        (self.td / "vendor" / "something.py").write_text("\n")
        (self.td / "vendor" / "everything.py").write_text("\n")

        def say_hello(path: Path) -> str:
            return f"hello {path}"

        with self.subTest("local root no gitignore"):
            with cd(self.td):
                result = sorted(core.walk_and_run([Path(".")], say_hello).keys())
                expected = [
                    Path("foo") / "bar.py",
                    Path("foo") / "car.py",
                    Path("foo") / "car.pyi",
                    Path("foo") / "foo.py",
                    Path("vendor") / "everything.py",
                    Path("vendor") / "something.py",
                ]
                self.assertListEqual(expected, result)

        with self.subTest("local subdir no gitignore"):
            with cd(self.td):
                result = sorted(core.walk_and_run([Path("foo")], say_hello).keys())
                expected = [
                    Path("foo") / "bar.py",
                    Path("foo") / "car.py",
                    Path("foo") / "car.pyi",
                    Path("foo") / "foo.py",
                ]
                self.assertListEqual(expected, result)

        (self.td / ".gitignore").write_text("**/foo.py\nvendor/\n")

        with self.subTest("local root with gitignore"):
            with cd(self.td):
                result = sorted(core.walk_and_run([Path(".")], say_hello).keys())
                expected = [
                    Path("foo") / "bar.py",
                    Path("foo") / "car.py",
                    Path("foo") / "car.pyi",
                ]
                self.assertListEqual(expected, result)

        with self.subTest("local subdir with gitignore"):
            with cd(self.td):
                result = sorted(core.walk_and_run([Path("foo")], say_hello).keys())
                expected = [
                    Path("foo") / "bar.py",
                    Path("foo") / "car.py",
                    Path("foo") / "car.pyi",
                ]
                self.assertListEqual(expected, result)
