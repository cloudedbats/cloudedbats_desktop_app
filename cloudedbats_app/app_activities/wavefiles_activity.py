#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: http://cloudedbats.org
# Copyright (c) 2018 Arnold Andreasson 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import sys
import numpy as np
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

import hdf54bats
import dsp4bats
from cloudedbats_app import app_framework
from cloudedbats_app import app_utils
from cloudedbats_app import app_core
from platform import node


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
#         tabWidget.addTab(self._content_adv_filter(), 'Advanced filter')
        tabWidget.addTab(self._content_help(), 'Help')
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
        self.clear_filter_button = QtWidgets.QPushButton('Clear')
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
        self.add_button = QtWidgets.QPushButton('Import wavefile...')
        self.add_button.clicked.connect(self.import_wavefile)
        self.rename_button = QtWidgets.QPushButton('(Rename wavefile...)')
        self.rename_button.clicked.connect(self.rename_wavefile)
        self.delete_button = QtWidgets.QPushButton('Delete wavefile(s)...')
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
        hlayout.addWidget(QtWidgets.QLabel('Type filter:'), 1)
        hlayout.addWidget(self.type_filter_combo, 5)
        hlayout.addWidget(QtWidgets.QLabel('Title filter:'), 1)
        hlayout.addWidget(self.title_filter_edit, 10)
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
                item_id = str(self.wavefiles_tableview.model().index(modelIndex.row(), 0).data())
                # Sync.
                app_core.DesktopAppSync().set_selected_item_id(item_id)
        except Exception as e:
#             pass
            print('Exception: ', e)
    
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
            h5wavefile = hdf54bats.Hdf5Wavefiles(self.dir_path, self.survey_name)
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
            dataset_table.set_header(['item_id', 'item_type', 'item_title'])
            for key in sorted(events_dict.keys()):
                item_dict = events_dict.get(key, {})
                row = []
                item_id = item_dict.get('item_id', '')
                item_type = item_dict.get('item_type', '')
                row.append(item_id)
                row.append(item_type)
                row.append(item_dict.get('item_title', ''))
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
#                     except Exception as e:
#                         print('EXCEPTION: ', e)
                    
            #
            self.wavefiles_tableview.setTableModel(dataset_table)
            self.wavefiles_tableview.resizeColumnsToContents()
        finally:
            self.wavefiles_tableview.blockSignals(False)
            self.wavefiles_tableview.getSelectionModel().blockSignals(False)
    
    def import_wavefile(self):
        """ """
        try:        
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
            dialog = DeleteDialog(self)
            if dialog.exec_():
                self.refresh()
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
        self.dir_path = app_core.DesktopAppSync().get_workspace()
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
            print('EXCEPTION: ', e)
                
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
        
        path_array = list(dataframe['abs_file_path'])
        print('abs_file_path: ', path_array)
        
        for wave_file_path in sorted(path_array):
#                 self.groupid_combo.addItem(event_group)
                item = QtGui.QStandardItem(wave_file_path)
                item.setCheckState(QtCore.Qt.Unchecked)
                item.setCheckable(True)
                self._items_model.appendRow(item)

    def _import_wavefiles(self):
        """ """
        try:        
            try:
                detectorgroup = self.detector_combo.currentText()
                self._parentwidget._write_to_status_bar('- Busy: Importing wave files.')
                
                h5wavefile = hdf54bats.Hdf5Wavefiles(self.dir_path, self.survey_name)
                wurb_utils = dsp4bats.WurbFileUtils()
                
                for rowindex in range(self._items_model.rowCount()):
                    try:
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
                        
                            h5wavefile.add_wavefile(parent_id=detectorgroup, new_name=name, title=title, array=signal)
                            
                            h5wavefile.set_user_metadata(detectorgroup + '.' + name, metadata)
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
        self.setWindowTitle("Delete wavefile(s)")
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
                wave = hdf54bats.Hdf5Wavefiles(self.dir_path, self.survey_name)
                for rowindex in range(self._items_model.rowCount()):
                    item = self._items_model.item(rowindex, 0)
                    if item.checkState() == QtCore.Qt.Checked:
                        item_id = str(item.text())
                        wave.remove_wavefile(item_id, recursive=True)
            finally:
                self.accept() # Close dialog box.
        #
        except Exception as e:
            debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
            app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))


