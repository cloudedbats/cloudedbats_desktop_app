#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: http://cloudedbats.org
# Copyright (c) 2018 Arnold Andreasson 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import pathlib
from PyQt5 import QtCore

import hdf54bats
from cloudedbats_app import app_utils

@app_utils.singleton
class DesktopAppSync(QtCore.QObject):
    """ """
    workspace_changed = QtCore.pyqtSignal()
    survey_changed = QtCore.pyqtSignal()

    def __init__(self):
        """ """
        self.clear()
        super().__init__()
        #
        self.load_last_used()
        self.update_survey_dict()
#         self.set_workspace(self.workspace)
#         self.set_selected_survey(self.survey)
    
    def clear(self):
        """ """
        self.workspace = 'workspace_1'
        self.survey = ''
        self.survey_dict = {}
    
    def set_workspace(self, workspace=''):
        """ """
        self.clear()
        self.workspace = workspace
        self.update_survey_dict()
        # Emit signal after a short delay.
        QtCore.QTimer.singleShot(100, self._emit_workspace_changed)
        #
        self.save_last_used()
    
    def get_workspace(self):
        """ """
        return self.workspace
    
    def set_selected_survey(self, survey=''):
        """ """
        self.survey = survey
        # Emit signal after a short delay.
        QtCore.QTimer.singleShot(100, self._emit_survey_changed)
        #
        self.save_last_used()
     
    def get_selected_survey(self):
        """ """
        return self.survey
    
    def update_survey_dict(self):
        """ """
        ws = hdf54bats.Hdf5Workspace(self.workspace)
        self.survey_dict = {}
        # 
        h5_list = ws.get_h5_list()
        for h5_file_key in sorted(h5_list.keys()):
            h5_file_dict = h5_list[h5_file_key]
            h5_dict = {}
            h5_dict['h5_file'] = h5_file_dict['name']
            h5_dict['h5_title'] = h5_file_dict['title']
            h5_dict['h5_filepath'] = h5_file_dict['f5_filepath']
            #
            self.survey_dict[h5_file_dict['name']] = h5_dict
    
    def get_survey_dict(self):
        """ """
        return self.survey_dict
    
    def _emit_workspace_changed(self):
        """ """
        self.workspace_changed.emit()
    
    def _emit_survey_changed(self):
        """ """
        self.survey_changed.emit()
    
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
                        
                         
    