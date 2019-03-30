#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: http://cloudedbats.org
# Copyright (c) 2018 Arnold Andreasson 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

from cloudedbats_app import app_utils
from cloudedbats_app import app_activities

@app_utils.singleton
class ActivityManager(object):
    """ 
    The activity manager is used to set up available activites. 
    """
    def __init__(self):
        """ """
        self._parent = None
        self._activitylist = [] # List of activities derived from ActivityBase.        
    
    def set_parent(self, parentwidget):
        """ """
        self._parent = parentwidget
    
    def init_activities(self):
        """ Activity activator. """
        self._activitylist.append(app_activities.StartActivity('Welcome', self._parent))

        self._activitylist.append(app_activities.WorkspaceActivity('Workspace', self._parent))

        self._activitylist.append(app_activities.SurveyActivity('Survey', self._parent))

        self._activitylist.append(app_activities.WavefilesActivity('Wave files', self._parent))
        
        self._activitylist.append(app_activities.ScannerActivity('(Scanner)', self._parent))
        
        self._activitylist.append(app_activities.AnalysisActivity('(Analysis)', self._parent))
        
        self._activitylist.append(app_activities.ExportImportActivity('(Export/import)', self._parent))
        
        self._activitylist.append(app_activities.UploadDownloadActivity('(Upload/download)', self._parent))
        
        self._activitylist.append(app_activities.CloudActivity('(Cloud)', self._parent))
        
        self._activitylist.append(app_activities.DarwinCoreActivity('(Darwin core)', self._parent))
    
    def show_activity_by_name(self, object_name):
        """ Makes an activity visible. """
        for activity in self._activitylist:
            if activity.objectName() == object_name: 
                activity._parent.showActivity(activity)
                return
    
    def get_activity_list(self):
        """ """
        return self._activitylist
