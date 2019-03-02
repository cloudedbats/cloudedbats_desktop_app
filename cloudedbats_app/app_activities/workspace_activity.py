#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: http://cloudedbats.org
# Copyright (c) 2018 Arnold Andreasson 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import sys
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

import hdf54bats
from cloudedbats_app import app_framework
from cloudedbats_app import app_utils
from cloudedbats_app import app_core

class WorkspaceActivity(app_framework.ActivityBase):
    """ """

    def __init__(self, name, parentwidget):
        """ """
        self._last_used_dir_path = None
        # Initialize parent. Should be called after other 
        # initialization since the base class calls _create_content().
        super(WorkspaceActivity, self).__init__(name, parentwidget)
        
        # Use sync object for workspaces and surveys. 
        app_core.DesktopAppSync().workspace_changed.connect(self.refresh_survey_list)
        app_core.DesktopAppSync().survey_changed.connect(self.refresh_survey_list)
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
        self.workspacedir_edit.textChanged.connect(self.workspace_changed)
        self.workspacedir_button = QtWidgets.QPushButton('Browse...')
        self.workspacedir_button.clicked.connect(self.workspace_dir_browse)
        
        self.surveys_tableview = app_framework.ToolboxQTableView()
        self.surveys_tableview.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
#         self.surveys_tableview.clicked.connect(self.selected_survey_changed)
        self.surveys_tableview.getSelectionModel().selectionChanged.connect(self.selected_survey_changed)
        
        # Buttons.
        self.refresh_button = QtWidgets.QPushButton('Refresh')
        self.refresh_button.clicked.connect(self.refresh)
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
        dirdialog.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        dirdialog.setFileMode(QtWidgets.QFileDialog.Directory)
        dirdialog.setOptions(QtWidgets.QFileDialog.ShowDirsOnly |
                             QtWidgets.QFileDialog.DontResolveSymlinks)
        dirdialog.setDirectory(str(self.workspacedir_edit.text()))
        dirpath = dirdialog.getExistingDirectory()
        if dirpath:
            self.workspacedir_edit.setText(dirpath)

    def refresh(self):
        """ """
        app_core.DesktopAppSync().refresh()
    
    def workspace_changed(self):
        """ """
        dir_path = str(self.workspacedir_edit.text())
        app_core.DesktopAppSync().set_workspace(dir_path)
    
    def refresh_survey_list(self):
        """ """
        try:
            self.surveys_tableview.blockSignals(True)
            self.surveys_tableview.getSelectionModel().blockSignals(True)
            #
            selected_workspace = app_core.DesktopAppSync().get_workspace()
            h5_survey_dict = app_core.DesktopAppSync().get_surveys_dict()
            h5_selected_survey = app_core.DesktopAppSync().get_selected_survey()
            #
            dataset_table = app_framework.DatasetTable()
            header = ['h5_file', 'h5_title', 'h5_filepath']
            dataset_table.set_header(header)
