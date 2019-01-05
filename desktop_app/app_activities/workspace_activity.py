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

class WorkspaceActivity(app_framework.ActivityBase):
    """ """

    def __init__(self, name, parentwidget):
        """ """
        self._last_used_dir_path = None
        # Initialize parent. Should be called after other 
        # initialization since the base class calls _create_content().
        super(WorkspaceActivity, self).__init__(name, parentwidget)
    
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
        tabWidget.addTab(self._content_workspace(), 'Workspace')
        tabWidget.addTab(self._content_help(), 'Help')
        # 
        layout.addWidget(tabWidget)
        content.setLayout(layout)
    
    # === Workspace ===
    def _content_workspace(self):
        """ """
        widget = QtWidgets.QWidget()
        # From dir.
        self.workspacedir_edit = QtWidgets.QLineEdit('workspace_1')
        self.workspacedir_button = QtWidgets.QPushButton('Browse...')
        self.workspacedir_button.clicked.connect(self.workspace_dir_browse)
        
        self.surveys_tableview = app_framework.ToolboxQTableView()
#         self.surveys_tableview = app_framework.SelectableQListView()
#         self.surveys_tableview = QtWidgets.QTableView()
#        self.surveys_tableview.setSortingEnabled(True)
        # Buttons.
        self.name_combo = QtWidgets.QComboBox()
        self.name_combo.setEditable(False)
        self.name_combo.setMinimumWidth(150)
        self.name_combo.setMaximumWidth(200)
#         self.name_combo.addItems([])
        self.name_edit = QtWidgets.QLineEdit('survey_1')
        
        self.refresh_button = QtWidgets.QPushButton('Refresh...')
        self.refresh_button.clicked.connect(self.refresh_survey_list)
        self.add_button = QtWidgets.QPushButton('Add survey...')
        self.add_button.clicked.connect(self.add_survey)
        self.copy_button = QtWidgets.QPushButton('Copy survey...')
        self.copy_button.clicked.connect(self.copy_survey)
        self.rename_button = QtWidgets.QPushButton('Rename survey...')
        self.rename_button.clicked.connect(self.rename_survey)
        self.delete_button = QtWidgets.QPushButton('Delete survey(s)...')
        self.delete_button.clicked.connect(self.delete_survey)
        
        # Layout widgets.
        form1 = QtWidgets.QGridLayout()
        gridrow = 0
        label = QtWidgets.QLabel('Workspace:')
        form1.addWidget(label, gridrow, 0, 1, 1)
        form1.addWidget(self.workspacedir_edit, gridrow, 1, 1, 13)
        form1.addWidget(self.workspacedir_button, gridrow, 14, 1, 1)
        gridrow += 1
        label = QtWidgets.QLabel('Surveys in workspace:')
        form1.addWidget(label, gridrow, 0, 1, 2)
        gridrow += 1
        form1.addWidget(self.surveys_tableview, gridrow, 0, 1, 15)
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
    
    def workspace_dir_browse(self):
        """ """
        dirdialog = QtWidgets.QFileDialog(self)
        dirdialog.setFileMode(QtWidgets.QFileDialog.Directory)
        dirdialog.setOptions(QtWidgets.QFileDialog.ShowDirsOnly |
                             QtWidgets.QFileDialog.DontResolveSymlinks)
        dirdialog.setDirectory(str(self.workspacedir_edit.text()))
        dirpath = dirdialog.getExistingDirectory()
        if dirpath:
            self.workspacedir_edit.setText(dirpath)

    def refresh_survey_list(self):
        """ """
        dir_path = str(self.workspacedir_edit.text())
        ws = hdf54bats.Hdf5Workspace(dir_path)
        survey_list = []
        hdf5_path_list = []
        # Combo.
        self.name_combo.clear()
        for hdf5_file in sorted(ws.get_hdf5_list()):
            print('HDF5 file: ', hdf5_file)
            # Combo.
            self.name_combo.addItem(hdf5_file)
            # Table.
            survey_list.append(hdf5_file)
            hdf5_path_list.append(str(pathlib.Path(dir_path, hdf5_file).resolve()))
        #
