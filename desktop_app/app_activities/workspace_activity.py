#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: http://cloudedbats.org
# Copyright (c) 2018 Arnold Andreasson 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import sys
import string
import pathlib
import pandas
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

import hdf54bats
import metadata4bats
from desktop_app import app_framework
from desktop_app import app_utils

class WorkspaceActivity(app_framework.ActivityBase):
    """ """

    def __init__(self, name, parentwidget):
        """ """
        self._last_used_dir_path = None
        # Initialize parent. Should be called after other 
        # initialization since the base class calls _create_content().
        super(WorkspaceActivity, self).__init__(name, parentwidget)
        
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
        self.workspacedir_edit.textChanged.connect(self.refresh_survey_list)
        self.workspacedir_button = QtWidgets.QPushButton('Browse...')
        self.workspacedir_button.clicked.connect(self.workspace_dir_browse)
        
        self.surveys_tableview = app_framework.ToolboxQTableView()
#         self.surveys_tableview = app_framework.SelectableQListView()
#         self.surveys_tableview = QtWidgets.QTableView()
#        self.surveys_tableview.setSortingEnabled(True)
        
        # Buttons.
        self.refresh_button = QtWidgets.QPushButton('Refresh...')
        self.refresh_button.clicked.connect(self.refresh_survey_list)
        self.add_button = QtWidgets.QPushButton('Add survey...')
        self.add_button.clicked.connect(self.add_survey)
        self.rename_button = QtWidgets.QPushButton('Rename survey...')
        self.rename_button.clicked.connect(self.rename_survey)
        self.copy_button = QtWidgets.QPushButton('Copy survey...')
        self.copy_button.clicked.connect(self.copy_survey)
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
        form1.addWidget(self.refresh_button, gridrow, 14, 1, 1)
        gridrow += 1
        form1.addWidget(self.surveys_tableview, gridrow, 0, 1, 15)
        gridrow += 1
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.add_button)
        hlayout.addWidget(self.rename_button)
        hlayout.addWidget(self.copy_button)
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
        title_list = []
        h5_path_list = []
        # Table.
        h5_list = ws.get_hdf5_list()
        for h5_file_key in sorted(h5_list.keys()):
            h5_file_dict = h5_list[h5_file_key]
            print('HDF5 file: ', h5_file_dict)
            # Table.
            survey_list.append(h5_file_dict['name'])
            title_list.append(h5_file_dict['title'])
            h5_path_list.append(h5_file_dict['f5_filepath'])
        #
#         dataframe = pandas.DataFrame(survey_list, hdf5_path_list, columns=['survey', 'hdf5_path'])
        dataframe = pandas.DataFrame({'survey_file': survey_list, 
                                      'survey_title': title_list, 
                                      'h5_path': h5_path_list})
        model = app_framework.PandasModel(dataframe[['survey_title', 'survey_file', 'h5_path']])
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
            my_dialog = NewSurveyDialog(self)
            if my_dialog.exec_():
                self.refresh_survey_list()
        except Exception as e:
            debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
            app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))

    def rename_survey(self):
        """ """
        try:        
            my_dialog = RenameSurveyDialog(self)
            if my_dialog.exec_():
                self.refresh_survey_list()
        except Exception as e:
            debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
            app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))

    def copy_survey(self):
        """ """
        try:        
            my_dialog = CopySurveyDialog(self)
            if my_dialog.exec_():
                self.refresh_survey_list()
        except Exception as e:
            debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
            app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))
        
    def delete_survey(self):
        """ """
        try:        
            dialog = DeleteDialog(self)
            if dialog.exec_():
                self.refresh_survey_list()
        except Exception as e:
            debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
            app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))


#         try:
#             dir_path = str(self.workspacedir_edit.text())
#             name_combo = self.name_combo.currentText()
#             ws = hdf54bats.Hdf5Workspace(dir_path)
#             ws.delete_hdf5(name_combo)
#             self.refresh_survey_list()
#         except Exception as e:
#             print('TODO: ERROR: ', e)

        
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

### Utility:
def str_to_valid_ascii(text):
    """
        TODO: Move this to utilities.
    """
    new_text = []
    for c in text.lower().replace(' ', '_'):
        if c in string.ascii_lowercase:
            new_text.append(c)
        elif c in string.digits:
            new_text.append(c)
        elif c in string.punctuation:
            new_text.append('_')
        else:
            if c == 'å': new_text.append('a')
            elif c == 'ä': new_text.append('a')
            elif c == 'ö': new_text.append('o')
            else: new_text.append('_')
    
    return ''.join(new_text)



