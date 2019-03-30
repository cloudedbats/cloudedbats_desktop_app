#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: http://cloudedbats.org
# Copyright (c) 2018 Arnold Andreasson 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import sys
import time
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

import hdf54bats
from cloudedbats_app import app_framework
from cloudedbats_app import app_utils
from cloudedbats_app import app_core
from PyQt5.Qt import QWidget

class SurveyActivity(app_framework.ActivityBase):
    """ """

    def __init__(self, name, parentwidget):
        """ """
        self.last_used_dir_path = None
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
        self.activityheader = app_framework.HeaderQLabel()
        self.activityheader.setText('<h2>' + self.objectName() + '</h2>')
        layout.addWidget(self.activityheader)
        # Add tabs.
        tabWidget = QtWidgets.QTabWidget()
        tabWidget.addTab(self.content_survey(), 'Survey')
        tabWidget.addTab(self._content_more(), '(More)')
        tabWidget.addTab(self._content_help(), '(Help)')
        # 
        layout.addWidget(tabWidget)
        content.setLayout(layout)
    
    # === Survey ===
    def content_survey(self):
        """ """
        widget = QtWidgets.QWidget()
        # Workspace and survey..
        self.survey_combo = QtWidgets.QComboBox()
        self.survey_combo.setEditable(False)
        self.survey_combo.setMinimumWidth(250)
#         self.survey_combo.setMaximumWidth(300)
        self.survey_combo.addItems(['<select survey>'])
        self.survey_combo.currentIndexChanged.connect(self.survey_changed)
        # Filters.
#         self.filter_event_combo = QtWidgets.QComboBox()
#         self.filter_event_combo.setEditable(False)
#         self.filter_event_combo.setMinimumWidth(150)
# #         self.filter_event_combo.setMaximumWidth(300)
#         self.filter_event_combo.addItems(['<select event>'])
#         self.filter_detector_combo = QtWidgets.QComboBox()
#         self.filter_detector_combo.setEditable(False)
#         self.filter_detector_combo.setMinimumWidth(150)
# #         self.filter_detector_combo.setMaximumWidth(300)
#         self.filter_detector_combo.addItems(['<select detector>'])
        
        self.events_tableview = app_framework.ToolboxQTableView()
        self.events_tableview.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
#         self.events_tableview.clicked.connect(self.selected_item_changed)
        self.events_tableview.getSelectionModel().selectionChanged.connect(self.selected_item_changed)
        
        # Filters.
        self.type_filter_combo = QtWidgets.QComboBox()
        self.type_filter_combo.setMinimumWidth(100)
        self.type_filter_combo.setMaximumWidth(120)
        self.type_filter_combo.addItems(['<select>', 'event', 'detector'])
        self.title_filter_edit = QtWidgets.QLineEdit('')
        self.clear_filter_button = QtWidgets.QPushButton('(Clear)')
