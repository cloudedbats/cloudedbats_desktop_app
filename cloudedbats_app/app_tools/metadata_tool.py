#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: http://cloudedbats.org
# Copyright (c) 2018 Arnold Andreasson 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

from PyQt5 import QtWidgets
from PyQt5 import QtCore

from cloudedbats_app import app_framework
from cloudedbats_app import app_core
import hdf54bats

class MetadataTool(app_framework.ToolBase):
    """ Metadata tool. """
    
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
        app_core.DesktopAppSync().item_id_changed.connect(self.update_metadata)
        self.update_metadata()

    def _create_content(self):
        """ """
        content = self._create_scrollable_content()
        layout = QtWidgets.QVBoxLayout()
        # Add tabs.
        tabWidget = QtWidgets.QTabWidget()
        tabWidget.addTab(self._content_meatadata(), 'Metadata')
        tabWidget.addTab(self._content_edit_meatadata(), 'Edit metadata')
        tabWidget.addTab(self._content_help(), 'Help')
        # 
        layout.addWidget(tabWidget)
        content.setLayout(layout)
    
    def _content_meatadata(self):
        """ """
        widget = QtWidgets.QWidget()

        # Workspace and survey..
        self.workspacedir_label = QtWidgets.QLabel('Workspace: -     ')
        self.survey_label = QtWidgets.QLabel('Survey: -')
        self.itemid_label = QtWidgets.QLabel('Item id: -')
        self.title_label = QtWidgets.QLabel('Title: -')
        self.metadata_list = QtWidgets.QListWidget()
        
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
        form1.addWidget(self.metadata_list, gridrow, 0, 100, 10)
        #
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(form1)
        widget.setLayout(layout)
        #
        return widget
        
    def _content_edit_meatadata(self):
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
        
    def update_metadata(self):
        """ """
        workspace = app_core.DesktopAppSync().get_workspace()
        survey = app_core.DesktopAppSync().get_selected_survey()
        item_id = app_core.DesktopAppSync().get_selected_item_id()
        #
        if not item_id:
            self.workspacedir_label.setText('Workspace: -     ')
            self.survey_label.setText('Survey: -')
            self.itemid_label.setText('Item id: -')
            return
        #
        self.workspacedir_label.setText('Workspace: <b>' + workspace + '</b>   ')
        self.survey_label.setText('Survey: <b>' + survey + '</b>')
        self.itemid_label.setText('Item id: <b>' + item_id + '</b>')
        #
        h5wavefile = hdf54bats.Hdf5Wavefile(workspace, survey)        
        title = h5wavefile.get_title(item_id)
        metadata_dict = h5wavefile.get_user_metadata(item_id)
        #
        self.title_label.setText('Title: <b>' + title + '</b>')
        self.metadata_list.clear()
        
        for key in sorted(metadata_dict):
            text = key + ': ' + ' ' * (15 - len(key)) + '\t' + str(metadata_dict.get(key, ''))
            self.metadata_list.addItem(text)
        
        return
        
    
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





##########################################################################################
##########################################################################################
##########################################################################################

