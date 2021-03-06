#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: http://cloudedbats.org
# Copyright (c) 2018 Arnold Andreasson 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import sys
import pathlib
import numpy as np
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

import hdf54bats
import dsp4bats
import metadata4bats
from cloudedbats_app import app_framework
from cloudedbats_app import app_utils
from cloudedbats_app import app_core
from PyQt5.Qt import QApplication
# from platform import node


class WavefilesActivity(app_framework.ActivityBase):
    """ """

    def __init__(self, name, parentwidget):
        """ """
        self._last_used_dir_path = None
        # Initialize parent. Should be called after other 
        # initialization since the base class calls _create_content().
        super().__init__(name, parentwidget)
        
        # Use sync object for workspaces and surveys. 
        app_core.DesktopAppSync().workspace_changed_signal.connect(self.refresh_survey_list)
        app_core.DesktopAppSync().survey_changed_signal.connect(self.refresh_survey_list)
        #
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
        tabWidget.addTab(self._content_more(), '(More)')
        tabWidget.addTab(self._content_help(), '(Help)')
        # 
        layout.addWidget(tabWidget)
        content.setLayout(layout)
    
    # === Workspaces ===
    def _content_wavefiles(self):
        """ """
        widget = QtWidgets.QWidget()
        # Survey..
        self.survey_combo = QtWidgets.QComboBox()
        self.survey_combo.setEditable(False)
        self.survey_combo.setMinimumWidth(250)
#         self.survey_combo.setMaximumWidth(300)
        self.survey_combo.addItems(['<select survey>'])
        self.survey_combo.currentIndexChanged.connect(self.survey_changed)
#         self.survey_combo.setMaximumWidth(300)
#         self.detector_combo = QtWidgets.QComboBox()
#         self.detector_combo.setEditable(False)
#         self.detector_combo.setMinimumWidth(250)
#         self.detector_combo.addItems(['<select detectors>'])
#         self.detector_combo.currentIndexChanged.connect(self.refresh_wavefile_list)
        
        # Filters.
        self.type_filter_combo = QtWidgets.QComboBox()
        self.type_filter_combo.setMinimumWidth(100)
        self.type_filter_combo.setMaximumWidth(120)
        self.type_filter_combo.addItems(['<select>', 'event', 'detector', 'wavefile'])
        self.title_filter_edit = QtWidgets.QLineEdit('')
        self.clear_filter_button = QtWidgets.QPushButton('(Clear)')
#         self.clear_filter_button.clicked.connect(self.clear_filter)
        
        self.wavefiles_tableview = app_framework.ToolboxQTableView()
        self.wavefiles_tableview.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
#         self.wavefiles_tableview.clicked.connect(self.selected_item_changed)
#         self.wavefiles_tableview.activated.connect(self.selected_item_changed) # When pressing enter on a highlighted row.
        self.wavefiles_tableview.getSelectionModel().selectionChanged.connect(self.selected_item_changed)
#         self.wavefiles_tableview.selectionModel().selectionChanged.connect(self.selected_item_changed)
#         self.wavefiles_tableview.getSelectionModel().currentRowChanged.connect(self.selected_item_changed)
#         self.wavefiles_tableview.selectionModel().currentRowChanged.connect(self.selected_item_changed)
#         self.wavefiles_tableview.getSelectionModel().currentChanged.connect(self.selected_item_changed)
#         self.wavefiles_tableview.selectionModel().currentChanged.connect(self.selected_item_changed)

        # Buttons.
        self.refresh_button = QtWidgets.QPushButton('Refresh')
        self.refresh_button.clicked.connect(self.refresh)
        self.add_button = QtWidgets.QPushButton('Import wavefiles...')
        self.add_button.clicked.connect(self.import_wavefile)
        self.rename_button = QtWidgets.QPushButton('(Rename wavefile...)')
        self.rename_button.clicked.connect(self.rename_wavefile)
        self.delete_button = QtWidgets.QPushButton('Delete wavefiles...')
        self.delete_button.clicked.connect(self.delete_wavefiles)
        
        # Layout widgets.
        form1 = QtWidgets.QGridLayout()
        form1.setSpacing(5)
        form1.setContentsMargins(5,5,5,5)
                
        gridrow = 0
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(QtWidgets.QLabel('Survey:'))
        hlayout.addWidget(self.survey_combo, 10)
        hlayout.addWidget(self.refresh_button)
