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
    workspace_changed = QtCore.pyqtSignal()
    survey_changed = QtCore.pyqtSignal()
    item_id_changed = QtCore.pyqtSignal()

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
        QtCore.QTimer.singleShot(120, self._emit_item_id_changed)

    def emit_all_signals(self):
        """ """
        # Emit signal after a short delay.
        QtCore.QTimer.singleShot(100, self._emit_workspace_changed)
        QtCore.QTimer.singleShot(110, self._emit_survey_changed)
        QtCore.QTimer.singleShot(120, self._emit_item_id_changed)

    def set_workspace(self, workspace=''):
        """ """
        print('- SET WORKSPACE: ', workspace)
        
        if self.workspace != workspace:
#             self.clear()
            self.workspace = workspace
            self.update_surveys_dict()
            # Emit signal after a short delay.
            QtCore.QTimer.singleShot(100, self._emit_workspace_changed)
            QtCore.QTimer.singleShot(110, self._emit_survey_changed)
            QtCore.QTimer.singleShot(120, self._emit_item_id_changed)
            #
            self.save_last_used()
    
    def get_workspace(self):
        """ """
        return self.workspace
    
    def set_selected_survey(self, survey=''):
        """ """
        print('- SET SURVEY: ', survey)
        
        if self.survey != survey:
            self.survey = survey
            self.event = ''
            self.update_events_dict()
            self.item_id = ''
            self.item_id_dict = {}
            # Emit signal after a short delay.
            QtCore.QTimer.singleShot(100, self._emit_survey_changed)
            QtCore.QTimer.singleShot(110, self._emit_item_id_changed)
            #
            self.save_last_used()
     
    def get_selected_survey(self):
        """ """
        return self.survey
    
    def set_selected_item_id(self, item_id):
        """ """
        print('- SET ITEM: ', item_id)
        
        if self.item_id != item_id:
            self.item_id = item_id
            self.update_metadata_dict()
            # Emit signal after a short delay.
            QtCore.QTimer.singleShot(100, self._emit_item_id_changed)
    
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
                h5_ws = hdf54bats.Hdf5Workspace(self.workspace)
                # 
                h5_list = h5_ws.get_h5_list()
                for h5_file_key in sorted(h5_list.keys()):
                    h5_file_dict = h5_list[h5_file_key]
                    
                    print('- Survey: ', h5_file_dict['name'])
                        
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
                try:
                    h5_event = hdf54bats.Hdf5Event(self.workspace, self.survey)
                    h5_detector = hdf54bats.Hdf5Detector(self.workspace, self.survey)
                    h5_wavefile = hdf54bats.Hdf5Detector(self.workspace, self.survey)
                    # 
                    for event_id in sorted(h5_event.get_children('', close=False)):
                        
                        print('- Event: ', event_id)
                        
                        item_dict = {}
                        item_dict['item_id'] = event_id
                        item_dict['item_type'] = 'event'
                        item_dict['item_title'] = h5_event.get_title(event_id, close=False)
                        self.events_dict[event_id] = item_dict
                        
                        for detector_id in sorted(h5_detector.get_children(event_id, close=False)):
                        
                            print('- Detector: ', detector_id)
                            
                            item_dict = {}
                            item_dict['item_id'] = detector_id
                            item_dict['item_type'] = 'detector'
                            item_dict['item_title'] = h5_detector.get_title(detector_id, close=False)
                            self.events_dict[detector_id] = item_dict
                             
                            for wavefile_id in sorted(h5_wavefile.get_children(detector_id, close=False)):
                            
                                print('- Wavefile: ', wavefile_id)
                                
                                item_dict = {}
                                item_dict['item_id'] = wavefile_id
                                item_dict['item_type'] = 'wavefile'
                                item_dict['item_title'] = h5_detector.get_title(wavefile_id, close=False)
                                self.events_dict[wavefile_id] = item_dict
                except Exception as e:
                    debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
                    app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))
            finally:
                h5_event.close()
                h5_detector.close()
                h5_wavefile.close()
    
    def get_events_dict(self):
        """ """
        return self.events_dict
    
    def update_metadata_dict(self):
        """ """
        self.metadata_dict = {}
        if self.workspace and self.survey:
            try:
                try:
                    h5_wavefile = hdf54bats.Hdf5Wavefile(self.workspace, self.survey)
                    self.metadata_dict = h5_wavefile.get_user_metadata(self.item_id, close=False)
                    self.metadata_dict['item_title'] = h5_wavefile.get_title(self.item_id, close=False)
                except Exception as e:
                    debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
                    app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))
            finally:
                h5_wavefile.close()
        
    def get_metadata_dict(self):
        """ """
        return self.metadata_dict
    
    
    def _emit_workspace_changed(self):
        """ """
        self.workspace_changed.emit()
    
    def _emit_survey_changed(self):
        """ """
        self.survey_changed.emit()
    
    def _emit_item_id_changed(self):
        """ """
        self.item_id_changed.emit()
    
    
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
    
    