# from PyQt5 import QtWidgets
# from PyQt5 import QtCore
# 
# # from matplotlib import path
# # from matplotlib import pyplot
# # import numpy as np
#  
# # import cartopy.crs as ccrs
# # from cartopy.io.img_tiles import OSM
# 
# from cloudedbats_app import app_framework
# 
# class MetadataTool(app_framework.ToolBase):
#     """
#     """
#     
#     def __init__(self, name, parentwidget):
#         """ """
#         # Initialize parent. Should be called after other 
#         # initialization since the base class calls _create_content().
#         super(MetadataTool, self).__init__(name, parentwidget)
#         #
#         # Where is the tool allowed to dock in the main window.
#         self.setAllowedAreas(QtCore.Qt.RightDockWidgetArea | 
#                              QtCore.Qt.BottomDockWidgetArea)
#         self.setBaseSize(600,600)        
#         # Default position. Hide as default.
#         self._parent.addDockWidget(QtCore.Qt.RightDockWidgetArea, self)
#         self.hide()
# 
#     def _create_content(self):
#         """ """
#         content = self._create_scrollable_content()
#         contentLayout = QtWidgets.QVBoxLayout()
#         content.setLayout(contentLayout)
#         contentLayout.addLayout(self._content_person_info())
#         contentLayout.addLayout(self._content_buttons())
#         contentLayout.addStretch(5)
# 
#     def _content_person_info(self):
#         """ """
#         # Active widgets and connections.
#         self._nameedit = QtWidgets.QLineEdit('<Name>')
#         self._emailedit = QtWidgets.QLineEdit('<Email>')
#         self._customerlist = QtWidgets.QListWidget()
#         # Layout.
#         layout = QtWidgets.QFormLayout()
#         layout.addRow('&Name:', self._nameedit)
#         layout.addRow('&Email:', self._emailedit)
#         layout.addRow('&Projects:', self._customerlist)
#         # Test data.
#         self._customerlist.addItem('<First project.>')
#         self._customerlist.addItem('<Second project.>')
#         #
#         return layout
# 
#     def _content_buttons(self):
#         """ """
#         # Active widgets and connections.
#         self._testbutton = QtWidgets.QPushButton('Write to log')
#         self._testbutton.clicked.connect(self._test)                
#         # Layout.
#         layout = QtWidgets.QHBoxLayout()
#         layout.addStretch(5)
#         layout.addWidget(self._testbutton)
#         #
#         return layout
# 
#     def _test(self):
#         """ """
#         app_framework.Logging().log('Name: ' + str(self._emailedit.text()))
# 
# 
# 
# # """
# # Produces a map showing London Underground station locations with high
# # resolution background imagery provided by OpenStreetMap.
# # 
# # """
# # from matplotlib.path import Path
# # import matplotlib.pyplot as plt
# # import numpy as np
# # 
# # import cartopy.crs as ccrs
# # from cartopy.io.img_tiles import OSM
# # 
# # 
# # def tube_locations():
# #     """
# #     Returns an (n, 2) array of selected London Tube locations in Ordnance
# #     Survey GB coordinates.
# # 
# #     Source: http://www.doogal.co.uk/london_stations.php
# # 
# #     """
# #     return np.array([[531738., 180890.], [532379., 179734.],
# #                      [531096., 181642.], [530234., 180492.],
# #                      [531688., 181150.], [530242., 180982.],
# #                      [531940., 179144.], [530406., 180380.],
# #                      [529012., 180283.], [530553., 181488.],
# #                      [531165., 179489.], [529987., 180812.],
# #                      [532347., 180962.], [529102., 181227.],
# #                      [529612., 180625.], [531566., 180025.],
# #                      [529629., 179503.], [532105., 181261.],
# #                      [530995., 180810.], [529774., 181354.],
# #                      [528941., 179131.], [531050., 179933.],
# #                      [530240., 179718.]])
# # 
# # 
# # def main():
# #     imagery = OSM()
# # 
# #     ax = plt.axes(projection=imagery.crs)
# #     ax.set_extent((-0.14, -0.1, 51.495, 51.515))
# # 
# #     # Construct concentric circles and a rectangle,
# #     # suitable for a London Underground logo.
# #     theta = np.linspace(0, 2 * np.pi, 100)
# #     circle_verts = np.vstack([np.sin(theta), np.cos(theta)]).T
# #     concentric_circle = Path.make_compound_path(Path(circle_verts[::-1]),
# #                                                 Path(circle_verts * 0.6))
# # 
# #     rectangle = Path([[-1.1, -0.2], [1, -0.2], [1, 0.3], [-1.1, 0.3]])
# # 
# #     # Add the imagery to the map.
# #     ax.add_image(imagery, 14)
# # 
# #     # Plot the locations twice, first with the red concentric circles,
# #     # then with the blue rectangle.
# #     xs, ys = tube_locations().T
# #     plt.plot(xs, ys, transform=ccrs.OSGB(),
# #              marker=concentric_circle, color='red', markersize=9,
# #              linestyle='')
# #     plt.plot(xs, ys, transform=ccrs.OSGB(),
# #              marker=rectangle, color='blue', markersize=11,
# #              linestyle='')
# # 
# #     plt.title('London underground locations')
# #     plt.show()
