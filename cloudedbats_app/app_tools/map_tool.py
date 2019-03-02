#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: http://cloudedbats.org
# Copyright (c) 2018 Arnold Andreasson 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

from PyQt5 import QtWidgets
from PyQt5 import QtCore
import matplotlib.backends.backend_qt5agg as mpl_backend
import matplotlib.figure as mpl_figure

import geotiler # From https://github.com/wrobell/geotiler 
                # Example: https://github.com/wrobell/geotiler/blob/master/examples/ex-matplotlib.py 
#
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
#         self.update_map()

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
        
        # Matplotlib figure and canvas for Qt5.
        self._figure = mpl_figure.Figure()
        self._canvas = mpl_backend.FigureCanvasQTAgg(self._figure) 
        self.axes = self._figure.add_subplot(111)       
        self._canvas.show()

#         self.metadata_list = QtWidgets.QListWidget()

#         self.map_webview = QWebEngineView(self)
        
        # Layout widgets.
        form1 = QtWidgets.QGridLayout()
        gridrow = 0
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.workspacedir_label)
        hlayout.addWidget(self.survey_label)
        hlayout.addStretch(5)
        form1.addLayout(hlayout, gridrow, 0, 1, 10)
        gridrow += 1
        form1.addWidget(self.itemid_label, gridrow, 0, 1, 10)
        gridrow += 1
        form1.addWidget(QtWidgets.QLabel(''), gridrow, 0, 1, 10)
        gridrow += 1
        form1.addWidget(self.title_label, gridrow, 0, 1, 10)
#         gridrow += 1
#         form1.addWidget(QtWidgets.QLabel(''), gridrow, 0, 1, 10)
        gridrow += 1
        form1.addWidget(self._canvas, gridrow, 0, 100, 100)
#         form1.addWidget(self.map_webview, gridrow, 0, 100, 10)
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
         
        
        
        #### Dont use geotiler. Wrong license.
        return
        
        
#         bbox = 11.78560, 46.48083, 11.79067, 46.48283
#         # Download background map using OpenStreetMap.
#         mm = geotiler.Map(extent=bbox, zoom=18)
 
        center = (long_dd, lat_dd)
        # Download background map using OpenStreetMap.
        mm = geotiler.Map(center=center, zoom=9, size=(500,300))
 
        self.axes.cla()
        img = geotiler.render_map(mm)
        self.axes.imshow(img)
 
        # Plot custom points.
#         x0, y0 = 11.78816, 46.48114 # http://www.openstreetmap.org/search?query=46.48114%2C11.78816
#         x1, y1 = 11.78771, 46.48165 # http://www.openstreetmap.org/search?query=46.48165%2C11.78771
        x0, y0 = center
        x1, y1 = center
        points = ((x0, y0), (x1, y1))
        x, y = zip(*(mm.rev_geocode(p) for p in points))
        self.axes.scatter(x, y, c='red', edgecolor='none', s=20, alpha=0.9)
 
         
#         plt.savefig('ex-matplotlib.pdf', bbox_inches='tight')
#         plt.close()
        self._canvas.draw()


                
#         mapa = folium.Map(location=[46.3014, -123.7390], zoom_start=7)
#         mapa.save("test.html")
#         self.map_webview.load(QtCore.QUrl("test.html")) 
    
#     def plot_positions_on_map(self, map_file_path=None):
#         """ Plots positions on an interactive OpenStreetMap by using the folium library. 
#             Note: A map can only be created if lat/long is in file name. """
#         if folium_installed == False:
#             if self.debug:
#                 print('\n', 'Warning: Position map not created. Folium is not installed.', '\n')
#             return
#         # Create name if not specified.
#         if map_file_path is None:
#             map_file_path=str(pathlib.Path(self.scanning_results_dir, 
#                                            'positions_map.html'))        
#         # Remove rows with no position.
#         files_with_pos_df = pandas.DataFrame(self.files_df)
#         files_with_pos_df.latlong_str.replace('', numpy.nan, inplace=True)
#         files_with_pos_df.dropna(subset=['latlong_str'], inplace=True) 
#         if len(files_with_pos_df) > 0:
#             # Group by positions and count files at each position.
#             distinct_df = pandas.DataFrame(
#                     {'file_count' : files_with_pos_df.groupby( ['latlong_str', 
#                                                                 'latitude_dd', 
#                                                                 'longitude_dd']).size()
#                     }).reset_index()
#             # Add a column for description to be shown when hovering over point in map.
#             distinct_df['description'] = 'Pos: ' + distinct_df['latlong_str'] + \
#                                          ' Count: ' + distinct_df['file_count'].astype(str)
#             # Use the mean value as center for the map.
#             center_lat = distinct_df.latitude_dd.mean()
#             center_long = distinct_df.longitude_dd.mean()
#             # Create map object.
#             map_osm = folium.Map(location=[center_lat, center_long], zoom_start=8)
#             # Loop over positions an create markers.
#             for long, lat, desc in zip(distinct_df.longitude_dd.values,
#                                      distinct_df.latitude_dd.values,
#                                      distinct_df.description.values):
#                 # The description column is used for popup messages.
#                 marker = folium.Marker([lat, long], popup=desc).add_to(map_osm)            
#             # Write to html file.
#             map_osm.save(map_file_path)
#             if self.debug:
#                 print('Position map saved here: ', map_file_path)
#         else:
#             if self.debug:
#                 print('\n', 'Warning: Position map not created. Lat/long positions are missing.', '\n')
    
    
    
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


