# Copyright 2021 John Reese
# Licensed under the MIT license

import unittest
from concurrent.futures import ThreadPoolExecutor

import trailrunner.core

if __name__ == "__main__":  # pragma: no cover
    trailrunner.core.EXECUTOR = ThreadPoolExecutor
    unittest.main(module="trailrunner.tests", verbosity=2)
