#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: http://cloudedbats.org
# Copyright (c) 2018 Arnold Andreasson 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import sys
import string
import numpy as np
import pandas
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

import hdf54bats
import metadata4bats
from desktop_app import app_framework
from desktop_app import app_utils
from desktop_app import app_core
import dsp4bats


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
#         tabWidget.addTab(self._content_adv_filter(), 'Advanced filter')
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
        self.add_button.clicked.connect(self.import_wavefile)
        self.rename_button = QtWidgets.QPushButton('(Rename wavefile...)')
        self.rename_button.clicked.connect(self.rename_wavefile)
        self.delete_button = QtWidgets.QPushButton('Delete wavefile(s)...')
        self.delete_button.clicked.connect(self.delete_wavefiles)
        
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
    
#     def _content_adv_filter(self):
#         """ """
#         widget = QtWidgets.QWidget()
#         #
#         return widget
    
    def refresh_survey_list(self):
        """ """
        self.survey_combo.clear()
        self.survey_combo.addItem('<select survey>')
        dir_path = str(self.workspacedir_edit.text())
        ws = hdf54bats.Hdf5Workspace(dir_path)
        h5_list = ws.get_h5_list()
        for h5_file_key in sorted(h5_list.keys()):
            h5_file_dict = h5_list[h5_file_key]
            self.survey_combo.addItem(h5_file_dict['name'])
            
            self.survey_combo.setCurrentIndex(1)
    
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
        
        event = hdf54bats.Hdf5Event(dir_path, survey_name)
        detector = hdf54bats.Hdf5Detector(dir_path, survey_name)
        wave = hdf54bats.Hdf5Wavefile(dir_path, survey_name)
         
        id_list = []
        type_list = []
        event_list = []
        detector_list = []
        title_list = []
        # Combo.
        for event_group in sorted(event.get_children('')):
            print('Group path: ', event_group)
            # Table.
            id_list.append(event_group)
            type_list.append('event')
            event_list.append(event_group)
            detector_list.append('')
            title_list.append(event_group)
             
            for detector_group in sorted(detector.get_children(event_group)):
                # Table.
                id_list.append(detector_group)
                type_list.append('detector')
                event_list.append(event_group)
                detector_list.append(detector_group.split('.')[1])
                title_list.append(detector_group.split('.')[1])
                
                wavefiles = wave.get_wavefiles(from_top_node=detector_group)
                for wave_id in sorted(wavefiles):
                    # Table.
                    id_list.append(wave_id)
                    type_list.append('wavefile')
                    event_list.append('')
                    detector_list.append('')
                    title_list.append(wavefiles[wave_id])

        #
#         dataframe = pandas.DataFrame(event_list, hdf5_path_list, columns=['event', 'hdf5_path'])
        dataframe = pandas.DataFrame({'id': id_list, 
                                      'type': type_list, 
                                      'event': event_list, 
                                      'detector': detector_list, 
                                      'title': title_list})
        model = app_framework.PandasModel(dataframe[['id', 
                                                     'type', 
#                                                      'event', 
#                                                      'detector', 
                                                     'title']])
        self.events_tableview.setModel(model)
        self.events_tableview.resizeColumnsToContents()
    
    def import_wavefile(self):
        """ """
        try:        
            my_dialog = ImportWavefileDialog(self)
            if my_dialog.exec_():
                self.refresh_event_list()
        except Exception as e:
            debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
            app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))
       
    def rename_wavefile(self):
        """ """
        
    def delete_wavefiles(self):
        """ """
        try:        
            dialog = DeleteDialog(self)
            if dialog.exec_():
                self.refresh_event_list()
        except Exception as e:
            debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
            app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))
        
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
        self.setWindowTitle("Import wavefile")
        self._parentwidget = parentwidget
        self.setLayout(self._content())
        #
        self.dir_path = str(self._parentwidget.workspacedir_edit.text())
        self.survey_name = str(self._parentwidget.survey_combo.currentText())
        # 
        self.update_event_list()

    def _content(self):
        """ """
        # From dir.
        self.sourcedir_edit = QtWidgets.QLineEdit('')
        self.sourcedir_button = QtWidgets.QPushButton('Browse...')
        self.sourcedir_button.clicked.connect(self.source_dir_browse)
        self.recursive_checkbox = QtWidgets.QCheckBox('Include subdirectories')
        self.recursive_checkbox.setChecked(False)
        # View from dir content as table.
        self.sourcecontent_button = QtWidgets.QPushButton('View files')
        self.sourcecontent_button.clicked.connect(self.load_data)
        
        self.detectortype_combo = QtWidgets.QComboBox()
        self.detectortype_combo.setEditable(False)
        self.detectortype_combo.setMinimumWidth(400)
        self.detectortype_combo.addItems(['Generic', 
                                          'Generic-GUANO', 
                                          'AudioMoth', 
                                          'Pettersson-M500X', 
                                          'CloudedBats-WURB', 
                                          'CloudedBats-Pathfinder', 
                                          ])
        
