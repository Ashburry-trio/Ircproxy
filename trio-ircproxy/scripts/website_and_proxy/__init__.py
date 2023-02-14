#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from os import path
from .system_data import SystemData
_dir = path.dirname(path.abspath(__file__))
sys.path.insert(0, _dir)
Settings_ini = SystemData.Settings_ini

