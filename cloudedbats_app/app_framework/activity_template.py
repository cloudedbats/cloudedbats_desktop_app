#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: http://cloudedbats.org
# Copyright (c) 2018 Arnold Andreasson 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

from PyQt5 import QtWidgets

from cloudedbats_app import app_utils
from cloudedbats_app import app_framework

class TemplateActivity(app_framework.ActivityBase):
    """
    Template class for new activities.
    """
    def __init__(self, name, parentwidget):
        """ """
        # Initialize parent. Should be called after other 
        # initialization since the base class calls _create_content().
        super(TemplateActivity, self).__init__(name, parentwidget)

    def _create_content(self):
        """ """
        content = self._create_scrollable_content()
        contentLayout = QtWidgets.QVBoxLayout()
        content.setLayout(contentLayout)
        # Add activity name at top.
        self._activityheader = app_framework.HeaderQLabel()
        self._activityheader.setText('<h2>' + self.objectName() + '</h2>')
        contentLayout.addWidget(self._activityheader)
        # Add content to the activity.
        contentLayout.addLayout(self._content_person_info())
        contentLayout.addLayout(self._content_buttons())
        contentLayout.addStretch(5)

    def _content_person_info(self):
        """ """
        # Active widgets and connections.
        self._nameedit = QtWidgets.QLineEdit('<Name>')
        self._emailedit = QtWidgets.QLineEdit('<Email>')
        self._customerlist = QtWidgets.QListWidget()
        # Layout.
        layout = QtWidgets.QFormLayout()
        layout.addRow('&Name:', self._nameedit)
        layout.addRow('&Mail:', self._emailedit)
        layout.addRow('&Projects:', self._customerlist)
        # Test data.
        self._customerlist.addItem('<First project.>')
        self._customerlist.addItem('<Second project.>')
        #
        return layout

    def _content_buttons(self):
        """ """
        # Active widgets and connections.
        self._testbutton = QtWidgets.QPushButton('Write info to log')
        self._testbutton.clicked.connect(self._test)                
        # Layout.
        layout = QtWidgets.QHBoxLayout()
        layout.addStretch(5)
        layout.addWidget(self._testbutton)
        #
        return layout

    def _test(self):
        """ """
        app_utils.Logging().log('Name: ' + str(self._nameedit.text()))
        app_utils.Logging().log('E-mail: ' + str(self._emailedit.text()))
        