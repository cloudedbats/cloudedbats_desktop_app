#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: http://cloudedbats.org
# Copyright (c) 2018 Arnold Andreasson 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import sys
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5 import QtCore

import hdf54bats
from cloudedbats_app import app_framework
from cloudedbats_app import app_utils
from cloudedbats_app import app_core

class ScannerActivity(app_framework.ActivityBase):
    """ Used for scanning wavwfiles. """

    def __init__(self, name, parentwidget):
        """ """
        self._last_used_dir_path = None
        # Initialize parent. Should be called after other 
        # initialization since the base class calls _create_content().
        super(ScannerActivity, self).__init__(name, parentwidget)
        #
        self._load_item_data()
        # Use sync object for workspaces and surveys. 
#         app_core.DesktopAppSync().workspace_changed_signal.connect(self._load_item_data)
        app_core.DesktopAppSync().survey_changed_signal.connect(self._load_item_data)
    
    def _create_content(self):
        """ """
        content = self._create_scrollable_content()
        layout = QtWidgets.QVBoxLayout()
        # Add activity name at top.
        self._activityheader = app_framework.HeaderQLabel()
        self._activityheader.setText('<h2>' + self.objectName() + '</h2>')
        layout.addWidget(self._activityheader)
        # Add tabs.
        tabWidget = QtWidgets.QTabWidget()
        tabWidget.addTab(self._content_scanner(), 'Scanner')
        tabWidget.addTab(self._content_more(), '(More)')
        tabWidget.addTab(self._content_help(), '(Help)')
        # 
        layout.addWidget(tabWidget)
        content.setLayout(layout)
    
    # === Scanner ===
    def _content_scanner(self):
        """ """
        widget = QtWidgets.QWidget()
        # List.
        items_listview = QtWidgets.QListView()
        self._items_model = QtGui.QStandardItemModel()
        items_listview.setModel(self._items_model)
        # Select in list.
        clearall_button = app_framework.ClickableQLabel('Clear all')
        clearall_button.label_clicked.connect(self._uncheck_all_items)
        markall_button = app_framework.ClickableQLabel('Mark all')
        markall_button.label_clicked.connect(self._check_all_items)
        # Frequencies.
        self.lowfreqfilter_edit = QtWidgets.QDoubleSpinBox()
        self.lowfreqfilter_edit.setRange(0.0, 250.0)
        self.lowfreqfilter_edit.setValue(15.0)
        self.highfreqfilter_edit = QtWidgets.QDoubleSpinBox()
        self.highfreqfilter_edit.setRange(0.0, 250.0)
        self.highfreqfilter_edit.setValue(250.0)
        self.usehighlimit_checkbox = QtWidgets.QCheckBox('Use high limit')
        self.usehighlimit_checkbox.setChecked(False)
        self.usehighlimit_checkbox.stateChanged.connect(self.enable_high_limit)
        self.highfreqfilter_edit.setEnabled(False)
        # Run.
        self.scanfiles_button = QtWidgets.QPushButton("Scan files")
        self.scanfiles_button.clicked.connect(self.scan_files)
        
        # Layout widgets.
        hbox1 = QtWidgets.QHBoxLayout()
        hbox1.addWidget(clearall_button)
        hbox1.addWidget(markall_button)
        hbox1.addStretch(10)
        #
        hbox2 = QtWidgets.QHBoxLayout()
        hbox2.addWidget(QtWidgets.QLabel('Frequency limits. Low (kHz): '))
        hbox2.addWidget(self.lowfreqfilter_edit)
        hbox2.addWidget(QtWidgets.QLabel('High (kHz):'))
        hbox2.addWidget(self.highfreqfilter_edit)
        hbox2.addWidget(self.usehighlimit_checkbox)
        hbox2.addStretch(10)
        
        hbox3 = QtWidgets.QHBoxLayout()
        hbox3.addWidget(self.scanfiles_button)
        hbox3.addStretch(10)
        #
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(items_listview, 10)
        layout.addLayout(hbox1)
        layout.addLayout(hbox2)
        layout.addLayout(hbox3)
        #
        widget.setLayout(layout)
        #
        return widget
    
    def _load_item_data(self):
        """ """
        self.dir_path = app_core.DesktopAppSync().get_workspace()
        self.survey_name = app_core.DesktopAppSync().get_selected_survey()
        #
        try:
            self._items_model.clear()
            wavefiles = hdf54bats.Hdf5Wavefiles(self.dir_path, self.survey_name)
            from_top_node = ''
            nodes = wavefiles.get_child_nodes(from_top_node)
            for node_key in sorted(nodes):
                node_dict = nodes.get(node_key, {})
                node_item_id = node_dict.get('item_id', '')
                node_item_type = node_dict.get('item_type', '')
                if node_item_type == 'wavefile':
                    item = QtGui.QStandardItem(node_item_id)
                    item.setCheckState(QtCore.Qt.Unchecked)
                    item.setCheckable(True)
                    self._items_model.appendRow(item)
        except Exception as e:
            debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
            app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))
    
    def _check_all_items(self):
        """ """
        try:        
            for rowindex in range(self._items_model.rowCount()):
                item = self._items_model.item(rowindex, 0)
                item.setCheckState(QtCore.Qt.Checked)
        #
        except Exception as e:
            debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
            app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))
            
    def _uncheck_all_items(self):
        """ """
        try:        
            for rowindex in range(self._items_model.rowCount()):
                item = self._items_model.item(rowindex, 0)
                item.setCheckState(QtCore.Qt.Unchecked)
        #
        except Exception as e:
            debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
            app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))
    
    def enable_high_limit(self):
        """ """
        check_state = self.usehighlimit_checkbox.checkState()
        if check_state:
            self.highfreqfilter_edit.setEnabled(True)
        else:
            self.highfreqfilter_edit.setEnabled(False)
    
    def scan_files(self):
        """ """
        try:
            params = {}
            params['low_frequency_hz'] = float(self.lowfreqfilter_edit.text()) * 1000.0
            if self.usehighlimit_checkbox.isChecked():
                params['high_frequency_hz'] = float(self.highfreqfilter_edit.text()) * 1000.0
            #
            item_id_list = []
            for rowindex in range(self._items_model.rowCount()):
                item = self._items_model.item(rowindex, 0)
                if item.checkState() == QtCore.Qt.Checked:
                    item_id_list.append(str(item.text()))
            params['item_id_list'] = item_id_list
            #
            scanner = app_core.WaveFileScanner()
            scanner.scan_files_in_thread(params)
        #
        except Exception as e:
            debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
            app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))
    
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
        <h3>Scanner</h3>
        <p>
        Work in progress...
        </p>
        
        """

