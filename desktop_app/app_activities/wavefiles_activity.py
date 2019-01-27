#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: http://cloudedbats.org
# Copyright (c) 2018 Arnold Andreasson 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import pandas
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

import hdf54bats
import metadata4bats
from desktop_app import app_framework

class WavefilesActivity(app_framework.ActivityBase):
    """ """

    def __init__(self, name, parentwidget):
        """ """
        self._last_used_dir_path = None
        # Initialize parent. Should be called after other 
        # initialization since the base class calls _create_content().
        super().__init__(name, parentwidget)
        
        # Initiate data.
        self.refresh_survey_list()
    
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
        tabWidget.addTab(self._content_wavefiles(), 'Wavefiles')
        tabWidget.addTab(self._content_adv_filter(), 'Advanced filter')
        tabWidget.addTab(self._content_help(), 'Help')
        # 
        layout.addWidget(tabWidget)
        content.setLayout(layout)
    
    # === Workspaces ===
    def _content_wavefiles(self):
        """ """
        widget = QtWidgets.QWidget()
        # Workspace and survey..
        self.workspacedir_edit = QtWidgets.QLineEdit('workspace_1')
        self.workspacedir_edit.textChanged.connect(self.refresh_survey_list)
        self.survey_combo = QtWidgets.QComboBox()
        self.survey_combo.setEditable(False)
        self.survey_combo.setMinimumWidth(250)
#         self.survey_combo.setMaximumWidth(300)
        self.survey_combo.addItems(['<select survey>'])
        self.survey_combo.currentIndexChanged.connect(self.refresh_event_list)
#         self.survey_combo.setMaximumWidth(300)
        self.detector_combo = QtWidgets.QComboBox()
        self.detector_combo.setEditable(False)
        self.detector_combo.setMinimumWidth(250)
        self.detector_combo.addItems(['<select detectors>'])
        self.detector_combo.currentIndexChanged.connect(self.refresh_event_list)
        # Filters.
        self.filter_event_combo = QtWidgets.QComboBox()
        self.filter_event_combo.setEditable(False)
        self.filter_event_combo.setMinimumWidth(150)
#         self.filter_event_combo.setMaximumWidth(300)
        self.filter_event_combo.addItems(['<select event>'])
        self.filter_detector_combo = QtWidgets.QComboBox()
        self.filter_detector_combo.setEditable(False)
        self.filter_detector_combo.setMinimumWidth(150)
#         self.filter_detector_combo.setMaximumWidth(300)
        self.filter_detector_combo.addItems(['<select detector>'])
        
        self.events_tableview = app_framework.ToolboxQTableView()
#         self.surveys_tableview = app_framework.SelectableQListView()
#         self.surveys_tableview = QtWidgets.QTableView()
#        self.surveys_tableview.setSortingEnabled(True)
        # Buttons.
        self.refresh_button = QtWidgets.QPushButton('Refresh...')
        self.refresh_button.clicked.connect(self.refresh_event_list)
        self.add_button = QtWidgets.QPushButton('Import wavefile...')
        self.copy_button = QtWidgets.QPushButton('(Copy wavefile...)')
        self.rename_button = QtWidgets.QPushButton('(Rename wavefile...)')
        self.delete_button = QtWidgets.QPushButton('Delete wavefile(s)...')
        
        # Layout widgets.
        form1 = QtWidgets.QGridLayout()
        gridrow = 0
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(QtWidgets.QLabel('Workspace:'))
        hlayout.addWidget(self.workspacedir_edit, 7)
        hlayout.addWidget(QtWidgets.QLabel('Survey:'))
        hlayout.addWidget(self.survey_combo, 10)
        hlayout.addWidget(self.refresh_button)
#         hlayout.addStretch(10)
        form1.addLayout(hlayout, gridrow, 0, 1, 15)
        gridrow += 1
        label = QtWidgets.QLabel('Detectors:')
        form1.addWidget(label, gridrow, 0, 1, 1)
        form1.addWidget(self.detector_combo, gridrow, 1, 1, 13)
        gridrow += 1
        label = QtWidgets.QLabel('Wavefiles:')
        form1.addWidget(label, gridrow, 0, 1, 1)
        gridrow += 1
        form1.addWidget(self.events_tableview, gridrow, 0, 1, 15)
        gridrow += 1
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.add_button)
        hlayout.addWidget(self.copy_button)
        hlayout.addWidget(self.rename_button)
        hlayout.addWidget(self.delete_button)
        hlayout.addStretch(10)
        form1.addLayout(hlayout, gridrow, 0, 1, 15)
        #
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(form1)
        widget.setLayout(layout)
        #
        return widget        
    
    def refresh_survey_list(self):
        """ """
        self.survey_combo.clear()
        self.survey_combo.addItem('<select survey>')
        dir_path = str(self.workspacedir_edit.text())
        ws = hdf54bats.Hdf5Workspace(dir_path)
        h5_list = ws.get_hdf5_list()
        for h5_file_key in sorted(h5_list.keys()):
            h5_file_dict = h5_list[h5_file_key]
            self.survey_combo.addItem(h5_file_dict['name'])
    
    def refresh_event_list(self):
        """ """
        if self.survey_combo.currentIndex() == 0:
            self.events_tableview.setModel(app_framework.PandasModel()) # Clear.
            self.events_tableview.resizeColumnsToContents()
            return
        
        dir_path = str(self.workspacedir_edit.text())
        survey_name = str(self.survey_combo.currentText())
        if (not dir_path) or (not survey_name):
            self.events_tableview.setModel(app_framework.PandasModel()) # Clear.
            self.events_tableview.resizeColumnsToContents()
            return
        
        survey = hdf54bats.Hdf5Survey(dir_path, survey_name)
        event = hdf54bats.Hdf5Event(dir_path, survey_name)
        detector = hdf54bats.Hdf5Detector(dir_path, survey_name)
        
        group_id_list = []
        type_list = []
        event_list = []
        detector_list = []
        title_list = []
        # Combo.
        for event_group in sorted(survey.get_children('')):
            print('Group path: ', event_group)
            # Table.
            group_id_list.append(event_group)
            type_list.append('event')
            event_list.append(event_group)
            detector_list.append('')
            title_list.append(event_group)
            
            for detector_group in sorted(detector.get_children(event_group)):
                # Table.
                group_id_list.append(detector_group)
                type_list.append('detector')
                event_list.append(event_group)
                detector_list.append(detector_group.split('.')[1])
                title_list.append(detector_group.split('.')[1])
        #
#         dataframe = pandas.DataFrame(event_list, hdf5_path_list, columns=['event', 'hdf5_path'])
        dataframe = pandas.DataFrame({'group_id': group_id_list, 
                                      'type': type_list, 
                                      'event': event_list, 
                                      'detector': detector_list, 
                                      'title': title_list})
        model = app_framework.PandasModel(dataframe[['group_id', 
                                                     'type', 
                                                     'event', 
                                                     'detector', 
                                                     'title']])
        self.events_tableview.setModel(model)
        self.events_tableview.resizeColumnsToContents()
    
    def _content_adv_filter(self):
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
        <h3>Workspaces</h3>
        <p>
        Work in progress...
        </p>
        
        """

