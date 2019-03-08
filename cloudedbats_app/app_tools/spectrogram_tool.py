#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: http://cloudedbats.org
# Copyright (c) 2018 Arnold Andreasson 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import pathlib
import queue
import threading
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
import numpy as np
import matplotlib.backends.backend_qt5agg as mpl_backend
import matplotlib.figure as mpl_figure

from cloudedbats_app import app_framework
from cloudedbats_app import app_core
import dsp4bats
import hdf54bats

class SpectrogramTool(app_framework.ToolBase):
    """ Spectrogram plotting tool. """
    
    def __init__(self, name, parentwidget):
        """ """
        # Initialize parent. Should be called after other 
        # initialization since the base class calls _create_content().
        super(SpectrogramTool, self).__init__(name, parentwidget)
        # Where is the tool allowed to dock in the main window.
        self.setAllowedAreas(QtCore.Qt.RightDockWidgetArea | 
                             QtCore.Qt.BottomDockWidgetArea)
        self.setBaseSize(600,600)        
        # Default position. Hide as default.
        self._parent.addDockWidget(QtCore.Qt.RightDockWidgetArea, self)
        self.hide()
        # Plot queue. Used to separate threads.
        self.spectrogram_queue = queue.Queue(maxsize=100)
        self.spectrogram_thread = None
        self.spectrogram_active = False
        # Use sync object for workspaces and surveys. 
        app_core.DesktopAppSync().item_id_changed_signal.connect(self.plot_spectrogram)
        # Also when visible.
        self.visibilityChanged.connect(self.visibility_changed)
    
    def _create_content(self):
        """ """
        content = self._create_scrollable_content()
        layout = QtWidgets.QVBoxLayout()
        # Add tabs.
        tabWidget = QtWidgets.QTabWidget()
        tabWidget.addTab(self._content_spectrogram(), 'Spectrogram')
#         tabWidget.addTab(self._content_settings(), 'Settings')
        tabWidget.addTab(self._content_help(), 'Help')
        # 
        layout.addWidget(tabWidget)
        content.setLayout(layout)
    
    def _content_spectrogram(self):
        """ """
        widget = QtWidgets.QWidget()
        
#         self.workspacedir_label = QtWidgets.QLabel('Workspace: -     ')
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
        font = QtGui.QFont(QtGui.QFont('SansSerif', pointSize=-1, weight=QtGui.QFont.Bold))
        self.survey_edit.setFont(font)
        self.itemid_edit.setFont(font)
        self.title_edit.setFont(font)
        
        self.windowsize_combo = QtWidgets.QComboBox()
        self.windowsize_combo.setEditable(False)
        self.windowsize_combo.setMinimumWidth(80)
        self.windowsize_combo.setMaximumWidth(150)
        self.windowsize_combo.addItems(['128', 
                                        '256', 
                                        '512', 
                                        '1024', 
                                        '2048', 
                                        '4096', 
                                        ])
        self.windowsize_combo.setCurrentIndex(3)
        self.windowsize_combo.currentIndexChanged.connect(self.plot_spectrogram)
        
        self.timeresolution_combo = QtWidgets.QComboBox()
        self.timeresolution_combo.setEditable(False)
        self.timeresolution_combo.setMinimumWidth(80)
        self.timeresolution_combo.setMaximumWidth(150)
        self.timeresolution_combo.addItems(['2 ms', 
                                             '1 ms', 
                                             '1/2 ms', 
                                             '1/4 ms', 
                                             '1/8 ms', 
                                             ])
        self.timeresolution_combo.setCurrentIndex(1)
        self.timeresolution_combo.currentIndexChanged.connect(self.plot_spectrogram)
        
        self.viewpart_combo = QtWidgets.QComboBox()
        self.viewpart_combo.setEditable(False)
        self.viewpart_combo.setMinimumWidth(80)
        self.viewpart_combo.setMaximumWidth(150)
        self.viewpart_combo.addItems(['All', 
                                      '0-1 s', 
                                      '1-2 s', 
                                      '2-3 s', 
                                      '3-4 s', 
                                      '4-5 s', 
                                      '5-6 s', 
                                      '6-7 s', 
                                      '7-8 s', 
                                      '8-9 s', 
                                      '9-10 s', 
                                      ])
        self.viewpart_combo.setCurrentIndex(0)
        self.viewpart_combo.currentIndexChanged.connect(self.plot_spectrogram)
        
        # Matplotlib figure and canvas for Qt5.
        self._figure = mpl_figure.Figure()
        self._canvas = mpl_backend.FigureCanvasQTAgg(self._figure) 
        self.axes = self._figure.add_subplot(111)       
        self._figure.tight_layout()
        self._canvas.show()
        
        # Layout widgets.
        form1 = QtWidgets.QGridLayout()
        gridrow = 0