#         self.clear_filter_button.clicked.connect(self.clear_filter)
        
        # Buttons.
        self.refresh_button = QtWidgets.QPushButton('Refresh')
        self.refresh_button.clicked.connect(self.refresh)
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
    
    def refresh(self):
        """ """
        app_core.DesktopAppSync().refresh()
    
    def survey_changed(self):
        """ """
        if self.survey_combo.currentIndex() > 0:
            selected_survey = str(self.survey_combo.currentText())
            app_core.DesktopAppSync().set_selected_survey(selected_survey)
        else:
            app_core.DesktopAppSync().refresh()
            
    def selected_item_changed(self):
        """ """
        try:
            modelIndex = self.events_tableview.currentIndex()
            if modelIndex.isValid():
                item_id = str(self.events_tableview.model().index(modelIndex.row(), 2).data())
                # Sync.
                app_core.DesktopAppSync().set_selected_item_id(item_id)
        except Exception as e:
            debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
            app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))
    
    def refresh_survey_list(self):
        """ """
        try:
            self.survey_combo.blockSignals(True)
            # Clear combo.
            self.survey_combo.clear()
            self.survey_combo.addItem('<select survey>')
            # Clear table.
            dataset_table = app_framework.DatasetTable()
            self.events_tableview.setTableModel(dataset_table)
            self.events_tableview.resizeColumnsToContents()
            # Add to combo.
            selected_survey = app_core.DesktopAppSync().get_selected_survey()
            survey_dict = app_core.DesktopAppSync().get_surveys_dict()
            index = 0
            row_index = 0
            for h5_key in sorted(survey_dict):
                h5_dict = survey_dict[h5_key]
                h5_file = h5_dict['h5_file']
                self.survey_combo.addItem(h5_file)
                row_index += 1
                if h5_file == selected_survey:
                    index = row_index
            self.survey_combo.setCurrentIndex(index)
        finally:
            self.survey_combo.blockSignals(False)
        #
        self.refresh_event_list()
    
    def refresh_event_list(self):
        """ """
        try:
            self.events_tableview.blockSignals(True)
            self.events_tableview.getSelectionModel().blockSignals(True)
            #
            if self.survey_combo.currentIndex() == 0:
                dataset_table = app_framework.DatasetTable()
                self.events_tableview.setTableModel(dataset_table)
                self.events_tableview.resizeColumnsToContents()
                return
            
            dir_path = app_core.DesktopAppSync().get_workspace()
            survey_name = str(self.survey_combo.currentText())
            if (not dir_path) or (not survey_name):
                dataset_table = app_framework.DatasetTable()
                self.events_tableview.setTableModel(dataset_table)
                self.events_tableview.resizeColumnsToContents()
                return
            #
            events_dict = app_core.DesktopAppSync().get_events_dict()
            
            dataset_table = app_framework.DatasetTable()
#             dataset_table.set_header(['item_title', 'item_type', 'item_id'])
            dataset_table.set_header(['Title', 'Type', 'Item id'])
            for key in events_dict.keys():
                item_dict = events_dict.get(key, {})
                item_type = item_dict.get('item_type', '')
                if item_type in ['event', 'detector']:
                    row = []
                    row.append(item_dict.get('item_title', ''))
                    row.append(item_dict.get('item_type', ''))
                    row.append(item_dict.get('item_id', ''))
                    dataset_table.append_row(row)
            #
            self.events_tableview.setTableModel(dataset_table)
            self.events_tableview.resizeColumnsToContents()
        finally:
            self.events_tableview.blockSignals(False)
            self.events_tableview.getSelectionModel().blockSignals(False)
        
    def add_event(self):
        """ """
        try:
            if self.survey_combo.currentIndex() == 0:
                QtWidgets.QMessageBox.warning(self, 'Warning', 
                     'Survey not selected, please try again.', 
                     QtWidgets.QMessageBox.Ok)
                return
            #
            my_dialog = NewEventDialog(self)
            if my_dialog.exec_():
                self.refresh()
        except Exception as e:
            debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
            app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))

    def add_detector(self):
        """ """
        try:
            if self.survey_combo.currentIndex() == 0:
                QtWidgets.QMessageBox.warning(self, 'Warning', 
                     'Survey not selected, please try again.', 
                     QtWidgets.QMessageBox.Ok)
                return
            #
            my_dialog = NewDetectorDialog(self)
            if my_dialog.exec_():
                self.refresh()
        except Exception as e:
            debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
            app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))

    def rename_content(self):
        """ """
        try:
            if self.survey_combo.currentIndex() == 0:
                QtWidgets.QMessageBox.warning(self, 'Warning', 
                     'Survey not selected, please try again.', 
                     QtWidgets.QMessageBox.Ok)
                return
            #