class NewSurveyDialog(QtWidgets.QDialog):
    """ This dialog is allowed to access private parts in the parent widget. """
    def __init__(self, parentwidget):
        """ """
        super().__init__(parentwidget)
        self.setWindowTitle("New survey")
        self._parentwidget = parentwidget
        self.setLayout(self._content())

    def _content(self):
        """ """
        self._surveyname_edit = QtWidgets.QLineEdit('')
        self._surveyname_edit.setMinimumWidth(400)
        self._surveyfilename_edit = QtWidgets.QLineEdit('')
        self._surveyfilename_edit.setMinimumWidth(400)
        self._surveyfilename_edit.setEnabled(False)
        self._surveyname_edit.textChanged.connect(self._update_filename)
        cancel_button = QtWidgets.QPushButton('Cancel')
        cancel_button.clicked.connect(self.reject) # Close dialog box.               
        self.createsurvey_button = QtWidgets.QPushButton('Create survey')
        self.createsurvey_button.clicked.connect(self._create_survey)
        self.createsurvey_button.setEnabled(False)
        self.createsurvey_button.setDefault(False)
        # Layout widgets.
        formlayout = QtWidgets.QFormLayout()
        formlayout.addRow('Survey name:', self._surveyname_edit)
        formlayout.addRow('Survey filename:', self._surveyfilename_edit)
        # 
        hbox1 = QtWidgets.QHBoxLayout()
        hbox1.addStretch(10)
        hbox1.addWidget(cancel_button)
        hbox1.addWidget(self.createsurvey_button)
        # 
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(formlayout, 10)
        layout.addLayout(hbox1)
        # 
        return layout
    
    def _update_filename(self, text):
        """ """
        new_text = str_to_valid_ascii(text)
        if len(new_text) > 0:
            self._surveyfilename_edit.setText(new_text + '.h5')
            self.createsurvey_button.setEnabled(True)
            self.createsurvey_button.setDefault(True)
        else:
            self._surveyfilename_edit.setText('')
            self.createsurvey_button.setEnabled(False)
            self.createsurvey_button.setDefault(False)

    def _create_survey(self):
        """ """
        try:
            dir_path = str(self._parentwidget.workspacedir_edit.text())
            name = str(self._surveyname_edit.text())
            filename = str(self._surveyfilename_edit.text())
            ws = hdf54bats.Hdf5Workspace(dir_path, create_ws=True)
            ws.create_hdf5(filename, title=name)
            self.accept() # Close dialog box.
        except Exception as e:
            print('TODO: ERROR: ', e)
            self.accept() # Close dialog box.


