#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: http://cloudedbats.org
# Copyright (c) 2018 Arnold Andreasson 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import sys
from PyQt5 import QtWidgets
from PyQt5 import QtCore
import matplotlib.backends.backend_qt5agg as mpl_backend
import matplotlib.figure as mpl_figure
import tilemapbase

from cloudedbats_app import app_utils
from cloudedbats_app import app_framework
from cloudedbats_app import app_core

class MapTool(app_framework.ToolBase):
    """ map tool. """
    
    def __init__(self, name, parentwidget):
        """ """
        self.spectrogram_thread = None
        self.spectrogram_thread_active = False
        # Initialize parent. Should be called after other 
        # initialization since the base class calls _create_content().
        super().__init__(name, parentwidget)
        #
        # Where is the tool allowed to dock in the main window.
        self.setAllowedAreas(QtCore.Qt.RightDockWidgetArea | 
                             QtCore.Qt.BottomDockWidgetArea)
        self.setBaseSize(600,600)        
        # Default position. Hide as default.
        self._parent.addDockWidget(QtCore.Qt.RightDockWidgetArea, self)
        self.hide()
        # Use sync object for workspaces and surveys. 
        app_core.DesktopAppSync().item_id_changed.connect(self.update_map)

        # Map init.
        tilemapbase.init(create=True)
        self.osm_tiles = tilemapbase.tiles.OSM
    
    def _create_content(self):
        """ """
        content = self._create_scrollable_content()
        layout = QtWidgets.QVBoxLayout()
        # Add tabs.
        tabWidget = QtWidgets.QTabWidget()
        tabWidget.addTab(self._content_map(), 'Map')
        tabWidget.addTab(self._content_settings(), 'Settings')
        tabWidget.addTab(self._content_help(), 'Help')
        # 
        layout.addWidget(tabWidget)
        content.setLayout(layout)
    
    def _content_map(self):
        """ """
        widget = QtWidgets.QWidget()

        # Workspace and survey..
        self.workspacedir_label = QtWidgets.QLabel('Workspace: -     ')
        self.survey_label = QtWidgets.QLabel('Survey: -')
        self.itemid_label = QtWidgets.QLabel('Item id: -')
        self.title_label = QtWidgets.QLabel('Title: -')
        #
        self.zoom_combo = QtWidgets.QComboBox()
        self.zoom_combo.setEditable(False)
        self.zoom_combo.setMinimumWidth(80)
        self.zoom_combo.setMaximumWidth(150)
        self.zoom_combo.addItems(['10.0', 
                                  '5.0', 
                                  '1.0', 
                                  '0.5', 
                                  '0.1', 
                                  '0.05', 
                                  '0.01', 
                                  '0.005', 
                                  '0.001', 
                                  ])
        self.zoom_combo.setCurrentIndex(3)

        # Matplotlib figure and canvas for Qt5.
        self._figure = mpl_figure.Figure()
        self._canvas = mpl_backend.FigureCanvasQTAgg(self._figure) 
        self._canvas.setMinimumWidth(300)
        self._canvas.setMinimumHeight(300)
        self.axes = self._figure.add_subplot(111)
        self._figure.tight_layout()
        self.axes.xaxis.set_visible(False)
        self.axes.yaxis.set_visible(False)
        self._canvas.show()

        # Layout widgets.
        form1 = QtWidgets.QGridLayout()
        gridrow = 0
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.survey_label)
        hlayout.addStretch(20)
        hlayout.addWidget(app_framework.RightAlignedQLabel('Zoom:'))
        hlayout.addWidget(self.zoom_combo)
        form1.addLayout(hlayout, gridrow, 0, 1, 100)
        gridrow += 1
        form1.addWidget(self.itemid_label, gridrow, 0, 1, 100)
        gridrow += 1
        form1.addWidget(self.title_label, gridrow, 0, 1, 100)
        gridrow += 1
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self._canvas)
        hlayout.addStretch(50)
        form1.addWidget(self._canvas, gridrow, 0, 100, 100)
        #
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(form1)
        widget.setLayout(layout)
        #
        return widget
        
    def _content_settings(self):
        """ """
        widget = QtWidgets.QWidget()
        #
        self.todo_label = QtWidgets.QLabel('<b>TODO...</b>')
        
        # Layout widgets.
        form1 = QtWidgets.QGridLayout()
        gridrow = 0
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.todo_label)
        hlayout.addStretch(10)
        form1.addLayout(hlayout, gridrow, 0, 1, 10)
        #
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(form1)
        layout.addStretch(100)
        widget.setLayout(layout)
        #
        return widget
    
    def update_map(self):
        """ """
        try:
            workspace = app_core.DesktopAppSync().get_workspace()
            survey = app_core.DesktopAppSync().get_selected_survey()
            item_id = app_core.DesktopAppSync().get_selected_item_id()
            item_metadata = app_core.DesktopAppSync().get_metadata_dict()
            item_title = item_metadata.get('item_title', '')
            latitude_dd = item_metadata.get('latitude_dd', '')
            longitude_dd = item_metadata.get('longitude_dd', '')
            #
            if not item_id:
                self.workspacedir_label.setText('Workspace: -     ')
                self.survey_label.setText('Survey: -')
                self.itemid_label.setText('Item id: -')
                self.title_label.setText('Title: -')
                return
            #
            self.workspacedir_label.setText('Workspace: <b>' + workspace + '</b>   ')
            self.survey_label.setText('Survey: <b>' + survey + '</b>')
            self.itemid_label.setText('Item id: <b>' + item_id + '</b>')
            self.title_label.setText('Title: <b>' + item_title + '</b>')
            #
            try:
                lat_dd = float(latitude_dd)
                long_dd = float(longitude_dd)
            except:
                # Clear.
                self.axes.cla()
                self._canvas.draw()
                return
             
    
            current_position = (long_dd, lat_dd)
           
            degree_range = 0.05
            
            zoom_range = self.zoom_combo.currentText()
            try:
                degree_range = float(zoom_range)
            except:
                pass
            
            extent = tilemapbase.Extent.from_lonlat(current_position[0] - degree_range, current_position[0] + degree_range,
                              current_position[1] - degree_range, current_position[1] + degree_range)
            extent = extent.to_aspect(1.0)
            
            self.axes.cla()
            
            self.axes.xaxis.set_visible(False)
            self.axes.yaxis.set_visible(False)
            
            plotter = tilemapbase.Plotter(extent, self.osm_tiles, width=600)
            plotter.plot(self.axes, self.osm_tiles)
            
            x, y = tilemapbase.project(*current_position)
            self.axes.scatter(x,y, marker=".", color="black", linewidth=20)
            #
            self._canvas.draw()
        
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
#         label.setText(self.get_help_text())
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