#         dataframe = pandas.DataFrame(survey_list, hdf5_path_list, columns=['survey', 'hdf5_path'])
        dataframe = pandas.DataFrame({'survey': survey_list, 'hdf5_path': hdf5_path_list})
        model = app_framework.PandasModel(dataframe[['survey', 'hdf5_path']])
        self.surveys_tableview.setModel(model)
        self.surveys_tableview.resizeColumnsToContents()
        
#         model = app_framework.PandasModel(dataframe[
#         ['file_stem', 'file_name', 'detector_id', 'datetime', 'datetime_str', 'latitude_dd',
#         'longitude_dd', 'latlong_str', 'rec_type', 'frame_rate_hz',
#         'file_frame_rate_hz', 'is_te', 'comments', 'dir_path', 
#         'file_path', 'abs_file_path']
#                                                     ])
#         self.sourcefiles_tableview.setModel(model)
        
        
        
    def add_survey(self):
        """ """
        try:
            dir_path = str(self.workspacedir_edit.text())
            name = self.name_edit.text()
            ws = hdf54bats.Hdf5Workspace(dir_path)
            ws.create_hdf5(name)
            # One survey in each file. Same name.
            survey = hdf54bats.Hdf5Survey(dir_path, name)
            survey.add_survey('', name)
            self.refresh_survey_list()
        except Exception as e:
            print('TODO: ERROR: ', e)

    def copy_survey(self):
        """ """
        try:
            dir_path = str(self.workspacedir_edit.text())
            name_combo = self.name_combo.currentText()
            name = self.name_edit.text()
            ws = hdf54bats.Hdf5Workspace(dir_path)
            ws.copy_hdf5(name_combo, name)
            self.refresh_survey_list()
        except Exception as e:
            print('TODO: ERROR: ', e)
        
    def rename_survey(self):
        """ """
        try:
            dir_path = str(self.workspacedir_edit.text())
            name_combo = self.name_combo.currentText()
            name = self.name_edit.text()
            ws = hdf54bats.Hdf5Workspace(dir_path)
            ws.rename_hdf5(name_combo, name)
            self.refresh_survey_list()
        except Exception as e:
            print('TODO: ERROR: ', e)

    def delete_survey(self):
        """ """
        try:
            dir_path = str(self.workspacedir_edit.text())
            name_combo = self.name_combo.currentText()
            ws = hdf54bats.Hdf5Workspace(dir_path)
            ws.delete_hdf5(name_combo)
            self.refresh_survey_list()
        except Exception as e:
            print('TODO: ERROR: ', e)

        
#         scanner = app_core.WaveFileScanner()
#         dataframe = scanner.get_file_info_as_dataframe(dir_path)
#                 
# #         model = app_framework.PandasModel(dataframe[['file_name', 'file_path', 'frame_rate_hz']])
#         model = app_framework.PandasModel(dataframe[
#         ['file_stem', 'file_name', 'detector_id', 'datetime', 'datetime_str', 'latitude_dd',
#         'longitude_dd', 'latlong_str', 'rec_type', 'frame_rate_hz',
#         'file_frame_rate_hz', 'is_te', 'comments', 'dir_path', 
#         'file_path', 'abs_file_path']
#                                                     ])
#         self.sourcefiles_tableview.setModel(model)
#         
#         
# #        ['detector_id', 'datetime', 'datetime_str', 'latitude_dd',
# #        'longitude_dd', 'latlong_str', 'rec_type', 'frame_rate_hz',
# #        'file_frame_rate_hz', 'is_te', 'comments', 'dir_path', 'file_name',
# #        'file_path', 'file_stem', 'abs_file_path']
#         
#         
#         
# 
#         self.sourcefiles_tableview.resizeColumnsToContents()


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
        <h3>Workspace</h3>
        <p>
        Work in progress...
        </p>
        
        """