class RenameSurveyDialog(QtWidgets.QDialog):
    """ This dialog is allowed to access private parts in the parent widget. """
    def __init__(self, parentwidget):
        """ """
        super().__init__(parentwidget)
        self.setWindowTitle("Rename survey")
        self._parentwidget = parentwidget
        self.setLayout(self._content())
        # 
        self.update_survey_list()
    
    def _content(self):
        """ """
        self.name_combo = QtWidgets.QComboBox()
        self.name_combo.setEditable(False)
        self.name_combo.setMinimumWidth(400)
        self.name_combo.currentIndexChanged.connect(self._set_filename)
        
        self._surveyname_edit = QtWidgets.QLineEdit('')
        self._surveyname_edit.setMinimumWidth(400)
        self._surveyfilename_edit = QtWidgets.QLineEdit('')
        self._surveyfilename_edit.setMinimumWidth(400)
        self._surveyfilename_edit.setEnabled(False)
        self._surveyname_edit.textChanged.connect(self._update_filename)
        cancel_button = QtWidgets.QPushButton('Cancel')
        cancel_button.clicked.connect(self.reject) # Close dialog box.               
        self.renamesurvey_button = QtWidgets.QPushButton('Rename survey')
        self.renamesurvey_button.clicked.connect(self._rename_survey)
        self.renamesurvey_button.setEnabled(False)
        self.renamesurvey_button.setDefault(False)
        # Layout widgets.
        formlayout = QtWidgets.QFormLayout()
        formlayout.addRow('Select survey:', self.name_combo)
        formlayout.addRow('New name:', self._surveyname_edit)
        formlayout.addRow('New filename:', self._surveyfilename_edit)
        # 
        hbox1 = QtWidgets.QHBoxLayout()
        hbox1.addStretch(10)
        hbox1.addWidget(cancel_button)
        hbox1.addWidget(self.renamesurvey_button)
        # 
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(formlayout, 10)
        layout.addLayout(hbox1)
        # 
        return layout
    
    def update_survey_list(self):
        """ """
        dir_path = str(self._parentwidget.workspacedir_edit.text())
        ws = hdf54bats.Hdf5Workspace(dir_path)
        # Combo.
        self.name_combo.clear()
        h5_list = ws.get_hdf5_list()
        for h5_file_key in sorted(h5_list.keys()):
            h5_file_dict = h5_list[h5_file_key]
            print('HDF5 file: ', h5_file_dict)
            # Combo.
            self.name_combo.addItem(h5_file_dict['name'])
    
    def _set_filename(self, _index):
        """ """
        survey_name = str(self.name_combo.currentText())
        if survey_name:
            dir_path = str(self._parentwidget.workspacedir_edit.text())
            ws = hdf54bats.Hdf5Workspace(dir_path)
            title = ws.get_hdf5_title(survey_name)
            self._surveyname_edit.setText(title)
        else:
            self._surveyname_edit.setText('')
    
    def _update_filename(self, text):
        """ """
        new_text = str_to_valid_ascii(text)
        if len(new_text) > 0:
            self._surveyfilename_edit.setText(new_text + '.h5')
            self.renamesurvey_button.setEnabled(True)
            self.renamesurvey_button.setDefault(True)
        else:
            self._surveyfilename_edit.setText('')
            self.renamesurvey_button.setEnabled(False)
            self.renamesurvey_button.setDefault(False)

    def _rename_survey(self):
        """ """
        try:
            dir_path = str(self._parentwidget.workspacedir_edit.text())
            name_combo = self.name_combo.currentText()
            name = self._surveyname_edit.text()
            filename = self._surveyfilename_edit.text()
            ws = hdf54bats.Hdf5Workspace(dir_path)
            ws.rename_hdf5(name_combo, filename)
            ws.set_hdf5_title(filename, name)
            self.update_survey_list()
            self.accept() # Close dialog box.
        except Exception as e:
            print('TODO: ERROR: ', e)
            self.accept() # Close dialog box.


class CopySurveyDialog(QtWidgets.QDialog):
    """ This dialog is allowed to access private parts in the parent widget. """
    def __init__(self, parentwidget):
        """ """
        super().__init__(parentwidget)
        self.setWindowTitle("Copy survey")
        self._parentwidget = parentwidget
        self.setLayout(self._content())
        # 
        self.update_survey_list()
    
    def _content(self):
        """ """
        self.name_combo = QtWidgets.QComboBox()
        self.name_combo.setEditable(False)
        self.name_combo.setMinimumWidth(400)
        self.name_combo.currentIndexChanged.connect(self._set_filename)
        
        self._surveyname_edit = QtWidgets.QLineEdit('')
        self._surveyname_edit.setMinimumWidth(400)
        self._surveyfilename_edit = QtWidgets.QLineEdit('')
        self._surveyfilename_edit.setMinimumWidth(400)
        self._surveyfilename_edit.setEnabled(False)
        self._surveyname_edit.textChanged.connect(self._update_filename)
        cancel_button = QtWidgets.QPushButton('Cancel')
        cancel_button.clicked.connect(self.reject) # Close dialog box.               
        self.copysurvey_button = QtWidgets.QPushButton('Copy survey')
        self.copysurvey_button.clicked.connect(self._create_survey)
        self.copysurvey_button.setEnabled(False)
        self.copysurvey_button.setDefault(False)
        # Layout widgets.
        formlayout = QtWidgets.QFormLayout()
        formlayout.addRow('Select survey:', self.name_combo)
        formlayout.addRow('Copy to name:', self._surveyname_edit)
        formlayout.addRow('Copy to filename:', self._surveyfilename_edit)
        # 
        hbox1 = QtWidgets.QHBoxLayout()
        hbox1.addStretch(10)
        hbox1.addWidget(cancel_button)
        hbox1.addWidget(self.copysurvey_button)
        # 
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(formlayout, 10)
        layout.addLayout(hbox1)
        # 
        return layout
    
    def update_survey_list(self):
        """ """
        dir_path = str(self._parentwidget.workspacedir_edit.text())
        ws = hdf54bats.Hdf5Workspace(dir_path)
        # Combo.
        self.name_combo.clear()
        h5_list = ws.get_hdf5_list()
        for h5_file_key in sorted(h5_list.keys()):
            h5_file_dict = h5_list[h5_file_key]
            print('HDF5 file: ', h5_file_dict)
            # Combo.
            self.name_combo.addItem(h5_file_dict['name'])

    def _set_filename(self, _index):
        """ """
        survey_name = str(self.name_combo.currentText())
        if survey_name:
            dir_path = str(self._parentwidget.workspacedir_edit.text())
            ws = hdf54bats.Hdf5Workspace(dir_path)
            title = ws.get_hdf5_title(survey_name)
            self._surveyname_edit.setText(title)
        else:
            self._surveyname_edit.setText('')
    
    def _update_filename(self, text):
        """ """
        new_text = str_to_valid_ascii(text)
        if len(new_text) > 0:
            self._surveyfilename_edit.setText(new_text + '.h5')
            self.copysurvey_button.setEnabled(True)
            self.copysurvey_button.setDefault(True)
        else:
            self._surveyfilename_edit.setText('')
            self.copysurvey_button.setEnabled(False)
            self.copysurvey_button.setDefault(False)

    def _create_survey(self):
        """ """
        try:
            dir_path = str(self._parentwidget.workspacedir_edit.text())
            name_combo = self.name_combo.currentText()
            name = self._surveyname_edit.text()
            filename = self._surveyfilename_edit.text()
            ws = hdf54bats.Hdf5Workspace(dir_path)
            ws.copy_hdf5(name_combo, filename)
            ws.set_hdf5_title(filename, name)
            self.update_survey_list()
            self.accept() # Close dialog box.
        except Exception as e:
            print('TODO: ERROR: ', e)
            self.accept() # Close dialog box.


