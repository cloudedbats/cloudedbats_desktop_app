#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: http://cloudedbats.org
# Copyright (c) 2018 Arnold Andreasson 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import sys
import queue
import threading
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
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
        # Plot map queue. Used to separate threads.
        self.plot_map_queue = queue.Queue(maxsize=2) # Note: Small buffer.
        self.plot_map_thread = None
#         self.plot_map_active = False
        self.plot_map_active = True
        self.last_used_latitude = 0.0
        self.last_used_longitude = 0.0
        self.last_used_degree_range = 0.0

        # Use sync object for workspaces and surveys. 
        app_core.DesktopAppSync().item_id_changed_signal.connect(self.plot_map)

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
        tabWidget.addTab(self._content_more(), '(More)')
        tabWidget.addTab(self._content_help(), '(Help)')
        # 
        layout.addWidget(tabWidget)
        content.setLayout(layout)
    
    def _content_map(self):
        """ """
        widget = QtWidgets.QWidget()

        # Workspace and survey..
        self.survey_label = QtWidgets.QLabel('Survey: ')
        self.itemid_label = QtWidgets.QLabel('Item id: ')
        self.title_label = QtWidgets.QLabel('Title: ')
        self.survey_edit = QtWidgets.QLineEdit('')
        self.itemid_edit = QtWidgets.QLineEdit('')
        self.title_edit = QtWidgets.QLineEdit('')
        self.survey_edit.setReadOnly(True)
        self.itemid_edit.setReadOnly(True)
        self.title_edit.setReadOnly(True)
        self.survey_edit.setMaximumWidth(1000)
        self.itemid_edit.setMaximumWidth(1000)
        self.title_edit.setMaximumWidth(1000)
        self.survey_edit.setFrame(False)
        self.itemid_edit.setFrame(False)
        self.title_edit.setFrame(False)
        font = QtGui.QFont('Helvetica', pointSize=-1, weight=QtGui.QFont.Bold)
        self.survey_edit.setFont(font)
        self.itemid_edit.setFont(font)
        self.title_edit.setFont(font)
        #
        self.zoom_combo = QtWidgets.QComboBox()
        self.zoom_combo.setEditable(False)
        self.zoom_combo.setMinimumWidth(80)
        self.zoom_combo.setMaximumWidth(150)
        self.zoom_combo.addItems(['10.0', 
                                  '3.0', 
                                  '1.0', 
                                  '0.3', 
                                  '0.1',
                                  '0.03', 
                                  '0.01', 
                                  '0.003', 
                                  '0.001', 
                                  ])
        self.zoom_combo.setCurrentIndex(4)
        self.zoom_combo.currentIndexChanged.connect(self.plot_map)

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
        form1.addWidget(self.survey_label, gridrow, 0, 1, 1)
        form1.addWidget(self.survey_edit, gridrow, 1, 1, 27)
        form1.addWidget(app_framework.RightAlignedQLabel('Zoom:'), gridrow, 28, 1, 1)
        form1.addWidget(self.zoom_combo, gridrow, 29, 1, 1)
        gridrow += 1
#         form1.addWidget(self.itemid_label, gridrow, 0, 1, 100)
        form1.addWidget(self.itemid_label, gridrow, 0, 1, 1)
        form1.addWidget(self.itemid_edit, gridrow, 1, 1, 30)
        gridrow += 1
#         form1.addWidget(self.title_label, gridrow, 0, 1, 100)
        form1.addWidget(self.title_label, gridrow, 0, 1, 1)
        form1.addWidget(self.title_edit, gridrow, 1, 1, 30)
        gridrow += 1
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self._canvas)
        hlayout.addStretch(50)
        form1.addLayout(hlayout, gridrow, 0, 1, 30)
