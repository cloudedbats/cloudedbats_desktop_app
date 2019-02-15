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
from cloudedbats_app import app_framework
from cloudedbats_app import app_utils
from hdf54bats.hdf5_detector import Hdf5Detector

class SurveyActivity(app_framework.ActivityBase):
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
        tabWidget.addTab(self._content_survey(), 'Survey')
        tabWidget.addTab(self._content_help(), 'Help')
        # 
        layout.addWidget(tabWidget)
        content.setLayout(layout)
    
    # === Survey ===
    def _content_survey(self):
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
#         self.events_tableview = app_framework.SelectableQListView()
#         self.events_tableview = QtWidgets.QTableView()
#        self.events_tableview.setSortingEnabled(True)
        
        
        # Filters.
        self.event_filter_combo = QtWidgets.QComboBox()
        self.detector_filter_combo = QtWidgets.QComboBox()
        
        
        # Buttons.
        self.refresh_button = QtWidgets.QPushButton('Refresh...')
        self.refresh_button.clicked.connect(self.refresh_event_list)
        self.add_event_button = QtWidgets.QPushButton('Add event...')
        self.add_event_button.clicked.connect(self.add_event)
        self.add_detector_button = QtWidgets.QPushButton('Add detector...')
        self.add_detector_button.clicked.connect(self.add_detector)
        self.rename_button = QtWidgets.QPushButton('(Rename...)')
        self.rename_button.clicked.connect(self.rename_content)
        self.copy_button = QtWidgets.QPushButton('(Copy...)')
        self.copy_button.clicked.connect(self.copy_content)
        self.delete_button = QtWidgets.QPushButton('Delete...')
        self.delete_button.clicked.connect(self.delete_content)
        
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
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(QtWidgets.QLabel('Filters:'), 1)
        hlayout.addWidget(self.filter_event_combo, 10)
        hlayout.addWidget(self.filter_detector_combo, 10)
#         hlayout.addStretch(10)
        form1.addLayout(hlayout, gridrow, 0, 1, 15)
        gridrow += 1
        label = QtWidgets.QLabel('Survey content:')
        form1.addWidget(label, gridrow, 0, 1, 1)
        gridrow += 1
        form1.addWidget(self.events_tableview, gridrow, 0, 1, 15)
        gridrow += 1
        hlayout = QtWidgets.QHBoxLayout()
#         hlayout.addWidget(self.refresh_button)
        hlayout.addWidget(self.add_event_button)
        hlayout.addWidget(self.add_detector_button)
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
        
    def add_event(self):
        """ """
        try:        
            my_dialog = NewEventDialog(self)
            if my_dialog.exec_():
                self.refresh_event_list()
        except Exception as e:
            debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
            app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))
#         try:
#             dir_path = str(self.workspacedir_edit.text())
#             survey_name = str(self.survey_combo.currentText())
#             events = hdf54bats.Hdf5Event(dir_path, survey_name)
#             name = self.name_edit.text()
#             events.add_event(parents='', name=name)
#             self.refresh_event_list()
#         except Exception as e:
#             print('TODO: ERROR: ', e)

    def add_detector(self):
        """ """
        try:        
            my_dialog = NewDetectorDialog(self)
            if my_dialog.exec_():
                self.refresh_event_list()
        except Exception as e:
            debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
            app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))
#         try:
#             dir_path = str(self.workspacedir_edit.text())
#             survey_name = str(self.survey_combo.currentText())
#             events = hdf54bats.Hdf5Event(dir_path, survey_name)
#             name = self.name_edit.text()
#             events.add_event(parents='', name=name)
#             self.refresh_event_list()
#         except Exception as e:
#             print('TODO: ERROR: ', e)

    def rename_content(self):
        """ """
        try:        
            my_dialog = RenameDialog(self)
            if my_dialog.exec_():
                self.refresh_event_list()
        except Exception as e:
            debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
            app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))
#         try:
#             dir_path = str(self.workspacedir_edit.text())
#             survey_name = str(self.survey_combo.currentText())
#             events = hdf54bats.Hdf5Event(dir_path, survey_name)
#             name_combo = self.name_combo.currentText()
# #             nodepath = survey_name + '.' + name_combo
#             nodepath = name_combo
#             events.remove_event(nodepath=nodepath)
#             self.refresh_event_list()
#         except Exception as e:
#             print('TODO: ERROR: ', e)
    
    def copy_content(self):
        """ """
        try:        
            my_dialog = CopyDialog(self)
            if my_dialog.exec_():
                self.refresh_event_list()
        except Exception as e:
            debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
            app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))