#         self.sourcefiles_tableview = app_framework.ToolboxQTableView()
        items_listview = QtWidgets.QListView()
        self._items_model = QtGui.QStandardItemModel()
        items_listview.setModel(self._items_model)
        
        clearall_button = app_framework.ClickableQLabel('Clear all')
        clearall_button.label_clicked.connect(self._uncheck_all_items)
        markall_button = app_framework.ClickableQLabel('Mark all')
        markall_button.label_clicked.connect(self._check_all_items)
        self.filter_edit = QtWidgets.QLineEdit('')
        self.filterclear_button = QtWidgets.QPushButton('Clear')
        
        self.detector_combo = QtWidgets.QComboBox()
        self.detector_combo.setEditable(False)
        self.detector_combo.setMinimumWidth(400)
        
        
        cancel_button = QtWidgets.QPushButton('Cancel')
        cancel_button.clicked.connect(self.reject) # Close dialog box.               
        self.importwavefiles_button = QtWidgets.QPushButton('Import wavefiles')
        self.importwavefiles_button.clicked.connect(self._import_wavefiles)
        self.importwavefiles_button.setEnabled(True)
        self.importwavefiles_button.setDefault(False)
        # Layout widgets.
        form1 = QtWidgets.QGridLayout()
        gridrow = 0
        label = QtWidgets.QLabel('From directory:')
        form1.addWidget(label, gridrow, 0, 1, 1)
        form1.addWidget(self.sourcedir_edit, gridrow, 1, 1, 13)
        form1.addWidget(self.sourcedir_button, gridrow, 14, 1, 1)
        gridrow += 1
        form1.addWidget(self.recursive_checkbox, gridrow, 1, 1, 13)
        gridrow += 1
        label = QtWidgets.QLabel('Detector type:')
        form1.addWidget(label, gridrow, 0, 1, 1)
        form1.addWidget(self.detectortype_combo, gridrow, 1, 1, 13)
        form1.addWidget(self.sourcecontent_button, gridrow, 14, 1, 1)
        gridrow += 1
#         form1.addWidget(self.sourcefiles_tableview, gridrow, 1, 1, 15)
        form1.addWidget(items_listview, gridrow, 1, 1, 15)
        gridrow += 1
        hbox1 = QtWidgets.QHBoxLayout()
        hbox1.addWidget(clearall_button)
        hbox1.addWidget(markall_button)
        label = QtWidgets.QLabel('Filter:')
        hbox1.addWidget(label)
        hbox1.addWidget(self.filter_edit,20)
        hbox1.addWidget(self.filterclear_button)
        form1.addLayout(hbox1, gridrow, 1, 1, 15)
        gridrow += 1
        label = QtWidgets.QLabel('Target:')
        form1.addWidget(label, gridrow, 0, 1, 1)
        gridrow += 1
        label = QtWidgets.QLabel('To detector:')
        form1.addWidget(label, gridrow, 0, 1, 1)
        form1.addWidget(self.detector_combo, gridrow, 1, 1, 14)
        # 
        hbox1 = QtWidgets.QHBoxLayout()
        hbox1.addStretch(10)
        hbox1.addWidget(cancel_button)
        hbox1.addWidget(self.importwavefiles_button)
        # 
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(form1, 20)
        layout.addLayout(hbox1)
        # 
        return layout
    
    def update_event_list(self):
        """ """
        self.detector_combo.clear()
        survey = hdf54bats.Hdf5Survey(self.dir_path, self.survey_name)
        event = hdf54bats.Hdf5Event(self.dir_path, self.survey_name)
        for event_group in sorted(survey.get_children('')):
            for detector_group in sorted(event.get_children(event_group)):
                self.detector_combo.addItem(detector_group)
                
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
    
    def load_data(self):
        """ """
        dir_path = str(self.sourcedir_edit.text())
        scanner = app_core.WaveFileScanner()
        dataframe = scanner.get_file_info_as_dataframe(dir_path)
                
