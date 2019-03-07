#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: http://cloudedbats.org
# Copyright (c) 2018 Arnold Andreasson 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import time
from PyQt5 import QtWidgets
from PyQt5 import QtCore

from cloudedbats_app import app_framework
from cloudedbats_app import app_core

class MetadataTool(app_framework.ToolBase):
    """ Metadata tool. """
    
    def __init__(self, name, parentwidget):
        """ """
        self.spectrogram_thread = None
        self.spectrogram_thread_active = False
        # Initialize parent. Should be called after other 
        # initialization since the base class calls _create_content().
        super().__init__(name, parentwidget)
        #
        # Where is the tool allowed to dock in the main window.
        self.setAllowedAreas(QtCore.Qt.RightDockWidgetArea | 
                             QtCore.Qt.BottomDockWidgetArea)
        self.setBaseSize(600,600)        
        # Default position. Hide as default.
        self._parent.addDockWidget(QtCore.Qt.RightDockWidgetArea, self)
        self.hide()
        # Use sync object for workspaces and surveys. 
        app_core.DesktopAppSync().item_id_changed_signal.connect(self.update_metadata)
        self.update_metadata()

    def _create_content(self):
        """ """
        content = self._create_scrollable_content()
        layout = QtWidgets.QVBoxLayout()
        # Add tabs.
        tabWidget = QtWidgets.QTabWidget()
        tabWidget.addTab(self._content_meatadata(), 'Metadata')
        tabWidget.addTab(self._content_edit_meatadata(), 'Edit metadata')
        tabWidget.addTab(self._content_help(), 'Help')
        # 
        layout.addWidget(tabWidget)
        content.setLayout(layout)
    
    def _content_meatadata(self):
        """ """
        widget = QtWidgets.QWidget()

        # Workspace and survey..
        self.survey_label = QtWidgets.QLabel('Survey: -')
        self.itemid_label = QtWidgets.QLabel('Item id: -')
        self.title_label = QtWidgets.QLabel('Title: -')
        self.metadata_list = QtWidgets.QListWidget()
        
        # Layout widgets.
        form1 = QtWidgets.QGridLayout()
        gridrow = 0
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.survey_label)
        hlayout.addStretch(5)
        form1.addLayout(hlayout, gridrow, 0, 1, 10)
        gridrow += 1
        form1.addWidget(self.itemid_label, gridrow, 0, 1, 10)
        gridrow += 1
        form1.addWidget(QtWidgets.QLabel(''), gridrow, 0, 1, 10)
        gridrow += 1
        form1.addWidget(self.title_label, gridrow, 0, 1, 10)
#         gridrow += 1
#         form1.addWidget(QtWidgets.QLabel(''), gridrow, 0, 1, 10)
        gridrow += 1
        form1.addWidget(self.metadata_list, gridrow, 0, 100, 10)
        #
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(form1)
        widget.setLayout(layout)
        #
        return widget
        
    def _content_edit_meatadata(self):
        """ """
        widget = QtWidgets.QWidget()
        #
        self.todo_label = QtWidgets.QLabel('<b>TODO...</b>')
        
        # Layout widgets.
        form1 = QtWidgets.QGridLayout()
        gridrow = 0
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.todo_label)
        hlayout.addStretch(10)
        form1.addLayout(hlayout, gridrow, 0, 1, 10)
        #
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(form1)
        layout.addStretch(100)
        widget.setLayout(layout)
        #
        return widget
        
    def update_metadata(self):
        """ """
        workspace = app_core.DesktopAppSync().get_workspace()
        survey = app_core.DesktopAppSync().get_selected_survey()
        item_id = app_core.DesktopAppSync().get_selected_item_id()
        metadata_dict = app_core.DesktopAppSync().get_metadata_dict()
        #
        self.metadata_list.clear()
        if not item_id:
            self.survey_label.setText('Survey: -')
            self.itemid_label.setText('Item id: -')
            return
        #
        self.survey_label.setText('Survey: <b>' + survey + '</b>')
        self.itemid_label.setText('Item id: <b>' + item_id + '</b>')
        self.title_label.setText('Title: <b>' + metadata_dict.get('item_title', '') + '</b>')
        #
        for key in sorted(metadata_dict):
            text = key + ': ' + ' ' * (15 - len(key)) + '\t' + str(metadata_dict.get(key, ''))
            self.metadata_list.addItem(text)
        #
        return
        
    
    # === Help ===
    def _content_help(self):
        """ """
        widget = QtWidgets.QWidget()
        #
        # Active widgets and connections.
        label = app_framework.RichTextQLabel()
#         label.setText(self.get_help_text())
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

