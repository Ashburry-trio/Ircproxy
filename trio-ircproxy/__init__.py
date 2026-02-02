#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from os import path

from .version import VERSION_NUM, __version__

_dir = path.dirname(path.abspath(__file__))
sys.path.insert(0, _dir)
__all__ = ["__version__", "VERSION_NUM"]
