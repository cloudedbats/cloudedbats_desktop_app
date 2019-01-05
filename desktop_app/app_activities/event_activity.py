#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: http://cloudedbats.org
# Copyright (c) 2018 Arnold Andreasson 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import pathlib
import pandas
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

import hdf54bats
import metadata4bats
from desktop_app import app_framework

class EventActivity(app_framework.ActivityBase):
    """ """

    def __init__(self, name, parentwidget):
        """ """
        self._last_used_dir_path = None
        # Initialize parent. Should be called after other 
        # initialization since the base class calls _create_content().
        super().__init__(name, parentwidget)
    
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
        tabWidget.addTab(self._content_event(), 'Event')
        tabWidget.addTab(self._content_help(), 'Help')
        # 
        layout.addWidget(tabWidget)
        content.setLayout(layout)
    
    # === Event ===
    def _content_event(self):
        """ """
        widget = QtWidgets.QWidget()
        # From dir.
        self.workspacedir_edit = QtWidgets.QLineEdit('workspace_1')
        self.survey_combo = QtWidgets.QComboBox()
        self.survey_combo.setEditable(False)
        self.survey_combo.setMinimumWidth(250)
        self.survey_combo.setMaximumWidth(300)
        self.survey_combo.addItems(['survey_1'])
        
        self.detectors_tableview = app_framework.ToolboxQTableView()
#         self.detectors_tableview = app_framework.SelectableQListView()
#         self.detectors_tableview = QtWidgets.QTableView()
#        self.detectors_tableview.setSortingEnabled(True)
        # Buttons.
        self.name_combo = QtWidgets.QComboBox()
        self.name_combo.setEditable(False)
        self.name_combo.setMinimumWidth(250)
        self.name_combo.setMaximumWidth(500)
#         self.name_combo.addItems([])
        self.name_edit = QtWidgets.QLineEdit('detector_1')
        
        self.refresh_button = QtWidgets.QPushButton('Refresh...')
        self.refresh_button.clicked.connect(self.refresh_detector_list)
        self.add_button = QtWidgets.QPushButton('Add detector...')
        self.add_button.clicked.connect(self.add_detector)
        self.delete_button = QtWidgets.QPushButton('Delete detector(s)...')
        self.delete_button.clicked.connect(self.delete_detector)
        
        # Layout widgets.
        form1 = QtWidgets.QGridLayout()
        gridrow = 0
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(QtWidgets.QLabel('Workspace:'))
        hlayout.addWidget(self.workspacedir_edit)
        hlayout.addWidget(QtWidgets.QLabel('Survey:'))
        hlayout.addWidget(self.survey_combo)
        hlayout.addStretch(10)
        form1.addLayout(hlayout, gridrow, 0, 1, 15)
        gridrow += 1
        label = QtWidgets.QLabel('Detectors for event:')
        form1.addWidget(label, gridrow, 0, 1, 1)
        gridrow += 1
        form1.addWidget(self.detectors_tableview, gridrow, 0, 1, 15)
        gridrow += 1
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.name_combo)
        hlayout.addWidget(self.name_edit)
        hlayout.addStretch(10)
        form1.addLayout(hlayout, gridrow, 0, 1, 15)
        gridrow += 1
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.refresh_button)
        hlayout.addWidget(self.add_button)
        hlayout.addWidget(self.delete_button)
        hlayout.addStretch(10)
        form1.addLayout(hlayout, gridrow, 0, 1, 15)
        #
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(form1)
        widget.setLayout(layout)
        #
        return widget        
    
    def refresh_detector_list(self):
        """ """
        dir_path = str(self.workspacedir_edit.text())
        survey_name = str(self.survey_combo.currentText())
        survey = hdf54bats.Hdf5Survey(dir_path, survey_name)
        event = hdf54bats.Hdf5Event(dir_path, survey_name)
        
        detector_list = []
        hdf5_path_list = []
        # Combo.
        self.name_combo.clear()
        for survey_groups in sorted(survey.get_children(survey_name)):
            print('Survey groups: ', survey_groups)
            # Combo.
            self.name_combo.addItem(survey_groups)
            for event_groups in sorted(event.get_children(survey_groups)):
                print('Event groups: ', event_groups)
                # Combo.
                self.name_combo.addItem(event_groups)
                # Table.
                detector_list.append(event_groups)
                hdf5_path_list.append(str(pathlib.Path(dir_path, survey_name + '.h5').resolve()))
        #
#         dataframe = pandas.DataFrame(detector_list, hdf5_path_list, columns=['detector', 'hdf5_path'])
        dataframe = pandas.DataFrame({'detector': detector_list, 'hdf5_path': hdf5_path_list})
        model = app_framework.PandasModel(dataframe[['detector', 'hdf5_path']])
        self.detectors_tableview.setModel(model)
        self.detectors_tableview.resizeColumnsToContents()
        
    def add_detector(self):
        """ """
        try:
            dir_path = str(self.workspacedir_edit.text())
            survey_name = str(self.survey_combo.currentText())
            detectors = hdf54bats.Hdf5Detector(dir_path, survey_name)
            event_name = self.name_combo.currentText()
            name = self.name_edit.text()
            detectors.add_detector(parents=event_name, name=name)
            self.refresh_detector_list()
        except Exception as e:
            print('TODO: ERROR: ', e)

    def delete_detector(self):
        """ """
        try:
            dir_path = str(self.workspacedir_edit.text())
            survey_name = str(self.survey_combo.currentText())
            detectors = hdf54bats.Hdf5Detector(dir_path, survey_name)
            name_combo = self.name_combo.currentText()
#             nodepath = survey_name + '.' + name_combo
            nodepath = name_combo
            detectors.remove_detector(nodepath=nodepath)
            self.refresh_detector_list()
        except Exception as e:
            print('TODO: ERROR: ', e)
    
    
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