#         hlayout = QtWidgets.QHBoxLayout()
#         hlayout.addWidget(self.survey_label)
#         hlayout.addWidget(self.survey_edit)
#         hlayout.addStretch(20)
#         hlayout.addWidget(app_framework.RightAlignedQLabel('FFT window size:'))
#         hlayout.addWidget(self.windowsize_combo)
#         form1.addLayout(hlayout, gridrow, 0, 1, 20)
        form1.addWidget(self.survey_label, gridrow, 0, 1, 1)
        form1.addWidget(self.survey_edit, gridrow, 1, 1, 27)
        label = app_framework.RightAlignedQLabel('FFT window size:')
        form1.addWidget(label, gridrow, 28, 1, 1)
        form1.addWidget(self.windowsize_combo, gridrow, 29, 1, 1)
        gridrow += 1
#         hlayout = QtWidgets.QHBoxLayout()
#         hlayout.addWidget(self.itemid_label)
#         hlayout.addStretch(20)
#         hlayout.addWidget(app_framework.RightAlignedQLabel('Time resolution:'))
#         hlayout.addWidget(self.timeresolution_combo)
#         form1.addLayout(hlayout, gridrow, 0, 1, 20)
        form1.addWidget(self.itemid_label, gridrow, 0, 1, 1)
        form1.addWidget(self.itemid_edit, gridrow, 1, 1, 27)
        label = app_framework.RightAlignedQLabel('Time resolution:')
        form1.addWidget(label, gridrow, 28, 1, 1)
        form1.addWidget(self.timeresolution_combo, gridrow, 29, 1, 1)
        gridrow += 1