#             my_dialog = RenameDialog(self)
#             if my_dialog.exec_():
#                 self.refresh()
        except Exception as e:
            debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
            app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))
    
    def copy_content(self):
        """ """
        try:
            if self.survey_combo.currentIndex() == 0:
                QtWidgets.QMessageBox.warning(self, 'Warning', 
                     'Survey not selected, please try again.', 
                     QtWidgets.QMessageBox.Ok)
                return
            #
#             my_dialog = CopyDialog(self)
#             if my_dialog.exec_():
#                 self.refresh()
        except Exception as e:
            debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
            app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))
    
    def delete_content(self):
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
        self.parentwidget = parentwidget
        self.setLayout(self.content())
        #
        self.dir_path = app_core.DesktopAppSync().get_workspace()
        self.survey_name = str(self.parentwidget.survey_combo.currentText())
        #
        self.enable_buttons()
    
    def content(self):
        """ """
        self.eventtitle_edit = QtWidgets.QLineEdit('')
        self.eventtitle_edit.setMinimumWidth(400)
        self.eventtitle_edit.textChanged.connect(self.update_groupname)
        self.auto_checkbox = QtWidgets.QCheckBox('Auto')
        self.auto_checkbox.setChecked(True)
        self.auto_checkbox.stateChanged.connect(self.enable_buttons)
        self.eventgroup_edit = QtWidgets.QLineEdit('')
        self.eventgroup_edit.setMinimumWidth(400)
        self.eventgroup_edit.setEnabled(False)
        self.eventgroup_edit.textChanged.connect(self.enable_buttons)
        cancel_button = QtWidgets.QPushButton('Cancel')
        cancel_button.clicked.connect(self.reject) # Close dialog box.               
        self.createevent_button = QtWidgets.QPushButton('Create event')
        self.createevent_button.clicked.connect(self.create_event)
        self.createevent_button.setEnabled(False)
        self.createevent_button.setDefault(False)
        # Layout widgets.
        form1 = QtWidgets.QGridLayout()
        gridrow = 0
        label = QtWidgets.QLabel('Event title:')
        form1.addWidget(label, gridrow, 0, 1, 1)
        form1.addWidget(self.eventtitle_edit, gridrow, 1, 1, 9)
        gridrow += 1
        label = QtWidgets.QLabel('Event id:')
        form1.addWidget(label, gridrow, 0, 1, 1)
        form1.addWidget(self.eventgroup_edit, gridrow, 1, 1, 8)
        form1.addWidget(self.auto_checkbox, gridrow, 9, 1, 1)
        #
        hbox1 = QtWidgets.QHBoxLayout()
        hbox1.addStretch(10)
        hbox1.addWidget(cancel_button)
        hbox1.addWidget(self.createevent_button)        
        # 
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(form1, 10)
        layout.addLayout(hbox1)
        # 
        return layout
    
    def enable_buttons(self):
        """ """
        if len(str(self.eventgroup_edit.text())) > 0:
            self.createevent_button.setEnabled(True)
            self.createevent_button.setDefault(True)
        else:
            self.createevent_button.setEnabled(False)
            self.createevent_button.setDefault(False)
        #
        check_state = self.auto_checkbox.checkState()
        if check_state:
            self.eventgroup_edit.setEnabled(False)
        else:
            self.eventgroup_edit.setEnabled(True)
    
    def update_groupname(self, text):
        """ """
        if self.auto_checkbox.checkState():
            new_text = hdf54bats.str_to_ascii(text)
            if len(new_text) > 0:
                self.eventgroup_edit.setText(new_text)
            else:
                self.eventgroup_edit.setText('')
        self.enable_buttons()
    
    def create_event(self):
        """ """
        try:
            event = hdf54bats.Hdf5Events(self.dir_path, self.survey_name)
            eventtitle = str(self.eventtitle_edit.text())
            eventgroup = str(self.eventgroup_edit.text())
            event.add_event(parent_id='', new_event_name=eventgroup, title=eventtitle)
            self.accept() # Close dialog box.
        except Exception as e:
            debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
            app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))