class DeleteDialog(QtWidgets.QDialog):
    """ This dialog is allowed to access private parts in the parent widget. """
    def __init__(self, parentwidget):
        """ """
        super(DeleteDialog, self).__init__(parentwidget)
        self.setWindowTitle("Delete datasets and samples")
        self._parentwidget = parentwidget
        self.setLayout(self._content())
        self.setMinimumSize(500, 500)
        self._load_dataset_data()
#         self._load_sample_data()
        
    def _content(self):
        """ """  
        contentLayout = QtWidgets.QVBoxLayout(self)
        self.setLayout(contentLayout)
        #
        self._main_tab_widget = QtWidgets.QTabWidget(self)
        contentLayout.addWidget(self._main_tab_widget)
        self._main_tab_widget.addTab(self._dataset_content(), 'Delete datasets')
#         self._main_tab_widget.addTab(self._sample_content(), 'Delete samples')
        
        return contentLayout                

    # DATASETS.
    
    def _dataset_content(self):
        """ """
        widget = QtWidgets.QWidget()
        #  
        datasets_listview = QtWidgets.QListView()
        self._datasets_model = QtGui.QStandardItemModel()
        datasets_listview.setModel(self._datasets_model)

        clearall_button = app_framework.ClickableQLabel('Clear all')
        clearall_button.label_clicked.connect(self._uncheck_all_datasets)                
        markall_button = app_framework.ClickableQLabel('Mark all')
        markall_button.label_clicked.connect(self._check_all_datasets)                
        cancel_button = QtWidgets.QPushButton('Cancel')
        cancel_button.clicked.connect(self.reject) # Close dialog box.               
        delete_button = QtWidgets.QPushButton('Delete marked dataset(s)')
        delete_button.clicked.connect(self._delete_marked_datasets)               
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
        layout.addWidget(datasets_listview, 10)
        layout.addLayout(hbox1)
        layout.addLayout(hbox2)
        #
        widget.setLayout(layout)
        #
        return widget                

    def _load_dataset_data(self):
        """ """
        try:
            self._datasets_model.clear()
            dir_path = str(self._parentwidget.workspacedir_edit.text())
            ws = hdf54bats.Hdf5Workspace(dir_path)
            h5_list = ws.get_hdf5_list()
            for h5_file_key in sorted(h5_list.keys()):
                item = QtGui.QStandardItem(h5_file_key)
                item.setCheckState(QtCore.Qt.Unchecked)
                item.setCheckable(True)
                self._datasets_model.appendRow(item)
        #
        except Exception as e:
            debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
            app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))
            
    def _check_all_datasets(self):
        """ """
        try:        
            for rowindex in range(self._datasets_model.rowCount()):
                item = self._datasets_model.item(rowindex, 0)
                item.setCheckState(QtCore.Qt.Checked)
        #
        except Exception as e:
            debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
            app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))
            
    def _uncheck_all_datasets(self):
        """ """
        try:        
            for rowindex in range(self._datasets_model.rowCount()):
                item = self._datasets_model.item(rowindex, 0)
                item.setCheckState(QtCore.Qt.Unchecked)
        #
        except Exception as e:
            debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
            app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))

    def _delete_marked_datasets(self):
        """ """
        try:        
            dir_path = str(self._parentwidget.workspacedir_edit.text())
            ws = hdf54bats.Hdf5Workspace(dir_path)
            for rowindex in range(self._datasets_model.rowCount()):
                item = self._datasets_model.item(rowindex, 0)
                if item.checkState() == QtCore.Qt.Checked:
                    survey_filename = str(item.text())
                    ws.delete_hdf5(survey_filename)
            #
