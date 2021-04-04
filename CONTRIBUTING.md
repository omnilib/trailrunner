# Contributing to trailrunner

## Preparation

You'll need to have Python 3.6 or newer available for testing.
I recommend using [pyenv][] for this:

    $ pyenv install 3.9.4
    $ pyenv shell 3.9.4


## Setup

Create a fresh development enviroment, and install the
appropriate tools and dependencies:

    $ cd <path/to/trailrunner>
    $ make venv
    $ source .venv/bin/activate


## Submitting

Before submitting a pull request, please ensure
that you have done the following:

* Documented changes or features in README.md
* Added appropriate license headers to new files
* Written or modified tests for new functionality
* Used `make format` to format code appropriately
* Validated and tested code with `make lint test`

[pyenv]: https://github.com/pyenv/pyenv