class NewDetectorDialog(QtWidgets.QDialog):
    """ This dialog is allowed to access private parts in the parent widget. """
    def __init__(self, parentwidget):
        """ """
        super().__init__(parentwidget)
        self.setWindowTitle("New detector")
        self.parentwidget = parentwidget
        self.setLayout(self.content())
        #
        self.dir_path = app_core.DesktopAppSync().get_workspace()
        self.survey_name = str(self.parentwidget.survey_combo.currentText())
        # 
        self.update_event_list()
        #
        self.detectortitle_edit.setFocus()

    def content(self):
        """ """
        self.event_combo = QtWidgets.QComboBox()
        self.event_combo.setEditable(False)
        self.event_combo.addItem('<select>')
        self.event_combo.setMinimumWidth(400)
        self.event_combo.currentIndexChanged.connect(self.enable_buttons)
        
        self.detectortitle_edit = QtWidgets.QLineEdit('')
        self.detectortitle_edit.setMinimumWidth(400)
        self.detectortitle_edit.textChanged.connect(self.update_groupname)
        self.auto_checkbox = QtWidgets.QCheckBox('Auto')
        self.auto_checkbox.setChecked(True)
        self.auto_checkbox.stateChanged.connect(self.enable_buttons)
        self.detectorgroup_edit = QtWidgets.QLineEdit('')
        self.detectorgroup_edit.setMinimumWidth(400)
        self.detectorgroup_edit.setEnabled(False)
        self.detectorgroup_edit.textChanged.connect(self.enable_buttons)
        cancel_button = QtWidgets.QPushButton('Cancel')
        cancel_button.clicked.connect(self.reject) # Close dialog box.               
        self.createdetector_button = QtWidgets.QPushButton('Create detector')
        self.createdetector_button.clicked.connect(self.create_detector)
        self.createdetector_button.setEnabled(False)
        self.createdetector_button.setDefault(False)
        # Layout widgets.
        form1 = QtWidgets.QGridLayout()
        gridrow = 0
        label = QtWidgets.QLabel('Event id:')
        form1.addWidget(label, gridrow, 0, 1, 1)
        form1.addWidget(self.event_combo, gridrow, 1, 1, 9)
        gridrow += 1
        label = QtWidgets.QLabel('Detector title:')
        form1.addWidget(label, gridrow, 0, 1, 1)
        form1.addWidget(self.detectortitle_edit, gridrow, 1, 1, 9)
        gridrow += 1
        label = QtWidgets.QLabel('Detector id:')
        form1.addWidget(label, gridrow, 0, 1, 1)
        form1.addWidget(self.detectorgroup_edit, gridrow, 1, 1, 8)
        form1.addWidget(self.auto_checkbox, gridrow, 9, 1, 1)
        #
        hbox1 = QtWidgets.QHBoxLayout()
        hbox1.addStretch(10)
        hbox1.addWidget(cancel_button)
        hbox1.addWidget(self.createdetector_button)
        # 
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(form1, 10)
        layout.addLayout(hbox1)
        #
        return layout
    
    def enable_buttons(self):
        """ """
        if (len(str(self.detectorgroup_edit.text())) > 0) and \
           (self.event_combo.currentIndex() > 0):
            self.createdetector_button.setEnabled(True)
            self.createdetector_button.setDefault(True)
        else:
            self.createdetector_button.setEnabled(False)
            self.createdetector_button.setDefault(False)
        #
        check_state = self.auto_checkbox.checkState()
        if check_state:
            self.detectorgroup_edit.setEnabled(False)
        else:
            self.detectorgroup_edit.setEnabled(True)
    
    def update_groupname(self, text):
        """ """
        if self.auto_checkbox.checkState():
            new_text = hdf54bats.str_to_ascii(text)
            if len(new_text) > 0:
                self.detectorgroup_edit.setText(new_text)
            else:
                self.detectorgroup_edit.setText('')
        self.enable_buttons()
    