#         hlayout.addStretch(10)
        form1.addLayout(hlayout, gridrow, 0, 1, 15)
        gridrow += 1
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(QtWidgets.QLabel('(Title filter:)'), 1)
        hlayout.addWidget(self.title_filter_edit, 10)
        hlayout.addWidget(QtWidgets.QLabel('(Type filter:)'), 1)
        hlayout.addWidget(self.type_filter_combo, 5)
        hlayout.addWidget(self.clear_filter_button)
#         hlayout.addStretch(10)
        form1.addLayout(hlayout, gridrow, 0, 1, 15)
        gridrow += 1
        label = QtWidgets.QLabel('Wavefiles:')
        form1.addWidget(label, gridrow, 0, 1, 1)
        gridrow += 1
        form1.addWidget(self.wavefiles_tableview, gridrow, 0, 1, 15)
        gridrow += 1
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.add_button)
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
    
    def refresh(self):
        """ """
        app_core.DesktopAppSync().refresh()
    
    def survey_changed(self):
        """ """
        if self.survey_combo.currentIndex() > 0:
            selected_survey = str(self.survey_combo.currentText())
            # Sync.
            app_core.DesktopAppSync().set_selected_survey(selected_survey)
        else:
            app_core.DesktopAppSync().refresh()
    
    def selected_item_changed(self):
        """ """
        try:
            modelIndex = self.wavefiles_tableview.currentIndex()
            if modelIndex.isValid():
                item_id = str(self.wavefiles_tableview.model().index(modelIndex.row(), 2).data())
                # Sync.
                app_core.DesktopAppSync().set_selected_item_id(item_id)
        except Exception as e:
            debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
            app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))
    
    def refresh_survey_list(self):
        """ """
        try:
            self.survey_combo.blockSignals(True)
            self.survey_combo.clear()
            self.survey_combo.addItem('<select survey>')
            selected_survey = app_core.DesktopAppSync().get_selected_survey()
            survey_dict = app_core.DesktopAppSync().get_surveys_dict()
            index = 0
            for row_index, h5_key in enumerate(sorted(survey_dict)):
                h5_dict = survey_dict[h5_key]
                h5_file = h5_dict['h5_file']
                self.survey_combo.addItem(h5_file)
                if h5_file == selected_survey:
                    index = row_index + 1
            self.survey_combo.setCurrentIndex(index)
        finally:
            self.survey_combo.blockSignals(False)
        #
        self.refresh_wavefile_list()
    
    def refresh_wavefile_list(self):
        """ """
        try:
            self.wavefiles_tableview.blockSignals(True)
            self.wavefiles_tableview.getSelectionModel().blockSignals(True)
            #
            self.dir_path = app_core.DesktopAppSync().get_workspace()
            self.survey_name = app_core.DesktopAppSync().get_selected_survey()
            #
            if self.survey_combo.currentIndex() == 0:
                dataset_table = app_framework.DatasetTable()
                self.wavefiles_tableview.setTableModel(dataset_table)
                self.wavefiles_tableview.resizeColumnsToContents()
                return
             
            dir_path = app_core.DesktopAppSync().get_workspace()
            survey_name = str(self.survey_combo.currentText())
            if (not dir_path) or (not survey_name):
                dataset_table = app_framework.DatasetTable()
                self.wavefiles_tableview.setTableModel(dataset_table)
                self.wavefiles_tableview.resizeColumnsToContents()
                return
            #
            events_dict = app_core.DesktopAppSync().get_events_dict()
            #
            dataset_table = app_framework.DatasetTable()
#             dataset_table.set_header(['item_title', 'item_type', 'item_id'])
            dataset_table.set_header(['Title', 'Type', 'Item id'])
            for key in sorted(events_dict.keys()):
                item_dict = events_dict.get(key, {})
                row = []
                item_id = item_dict.get('item_id', '')
                item_type = item_dict.get('item_type', '')
                item_title = item_dict.get('item_title', '')
                row.append(item_title)
                row.append(item_type)
                row.append(item_id)
                dataset_table.append_row(row)
                #
