#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: http://cloudedbats.org
# Copyright (c) 2018 Arnold Andreasson 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

from cloudedbats_app import app_framework

class NewActivity(app_framework.ActivityBase):
    """ """

    def __init__(self, name, parentwidget):
        """ """
        self._last_used_dir_path = None
        # Initialize parent. Should be called after other 
        # initialization since the base class calls _create_content().
        super(NewActivity, self).__init__(name, parentwidget)
    
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
        contentLayout.addWidget(self._content_tabs())
    
    def _content_tabs(self):
        """ """
        # Active widgets and connections.
        selectdatabox = QtWidgets.QGroupBox('', self)
        tabWidget = QtWidgets.QTabWidget()
        tabWidget.addTab(self._content_new(), 'New')
        tabWidget.addTab(self._content_more(), '(More)')
        tabWidget.addTab(self._content_help(), '(Help)')
        # Layout widgets.
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(tabWidget)
        selectdatabox.setLayout(layout)        
        #
        return selectdatabox
    
    # === New ===
    def _content_new(self):
        """ """
        widget = QtWidgets.QWidget()
        #
        
        # Layout widgets.
        form1 = QtWidgets.QGridLayout()
        gridrow = 0
        label = QtWidgets.QLabel('Work in progress...')
        form1.addWidget(label, gridrow, 0, 1, 1)
        #
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(form1)
        layout.addStretch(25)
        widget.setLayout(layout)
        #
        return widget
    
    # === More ===
    def _content_more(self):
        """ """
        widget = QtWidgets.QWidget()
        #
        return widget
 
    # === Help ===
    def _content_help(self):
        """ """
        widget = QtWidgets.QWidget()
        #
        # Active widgets and connections.
        label = app_framework.RichTextQLabel()
        label.setText(self.get_help_text())
        # Layout.
        layout = QtWidgets.QGridLayout()
        gridrow = 0
        layout.addWidget( QtWidgets.QLabel(''), gridrow, 0, 1, 1) # Add space to the left.
        layout.addWidget(label, gridrow, 1, 1, 20)
        gridrow += 1
        layout.addWidget(QtWidgets.QLabel(''), gridrow, 1, 1, 20)
        #
        widget.setLayout(layout)                
        #
        return widget
 
    def get_help_text(self):
        """ """
        return """
        <p>&nbsp;</p>
        <h3>New</h3>
        <p>
        Work in progress...
        </p>
        
        """