#     def update_groupname(self, text):
#         """ """
#         if self.auto_checkbox.checkState():
#             new_text = hdf54bats.str_to_ascii(text)
#             if len(new_text) > 0:
#                 self.detectorgroup_edit.setText(new_text)
#             else:
#                 self.detectorgroup_edit.setText('')
#         #
#         new_id = self.detectorgroup_edit.text()
#         if (len(new_id) > 0) and (self.event_combo.currentIndex() > 0):
#             self.createdetector_button.setEnabled(True)
#             self.createdetector_button.setDefault(True)
#         else:
#             self.createdetector_button.setEnabled(False)
#             self.createdetector_button.setDefault(False)

    def update_event_list(self):
        """ """
        selected_event_id = app_core.DesktopAppSync().get_selected_item_id(item_type='event')
        events_dict = app_core.DesktopAppSync().get_events_dict()
        self.event_combo.clear()
        self.event_combo.addItem('<select>')
        index = 0
        row_index = 0
        for key in sorted(events_dict.keys()):
            item_dict = events_dict.get(key, '')
            item_type = item_dict.get('item_type', '')
            if item_type == 'event':
                self.event_combo.addItem(key)
                row_index += 1
                if key == selected_event_id:
                    index = row_index
        self.event_combo.setCurrentIndex(index)

    def auto_changed(self):
        """ """
        check_state = self.auto_checkbox.checkState()
        if check_state:
            self.detectorgroup_edit.setEnabled(False)
        else:
            self.detectorgroup_edit.setEnabled(True)
    
    def create_detector(self):
        """ """
        try:
            if self.event_combo.currentIndex() > 0:
                detector = hdf54bats.Hdf5Events(self.dir_path, self.survey_name)
                eventgroup = self.event_combo.currentText()
                detectortitle = str(self.detectortitle_edit.text())
                detectorgroup = str(self.detectorgroup_edit.text())
                detector.add_event(parent_id=eventgroup, new_event_name=detectorgroup, 
                                   title=detectortitle, item_type='detector')
                self.accept() # Close dialog box.
        except Exception as e:
            debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
            app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))
            self.accept() # Close dialog box.


class RenameDialog(QtWidgets.QDialog):
    """ This dialog is allowed to access private parts in the parent widget. """
    def __init__(self, parentwidget):
        """ """
        super().__init__(parentwidget)
        self.setWindowTitle("Rename event or detector")
        self.parentwidget = parentwidget
        self.setLayout(self.content())
        #
        self.dir_path = app_core.DesktopAppSync().get_workspace()
        self.survey_name = str(self.parentwidget.survey_combo.currentText())
        # 
        self.update_item_list()
        #
        self.itemtitle_edit.setFocus()
    
    def content(self):
        """ """
        self.groupid_combo = QtWidgets.QComboBox()
        self.groupid_combo.setEditable(False)
        self.groupid_combo.setMinimumWidth(400)
        self.groupid_combo.addItem('<select>')
        self.groupid_combo.currentIndexChanged.connect(self.enable_buttons)
        
        self.itemtitle_edit = QtWidgets.QLineEdit('')
        self.itemtitle_edit.setMinimumWidth(400)
        self.itemtitle_edit.textChanged.connect(self.update_groupname)
        self.itemgroupname_edit = QtWidgets.QLineEdit('')
        self.itemgroupname_edit.setMinimumWidth(400)
        self.itemgroupname_edit.setEnabled(False)
        cancel_button = QtWidgets.QPushButton('Cancel')
        cancel_button.clicked.connect(self.reject) # Close dialog box.               
        self.renameitem_button = QtWidgets.QPushButton('Rename item')
        self.renameitem_button.clicked.connect(self.rename_item)
        self.renameitem_button.setEnabled(False)
        self.renameitem_button.setDefault(False)
        # Layout widgets.
        formlayout = QtWidgets.QFormLayout()
        formlayout.addRow('Select item:', self.groupid_combo)
        formlayout.addRow('New name:', self.itemtitle_edit)
        formlayout.addRow('New groupname:', self.itemgroupname_edit)
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
    
    def enable_buttons(self):
        """ """
        if self.groupid_combo.currentIndex() > 0:
            self.renameitem_button.setEnabled(True)
            self.renameitem_button.setDefault(True)
        else:
            self.renameitem_button.setEnabled(False)
            self.renameitem_button.setDefault(False)
    
    def update_groupname(self, text):
        """ """
        self.renameitem_button.setEnabled(False)
        self.renameitem_button.setDefault(False)