#         form1.addWidget(self._canvas, gridrow, 0, 30, 30)
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
    
    def close(self):
        """ """
        try:
            # Terminate plot_map thread.
            self.plot_map_active = False
            #
            while self.plot_map_queue.qsize() > 5:
                try: self.plot_map_queue.get_nowait()
                except queue.Empty: break # Exits while loop.
            # Send on queue to release thread.
            self.plot_map_queue.put(False)
        except Exception as e:
            debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
            app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))
    
    def visibility_changed(self, visible):
        """ """
        try:
            if visible:
                QtCore.QTimer.singleShot(100, self.plot_map)
                 
        except Exception as e:
            debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
            app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))
    
    def plot_map(self):
        """ Use a thread to relese the user. """
        try:
            workspace = app_core.DesktopAppSync().get_workspace()
            survey = app_core.DesktopAppSync().get_selected_survey()
            item_id = app_core.DesktopAppSync().get_selected_item_id(item_type='wavefile')
            item_metadata = app_core.DesktopAppSync().get_metadata_dict()
            item_title = item_metadata.get('item_title', '')
            #
            try:
                # Check if thread is running.
                if not self.plot_map_thread:
#                     self.plot_map_active = True
                    self.plot_map_thread = threading.Thread(target = self.run_map_plotter, 
                                                               args=())
                    self.plot_map_thread.start()
            
            except Exception as e:
                debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
                app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))
            
            plot_map_dict = {}
            plot_map_dict['workspace'] = workspace
            plot_map_dict['survey'] = survey
            plot_map_dict['item_id'] = item_id
            plot_map_dict['item_title'] = item_title
            #
            while self.plot_map_queue.qsize() > 1:
                try:
                    self.plot_map_queue.get_nowait()
                except queue.Empty:
                    break # Exits while loop.
            #
            self.plot_map_queue.put(plot_map_dict)
        
        except Exception as e:
            debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
            app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))
    
    def run_map_plotter(self):
        """ """
        try:
            try:
                while self.plot_map_active:
                    queue_item = self.plot_map_queue.get()
                    if queue_item == False:
                        # Exit.
                        self.plot_map_active = False
                        continue
                    #
                    if self.isVisible():
                        self.update_map()
            finally:
                self.plot_map_thread = None
        
        except Exception as e:
            debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
            app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))
    
    def update_map(self):
        """ """
        if not self.isVisible():
            self.last_used_latitude = 0.0
            self.last_used_longitude = 0.0
            self.last_used_degree_range = 0.0
            return
        
        try:
            survey = app_core.DesktopAppSync().get_selected_survey()
            item_id = app_core.DesktopAppSync().get_selected_item_id()
            item_metadata = app_core.DesktopAppSync().get_metadata_dict()
            item_title = item_metadata.get('item_title', '')
            latitude_dd = item_metadata.get('rec_latitude_dd', '')
            if not latitude_dd:
                latitude_dd = item_metadata.get('latitude_dd', '')
            longitude_dd = item_metadata.get('rec_longitude_dd', '')
            if not longitude_dd:
                longitude_dd = item_metadata.get('longitude_dd', '')
            #
            self.survey_edit.setText(survey)
            self.itemid_edit.setText(item_id)
            self.title_edit.setText(item_title)
            #
            if not item_id:
                self.last_used_latitude = 0.0
                self.last_used_longitude = 0.0
                self.last_used_degree_range = 0.0
                self.axes.cla()
                self._canvas.draw()
                return
            #
            lat_dd = 0.0
            long_dd = 0.0
            try:
                lat_dd = float(latitude_dd)
                long_dd = float(longitude_dd)
            except:
                self.last_used_latitude = 0.0
                self.last_used_longitude = 0.0
                self.last_used_degree_range = 0.0
                self.axes.cla()
                self._canvas.draw()
                return
            #
            if (lat_dd == 0.0) or (long_dd == 0):
                    # Clear.
                    self.last_used_latitude = 0.0
                    self.last_used_longitude = 0.0
                    self.last_used_degree_range = 0.0
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
            # Don't redraw the same map.
            if (self.last_used_latitude == lat_dd) and \
               (self.last_used_longitude == long_dd) and \
               (self.last_used_degree_range == degree_range):
                return
            #
            self.last_used_latitude = lat_dd
            self.last_used_longitude = long_dd
            self.last_used_degree_range = degree_range
            #
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


