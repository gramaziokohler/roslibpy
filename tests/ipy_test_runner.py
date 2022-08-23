# Installation:
#
#   $ ipy -X:Frames -m ensurepip
#   $ ipy -X:Frames -m pip install ironpython-pytest
#
# Usage:
#   $ ipy tests/ipy_test_runner.py

from __future__ import print_function

import os

import pytest

HERE = os.path.dirname(__file__)

if __name__ == "__main__":
    pytest.run(HERE)