#         model = app_framework.PandasModel(dataframe[['file_name', 'file_path', 'frame_rate_hz']])
        model = app_framework.PandasModel(dataframe[
        ['file_stem', 'file_name', 'detector_id', 'datetime', 'datetime_str', 'latitude_dd',
        'longitude_dd', 'latlong_str', 'rec_type', 'frame_rate_hz',
        'file_frame_rate_hz', 'is_te', 'comments', 'dir_path', 
        'file_path', 'abs_file_path']
                                                    ])
#         self.sourcefiles_tableview.setModel(model)
        
        path_array = list(dataframe['abs_file_path'])
        print('abs_file_path: ', path_array)
        
        for wave_file_path in sorted(path_array):
#                 self.groupid_combo.addItem(event_group)
                item = QtGui.QStandardItem(wave_file_path)
                item.setCheckState(QtCore.Qt.Unchecked)
                item.setCheckable(True)
                self._items_model.appendRow(item)

        
#        ['detector_id', 'datetime', 'datetime_str', 'latitude_dd',
#        'longitude_dd', 'latlong_str', 'rec_type', 'frame_rate_hz',
#        'file_frame_rate_hz', 'is_te', 'comments', 'dir_path', 'file_name',
#        'file_path', 'file_stem', 'abs_file_path']
        
        
        
        
#         self.sourcefiles_tableview.resizeColumnsToContents()


    def _import_wavefiles(self):
        """ """
        try:        
            detectorgroup = self.detector_combo.currentText()
            self._parentwidget._write_to_status_bar('- Busy: Importing wave files.')
            
            h5wavefile = hdf54bats.Hdf5Wavefile(self.dir_path, self.survey_name)
            wurb_utils = dsp4bats.WurbFileUtils()
            
            for rowindex in range(self._items_model.rowCount()):
                item = self._items_model.item(rowindex, 0)
                if item.checkState() == QtCore.Qt.Checked:
                    wave_file_path = str(item.text())
#                     wave.remove_wavefile(item_id)
                    
                    wave_reader = None
                    try:
                        metadata = wurb_utils.extract_metadata(wave_file_path)
                        
                        file_name = metadata['file_name']
                        title = file_name
                        if 'datetime_str' in metadata:
                            datetime_str = metadata['datetime_str'][0:15]
                            name = 'wave_' + hdf54bats.str_to_ascii(datetime_str)
                        else:
                            name = metadata['file_stem'].lower()
                        
                        self._parentwidget._write_to_status_bar('- Busy: Importing: ' + file_name)
                    
                        wave_reader = dsp4bats.WaveFileReader(wave_file_path)
                        signal = np.array([], dtype=np.int16)
                        buffer = wave_reader.read_buffer(convert_to_float=False)
                        while len(buffer) > 0:
                            signal = np.append(signal, buffer)
                            buffer = wave_reader.read_buffer(convert_to_float=False)
                    finally:
                        if wave_reader:
                            wave_reader.close()
                
                    h5wavefile.add_wavefile(detectorgroup, name, title, signal)
                    
                    h5wavefile.set_user_metadata(detectorgroup + '.' + name, metadata)
                
            self._parentwidget._write_to_status_bar('')
            
#             self._parentwidget._emit_change_notification()
            self.accept() # Close dialog box.
        #
        except Exception as e:
            debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
            app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))
            self.accept() # Close dialog box.

        
