#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: http://cloudedbats.org
# Copyright (c) 2018 Arnold Andreasson 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

# Version for "Cloudedbats - desktop application".
# Format: <year>.<month>.<bugfix>, example: '2018.02.0' 
import time
year_month = time.strftime("%Y.%m.")
bugfix = 0
__version__ = year_month + str(bugfix)

# Matplotlib for PyQt5. 
# Backend must be defined before other matplotlib imports.
import matplotlib
matplotlib.use('Qt5agg')

# CloudedBats desktop application framework.
import app_framework

# Set up python path to other cloudedbats libs.
import sys
sys.path.append('../../cloudedbats_dsp')

if __name__ == "__main__":
    app_framework.set_version(__version__)
    app_framework.desktop_application()