#         new_text = hdf54bats.str_to_ascii(text)
#         if len(new_text) > 0:
#             self.itemgroupname_edit.setText(new_text)
#             self.renameitem_button.setEnabled(True)
#             self.renameitem_button.setDefault(True)
#         else:
#             self.itemgroupname_edit.setText('')
#             self.renameitem_button.setEnabled(False)
#             self.renameitem_button.setDefault(False)
    
    def update_item_list(self):
        """ """
        selected_event_id = app_core.DesktopAppSync().get_selected_item_id(item_type='event')
        selected_detector_id = app_core.DesktopAppSync().get_selected_item_id(item_type='detector')
        events_dict = app_core.DesktopAppSync().get_events_dict()
        self.groupid_combo.clear()
        self.groupid_combo.addItem('<select>')
        index = 0
        row_index = 0
        for key in sorted(events_dict.keys()):
            item_dict = events_dict.get(key, '')
            item_type = item_dict.get('item_type', '')
            if item_type in ['event', 'detector']:
                self.groupid_combo.addItem(key)
                row_index += 1
                if key == selected_event_id:
                    index = row_index
                if key == selected_detector_id:
                    index = row_index
        self.groupid_combo.setCurrentIndex(index)
    
    def set_groupname(self, _index):
        """ """
        item_name = str(self.groupid_combo.currentText())
        if item_name and (self.groupid_combo.currentIndex() > 0):
            self.itemtitle_edit.setText(item_name)
        else:
            self.itemtitle_edit.setText('')
    
    def rename_item(self):
        """ """
        self.accept() # Close dialog box.
#         try:
#             detector = hdf54bats.Hdf5Samples(self.dir_path, self.survey_name)
#             eventgroup = self.event_combo.currentText()
#             detectortitle = str(self.detectortitle_edit.text())
#             detectorgroup = str(self.detectorgroup_edit.text())
#             detector.rename_detector(parent_id=eventgroup, name=detectorgroup, title=detectortitle)
#             self.accept() # Close dialog box.
#         except Exception as e:
#             debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
#             app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))
#             self.accept() # Close dialog box.



class CopyDialog(QtWidgets.QDialog):
    """ This dialog is allowed to access private parts in the parent widget. """
    def __init__(self, parentwidget):
        """ """
        super().__init__(parentwidget)
        self.setWindowTitle("Copy event or detector")
        self.parentwidget = parentwidget
        self.setLayout(self.content())
        #
        self.itemtitle_edit.setFocus()
        #
        self.dir_path = app_core.DesktopAppSync().get_workspace()
        self.survey_name = str(self.parentwidget.survey_combo.currentText())
        # 
        self.update_item_list()
    
    def content(self):
        """ """
        self.groupid_combo = QtWidgets.QComboBox()
        self.groupid_combo.setEditable(False)
        self.groupid_combo.setMinimumWidth(400)
        self.groupid_combo.addItem('<select>')
        self.groupid_combo.currentIndexChanged.connect(self.enable_buttons)
        
        self.itemtitle_edit = QtWidgets.QLineEdit('')
        self.itemtitle_edit.setMinimumWidth(400)
        self.itemtitle_edit.textChanged.connect(self.update_groupname)
        self.itemgroupname_edit = QtWidgets.QLineEdit('')
        self.itemgroupname_edit.setMinimumWidth(400)
        self.itemgroupname_edit.setEnabled(False)
        cancel_button = QtWidgets.QPushButton('Cancel')
        cancel_button.clicked.connect(self.reject) # Close dialog box.               
        self.copyitem_button = QtWidgets.QPushButton('Copy item')
        self.copyitem_button.clicked.connect(self.create_item)
        self.copyitem_button.setEnabled(False)
        self.copyitem_button.setDefault(False)
        # Layout widgets.
        formlayout = QtWidgets.QFormLayout()
        formlayout.addRow('Select item:', self.groupid_combo)
        formlayout.addRow('Copy to name:', self.itemtitle_edit)
        formlayout.addRow('Copy to groupname:', self.itemgroupname_edit)
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
    
    def enable_buttons(self):
        """ """
        if self.groupid_combo.currentIndex() > 0:
            self.copyitem_button.setEnabled(True)
            self.copyitem_button.setDefault(True)
        else:
            self.copyitem_button.setEnabled(False)
            self.copyitem_button.setDefault(False)
    
    def update_groupname(self, text):
        """ """
