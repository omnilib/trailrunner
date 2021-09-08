trailrunner
===========

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