#                 if item_type == 'detector':
#                     try:
#                         nodes = h5wavefile.get_child_nodes(item_id)
#                         for node_key in sorted(nodes):
#                             node_dict = nodes.get(node_key, {})
#                             node_row = []
#                             node_item_id = node_dict.get('item_id', '')
#                             node_item_type = node_dict.get('item_type', '')
#                             if node_item_type == 'wavefile':
#                                 node_row.append(node_item_id)
#                                 node_row.append(node_item_type)
#                                 node_row.append(node_dict.get('item_title', ''))
#                                 dataset_table.append_row(node_row)
#                             
#                 except Exception as e:
#                     debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
#                     app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))
                    
            #
            self.wavefiles_tableview.setTableModel(dataset_table)
            self.wavefiles_tableview.resizeColumnsToContents()
        finally:
            self.wavefiles_tableview.blockSignals(False)
            self.wavefiles_tableview.getSelectionModel().blockSignals(False)
    
    def import_wavefile(self):
        """ """
        try:
            if self.survey_combo.currentIndex() == 0:
                QtWidgets.QMessageBox.warning(self, 'Warning', 
                     'Survey not selected, please try again.', 
                     QtWidgets.QMessageBox.Ok)
                return
            #
            my_dialog = ImportWavefileDialog(self)
            if my_dialog.exec_():
                self.refresh()
        except Exception as e:
            debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
            app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))
       
    def rename_wavefile(self):
        """ """
        
    def delete_wavefiles(self):
        """ """
        try:
            if self.survey_combo.currentIndex() == 0:
                QtWidgets.QMessageBox.warning(self, 'Warning', 
                     'Survey not selected, please try again.', 
                     QtWidgets.QMessageBox.Ok)
                return
            #
            dialog = DeleteDialog(self)
            if dialog.exec_():
                self.refresh()
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
        <h3>Workspaces</h3>
        <p>
        Work in progress...
        </p>
        
        """



class ImportWavefileDialog(QtWidgets.QDialog):
    """ This dialog is allowed to access private parts in the parent widget. """
    def __init__(self, parentwidget):
        """ """
        super().__init__(parentwidget)
        self.setWindowTitle("Import wavefiles")
        self._parentwidget = parentwidget
        self.setLayout(self._content())
        #
        self.dir_path = app_core.DesktopAppSync().get_workspace()
        self.survey_name = str(self._parentwidget.survey_combo.currentText())
        # 
        self.update_event_list()
        self.enable_buttons()
    
    def _content(self):
        """ """
        # Target detector as item_id
        self.detector_combo = QtWidgets.QComboBox()
        self.detector_combo.setEditable(False)
        self.detector_combo.setMinimumWidth(400)
        self.detector_combo.currentIndexChanged.connect(self.enable_buttons)
        # Detector type.
        self.detectortype_combo = QtWidgets.QComboBox()
        self.detectortype_combo.setEditable(False)
        self.detectortype_combo.setMinimumWidth(400)
        self.detectortype_combo.addItems(['CloudedBats-WURB/Pathfinder', 
                                          'Generic', 
                                          '(Generic GUANO)', 
                                          'AudioMoth version 1.0', 
                                          '(AudioMoth version 1.2)', 
                                          '(Pettersson-M500X)', 
                                          ])
        # Detector location.
        self.location_combo = QtWidgets.QComboBox()
        self.location_combo.setEditable(False)
        self.location_combo.setMinimumWidth(400)
        self.location_combo.addItems(['Get from wave files', 
                                      'Enter manually', 
                                      'Unknown location', 
                                      ])
        self.location_combo.currentIndexChanged.connect(self.enable_buttons)
        self.latitude_dd_edit = QtWidgets.QLineEdit('')
        self.latitude_dd_edit.setPlaceholderText('dd.dddd')
        self.logitude_dd_edit = QtWidgets.QLineEdit('')
        self.logitude_dd_edit.setPlaceholderText('ddd.dddd')
        # Processing during import.
        self.processing_combo = QtWidgets.QComboBox()
        self.processing_combo.setEditable(False)
        self.processing_combo.setMinimumWidth(400)
        self.processing_combo.addItems(['Import all files', 
                                        '(Import files containing sound only)', 
                                        '(Cut up files into parts)', 
                                        '(Cut up into parts containing sound)', 
                                        ])
        self.processing_max_length_edit = QtWidgets.QLineEdit('')
        
        
        # Select files
        self.sourcedir_edit = QtWidgets.QLineEdit('../../../batfiles')
#         self.sourcedir_edit = QtWidgets.QLineEdit('')
        self.sourcedir_button = QtWidgets.QPushButton('Browse...')
        self.sourcedir_button.clicked.connect(self.source_dir_browse)
        self.recursive_checkbox = QtWidgets.QCheckBox('Include subdirectories')
        self.recursive_checkbox.setChecked(False)
        self.addfiles_button = QtWidgets.QPushButton('Add files in directory')
        self.addfiles_button.clicked.connect(self.add_files)
        self.addmorefiles_button = QtWidgets.QPushButton('(Add other files...)')
#         self.addmorefiles_button.clicked.connect(self.add_more_files)
        self.clearfiles_button = QtWidgets.QPushButton('Clear')
        self.clearfiles_button.clicked.connect(self.clear_files)
         
        self.items_listview = QtWidgets.QListView()
        self._items_model = QtGui.QStandardItemModel()
        self.items_listview.setModel(self._items_model)
         
        self.clearall_button = app_framework.ClickableQLabel('Clear all')
        self.clearall_button.label_clicked.connect(self._uncheck_all_items)
        self.markall_button = app_framework.ClickableQLabel('Mark all')
        self.markall_button.label_clicked.connect(self._check_all_items)
        
        self.cancel_button = QtWidgets.QPushButton('Cancel')
        self.cancel_button.clicked.connect(self.reject) # Close dialog box.               
        self.importwavefiles_button = QtWidgets.QPushButton('Import wavefiles')
        self.importwavefiles_button.clicked.connect(self._import_wavefiles)
        self.importwavefiles_button.setEnabled(True)
        self.importwavefiles_button.setDefault(False)
        
        # Layout widgets.
        form1 = QtWidgets.QGridLayout()
        gridrow = 0
        label = QtWidgets.QLabel('Detector:')
        form1.addWidget(label, gridrow, 0, 1, 1)
        gridrow += 1
        label = QtWidgets.QLabel('To detector:')
        form1.addWidget(label, gridrow, 1, 1, 1)
        form1.addWidget(self.detector_combo, gridrow, 2, 1, 17)
        gridrow += 1
        label = QtWidgets.QLabel('Detector type:')
        form1.addWidget(label, gridrow, 1, 1, 1)
        form1.addWidget(self.detectortype_combo, gridrow, 2, 1, 17)
        gridrow += 1
        label = QtWidgets.QLabel('Detector location:')
        form1.addWidget(label, gridrow, 0, 1, 2)
        gridrow += 1
        label = QtWidgets.QLabel('Location:')
        form1.addWidget(label, gridrow, 1, 1, 1)
        form1.addWidget(self.location_combo, gridrow, 2, 1, 17)
        gridrow += 1
        label = QtWidgets.QLabel('Latitude (DD):')
        form1.addWidget(label, gridrow, 1, 1, 1)
        form1.addWidget(self.latitude_dd_edit, gridrow, 2, 1, 10)
        gridrow += 1
        label = QtWidgets.QLabel('Longitude (DD):')
        form1.addWidget(label, gridrow, 1, 1, 1)
        form1.addWidget(self.logitude_dd_edit, gridrow, 2, 1, 10)
        gridrow += 1
        label = QtWidgets.QLabel('Import processing:')
        form1.addWidget(label, gridrow, 0, 1, 2)
        gridrow += 1
        label = QtWidgets.QLabel('Processing:')
        form1.addWidget(label, gridrow, 1, 1, 1)
        form1.addWidget(self.processing_combo, gridrow, 2, 1, 17)
        gridrow += 1
        label = QtWidgets.QLabel('Max length (s):')
        form1.addWidget(label, gridrow, 1, 1, 1)
        form1.addWidget(self.processing_max_length_edit, gridrow, 2, 1, 10)
        
        gridrow += 1
        label = QtWidgets.QLabel('   ')
        form1.addWidget(label, gridrow, 0, 1, 10)
        gridrow += 1
        label = QtWidgets.QLabel('Select files to import:')
        form1.addWidget(label, gridrow, 0, 1, 10)
        gridrow += 1
        label = QtWidgets.QLabel('From directory:')
        form1.addWidget(label, gridrow, 1, 1, 1)
        form1.addWidget(self.sourcedir_edit, gridrow, 2, 1, 17)
        form1.addWidget(self.sourcedir_button, gridrow, 19, 1, 1)
        gridrow += 1
        hbox1 = QtWidgets.QHBoxLayout()
        hbox1.addStretch(10)
        hbox1.addWidget(self.recursive_checkbox)
        hbox1.addWidget(self.addfiles_button)
        hbox1.addWidget(self.addmorefiles_button)
        hbox1.addWidget(self.clearfiles_button)
        form1.addLayout(hbox1, gridrow, 1, 1, 19)

        gridrow += 1
        form1.addWidget(self.items_listview, gridrow, 1, 1, 19)
        gridrow += 1
        hbox1 = QtWidgets.QHBoxLayout()
        hbox1.addWidget(self.clearall_button)
        hbox1.addWidget(self.markall_button)
        hbox1.addStretch(20)
        form1.addLayout(hbox1, gridrow, 1, 1, 19)
        gridrow += 1
        label = QtWidgets.QLabel('   ')
        form1.addWidget(label, gridrow, 0, 1, 10)
        # 
        hbox1 = QtWidgets.QHBoxLayout()
        hbox1.addStretch(10)
        hbox1.addWidget(self.cancel_button)
        hbox1.addWidget(self.importwavefiles_button)
        # 
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(form1, 20)
        layout.addLayout(hbox1)
        # 
        return layout
    
    def enable_buttons(self):
        """ """
        if self.detector_combo.currentIndex() > 0:
            self.importwavefiles_button.setEnabled(True)
        else:
            self.importwavefiles_button.setEnabled(False)
        #
        if self.location_combo.currentText() == 'Enter manually':
            self.latitude_dd_edit.setEnabled(True)
            self.logitude_dd_edit.setEnabled(True)
        else:
            self.latitude_dd_edit.setEnabled(False)
            self.logitude_dd_edit.setEnabled(False)
    
    def update_event_list(self):
        """ """
        try:
            selected_detector_id = app_core.DesktopAppSync().get_selected_item_id(item_type='detector')
            events_dict = app_core.DesktopAppSync().get_events_dict()
            self.detector_combo.clear()
            self.detector_combo.addItem('<select>')
            index = 0
            row_index = 0
            for key in sorted(events_dict.keys()):
                item_dict = events_dict.get(key, '')
                item_type = item_dict.get('item_type', '')
                if item_type == 'detector':
                    self.detector_combo.addItem(key)
                    row_index += 1
                    if key == selected_detector_id:
                        index = row_index
            self.detector_combo.setCurrentIndex(index)
        except Exception as e:
            debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
            app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))
                
    def source_dir_browse(self):
        """ """
        dirdialog = QtWidgets.QFileDialog(self)
        dirdialog.setFileMode(QtWidgets.QFileDialog.Directory)
        dirdialog.setOptions(QtWidgets.QFileDialog.ShowDirsOnly |
                             QtWidgets.QFileDialog.DontResolveSymlinks)
        dirdialog.setDirectory(str(self.sourcedir_edit.text()))
        dirpath = dirdialog.getExistingDirectory()
        if dirpath:
            self.sourcedir_edit.setText(dirpath)
#             self.targetdir_edit.setText(dirpath + '_results')
        
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
    
    def add_files(self):
        """ """
        dir_path = str(self.sourcedir_edit.text())
        path_list = []
        # Search for wave files. 
#         if self.recursive_checkbox.isChecked():
#             path_list = list(pathlib.Path(dir_path).glob('**/*.wav'))
#             path_list += list(pathlib.Path(dir_path).glob('**/*.WAV'))
#         else:
#             path_list = list(pathlib.Path(dir_path).glob('*.wav'))
#             path_list += list(pathlib.Path(dir_path).glob('*.WAV'))

        file_ext_list = ['*.wav', '*.WAV']
        if self.recursive_checkbox.isChecked():
            file_ext_list = ['**/*.wav', '**/*.WAV']
        #
        for file_ext in file_ext_list:
            for file_name in pathlib.Path(dir_path).glob(file_ext):
                file_name_str = str(file_name).replace('/._', '/') # TODO: Strange chars when reading from ext. SSD?
                if file_name_str not in path_list:
                    path_list.append(file_name_str)
        #
        for wave_file_path in sorted(path_list):
                item = QtGui.QStandardItem(str(wave_file_path))
                item.setCheckState(QtCore.Qt.Unchecked)
                item.setCheckable(True)
                self._items_model.appendRow(item)
    
    def clear_files(self):
        """ """
        self._items_model.clear()
    
    def _import_wavefiles(self):
        """ """
        try:        
            try:
                detectorgroup = self.detector_combo.currentText()
                self._parentwidget._write_to_status_bar('- Busy: Importing wave files.')
                
                h5_wavefiles = hdf54bats.Hdf5Wavefiles(self.dir_path, self.survey_name)
#                 wurb_utils = dsp4bats.WurbFileUtils()
                
                
                
                
                for rowindex in range(self._items_model.rowCount()):
                    try:
                        item = self._items_model.item(rowindex, 0)
                        if item.checkState() == QtCore.Qt.Checked:
                            wave_file_path = str(item.text())
        #                     wave.remove_wavefile(item_id)
                            
                            wave_reader = None
                            try:
                                #
                                detector_type = self.detectortype_combo.currentText()
                                if detector_type == 'CloudedBats-WURB/Pathfinder':
                                    metadata_reader = metadata4bats.MetadataWavefileWurb(wave_file_path)
                                elif detector_type == 'Generic':
                                    metadata_reader = metadata4bats.MetadataWavefile(wave_file_path)
                                elif detector_type == '(Generic GUANO)':
                                    metadata_reader = metadata4bats.MetadataWavefile(wave_file_path)
                                elif detector_type == 'AudioMoth version 1.0':
                                    metadata_reader = metadata4bats.MetadataWavefileAudiomoth(wave_file_path)
                                elif detector_type == '(AudioMoth version 1.2)':
                                    metadata_reader = metadata4bats.MetadataWavefileAudiomoth(wave_file_path)
                                elif detector_type == '(Pettersson-M500X)':
                                    metadata_reader = metadata4bats.MetadataWavefile(wave_file_path)
                                else:
                                    metadata_reader = metadata4bats.MetadataWavefile(wave_file_path)
                                #
                                metadata_reader.extract_metadata()
                                metadata = metadata_reader.get_metadata()
                                #
                                file_name = metadata['rec_file_name']
                                title = file_name
                                if 'rec_datetime_local' in metadata:
                                    datetime_str = metadata['rec_datetime_local'][0:15]
                                    name = 'wave_' + hdf54bats.str_to_ascii(datetime_str)
                                else:
                                    name = metadata['rec_file_stem'].lower()
                                
                                
                                if self.location_combo.currentText() == 'Get from wave files':
                                    pass # Already done.
                                elif self.location_combo.currentText() == 'Enter manually':
                                    metadata['rec_latitude_dd'] = self.latitude_dd_edit.text()
                                    metadata['rec_longitude_dd'] = self.logitude_dd_edit.text()
                                elif self.location_combo.currentText() == 'Unknown location':
                                    metadata['rec_latitude_dd'] = ''
                                    metadata['rec_longitude_dd'] = ''
                                
                                name = hdf54bats.str_to_ascii(name)
                                self._parentwidget._write_to_status_bar('- Busy: Importing: ' + file_name)
                                
                                app_utils.Logging().info('Importing wavefile: ' + title)
                                QtWidgets.QApplication.processEvents()

                                wave_reader = dsp4bats.WaveFileReader(wave_file_path)
                                signal = np.array([], dtype=np.int16)
                                buffer = wave_reader.read_buffer(convert_to_float=False)
                                while len(buffer) > 0:
                                    signal = np.append(signal, buffer)
                                    buffer = wave_reader.read_buffer(convert_to_float=False)
                            finally:
                                if wave_reader:
                                    wave_reader.close()
                            
                            wavefile_id = h5_wavefiles.add_wavefile(parent_id=detectorgroup, node_id=name, title=title, array=signal)
                            h5_wavefiles.set_user_metadata(wavefile_id, metadata=metadata)
                    #
                    except Exception as e:
                        debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
                        app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))
            finally:    
                self._parentwidget._write_to_status_bar('')
                self.accept() # Close dialog box.
        #
        except Exception as e:
            debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
            app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))


class DeleteDialog(QtWidgets.QDialog):
    """ This dialog is allowed to access private parts in the parent widget. """
    def __init__(self, parentwidget):
        """ """
        super(DeleteDialog, self).__init__(parentwidget)
        self.setWindowTitle("Delete wavefiles")
        self._parentwidget = parentwidget
        self.setLayout(self._content())
        self.setMinimumSize(500, 500)
        #
        self.dir_path = app_core.DesktopAppSync().get_workspace()
        self.survey_name = str(self._parentwidget.survey_combo.currentText())
        #
        self._load_item_data()
        
    def _content(self):
        """ """  
        contentLayout = QtWidgets.QVBoxLayout(self)
        self.setLayout(contentLayout)
        #
        self._main_tab_widget = QtWidgets.QTabWidget(self)
        contentLayout.addWidget(self._main_tab_widget)
        self._main_tab_widget.addTab(self._item_content(), 'Delete wavefiles')
#         self._main_tab_widget.addTab(self._sample_content(), 'Delete detectors')
        
        return contentLayout                

    def _item_content(self):
        """ """
        widget = QtWidgets.QWidget()
        #  
        items_listview = QtWidgets.QListView()
        self._items_model = QtGui.QStandardItemModel()
        items_listview.setModel(self._items_model)

        clearall_button = app_framework.ClickableQLabel('Clear all')
        clearall_button.label_clicked.connect(self._uncheck_all_items)
        markall_button = app_framework.ClickableQLabel('Mark all')
        markall_button.label_clicked.connect(self._check_all_items)
        cancel_button = QtWidgets.QPushButton('Cancel')
        cancel_button.clicked.connect(self.reject) # Close dialog box.               
        delete_button = QtWidgets.QPushButton('Delete marked wavefiles')
        delete_button.clicked.connect(self._delete_marked_items)
        # Layout widgets.
        hbox1 = QtWidgets.QHBoxLayout()
        hbox1.addWidget(clearall_button)
        hbox1.addWidget(markall_button)
        hbox1.addStretch(10)
        #
        hbox2 = QtWidgets.QHBoxLayout()
        hbox2.addStretch(10)
        hbox2.addWidget(cancel_button)
        hbox2.addWidget(delete_button)
        #
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(items_listview, 10)
        layout.addLayout(hbox1)
        layout.addLayout(hbox2)
        #
        widget.setLayout(layout)
        #
        return widget
    
    def enable_buttons(self):
        """ """
        if self.detector_combo.currentIndex() > 0:
            self.importwavefiles_button.setEnabled(True)
        else:
            self.importwavefiles_button.setEnabled(False)
    
    def _load_item_data(self):
        """ """
        try:
            self._items_model.clear()
            h5_wavefiles = hdf54bats.Hdf5Wavefiles(self.dir_path, self.survey_name)
            from_top_node = ''
            nodes = h5_wavefiles.get_child_nodes(from_top_node)
            for node_key in sorted(nodes):
                node_dict = nodes.get(node_key, {})
                node_item_id = node_dict.get('item_id', '')
                node_item_type = node_dict.get('item_type', '')
                if node_item_type == 'wavefile':
                    item = QtGui.QStandardItem(node_item_id)
                    item.setCheckState(QtCore.Qt.Unchecked)
                    item.setCheckable(True)
                    self._items_model.appendRow(item)
                
                
                
#             nodes = h5wavefile.get_child_nodes(item_id)
#             for node_key in sorted(nodes):
#                 node_dict = nodes.get(node_key, {})
#                 node_row = []
#                 node_item_id = node_dict.get('item_id', '')
#                 node_item_type = node_dict.get('item_type', '')
#                 node_row.append(node_item_id)
#                 node_row.append(node_item_type)
#                 node_row.append(node_dict.get('item_title', ''))
#                 dataset_table.append_row(node_row)

#             self._items_model.clear()
#             wave = hdf54bats.Hdf5Wavefiles(self.dir_path, self.survey_name)
#             
#             from_top_node = ''
#             wavefiles_dict = wave.get_wavefiles(from_top_node)
#             
#             for wave_id in sorted(wavefiles_dict):
# #                 self.groupid_combo.addItem(event_group)
#                 item = QtGui.QStandardItem(wave_id)
#                 item.setCheckState(QtCore.Qt.Unchecked)
#                 item.setCheckable(True)
#                 self._items_model.appendRow(item)
        #
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

    def _delete_marked_items(self):
        """ """
        try:
            try:        
                h5_wavefiles = hdf54bats.Hdf5Wavefiles(self.dir_path, self.survey_name)
                for rowindex in range(self._items_model.rowCount()):
                    item = self._items_model.item(rowindex, 0)
                    if item.checkState() == QtCore.Qt.Checked:
                        item_id = str(item.text())
                        h5_wavefiles.remove_wavefile(item_id, recursive=True)
            finally:
                self.accept() # Close dialog box.
        #
        except Exception as e:
            debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
            app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))