#         self.copyitem_button.setEnabled(False)
#         self.copyitem_button.setDefault(False)
#         new_text = hdf54bats.str_to_ascii(text)
#         if len(new_text) > 0:
#             self.itemgroupname_edit.setText(new_text)
#             self.copyitem_button.setEnabled(True)
#             self.copyitem_button.setDefault(True)
#         else:
#             self.itemgroupname_edit.setText('')
#             self.copyitem_button.setEnabled(False)
#             self.copyitem_button.setDefault(False)
    
    def update_item_list(self):
        """ """
        selected_event_id = app_core.DesktopAppSync().get_selected_item_id(item_type='event')
        selected_detector_id = app_core.DesktopAppSync().get_selected_item_id(item_type='detector')
        events_dict = app_core.DesktopAppSync().get_events_dict()
        self.groupid_combo.clear()
        self.groupid_combo.addItem('<select>')
        index = 0
        row_index = 0
        for key in sorted(events_dict.keys()):
            item_dict = events_dict.get(key, '')
            item_type = item_dict.get('item_type', '')
            if item_type in ['event', 'detector']:
                self.groupid_combo.addItem(key)
                row_index += 1
                if key == selected_event_id:
                    index = row_index
                if key == selected_detector_id:
                    index = row_index
        self.groupid_combo.setCurrentIndex(index)
        
    def set_groupname(self, _index):
        """ """
        item_name = str(self.groupid_combo.currentText())
        if item_name and (self.groupid_combo.currentIndex() > 0):
            self.itemtitle_edit.setText(item_name)
        else:
            self.itemtitle_edit.setText('')
    
    def create_item(self):
        """ """
        self.accept() # Close dialog box.
#         try:
#             dir_path = app_core.DesktopAppSync().get_workspace()
#             name_combo = str(self.name_combo.currentText())
#             name = self.itemtitle_edit.text()
#             groupname = self.itemgroupname_edit.text()
#             ws = hdf54bats.Hdf5Workspace(dir_path)
#             ws.copy_hdf5(name_combo, groupname)
#             ws.set_h5_title(groupname, name)
#             self.update_item_list()
#             self.accept() # Close dialog box.
#         except Exception as e:
#             debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
#             app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))
#             self.accept() # Close dialog box.


class DeleteDialog(QtWidgets.QDialog):
    """ This dialog is allowed to access private parts in the parent widget. """
    def __init__(self, parentwidget):
        """ """
        super(DeleteDialog, self).__init__(parentwidget)
        self.setWindowTitle("Delete events and detectors")
        self.parentwidget = parentwidget
        self.setLayout(self.content())
        self.setMinimumSize(500, 500)
        #
        self.dir_path = app_core.DesktopAppSync().get_workspace()
        self.survey_name = str(self.parentwidget.survey_combo.currentText())
        #
        self.load_item_data()
        
    def content(self):
        """ """  
        contentLayout = QtWidgets.QVBoxLayout(self)
        self.setLayout(contentLayout)
        #
        self.main_tab_widget = QtWidgets.QTabWidget(self)
        contentLayout.addWidget(self.main_tab_widget)
        self.main_tab_widget.addTab(self.item_content(), 'Delete events and detectors')
