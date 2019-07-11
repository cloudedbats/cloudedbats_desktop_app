#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: http://cloudedbats.org
# Copyright (c) 2018 Arnold Andreasson 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

# Version for "Cloudedbats - desktop application".
# Format: <year>.<month>.<day>, example: '2019.01.01' 
# import time
# year_month_day = time.strftime("%Y.%m.%d")
year_month_day = '2019.07.11'
__version__ = year_month_day

# import os
# os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
# from PyQt5 import QtCore
# QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)

# Matplotlib for PyQt5. 
# Backend must be defined before other matplotlib imports.
import matplotlib
matplotlib.use('Qt5agg')

# CloudedBats desktop application framework.
from cloudedbats_app import app_framework

if __name__ == "__main__":

    app_framework.set_version(__version__)
    app_framework.desktop_application()
