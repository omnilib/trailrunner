# trailrunner

Walk paths and run things

[![version](https://img.shields.io/pypi/v/trailrunner.svg)](https://pypi.org/project/trailrunner)
[![documentation](https://readthedocs.org/projects/trailrunner/badge/?version=latest)](https://trailrunner.omnilib.dev)
[![changelog](https://img.shields.io/badge/change-log-blue)](https://trailrunner.omnilib.dev/en/latest/changelog.html)
[![license](https://img.shields.io/pypi/l/trailrunner.svg)](https://github.com/omnilib/trailrunner/blob/master/LICENSE)
[![build status](https://github.com/omnilib/trailrunner/workflows/Build/badge.svg?branch=main)](https://github.com/omnilib/trailrunner/actions)
[![code coverage](https://img.shields.io/codecov/c/gh/omnilib/trailrunner)](https://codecov.io/gh/omnilib/trailrunner)

trailrunner is a simple library for walking paths on the filesystem, and executing
functions for each file found. trailrunner obeys project level `.gitignore` files,
and runs functions on a process pool for increased performance. trailrunner is designed
for use by linting, formatting, and other developer tools that need to find and operate
on all files in project in a predictable fashion with a minimal API:

`walk()` takes a single `Path`, and generates a list of significant files in that tree:

```pycon
>>> from trailrunner import walk
>>> sorted(walk(Path("trailrunner")))
[
    PosixPath('trailrunner/__init__.py'),
    PosixPath('trailrunner/__version__.py'),
    PosixPath('trailrunner/core.py'),
    PosixPath('trailrunner/tests/__init__.py'),
    PosixPath('trailrunner/tests/__main__.py'),
    PosixPath('trailrunner/tests/core.py'),
]
```

`run()` takes a list of `Path` objects and a function, and runs that function once
for each path given. It runs these functions on a process pool, and returns a mapping
of paths to results:

```pycon
>>> from trailrunner import run
>>> paths = [Path('trailrunner/core.py'), Path('trailrunner/tests/core.py')]
>>> run(paths, str)
{
    PosixPath('trailrunner/core.py'): 'trailrunner/core.py',
    PosixPath('trailrunner/tests/core.py'): 'trailrunner/tests/core.py',
}
```

`walk_and_run()` does exactly what you would expect:

```pycon
>>> from trailrunner import walk_and_run
>>> walk_and_run([Path('trailrunner/tests')], str)
{
    PosixPath('trailrunner/tests/__init__.py'): 'trailrunner/tests/__init__.py',
    PosixPath('trailrunner/tests/__main__.py'): 'trailrunner/tests/__main__.py',
    PosixPath('trailrunner/tests/core.py'): 'trailrunner/tests/core.py',
}
```


Install
-------

trailrunner requires Python 3.6 or newer. You can install it from PyPI:

```shell-session
$ pip install trailrunner
```


License
-------

trailrunner is copyright [John Reese](https://jreese.sh), and licensed under
the MIT license.  I am providing code in this repository to you under an open
source license.  This is my personal repository; the license you receive to
my code is from me and not from my employer. See the `LICENSE` file for details.