#         self.main_tab_widget.addTab(self.sample_content(), 'Delete detectors')
        
        return contentLayout                
    
    def item_content(self):
        """ """
        widget = QtWidgets.QWidget()
        #  
        items_listview = QtWidgets.QListView()
        self.items_model = QtGui.QStandardItemModel()
        items_listview.setModel(self.items_model)

        clearall_button = app_framework.ClickableQLabel('Clear all')
        clearall_button.label_clicked.connect(self.uncheck_all_items)                
        markall_button = app_framework.ClickableQLabel('Mark all')
        markall_button.label_clicked.connect(self.check_all_items)                
        cancel_button = QtWidgets.QPushButton('Cancel')
        cancel_button.clicked.connect(self.reject) # Close dialog box.               
        self.delete_button = QtWidgets.QPushButton('Delete marked items')
        self.delete_button.clicked.connect(self.delete_marked_items)               
        # Layout widgets.
        hbox1 = QtWidgets.QHBoxLayout()
        hbox1.addWidget(clearall_button)
        hbox1.addWidget(markall_button)
        hbox1.addStretch(10)
        #
        hbox2 = QtWidgets.QHBoxLayout()
        hbox2.addStretch(10)
        hbox2.addWidget(cancel_button)
        hbox2.addWidget(self.delete_button)
        #
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(items_listview, 10)
        layout.addLayout(hbox1)
        layout.addLayout(hbox2)
        #
        widget.setLayout(layout)
        #
        return widget
    
#     def enable_buttons(self):
#         """ """
#         if self.detector_combo.currentIndex() > 0:
#             self.delete_button.setEnabled(True)
#             self.delete_button.setDefault(True)
#         else:
#             self.delete_button.setEnabled(False)
#             self.delete_button.setDefault(False)
    
    def load_item_data(self):
        """ """
        try:
            self.items_model.clear()
            events_dict = app_core.DesktopAppSync().get_events_dict()
            for key in sorted(events_dict.keys()):
                item_dict = events_dict.get(key, '')
                item_type = item_dict.get('item_type', '')
                if item_type in ['event', 'detector']:
                    item = QtGui.QStandardItem(key)
                    item.setCheckState(QtCore.Qt.Unchecked)
                    item.setCheckable(True)
                    self.items_model.appendRow(item)
        except Exception as e:
            debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
            app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))
            
    def check_all_items(self):
        """ """
        try:        
            for rowindex in range(self.items_model.rowCount()):
                item = self.items_model.item(rowindex, 0)
                item.setCheckState(QtCore.Qt.Checked)
        #
        except Exception as e:
            debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
            app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))
            
    def uncheck_all_items(self):
        """ """
        try:        
            for rowindex in range(self.items_model.rowCount()):
                item = self.items_model.item(rowindex, 0)
                item.setCheckState(QtCore.Qt.Unchecked)
        #
        except Exception as e:
            debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
            app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))

    def delete_marked_items(self):
        """ """
        try:        
            event = hdf54bats.Hdf5Events(self.dir_path, self.survey_name)
            for rowindex in range(self.items_model.rowCount()):
                item = self.items_model.item(rowindex, 0)
                if item.checkState() == QtCore.Qt.Checked:
                    item_groupname = str(item.text())
                    event.remove_event(item_groupname, recursive=True)
            #
#             self.parentwidget._emit_change_notification()
            self.accept() # Close dialog box.
        #
        except Exception as e:
            debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
            app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))
            self.accept() # Close dialog box.

