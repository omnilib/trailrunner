trailrunner
===========

v1.2.1
------

Bugfix release

- Fix: ignore file paths that don't exist, even if explicitly given

```
$ git shortlog -s v1.2.0...v1.2.1
     2	John Reese
```


v1.2.0
------

Feature release

- New: `run_iter()` variant that yields results as they complete (#52)
- Fix: `walk()` includes explicitly listed files, even if they don't match include pattern (#51)

```
$ git shortlog -s v1.1.3...v1.2.0
     7	John Reese
     6	dependabot[bot]
```


v1.1.3
------

Bugfix release

- Export `__all__` from trailrunner to satisfy strict type checkers (#40)

```
$ git shortlog -s v1.1.2...v1.1.3
     3	John Reese
     3	dependabot[bot]
```


v1.1.2
------

Maintenance release

- Added PEP 561 `py.typed` markers
- Tested on Python 3.10

```
$ git shortlog -s v1.1.1...v1.1.2
     9	John Reese
    29	dependabot[bot]
```


v1.1.1
------

Compatibility update:

- Support Python 3.6 again using futures3 module (#2)

```
$ git shortlog -s v1.1.0...v1.1.1
     3	John Reese
     1	Tim Hatch
```


v1.1.0
------

Feature release:

- New, class-based API with simple wrappers
- Added support for passing extras "excludes" when walking paths
- Excludes and gitignores are matched against root-relative paths as well
- Dropped support for Python 3.6, for consistency in multiprocessing

```
$ git shortlog -s v1.1.0b1...v1.1.0
     9	John Reese
```


v1.1.0b1
--------

Release Candidate

* Refactor into a Trailrunner class with simple wrappers
* Existing walk/run functions just chain to the new class instance
* Documented the new class and behaviors
* Improved documentation on utilities functions and global values
* Considering if 3.6 support should stay for the final release

```
$ git shortlog -s v1.0.0...v1.1.0b1
     8	John Reese
```


v1.0.0
------

Initial release

* `walk()`, `run()`, `walk_and_run()`
* That's pretty much it

```
$ git shortlog -s v1.0.0
     9	John Reese
```

