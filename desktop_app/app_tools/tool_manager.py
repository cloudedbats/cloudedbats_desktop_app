#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: http://cloudedbats.org
# Copyright (c) 2018 Arnold Andreasson 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import app_tools
import app_utils

@app_utils.singleton
class ToolManager(object):
    """
    The tool manager is used to set up available tools. 
    """
    def __init__(self):
        """ """
        self._parent = None
        self._toollist = [] # List of tools derived from ToolsBase.

    def set_parent(self, parentwidget):
        """ """
        self._parent = parentwidget

    def init_tools(self):
        """ Tool activator. """
        # The log tool should be loaded before other tools.
        self._toollist.append(app_tools.LogTool('Application log', self._parent))
        self._toollist.append(app_tools.SpectrogramTool('Spectrogram', self._parent))
        self._toollist.append(app_tools.CallShapesTool('Call shapes', self._parent))
        self._toollist.append(app_tools.MetricsPlotTool('Metrics plot', self._parent))
        self._toollist.append(app_tools.SpeciesTool('Species', self._parent))
#        self._toollist.append(app_tools.TemplateTool('Test tool (template)', self._parent))

    def get_tool_by_name(self, object_name):
        """ Returns the tool. """
        for tool in self._toollist:
            if tool.objectName() == object_name: 
                return tool
        return None
        
    def show_tool_by_name(self, object_name):
        """ Makes a tool visible. """
        for tool in self._toollist:
            if tool.objectName() == object_name: 
                tool.show_tool()
                return
        
    def get_tool_list(self):
        """ """
        return self._toollist
