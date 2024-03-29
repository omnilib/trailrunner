trailrunner
===========

[![Generated by attribution][attribution-badge]][attribution-url]


v1.4.0
------

Bugfix release

- Always resolve and exclude paths relative to project root (#83).
  This is change to how paths are walked and excluded, that will
  result in a closer match to how git would exclude files, and will
  also prevent excluding files based on path segments outside of the
  project root.
- New: debug CLI available via `python -m trailrunner` to validate
  behavior directly within active project directories. (#83)

```text
$ git shortlog -s v1.3.0...v1.4.0
     3	Amethyst Reese
```


v1.3.0
------

Feature release

- New: added `concurrency` parameter to Trailrunner class (#81)
- Fix: type annotations for pathspec package
- Dropped support for Python 3.6

```text
$ git shortlog -s v1.2.1...v1.3.0
    16	Amethyst Reese
     7	dependabot[bot]
```


v1.2.1
------

Bugfix release

- Fix: ignore file paths that don't exist, even if explicitly given

```text
$ git shortlog -s v1.2.0...v1.2.1
     2	Amethyst Reese
```


v1.2.0
------

Feature release

- New: `run_iter()` variant that yields results as they complete (#52)
- Fix: `walk()` includes explicitly listed files, even if they don't match include pattern (#51)

```text
$ git shortlog -s v1.1.3...v1.2.0
     7	Amethyst Reese
     6	dependabot[bot]
```


v1.1.3
------

Bugfix release

- Export `__all__` from trailrunner to satisfy strict type checkers (#40)

```text
$ git shortlog -s v1.1.2...v1.1.3
     3	Amethyst Reese
     3	dependabot[bot]
```


v1.1.2
------

Maintenance release

- Added PEP 561 `py.typed` markers
- Tested on Python 3.10

```text
$ git shortlog -s v1.1.1...v1.1.2
     9	Amethyst Reese
    29	dependabot[bot]
```


v1.1.1
------

Compatibility update:

- Support Python 3.6 again using futures3 module (#2)

```text
$ git shortlog -s v1.1.0...v1.1.1
     3	Amethyst Reese
     1	Tim Hatch
```


v1.1.0
------

Feature release:

- New, class-based API with simple wrappers
- Added support for passing extras "excludes" when walking paths
- Excludes and gitignores are matched against root-relative paths as well
- Dropped support for Python 3.6, for consistency in multiprocessing

```text
$ git shortlog -s v1.1.0b1...v1.1.0
     9	Amethyst Reese
```


v1.1.0b1
--------

Release Candidate

* Refactor into a Trailrunner class with simple wrappers
* Existing walk/run functions just chain to the new class instance
* Documented the new class and behaviors
* Improved documentation on utilities functions and global values
* Considering if 3.6 support should stay for the final release

```text
$ git shortlog -s v1.0.0...v1.1.0b1
     8	Amethyst Reese
```


v1.0.0
------

Initial release

* `walk()`, `run()`, `walk_and_run()`
* That's pretty much it

```text
$ git shortlog -s v1.0.0
     9	Amethyst Reese
```

[attribution-badge]:
    https://img.shields.io/badge/generated%20by-attribution-informational
[attribution-url]: https://attribution.omnilib.dev
