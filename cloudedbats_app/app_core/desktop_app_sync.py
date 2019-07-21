#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: http://cloudedbats.org
# Copyright (c) 2018 Arnold Andreasson 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import sys
import pathlib
from PyQt5 import QtCore

import hdf54bats
from cloudedbats_app import app_utils

@app_utils.singleton
class DesktopAppSync(QtCore.QObject):
    """ """
    workspace_changed_signal = QtCore.pyqtSignal()
    survey_changed_signal = QtCore.pyqtSignal()
    item_id_changed_signal = QtCore.pyqtSignal()
    clear_buffers_signal = QtCore.pyqtSignal()

    def __init__(self):
        """ """
        self.clear()
        super().__init__()
        #
        self.load_last_used()
        self.update_surveys_dict()
        self.update_events_dict()
    
    def clear(self):
        """ """
        self.workspace = 'workspace_1'
        self.survey = ''
        self.surveys_dict = {}
        self.event = '' 
        self.events_dict = {}
        self.item_id = ''
        self.metadata_dict = {}
    
    def refresh(self):
        """ """
        self.clear()
        self.load_last_used()
        self.update_surveys_dict()
        self.update_events_dict()
        # Emit signal after a short delay.
        QtCore.QTimer.singleShot(100, self._emit_workspace_changed)
        QtCore.QTimer.singleShot(110, self._emit_survey_changed)

    def emit_all_signals(self):
        """ """
        # Emit signal after a short delay.
        QtCore.QTimer.singleShot(100, self._emit_workspace_changed)
        QtCore.QTimer.singleShot(110, self._emit_survey_changed)

    def set_workspace(self, workspace=''):
        """ """
#         print('- SET WORKSPACE: ', workspace)
        if self.workspace != workspace:
            self.clear()
            self.workspace = workspace
            self.update_surveys_dict()
        
            # Emit signal after a short delay.
            QtCore.QTimer.singleShot(100, self._emit_workspace_changed)
            #
            self.save_last_used()
    
    def get_workspace(self):
        """ """
        return self.workspace
    
    def set_selected_survey(self, survey=''):
        """ """
#         print('- SET SURVEY: ', survey)
        if self.survey != survey:
            self.survey = survey
            self.surveys_dict = {}
            self.event = '' 
            self.events_dict = {}
            self.item_id = ''
            self.metadata_dict = {}
            self.update_events_dict()
        
            # Emit signal after a short delay.
            QtCore.QTimer.singleShot(100, self._emit_survey_changed)
            #
            self.save_last_used()
     
    def get_selected_survey(self):
        """ """
        return self.survey
    
    def set_selected_item_id(self, item_id):
        """ """
        if self.item_id != item_id:
            self.item_id = item_id
            
            # Emit signal after a short delay. 
            # The parameter is attach to avoid too many updates if item_id changes too fast.
            QtCore.QTimer.singleShot(100, lambda: self._emit_item_id_changed(item_id))
    
    def get_selected_item_id(self, item_type=''):
        """ """
        if item_type == '':
            return self.item_id
        #
        parts = self.item_id.split('.')
        if item_type == 'event':
            if len(parts) >= 1:
                return parts[0]
            else:
                return ''
        elif item_type == 'detector':
            if len(parts) >= 2:
                return parts[0] + '.' + parts[1]
            else:
                return ''
        elif item_type == 'wavefile':
            if len(parts) >= 3:
                return parts[0] + '.' + parts[1] + '.' + parts[2]
            else:
                return ''
        else:
            return self.item_id
    
    def update_surveys_dict(self):
        """ """
        self.survey_dict = {}
        if self.workspace:
            try:
                if not pathlib.Path(self.workspace).exists():
                    return
                h5_ws = hdf54bats.Hdf5Workspace(self.workspace)
                # 
                h5_list = h5_ws.get_h5_list()
                for h5_file_key in sorted(h5_list.keys()):
                    h5_file_dict = h5_list[h5_file_key]
                    h5_dict = {}
                    h5_dict['h5_file'] = h5_file_dict['name']
                    h5_dict['h5_title'] = h5_file_dict['title']
                    h5_dict['h5_filepath'] = h5_file_dict['f5_filepath']
                    #
                    self.survey_dict[h5_file_dict['name']] = h5_dict
            except Exception as e:
                debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
                app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))
    
    def get_surveys_dict(self):
        """ """
        return self.survey_dict
    
    def update_events_dict(self):
        """ """
        self.events_dict = {}
        if self.workspace and self.survey:
            try:
                if not pathlib.Path(self.workspace).exists():
                    return
                if not pathlib.Path(self.workspace, self.survey).exists():
                    return
                #
                h5_survey = hdf54bats.Hdf5Survey(self.workspace, self.survey)
                for item_id, group in h5_survey.get_child_groups().items():
                    item_dict = {}
                    item_dict['item_id'] = item_id
                    item_dict['item_type'] = group.get('item_type', '')
                    item_dict['item_title'] = group.get('item_title', '')
                    self.events_dict[item_id] = item_dict
            except Exception as e:
                debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
                app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))
    
    def get_events_dict(self):
        """ """
        return self.events_dict
    
    def update_metadata_dict(self):
        """ """
        self.metadata_dict = {}
        if self.workspace and self.survey:
            try:
                if not pathlib.Path(self.workspace).exists():
                    return
                if not pathlib.Path(self.workspace, self.survey).exists():
                    return
                #
                h5_wavefiles = hdf54bats.Hdf5Wavefiles(self.workspace, self.survey)
                self.metadata_dict = h5_wavefiles.get_user_metadata(self.item_id)
                self.metadata_dict['item_title'] = h5_wavefiles.get_item_title(self.item_id)
            except Exception as e:
                debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
                app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))
        
    def get_metadata_dict(self):
        """ """
        return self.metadata_dict
    
    
    def _emit_workspace_changed(self):
        """ """
        self.workspace_changed_signal.emit()
    
    def _emit_survey_changed(self):
        """ """
        self.survey_changed_signal.emit()
    
    def _emit_item_id_changed(self, item_id):
        """ """
        # Skip emit if item_id changes too fast, for example when 
        # the user holds down the arrow key.
        if item_id == self.item_id:
            self.update_metadata_dict()
            self.item_id_changed_signal.emit()
#         else:
#             # Clear buffers when scrolling too fast.
#             self.clear_buffers_signal.emit()
    
    
    def save_last_used(self):
        """ """
        settings_file = pathlib.Path('cloudedbats_app_config', 'desktop_app_settings.txt')
        if not settings_file.parent.exists():
            settings_file.parent.mkdir(parents=True)
        with settings_file.open('w', encoding='cp1252') as file:
            file.write('# Last used settings for CloudedBats Desktop app.\n')
            file.write('\n')
            file.write('last_used_workspace: ' + self.workspace + '\n')
            file.write('last_used_survey: ' + self.survey + '\n')
    
    def load_last_used(self):
        """ """
        settings_file = pathlib.Path('cloudedbats_app_config', 'desktop_app_settings.txt')
        if settings_file.exists():
            with settings_file.open('r', encoding='cp1252') as file:
                for row in file:
                    if '#' in row:
                        row = row.split('#')[0].strip()
                    if ':' in row:
                        parts = row.split(':', 1)
                        if len(parts) >= 2:
                            key = parts[0].strip()
                            value = parts[1].strip()
                            if 'last_used_workspace' in key:
                                self.workspace = value
                            if 'last_used_survey' in key:
                                self.survey = value
        else:
            self.save_last_used()
    
    