#         hlayout = QtWidgets.QHBoxLayout()
#         hlayout.addWidget(self.title_label)
#         hlayout.addStretch(20)
#         hlayout.addWidget(app_framework.RightAlignedQLabel('View part:'))
#         hlayout.addWidget(self.viewpart_combo)
#         form1.addLayout(hlayout, gridrow, 0, 1, 20)
        form1.addWidget(self.title_label, gridrow, 0, 1, 1)
        form1.addWidget(self.title_edit, gridrow, 1, 1, 27)
        label = app_framework.RightAlignedQLabel('View part:')
        form1.addWidget(label, gridrow, 28, 1, 1)
        form1.addWidget(self.viewpart_combo, gridrow, 29, 1, 1)
        gridrow += 1
        form1.addWidget(self._canvas, gridrow, 0, 100, 30)
        #
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(form1)
        widget.setLayout(layout)
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
    
    def close(self):
        """ """
        # Terminate spectrogram thread.
        self.spectrogram_active = False
        # Send on queue to release thread.
        self.spectrogram_queue.put(False)
        # 
        super().close()
        
    
    def visibility_changed(self, visible):
        """ """
        if visible:
            self.plot_spectrogram()
    
    def plot_spectrogram(self):
        """ Use a thread to relese the user. """
        workspace = app_core.DesktopAppSync().get_workspace()
        survey = app_core.DesktopAppSync().get_selected_survey()
        item_id = app_core.DesktopAppSync().get_selected_item_id(item_type='wavefile')
        item_metadata = app_core.DesktopAppSync().get_metadata_dict()
        item_title = item_metadata.get('item_title', '')
        #
        try:
            # Check if thread is running.
            if not self.spectrogram_thread:
                self.spectrogram_active = True
                self.spectrogram_thread = threading.Thread(target = self.run_spectrogram_plotter, 
                                                           args=())
                self.spectrogram_thread.start()
        except Exception as e:
            print('EXCEPTION in plot_spectrogram_in_thread: ', e)
            
        spectrogram_dict = {}
        spectrogram_dict['workspace'] = workspace
        spectrogram_dict['survey'] = survey
        spectrogram_dict['item_id'] = item_id
        spectrogram_dict['item_title'] = item_title
        #
        while self.spectrogram_queue.qsize() > 10:
            _dummy = self.spectrogram_queue.get(block=False)
            print('DEBUG: Spectrogram queue - skipped.')
        #
        self.spectrogram_queue.put(spectrogram_dict)
    
    def run_spectrogram_plotter(self):
        """ """
        try:
            while self.spectrogram_active:
                queue_item = self.spectrogram_queue.get()
                if queue_item == False:
                    # Exit.
                    self.spectrogram_active = False
                    continue
                #
                if self.isVisible():
                    workspace = queue_item.get('workspace', '') 
                    survey = queue_item.get('survey', '') 
                    item_id = queue_item.get('item_id', '') 
                    item_title = queue_item.get('item_title', '') 
                    #
                    self.create_spectrogram(workspace, survey, 
                                            item_id, item_title)
                    #
                    self.survey_edit.setText(survey)
                    self.itemid_edit.setText(item_id)
                    self.title_edit.setText(item_title)
        finally:
            self.spectrogram_thread = None

    def create_spectrogram(self, workspace, survey, item_id, item_title):
        """ """
        try:
            if not item_id:
                self.axes.cla()
                self._canvas.draw()
                return
            #
            h5wavefile = hdf54bats.Hdf5Wavefile(workspace, survey)
            try:
                signal = h5wavefile.get_wavefile(item_id, close=False)
                item_title = h5wavefile.get_title(item_id, close=False)
                item_metadata = h5wavefile.get_user_metadata(item_id, close=False)
            finally:
                h5wavefile.close()
            #
            sampling_freq_hz = item_metadata.get('frame_rate_hz', '')
            if not sampling_freq_hz:
                sampling_freq = 500000 # Correct for D500X.
            else:
                sampling_freq = int(sampling_freq_hz)
            #
            if len(signal) > (10 * sampling_freq):
                signal = signal[0:10 * sampling_freq]
                print('DEBUG: Warning: Signal truncated to 10 sec.')                    
            # Settings.
            window_size = int(self.windowsize_combo.currentText())
            timeresolution = self.timeresolution_combo.currentText()
            window_function = 'hann'
            jump = int(sampling_freq / 1000)
            if timeresolution == '2 ms':
                window_function = 'hann'
                jump = int(sampling_freq / 500)
            elif timeresolution == '1 ms':
                window_function = 'hann'
                jump = int(sampling_freq / 1000) # 1 ms.
            elif timeresolution == '1/2 ms':
                window_function = 'hann'
                jump = int(sampling_freq / 2000)
            elif timeresolution == '1/4 ms':
                window_function = 'blackh'
                jump = int(sampling_freq / 4000)
            elif timeresolution == '1/8 ms':
                window_function = 'kaiser'
                jump = int(sampling_freq / 8000)
            #
            viewpart = self.viewpart_combo.currentText()
            if viewpart == 'All':
                pass
            elif viewpart == '0-1 s':
                signal = signal[sampling_freq*0:sampling_freq*1]
            elif viewpart == '1-2 s':
                signal = signal[sampling_freq*1:sampling_freq*2]
            elif viewpart == '2-3 s':
                signal = signal[sampling_freq*2:sampling_freq*3]
            elif viewpart == '3-4 s':
                signal = signal[sampling_freq*3:sampling_freq*4]
            elif viewpart == '4-5 s':
                signal = signal[sampling_freq*4:sampling_freq*5]
            elif viewpart == '5-6 s':
                signal = signal[sampling_freq*5:sampling_freq*6]
            elif viewpart == '6-7 s':
                signal = signal[sampling_freq*6:sampling_freq*7]
            elif viewpart == '7-8 s':
                signal = signal[sampling_freq*7:sampling_freq*8]
            elif viewpart == '8-9 s':
                signal = signal[sampling_freq*8:sampling_freq*9]
            elif viewpart == '9-10 s':
                signal = signal[sampling_freq*9:sampling_freq*10]
            pos_in_sec_from = 0.0
            pos_in_sec_to = len(signal) / sampling_freq
            # Cut part from 1 sec signal.
            signal_short = signal[int(pos_in_sec_from * sampling_freq):int(pos_in_sec_to * sampling_freq)]
            # Create util.
            dbsf_util = dsp4bats.DbfsSpectrumUtil(window_size=window_size, 
                                                  window_function=window_function)
            # Create matrix.
            ### jump = int(sampling_freq/1000/jumps_per_ms)
            size = int(len(signal_short) / jump)
            matrix = dbsf_util.calc_dbfs_matrix(signal_short, matrix_size=size, jump=jump)
            # Plot.
            max_freq = sampling_freq / 1000 / 2 # kHz and Nyquist.

            # Plot.            
            self.axes.cla()
            #
            self.axes.imshow(matrix.T, 
                      cmap='viridis', 
                      origin='lower',
                      extent=(pos_in_sec_from, pos_in_sec_to, 
                              0, max_freq)
                     )
            self.axes.axis('tight')
#             self.axes.set_title(item_title)
            self.axes.set_ylabel('Frequency (kHz)')
            self.axes.set_xlabel('Time (s)')
            #ax.set_ylim([0,160])
            #
            self._canvas.draw()
            
        except Exception as e:
            print('EXCEPTION in plot_spectrogram: ', e)

    