#             header_cap = []
#             for item in header:
#                 header_cap.append(item.capitalize().replace('_', ' '))
#             dataset_table.set_header(header_cap)
            #
            try:
                self.workspacedir_edit.blockSignals(True)
                self.workspacedir_edit.setText(selected_workspace)
            finally:
                self.workspacedir_edit.blockSignals(False)
            #
            selected_survey_index = None
            for index, key in enumerate(sorted(h5_survey_dict)):
                h5_dict = h5_survey_dict[key]
                row = []
                for head in header:
                    row.append(h5_dict.get(head, ''))
                dataset_table.append_row(row)
                h5_file = h5_dict.get('h5_file', None)
                if h5_file and (h5_file == h5_selected_survey):
                    selected_survey_index = index
            #
            self.surveys_tableview.setTableModel(dataset_table)
            self.surveys_tableview.resizeColumnsToContents()
            #
            if selected_survey_index is not None:
                qt_index =self.surveys_tableview.model().index(selected_survey_index, 0)
                self.surveys_tableview.setCurrentIndex(qt_index)
        finally:
            self.surveys_tableview.blockSignals(False)
            self.surveys_tableview.getSelectionModel().blockSignals(False)
        
    
    def selected_survey_changed(self):
        """ """
        try:
            modelIndex = self.surveys_tableview.currentIndex()
            if modelIndex.isValid():
                h5_survey = self.surveys_tableview.model().index(modelIndex.row(), 0).data()
                app_core.DesktopAppSync().set_selected_survey(h5_survey)
        except:
            pass
    
    def add_survey(self):
        """ """
        try:        
            my_dialog = NewSurveyDialog(self)
            if my_dialog.exec_():
                self.refresh()
        except Exception as e:
            debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
            app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))
    
    def rename_survey(self):
        """ """
        try:        
            my_dialog = RenameSurveyDialog(self)
            if my_dialog.exec_():
                self.refresh()
        except Exception as e:
            debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
            app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))
    
    def copy_survey(self):
        """ """
        try:        
            my_dialog = CopySurveyDialog(self)
            if my_dialog.exec_():
                self.refresh()
        except Exception as e:
            debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
            app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))
    
    def delete_survey(self):
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
        <h3>Workspace</h3>
        <p>
        Work in progress...
        </p>
        
        """


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
        self._surveytitle_edit = QtWidgets.QLineEdit('')
        self._surveytitle_edit.setMinimumWidth(400)
        self.auto_checkbox = QtWidgets.QCheckBox('Auto')
        self.auto_checkbox.setChecked(True)
        self.auto_checkbox.stateChanged.connect(self.auto_changed)
        self._surveyfilename_edit = QtWidgets.QLineEdit('')
        self._surveyfilename_edit.setMinimumWidth(400)
        self._surveyfilename_edit.setEnabled(False)
        self._surveytitle_edit.textChanged.connect(self._update_filename)
        cancel_button = QtWidgets.QPushButton('Cancel')
        cancel_button.clicked.connect(self.reject) # Close dialog box.               
        self.createsurvey_button = QtWidgets.QPushButton('Create survey')
        self.createsurvey_button.clicked.connect(self._create_survey)
        self.createsurvey_button.setEnabled(False)
        self.createsurvey_button.setDefault(False)
        # Layout widgets.
        form1 = QtWidgets.QGridLayout()
        gridrow = 0
        label = QtWidgets.QLabel('Survey title:')
        form1.addWidget(label, gridrow, 0, 1, 1)
        form1.addWidget(self._surveytitle_edit, gridrow, 1, 1, 9)
        gridrow += 1
        label = QtWidgets.QLabel('Survey filename:')
        form1.addWidget(label, gridrow, 0, 1, 1)
        form1.addWidget(self._surveyfilename_edit, gridrow, 1, 1, 8)
        form1.addWidget(self.auto_checkbox, gridrow, 9, 1, 1)
        # 
        hbox1 = QtWidgets.QHBoxLayout()
        hbox1.addStretch(10)
        hbox1.addWidget(cancel_button)
        hbox1.addWidget(self.createsurvey_button)
        # 
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(form1, 10)
        layout.addLayout(hbox1)
        # 
        return layout
    
    def auto_changed(self):
        """ """
        check_state = self.auto_checkbox.checkState()
        if check_state:
            self._surveyfilename_edit.setEnabled(False)
        else:
            self._surveyfilename_edit.setEnabled(True)
    
    def _update_filename(self, text):
        """ """
        if self.auto_checkbox.checkState():
            new_text = hdf54bats.str_to_ascii(text)
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
            try:
                dir_path = app_core.DesktopAppSync().get_workspace()
                name = str(self._surveytitle_edit.text())
                filename = str(self._surveyfilename_edit.text())
                ws = hdf54bats.Hdf5Workspace(dir_path, create_ws=True)
                ws.create_h5(filename, title=name)
            finally:
                self.accept() # Close dialog box.
        except Exception as e:
            debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
            app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))


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
        
        self._surveytitle_edit = QtWidgets.QLineEdit('')
        self._surveytitle_edit.setMinimumWidth(400)
        self.auto_checkbox = QtWidgets.QCheckBox('Auto')
        self.auto_checkbox.setChecked(True)
        self.auto_checkbox.stateChanged.connect(self.auto_changed)
        self._surveyfilename_edit = QtWidgets.QLineEdit('')
        self._surveyfilename_edit.setMinimumWidth(400)
        self._surveyfilename_edit.setEnabled(False)
        self._surveytitle_edit.textChanged.connect(self._update_filename)
        cancel_button = QtWidgets.QPushButton('Cancel')
        cancel_button.clicked.connect(self.reject) # Close dialog box.               
        self.renamesurvey_button = QtWidgets.QPushButton('Rename survey')
        self.renamesurvey_button.clicked.connect(self._rename_survey)
        self.renamesurvey_button.setEnabled(False)
        self.renamesurvey_button.setDefault(False)
        # Layout widgets.
        form1 = QtWidgets.QGridLayout()
        gridrow = 0
        label = QtWidgets.QLabel('Select survey:')
        form1.addWidget(label, gridrow, 0, 1, 1)
        form1.addWidget(self.name_combo, gridrow, 1, 1, 9)
        gridrow += 1
        label = QtWidgets.QLabel('New title:')
        form1.addWidget(label, gridrow, 0, 1, 1)
        form1.addWidget(self._surveytitle_edit, gridrow, 1, 1, 9)
        gridrow += 1
        label = QtWidgets.QLabel('New filename:')
        form1.addWidget(label, gridrow, 0, 1, 1)
        form1.addWidget(self._surveyfilename_edit, gridrow, 1, 1, 8)
        form1.addWidget(self.auto_checkbox, gridrow, 9, 1, 1)
        # 
        hbox1 = QtWidgets.QHBoxLayout()
        hbox1.addStretch(10)
        hbox1.addWidget(cancel_button)
        hbox1.addWidget(self.renamesurvey_button)
        # 
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(form1, 10)
        layout.addLayout(hbox1)
        # 
        return layout
    
    def update_survey_list(self):
        """ """
        selected_survey = app_core.DesktopAppSync().get_selected_survey()
        survey_dict = app_core.DesktopAppSync().get_surveys_dict()
        self.name_combo.clear()
        index = 0
        for row_index, h5_key in enumerate(sorted(survey_dict)):
            h5_dict = survey_dict[h5_key]
            h5_file = h5_dict['h5_file']
            self.name_combo.addItem(h5_file)
            if h5_file == selected_survey:
                index = row_index
        self.name_combo.setCurrentIndex(index)
    
    def _set_filename(self, _index):
        """ """
        try:
            survey_name = str(self.name_combo.currentText())
            if survey_name:
                dir_path = app_core.DesktopAppSync().get_workspace()
                ws = hdf54bats.Hdf5Workspace(dir_path)
                title = ws.get_h5_title(survey_name)
                self._surveytitle_edit.setText(title)
            else:
                self._surveytitle_edit.setText('')
        except Exception as e:
            debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
            app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))

    
    def auto_changed(self):
        """ """
        check_state = self.auto_checkbox.checkState()
        if check_state:
            self._surveyfilename_edit.setEnabled(False)
        else:
            self._surveyfilename_edit.setEnabled(True)
    
    def _update_filename(self, text):
        """ """
        if self.auto_checkbox.checkState():
            new_text = hdf54bats.str_to_ascii(text)
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
            try:
                dir_path = app_core.DesktopAppSync().get_workspace()
                name_combo = self.name_combo.currentText()
                name = self._surveytitle_edit.text()
                filename = self._surveyfilename_edit.text()
                ws = hdf54bats.Hdf5Workspace(dir_path)
                ws.rename_h5(name_combo, filename)
                ws.set_h5_title(filename, name)
            finally:
                self.accept() # Close dialog box.
        except Exception as e:
            debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
            app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))


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
        
        self._surveytitle_edit = QtWidgets.QLineEdit('')
        self._surveytitle_edit.setMinimumWidth(400)
        self.auto_checkbox = QtWidgets.QCheckBox('Auto')
        self.auto_checkbox.setChecked(True)
        self.auto_checkbox.stateChanged.connect(self.auto_changed)
        self._surveyfilename_edit = QtWidgets.QLineEdit('')
        self._surveyfilename_edit.setMinimumWidth(400)
        self._surveyfilename_edit.setEnabled(False)
        self._surveytitle_edit.textChanged.connect(self._update_filename)
        cancel_button = QtWidgets.QPushButton('Cancel')
        cancel_button.clicked.connect(self.reject) # Close dialog box.               
        self.copysurvey_button = QtWidgets.QPushButton('Copy survey')
        self.copysurvey_button.clicked.connect(self._create_survey)
        self.copysurvey_button.setEnabled(False)
        self.copysurvey_button.setDefault(False)
        # Layout widgets.
        form1 = QtWidgets.QGridLayout()
        gridrow = 0
        label = QtWidgets.QLabel('Select survey:')
        form1.addWidget(label, gridrow, 0, 1, 1)
        form1.addWidget(self.name_combo, gridrow, 1, 1, 9)
        gridrow += 1
        label = QtWidgets.QLabel('Copy to title:')
        form1.addWidget(label, gridrow, 0, 1, 1)
        form1.addWidget(self._surveytitle_edit, gridrow, 1, 1, 9)
        gridrow += 1
        label = QtWidgets.QLabel('Copy to filename:')
        form1.addWidget(label, gridrow, 0, 1, 1)
        form1.addWidget(self._surveyfilename_edit, gridrow, 1, 1, 8)
        form1.addWidget(self.auto_checkbox, gridrow, 9, 1, 1)
        # 
        hbox1 = QtWidgets.QHBoxLayout()
        hbox1.addStretch(10)
        hbox1.addWidget(cancel_button)
        hbox1.addWidget(self.copysurvey_button)
        # 
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(form1, 10)
        layout.addLayout(hbox1)
        # 
        return layout
    
    def update_survey_list(self):
        """ """
        selected_survey = app_core.DesktopAppSync().get_selected_survey()
        survey_dict = app_core.DesktopAppSync().get_surveys_dict()
        self.name_combo.clear()
        index = 0
        for row_index, h5_key in enumerate(sorted(survey_dict)):
            h5_dict = survey_dict[h5_key]
            h5_file = h5_dict['h5_file']
            self.name_combo.addItem(h5_file)
            if h5_file == selected_survey:
                index = row_index
        self.name_combo.setCurrentIndex(index)

    def _set_filename(self, _index):
        """ """
        survey_name = str(self.name_combo.currentText())
        if survey_name:
            dir_path = app_core.DesktopAppSync().get_workspace()
            ws = hdf54bats.Hdf5Workspace(dir_path)
            title = ws.get_h5_title(survey_name)
            self._surveytitle_edit.setText(title)
        else:
            self._surveytitle_edit.setText('')
    
    def auto_changed(self):
        """ """
        check_state = self.auto_checkbox.checkState()
        if check_state:
            self._surveyfilename_edit.setEnabled(False)
        else:
            self._surveyfilename_edit.setEnabled(True)
    
    def _update_filename(self, text):
        """ """
        if self.auto_checkbox.checkState():
            new_text = hdf54bats.str_to_ascii(text)
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
            try:
                dir_path = app_core.DesktopAppSync().get_workspace()
                name_combo = self.name_combo.currentText()
                name = self._surveytitle_edit.text()
                filename = self._surveyfilename_edit.text()
                ws = hdf54bats.Hdf5Workspace(dir_path)
                ws.copy_h5(name_combo, filename)
                ws.set_h5_title(filename, name)
            finally:
                self.accept() # Close dialog box.
        except Exception as e:
            debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
            app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))


class DeleteDialog(QtWidgets.QDialog):
    """ This dialog is allowed to access private parts in the parent widget. """
    def __init__(self, parentwidget):
        """ """
        super(DeleteDialog, self).__init__(parentwidget)
        self.setWindowTitle("Delete surveys")
        self._parentwidget = parentwidget
        self.setLayout(self._content())
        self.setMinimumSize(500, 500)
        self._load_survey_data()
#         self._load_sample_data()
        
    def _content(self):
        """ """  
        contentLayout = QtWidgets.QVBoxLayout(self)
        self.setLayout(contentLayout)
        #
        self._main_tab_widget = QtWidgets.QTabWidget(self)
        contentLayout.addWidget(self._main_tab_widget)
        self._main_tab_widget.addTab(self._survey_content(), 'Delete surveys')
        
        return contentLayout
    
    def _survey_content(self):
        """ """
        widget = QtWidgets.QWidget()
        #  
        surveys_listview = QtWidgets.QListView()
        self._surveys_model = QtGui.QStandardItemModel()
        surveys_listview.setModel(self._surveys_model)

        clearall_button = app_framework.ClickableQLabel('Clear all')
        clearall_button.label_clicked.connect(self._uncheck_all_surveys)                
        markall_button = app_framework.ClickableQLabel('Mark all')
        markall_button.label_clicked.connect(self._check_all_surveys)                
        cancel_button = QtWidgets.QPushButton('Cancel')
        cancel_button.clicked.connect(self.reject) # Close dialog box.               
        delete_button = QtWidgets.QPushButton('Delete marked survey(s)')
        delete_button.clicked.connect(self._delete_marked_surveys)               
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
        layout.addWidget(surveys_listview, 10)
        layout.addLayout(hbox1)
        layout.addLayout(hbox2)
        #
        widget.setLayout(layout)
        #
        return widget                

    def _load_survey_data(self):
        """ """
        try:
            self._surveys_model.clear()
            surveys_dict = app_core.DesktopAppSync().get_surveys_dict()
            for h5_file in sorted(surveys_dict.keys()):
                item = QtGui.QStandardItem(h5_file)
                item.setCheckState(QtCore.Qt.Unchecked)
                item.setCheckable(True)
                self._surveys_model.appendRow(item)
        #
        except Exception as e:
            debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
            app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))
            
    def _check_all_surveys(self):
        """ """
        try:        
            for rowindex in range(self._surveys_model.rowCount()):
                item = self._surveys_model.item(rowindex, 0)
                item.setCheckState(QtCore.Qt.Checked)
        #
        except Exception as e:
            debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
            app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))
            
    def _uncheck_all_surveys(self):
        """ """
        try:        
            for rowindex in range(self._surveys_model.rowCount()):
                item = self._surveys_model.item(rowindex, 0)
                item.setCheckState(QtCore.Qt.Unchecked)
        #
        except Exception as e:
            debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
            app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))

    def _delete_marked_surveys(self):
        """ """
        try:
            try:        
                dir_path = app_core.DesktopAppSync().get_workspace()
                ws = hdf54bats.Hdf5Workspace(dir_path)
                for rowindex in range(self._surveys_model.rowCount()):
                    item = self._surveys_model.item(rowindex, 0)
                    if item.checkState() == QtCore.Qt.Checked:
                        survey_filename = str(item.text())
                        ws.delete_h5(survey_filename)
            finally:
                self.accept() # Close dialog box.
        #
        except Exception as e:
            debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
            app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))
            self.accept() # Close dialog box.

