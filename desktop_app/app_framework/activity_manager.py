#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: http://cloudedbats.org
# Copyright (c) 2018 Arnold Andreasson 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import app_framework
import app_activities

@app_framework.singleton
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
        
        
###        self._activitylist.append(app_activities.ScannerActivity('Wave file scanner', self._parent))
        
        
        self._activitylist.append(app_activities.StartActivity('Welcome', self._parent))
#         self._activitylist.append(app_activities.TestActivity('Test activity (template)', self._parent))
    
    def show_activity_by_name(self, object_name):
        """ Makes an activity visible. """
        for activity in self._activitylist:
            if activity.objectName() == object_name: 
                activity._parent.showActivity(activity)
                return
    
    def get_activity_list(self):
        """ """
        return self._activitylist