#         try:
#             self._parentwidget._write_to_status_bar("Importing wave files.")
#             
#             h5wavefile = hdf54bats.Hdf5Wavefile(self.dir_path, self.survey_name)
#             detectorgroup = self.detector_combo.currentText()
#             
#             detector_name = str(self._detectorname_edit.text())
#             
# #             wave_file = '/home/arnold/Desktop/batfiles/WURB2_20180908T212225+0200_N57.6627E12.6393_TE384_Myotis.wav'
# 
# 
#             wurb_utils = dsp4bats.WurbFileUtils()
# #             metadata = wurb_utils.extract_metadata(wave_file)
#             
#             wurb_utils.find_sound_files(dir_path='/home/arnold/Desktop/batfiles', recursive=True, wurb_files_only=True)            
#             df = wurb_utils.get_dataframe()
#             for wave_file in df.abs_file_path:
#                 self._parentwidget._write_to_status_bar('- Busy: Importing wave files.')
#                 try:
#                     metadata = wurb_utils.extract_metadata(wave_file)
#                     
#                     file_name = metadata['file_name']
#                     title = file_name
#                     datetime_str = metadata['datetime_str'][0:15]
#                     name = 'wave_' + hdf54bats.str_to_ascii(datetime_str)
#                     
#                     self._parentwidget._write_to_status_bar('- Busy: Importing: ' + file_name)
#                 
#                     wave_reader = dsp4bats.WaveFileReader(wave_file)
#                     signal = np.array([], dtype=np.int16)
#                     buffer = wave_reader.read_buffer(convert_to_float=False)
#                     while len(buffer) > 0:
#                         signal = np.append(signal, buffer)
#                         buffer = wave_reader.read_buffer(convert_to_float=False)
#                 finally:
#                     wave_reader.close()
#                 
#                 h5wavefile.add_wavefile(detectorgroup, name, title, signal)
#                 
#                 h5wavefile.set_user_metadata(detectorgroup + '.' + name, metadata)
# 
#             self._parentwidget._write_to_status_bar('')

#             import struct
#             import wave
#             waveFile = wave.open(wave_file, 'rb')
#             print('Frame number: ', waveFile.getnframes())
#             try:
#                 signal = np.array([], dtype=np.int16)
#                 buffer = waveFile.readframes(100000)
#                 while len(buffer) > 0:
#                     bufflength = int(len(buffer) / 2)
#                     struct_format = '<' + str(bufflength) + 'h'
#                     buffer2 = struct.unpack(struct_format, buffer)
#                     signal = np.append(signal, np.int16(buffer2))
#                     buffer = waveFile.readframes(100000)
#             finally:
#                 waveFile.close()
# 
#             print('Signal size: ', len(signal))
#             
# #             wave_data = np.array([1,2,3,4,5,], dtype=np.int16)
# #             wave_data = np.array(buffer, dtype=np.int16)
#             
#             print('DTYPE signal: ', signal.dtype)
            
            
#             detector = hdf54bats.Hdf5Detector(self.dir_path, self.survey_name)
#             eventgroup = self.detector_combo.currentText()
#             detectorname = str(self._detectorname_edit.text())
#             detectorgroup = str(self._detectorgroup_edit.text())
#             detector.add_detector(parents=eventgroup, name=detectorgroup, title=detectorname)
            self.accept() # Close dialog box.
        except Exception as e:
            self._parentwidget._write_to_status_bar('')
            print('TODO: ERROR: ', e)
            self.accept() # Close dialog box.


class DeleteDialog(QtWidgets.QDialog):
    """ This dialog is allowed to access private parts in the parent widget. """
    def __init__(self, parentwidget):
        """ """
        super(DeleteDialog, self).__init__(parentwidget)
        self.setWindowTitle("Delete wavefile(s)")
        self._parentwidget = parentwidget
        self.setLayout(self._content())
        self.setMinimumSize(500, 500)
        #
        self.dir_path = str(self._parentwidget.workspacedir_edit.text())
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
        self._main_tab_widget.addTab(self._item_content(), 'Delete wavefile(s)')
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
        delete_button = QtWidgets.QPushButton('Delete marked wavefile(s)')
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

    def _load_item_data(self):
        """ """
        try:
            self._items_model.clear()
            wave = hdf54bats.Hdf5Wavefile(self.dir_path, self.survey_name)
            
            from_top_node = ''
            wavefiles_dict = wave.get_wavefiles(from_top_node)
            
            for wave_id in sorted(wavefiles_dict):
#                 self.groupid_combo.addItem(event_group)
                item = QtGui.QStandardItem(wave_id)
                item.setCheckState(QtCore.Qt.Unchecked)
                item.setCheckable(True)
                self._items_model.appendRow(item)
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
            wave = hdf54bats.Hdf5Wavefile(self.dir_path, self.survey_name)
            for rowindex in range(self._items_model.rowCount()):
                item = self._items_model.item(rowindex, 0)
                if item.checkState() == QtCore.Qt.Checked:
                    item_id = str(item.text())
                    wave.remove_wavefile(item_id)
            
#             self._parentwidget._emit_change_notification()
            self.accept() # Close dialog box.
        #
        except Exception as e:
            debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
            app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))
            self.accept() # Close dialog box.