#             self._parentwidget._emit_change_notification()
            self.accept() # Close dialog box.
        #
        except Exception as e:
            debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
            app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))
            self.accept() # Close dialog box.

#     # SAMPLES.
#     
#     def _sample_content(self):
#         """ """  
#         widget = QtWidgets.QWidget()
#         #  
#         samples_listview = QtWidgets.QListView()
#         self._samples_model = QtGui.QStandardItemModel()
#         samples_listview.setModel(self._samples_model)
#         #
#         clearall_button = app_framework.ClickableQLabel('Clear all')
#         clearall_button.label_clicked.connect(self._uncheck_all_samples)                
#         markall_button = app_framework.ClickableQLabel('Mark all')
#         markall_button.label_clicked.connect(self._check_all_samples)                
#         delete_button = QtWidgets.QPushButton('Delete marked sample(s)')
#         delete_button.clicked.connect(self._delete_marked_samples)               
#         cancel_button = QtWidgets.QPushButton('Cancel')
#         cancel_button.clicked.connect(self.reject) # Close dialog box.               
#         # Layout widgets.
#         hbox1 = QtWidgets.QHBoxLayout()
#         hbox1.addWidget(clearall_button)
#         hbox1.addWidget(markall_button)
#         hbox1.addStretch(10)
#         #
#         hbox2 = QtWidgets.QHBoxLayout()
#         hbox2.addStretch(10)
#         hbox2.addWidget(delete_button)
#         hbox2.addWidget(cancel_button)
#         #
#         layout = QtWidgets.QVBoxLayout()
#         layout.addWidget(samples_listview, 10)
#         layout.addLayout(hbox1)
#         layout.addLayout(hbox2)
#         #
#         widget.setLayout(layout)
#         #
#         return widget                
# 
#     def _load_sample_data(self):
#         """ """
#         try:        
#             self._samples_model.clear()        
#             for datasetname in plankton_core.PlanktonCounterManager().get_dataset_names():
#                 item = QtGui.QStandardItem('Dataset: ' + datasetname)
#                 self._samples_model.appendRow(item)
#                 # Samples.
#                 for samplename in plankton_core.PlanktonCounterManager().get_sample_names(datasetname):
#                     item = QtGui.QStandardItem(samplename)
#                     item.setCheckState(QtCore.Qt.Unchecked)
#                     item.setCheckable(True)
#                     self._samples_model.appendRow(item)
#         #
#         except Exception as e:
#             debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
#             toolbox_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))
#             
#     def _check_all_samples(self):
#         """ """
#         try:        
#             for rowindex in range(self._samples_model.rowCount()):
#                 item = self._samples_model.item(rowindex, 0)
#                 if item.isCheckable ():
#                     item.setCheckState(QtCore.Qt.Checked)
#         #
#         except Exception as e:
#             debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
#             toolbox_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))
#             
#     def _uncheck_all_samples(self):
#         """ """
#         try:        
#             for rowindex in range(self._samples_model.rowCount()):
#                 item = self._samples_model.item(rowindex, 0)
#                 if item.isCheckable ():
#                     item.setCheckState(QtCore.Qt.Unchecked)
#         #
#         except Exception as e:
#             debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
#             toolbox_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))
# 
#     def _delete_marked_samples(self):
#         """ """
#         try:        
#             datasetname = None
#             samplename = None
#             for rowindex in range(self._samples_model.rowCount()):
#                 item = self._samples_model.item(rowindex, 0)
#                 if str(item.text()).startswith('Dataset: '):
#                     datasetname = str(item.text()).replace('Dataset: ', '')
#                 if item.checkState() == QtCore.Qt.Checked:
#                     samplename = str(item.text())
#                     print(samplename)
#                     plankton_core.PlanktonCounterManager().delete_sample(datasetname, samplename)
#             #            
#             self.accept() # Close dialog box.
#         #
#         except Exception as e:
#             debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
#             toolbox_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))