#         try:
#             dir_path = str(self.workspacedir_edit.text())
#             survey_name = str(self.survey_combo.currentText())
#             events = hdf54bats.Hdf5Event(dir_path, survey_name)
#             name_combo = self.name_combo.currentText()
# #             nodepath = survey_name + '.' + name_combo
#             nodepath = name_combo
#             events.remove_event(nodepath=nodepath)
#             self.refresh_event_list()
#         except Exception as e:
#             print('TODO: ERROR: ', e)
    
    def delete_content(self):
        """ """
        try:        
            dialog = DeleteDialog(self)
            if dialog.exec_():
                self.refresh_event_list()
        except Exception as e:
            debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
            app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))
#         try:
#             dir_path = str(self.workspacedir_edit.text())
#             survey_name = str(self.survey_combo.currentText())
#             events = hdf54bats.Hdf5Event(dir_path, survey_name)
#             name_combo = self.name_combo.currentText()
# #             nodepath = survey_name + '.' + name_combo
#             nodepath = name_combo
#             events.remove_event(nodepath=nodepath)
#             self.refresh_event_list()
#         except Exception as e:
#             print('TODO: ERROR: ', e)
    
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
        <h3>Survey</h3>
        <p>
        Work in progress...
        </p>
        
        """



class NewEventDialog(QtWidgets.QDialog):
    """ This dialog is allowed to access private parts in the parent widget. """
    def __init__(self, parentwidget):
        """ """
        super().__init__(parentwidget)
        self.setWindowTitle("New event")
        self._parentwidget = parentwidget
        self.setLayout(self._content())
        #
        self.dir_path = str(self._parentwidget.workspacedir_edit.text())
        self.survey_name = str(self._parentwidget.survey_combo.currentText())

    def _content(self):
        """ """
        self._eventname_edit = QtWidgets.QLineEdit('')
        self._eventname_edit.setMinimumWidth(400)
        self._eventgroup_edit = QtWidgets.QLineEdit('')
        self._eventgroup_edit.setMinimumWidth(400)
        self._eventgroup_edit.setEnabled(False)
        self._eventname_edit.textChanged.connect(self._update_groupname)
        cancel_button = QtWidgets.QPushButton('Cancel')
        cancel_button.clicked.connect(self.reject) # Close dialog box.               
        self.createevent_button = QtWidgets.QPushButton('Create event')
        self.createevent_button.clicked.connect(self._create_event)
        self.createevent_button.setEnabled(False)
        self.createevent_button.setDefault(False)
        # Layout widgets.
        formlayout = QtWidgets.QFormLayout()
        formlayout.addRow('Event name:', self._eventname_edit)
        formlayout.addRow('Event groupname:', self._eventgroup_edit)
        # 
        hbox1 = QtWidgets.QHBoxLayout()
        hbox1.addStretch(10)
        hbox1.addWidget(cancel_button)
        hbox1.addWidget(self.createevent_button)
        # 
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(formlayout, 10)
        layout.addLayout(hbox1)
        # 
        return layout
    
    def _update_groupname(self, text):
        """ """
        new_text = hdf54bats.str_to_ascii(text)
        if len(new_text) > 0:
            self._eventgroup_edit.setText(new_text)
            self.createevent_button.setEnabled(True)
            self.createevent_button.setDefault(True)
        else:
            self._eventgroup_edit.setText('')
            self.createevent_button.setEnabled(False)
            self.createevent_button.setDefault(False)

    def _create_event(self):
        """ """
        try:
            event = hdf54bats.Hdf5Event(self.dir_path, self.survey_name)
#             detector = hdf54bats.Hdf5Detector(dir_path, survey_name)
            eventname = str(self._eventname_edit.text())
            eventgroup = str(self._eventgroup_edit.text())
            event.add_event(parents='', name=eventgroup, title=eventname)
            self.accept() # Close dialog box.
        except Exception as e:
            print('TODO: ERROR: ', e)
            self.accept() # Close dialog box.


class NewDetectorDialog(QtWidgets.QDialog):
    """ This dialog is allowed to access private parts in the parent widget. """
    def __init__(self, parentwidget):
        """ """
        super().__init__(parentwidget)
        self.setWindowTitle("New detector")
        self._parentwidget = parentwidget
        self.setLayout(self._content())
        #
        self.dir_path = str(self._parentwidget.workspacedir_edit.text())
        self.survey_name = str(self._parentwidget.survey_combo.currentText())
        # 
        self.update_event_list()

    def _content(self):
        """ """
        self.event_combo = QtWidgets.QComboBox()
        self.event_combo.setEditable(False)
        self.event_combo.setMinimumWidth(400)
        
        self._detectorname_edit = QtWidgets.QLineEdit('')
        self._detectorname_edit.setMinimumWidth(400)
        self._detectorgroup_edit = QtWidgets.QLineEdit('')
        self._detectorgroup_edit.setMinimumWidth(400)
        self._detectorgroup_edit.setEnabled(False)
        self._detectorname_edit.textChanged.connect(self._update_groupname)
        cancel_button = QtWidgets.QPushButton('Cancel')
        cancel_button.clicked.connect(self.reject) # Close dialog box.               
        self.createdetector_button = QtWidgets.QPushButton('Create detector')
        self.createdetector_button.clicked.connect(self._create_detector)
        self.createdetector_button.setEnabled(False)
        self.createdetector_button.setDefault(False)
        # Layout widgets.
        formlayout = QtWidgets.QFormLayout()
        formlayout.addRow('Event:', self.event_combo)
        formlayout.addRow('Detector name:', self._detectorname_edit)
        formlayout.addRow('Detector groupname:', self._detectorgroup_edit)
        # 
        hbox1 = QtWidgets.QHBoxLayout()
        hbox1.addStretch(10)
        hbox1.addWidget(cancel_button)
        hbox1.addWidget(self.createdetector_button)
        # 
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(formlayout, 10)
        layout.addLayout(hbox1)
        # 
        return layout
    
    def update_event_list(self):
        """ """
        survey = hdf54bats.Hdf5Survey(self.dir_path, self.survey_name)
        self.event_combo.clear()
        for event_group in sorted(survey.get_children('')):
            self.event_combo.addItem(event_group)

    def _update_groupname(self, text):
        """ """
        new_text = hdf54bats.str_to_ascii(text)
        if len(new_text) > 0:
            self._detectorgroup_edit.setText(new_text)
            self.createdetector_button.setEnabled(True)
            self.createdetector_button.setDefault(True)
        else:
            self._detectorgroup_edit.setText('')
            self.createdetector_button.setEnabled(False)
            self.createdetector_button.setDefault(False)

    def _create_detector(self):
        """ """
        try:
            detector = hdf54bats.Hdf5Detector(self.dir_path, self.survey_name)
            eventgroup = self.event_combo.currentText()
            detectorname = str(self._detectorname_edit.text())
            detectorgroup = str(self._detectorgroup_edit.text())
            detector.add_detector(parents=eventgroup, name=detectorgroup, title=detectorname)
            self.accept() # Close dialog box.
        except Exception as e:
            print('TODO: ERROR: ', e)
            self.accept() # Close dialog box.


class RenameDialog(QtWidgets.QDialog):
    """ This dialog is allowed to access private parts in the parent widget. """
    def __init__(self, parentwidget):
        """ """
        super().__init__(parentwidget)
        self.setWindowTitle("Rename event or detector")
        self._parentwidget = parentwidget
        self.setLayout(self._content())
        #
        self.dir_path = str(self._parentwidget.workspacedir_edit.text())
        self.survey_name = str(self._parentwidget.survey_combo.currentText())
        # 
        self.update_item_list()
    
    def _content(self):
        """ """
        self.groupid_combo = QtWidgets.QComboBox()
        self.groupid_combo.setEditable(False)
        self.groupid_combo.setMinimumWidth(400)
        self.groupid_combo.currentIndexChanged.connect(self._set_groupname)
        
        self._itemname_edit = QtWidgets.QLineEdit('')
        self._itemname_edit.setMinimumWidth(400)
        self._itemgroupname_edit = QtWidgets.QLineEdit('')
        self._itemgroupname_edit.setMinimumWidth(400)
        self._itemgroupname_edit.setEnabled(False)
        self._itemname_edit.textChanged.connect(self._update_groupname)
        cancel_button = QtWidgets.QPushButton('Cancel')
        cancel_button.clicked.connect(self.reject) # Close dialog box.               
        self.renameitem_button = QtWidgets.QPushButton('Rename item')
        self.renameitem_button.clicked.connect(self._rename_item)
        self.renameitem_button.setEnabled(False)
        self.renameitem_button.setDefault(False)
        # Layout widgets.
        formlayout = QtWidgets.QFormLayout()
        formlayout.addRow('Select item:', self.groupid_combo)
        formlayout.addRow('New name:', self._itemname_edit)
        formlayout.addRow('New groupname:', self._itemgroupname_edit)
        # 
        hbox1 = QtWidgets.QHBoxLayout()
        hbox1.addStretch(10)
        hbox1.addWidget(cancel_button)
        hbox1.addWidget(self.renameitem_button)
        # 
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(formlayout, 10)
        layout.addLayout(hbox1)
        # 
        return layout
    
    def update_item_list(self):
        """ """
        survey = hdf54bats.Hdf5Survey(self.dir_path, self.survey_name)
        event = hdf54bats.Hdf5Event(self.dir_path, self.survey_name)
        self.groupid_combo.clear()
        for event_group in sorted(survey.get_children('')):
            self.groupid_combo.addItem(event_group)
            for detector_group in sorted(event.get_children(event_group)):
                self.groupid_combo.addItem(detector_group)
    
    def _set_groupname(self, _index):
        """ """
        item_name = str(self.groupid_combo.currentText())
        if item_name:
#             dir_path = str(self._parentwidget.workspacedir_edit.text())
#             ws = hdf54bats.Hdf5Workspace(dir_path)
#             title = ws.get_h5_title(item_name)
#             self._itemname_edit.setText(title)
            self._itemname_edit.setText(item_name)
        else:
            self._itemname_edit.setText('')
    
    def _update_groupname(self, text):
        """ """
        new_text = hdf54bats.str_to_ascii(text)
        if len(new_text) > 0:
            self._itemgroupname_edit.setText(new_text)
            self.renameitem_button.setEnabled(True)
            self.renameitem_button.setDefault(True)
        else:
            self._itemgroupname_edit.setText('')
            self.renameitem_button.setEnabled(False)
            self.renameitem_button.setDefault(False)

    def _rename_item(self):
        """ """
        self.accept() # Close dialog box.
#         try:
#             detector = hdf54bats.Hdf5Detector(self.dir_path, self.survey_name)
#             eventgroup = self.event_combo.currentText()
#             detectorname = str(self._detectorname_edit.text())
#             detectorgroup = str(self._detectorgroup_edit.text())
#             detector.rename_detector(parents=eventgroup, name=detectorgroup, title=detectorname)
#             self.accept() # Close dialog box.
#         except Exception as e:
#             print('TODO: ERROR: ', e)
#             self.accept() # Close dialog box.



class CopyDialog(QtWidgets.QDialog):
    """ This dialog is allowed to access private parts in the parent widget. """
    def __init__(self, parentwidget):
        """ """
        super().__init__(parentwidget)
        self.setWindowTitle("Copy event or detector")
        self._parentwidget = parentwidget
        self.setLayout(self._content())
        #
        self.dir_path = str(self._parentwidget.workspacedir_edit.text())
        self.survey_name = str(self._parentwidget.survey_combo.currentText())
        # 
        self.update_item_list()
    
    def _content(self):
        """ """
        self.groupid_combo = QtWidgets.QComboBox()
        self.groupid_combo.setEditable(False)
        self.groupid_combo.setMinimumWidth(400)
        self.groupid_combo.currentIndexChanged.connect(self._set_groupname)
        
        self._itemname_edit = QtWidgets.QLineEdit('')
        self._itemname_edit.setMinimumWidth(400)
        self._itemgroupname_edit = QtWidgets.QLineEdit('')
        self._itemgroupname_edit.setMinimumWidth(400)
        self._itemgroupname_edit.setEnabled(False)
        self._itemname_edit.textChanged.connect(self._update_groupname)
        cancel_button = QtWidgets.QPushButton('Cancel')
        cancel_button.clicked.connect(self.reject) # Close dialog box.               
        self.copyitem_button = QtWidgets.QPushButton('Copy item')
        self.copyitem_button.clicked.connect(self._create_item)
        self.copyitem_button.setEnabled(False)
        self.copyitem_button.setDefault(False)
        # Layout widgets.
        formlayout = QtWidgets.QFormLayout()
        formlayout.addRow('Select item:', self.groupid_combo)
        formlayout.addRow('Copy to name:', self._itemname_edit)
        formlayout.addRow('Copy to groupname:', self._itemgroupname_edit)
        # 
        hbox1 = QtWidgets.QHBoxLayout()
        hbox1.addStretch(10)
        hbox1.addWidget(cancel_button)
        hbox1.addWidget(self.copyitem_button)
        # 
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(formlayout, 10)
        layout.addLayout(hbox1)
        # 
        return layout
    
    def update_item_list(self):
        """ """
        survey = hdf54bats.Hdf5Survey(self.dir_path, self.survey_name)
        event = hdf54bats.Hdf5Event(self.dir_path, self.survey_name)
        self.groupid_combo.clear()
        for event_group in sorted(survey.get_children('')):
            self.groupid_combo.addItem(event_group)
            for detector_group in sorted(event.get_children(event_group)):
                self.groupid_combo.addItem(detector_group)

    def _set_groupname(self, _index):
        """ """
        item_name = str(self.groupid_combo.currentText())
        if item_name:
#             dir_path = str(self._parentwidget.workspacedir_edit.text())
#             ws = hdf54bats.Hdf5Workspace(dir_path)
#             title = ws.get_h5_title(item_name)
#             self._itemname_edit.setText(title)
            self._itemname_edit.setText(item_name)
        else:
            self._itemname_edit.setText('')
    
    def _update_groupname(self, text):
        """ """
        new_text = hdf54bats.str_to_ascii(text)
        if len(new_text) > 0:
            self._itemgroupname_edit.setText(new_text)
            self.copyitem_button.setEnabled(True)
            self.copyitem_button.setDefault(True)
        else:
            self._itemgroupname_edit.setText('')
            self.copyitem_button.setEnabled(False)
            self.copyitem_button.setDefault(False)

    def _create_item(self):
        """ """
        self.accept() # Close dialog box.
#         try:
#             dir_path = str(self._parentwidget.workspacedir_edit.text())
#             name_combo = str(self.name_combo.currentText())
#             name = self._itemname_edit.text()
#             groupname = self._itemgroupname_edit.text()
#             ws = hdf54bats.Hdf5Workspace(dir_path)
#             ws.copy_hdf5(name_combo, groupname)
#             ws.set_h5_title(groupname, name)
#             self.update_item_list()
#             self.accept() # Close dialog box.
#         except Exception as e:
#             print('TODO: ERROR: ', e)
#             self.accept() # Close dialog box.


class DeleteDialog(QtWidgets.QDialog):
    """ This dialog is allowed to access private parts in the parent widget. """
    def __init__(self, parentwidget):
        """ """
        super(DeleteDialog, self).__init__(parentwidget)
        self.setWindowTitle("Delete events and detectors")
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
        self._main_tab_widget.addTab(self._item_content(), 'Delete events and detectors')
#         self._main_tab_widget.addTab(self._sample_content(), 'Delete detectors')
        
        return contentLayout                

    # EVENTS.
    
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
        delete_button = QtWidgets.QPushButton('Delete marked item(s)')
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
            survey = hdf54bats.Hdf5Survey(self.dir_path, self.survey_name)
            event = hdf54bats.Hdf5Event(self.dir_path, self.survey_name)
            for event_group in sorted(survey.get_children('')):
#                 self.groupid_combo.addItem(event_group)
                item = QtGui.QStandardItem(event_group)
                item.setCheckState(QtCore.Qt.Unchecked)
                item.setCheckable(True)
                self._items_model.appendRow(item)
                for detector_group in sorted(event.get_children(event_group)):
#                     self.groupid_combo.addItem(detector_group)
                    item = QtGui.QStandardItem(detector_group)
                    item.setCheckState(QtCore.Qt.Unchecked)
                    item.setCheckable(True)
                    self._items_model.appendRow(item)
            
#             
#             self._items_model.clear()
#             dir_path = str(self._parentwidget.workspacedir_edit.text())
#             ws = hdf54bats.Hdf5Workspace(dir_path)
#             h5_list = ws.get_h5_list()
#             for h5_file_key in sorted(h5_list.keys()):
#                 item = QtGui.QStandardItem(h5_file_key)
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
            dir_path = str(self._parentwidget.workspacedir_edit.text())
            ws = hdf54bats.Hdf5Workspace(dir_path)
            event = hdf54bats.Hdf5Event(self.dir_path, self.survey_name)
            for rowindex in range(self._items_model.rowCount()):
                item = self._items_model.item(rowindex, 0)
                if item.checkState() == QtCore.Qt.Checked:
                    item_groupname = str(item.text())
                    event.remove_event(item_groupname)
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

