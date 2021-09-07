# Copyright 2021 John Reese
# Licensed under the MIT license

import sys
import typing

if sys.version_info < (3, 7):  # pragma: no cover
    if typing.TYPE_CHECKING:
        # futures3 does not have stubs
        from concurrent.futures import Executor

        class ProcessPoolExecutor(Executor):
            def __init__(self, **kwargs: typing.Any) -> None:
                pass

    else:
        from futures3.process import ProcessPoolExecutor
else:  # pragma: no cover
    from concurrent.futures import ProcessPoolExecutor

__all__ = ["ProcessPoolExecutor"]
