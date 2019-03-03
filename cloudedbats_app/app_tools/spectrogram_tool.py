#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: http://cloudedbats.org
# Copyright (c) 2018 Arnold Andreasson 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import pathlib
import threading
from PyQt5 import QtWidgets
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
        self.spectrogram_thread = None
        self.spectrogram_thread_active = False
        # Initialize parent. Should be called after other 
        # initialization since the base class calls _create_content().
        super(SpectrogramTool, self).__init__(name, parentwidget)
        #
        # Where is the tool allowed to dock in the main window.
        self.setAllowedAreas(QtCore.Qt.RightDockWidgetArea | 
                             QtCore.Qt.BottomDockWidgetArea)
        self.setBaseSize(600,600)        
        # Default position. Hide as default.
        self._parent.addDockWidget(QtCore.Qt.RightDockWidgetArea, self)
        self.hide()
        # Use sync object for workspaces and surveys. 
#         app_core.DesktopAppSync().workspace_changed.connect(self.refresh_survey_list)
#         app_core.DesktopAppSync().survey_changed.connect(self.refresh_survey_list)
        app_core.DesktopAppSync().item_id_changed.connect(self.plot_spectrogram)

        self.plot_spectrogram
#         self.refresh_survey_list()
#         self.refresh_wavefile_list(0)

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
        
        # Workspace and survey..
        self.workspacedir_label = QtWidgets.QLabel('Workspace: -     ')
        self.survey_label = QtWidgets.QLabel('Survey: -')
        self.itemid_label = QtWidgets.QLabel('Item id: -')
#         self.workspacedir_edit = QtWidgets.QLineEdit('workspace_1')
#         self.workspacedir_edit.textChanged.connect(self.refresh_survey_list)
#         self.survey_combo = QtWidgets.QComboBox()
#         self.survey_combo.setEditable(False)
#         self.survey_combo.setMinimumWidth(250)
# #         self.survey_combo.setMaximumWidth(300)
#         self.survey_combo.addItems(['<select survey>'])
#         self.survey_combo.currentIndexChanged.connect(self.refresh_wavefile_list)
# #         self.survey_combo.setMaximumWidth(300)
#         self.wavefile_combo = QtWidgets.QComboBox()
#         self.wavefile_combo.setEditable(False)
#         self.wavefile_combo.setMinimumWidth(250)
#         self.wavefile_combo.addItems(['<select wavefile>'])
#         self.wavefile_combo.currentIndexChanged.connect(self.plot_spectrogram)
#         
#         self.firstwave_button = QtWidgets.QPushButton('|<')
#         self.firstwave_button.clicked.connect(self.firstwave)
#         self.prevwave_button = QtWidgets.QPushButton('<')
#         self.prevwave_button.clicked.connect(self.prevwave)
#         self.nextwave_button = QtWidgets.QPushButton('>')
#         self.nextwave_button.clicked.connect(self.nextwave)
#         self.lastwave_button = QtWidgets.QPushButton('>|')
#         self.lastwave_button.clicked.connect(self.lastwave)

        # Wave file.
#         self.wavefilepath_edit = QtWidgets.QLineEdit('')
#         self.wavefilepath_button = QtWidgets.QPushButton('Browse...')
#         self.wavefilepath_button.clicked.connect(self.wavefile_browse)
#         self.wavefilepath_button.clicked.connect(self.test_plot)
        
        self.windowsize_combo = QtWidgets.QComboBox()
        self.windowsize_combo.setEditable(False)
        self.windowsize_combo.setMaximumWidth(300)
        self.windowsize_combo.addItems(['128', 
                                        '256', 
                                        '512', 
                                        '1024', 
                                        '2048', 
                                        '4096', 
                                        ])
        self.windowsize_combo.setCurrentIndex(2)
        self.windowsize_combo.currentIndexChanged.connect(self.plot_spectrogram)
        self.overlap_combo = QtWidgets.QComboBox()
        self.overlap_combo.setEditable(False)
        self.overlap_combo.setMaximumWidth(300)
        self.overlap_combo.addItems(['None', 
                                        'Low', 
                                        'Medium', 
                                        'High', 
                                        'Highest', 
                                       ])
        self.overlap_combo.setCurrentIndex(1)
        self.overlap_combo.currentIndexChanged.connect(self.plot_spectrogram)
        
        # Matplotlib figure and canvas for Qt5.
        self._figure = mpl_figure.Figure()
        self._canvas = mpl_backend.FigureCanvasQTAgg(self._figure) 
        self.axes = self._figure.add_subplot(111)       
        self._canvas.show()
        
        # Layout widgets.
        form1 = QtWidgets.QGridLayout()
        gridrow = 0
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.workspacedir_label)
        hlayout.addWidget(self.survey_label)
        hlayout.addStretch(5)
        form1.addLayout(hlayout, gridrow, 0, 1, 10)
        gridrow += 1
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.itemid_label)
        hlayout.addStretch(5)
        form1.addLayout(hlayout, gridrow, 0, 1, 10)
#         hlayout.addWidget(QtWidgets.QLabel('Workspace:'))
#         hlayout.addWidget(self.workspacedir_edit, 7)
#         hlayout.addWidget(QtWidgets.QLabel('Survey:'))
#         hlayout.addWidget(self.survey_combo, 10)
# #         hlayout.addWidget(self.refresh_button)
# #         hlayout.addStretch(10)
#         form1.addLayout(hlayout, gridrow, 0, 1, 15)
# #         gridrow += 1
# #         label = QtWidgets.QLabel('Wave file:')
# #         form1.addWidget(label, gridrow, 0, 1, 1)
# #         form1.addWidget(self.wavefilepath_edit, gridrow, 1, 1, 13)
# #         form1.addWidget(self.wavefilepath_button, gridrow, 14, 1, 1)
#         gridrow += 1
#         label = QtWidgets.QLabel('Wavefiles:')
#         form1.addWidget(label, gridrow, 0, 1, 1)
#         form1.addWidget(self.wavefile_combo, gridrow, 1, 1, 9)
#         form1.addWidget(self.firstwave_button, gridrow, 10, 1, 1)
#         form1.addWidget(self.prevwave_button, gridrow, 11, 1, 1)
#         form1.addWidget(self.nextwave_button, gridrow, 12, 1, 1)
#         form1.addWidget(self.lastwave_button, gridrow, 13, 1, 1)
# #         form1.addWidget(self.wavefilepath_button, gridrow, 14, 1, 1)
        gridrow += 1
        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch(10)
        hbox.addWidget(app_framework.RightAlignedQLabel('Window size:'))
        hbox.addWidget(self.windowsize_combo)
        hbox.addWidget(app_framework.RightAlignedQLabel('Overlap:'))
        hbox.addWidget(self.overlap_combo)
#         hbox.addStretch(10)
        form1.addLayout(hbox, gridrow, 0, 1, 10)
        gridrow += 1
        form1.addWidget(self._canvas, gridrow, 0, 100, 10)
        #
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(form1)
        widget.setLayout(layout)
        #
        return widget        
    
#     def wavefile_browse(self):
#         """ """
#         # OLD: From file.
# 
#         # Show select file dialog box. Multiple files can be selected.
#         namefilter = 'Wave files (*.wav *.WAV);;All files (*.*)'
#         filenames, _ = QtWidgets.QFileDialog.getOpenFileNames(
#                             self,
#                             'Import sample(s)',
#                             '', # self._last_used_excelfile_name,
#                             namefilter)
#         # Check if user pressed ok or cancel.
#         if filenames:
#             for filename in filenames:
#                 print('DEBUG: ', filename)
#                 self.wavefilepath_edit.setText(filename)
#                 self.plot_spectrogram()
    
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


    # === TODO: Move to Core ===
    
    def firstwave(self):
        """ """
        self.wavefile_combo.setCurrentIndex(0)
        
    def prevwave(self):
        """ """
        index = self.wavefile_combo.currentIndex()
        if index > 0:
            self.wavefile_combo.setCurrentIndex(index-1)
    
    def nextwave(self):
        """ """
        index = self.wavefile_combo.currentIndex()
        maxindex = self.wavefile_combo.count()
        if index < maxindex:
            self.wavefile_combo.setCurrentIndex(index+1)
    
    def lastwave(self):
        """ """
        maxindex = self.wavefile_combo.count()
        self.wavefile_combo.setCurrentIndex(maxindex-1)
    
#     def refresh_survey_list(self):
#         """ """
#         self.survey_combo.clear()
#         self.survey_combo.addItem('<select survey>')
#         dir_path = str(self.workspacedir_edit.text())
#         ws = hdf54bats.Hdf5Workspace(dir_path)
#         h5_list = ws.get_h5_list()
#         for h5_file_key in sorted(h5_list.keys()):
#             h5_file_dict = h5_list[h5_file_key]
#             self.survey_combo.addItem(h5_file_dict['name'])
#             
#             self.survey_combo.setCurrentIndex(1)
# 
#     def refresh_wavefile_list(self, index):
#         """ """
#         self.wavefile_combo.clear()
#         workspace = str(self.workspacedir_edit.text())
#         survey = str(self.survey_combo.currentText())
#         if survey not in ['', '<select survey>']:
#             h5wavefile = hdf54bats.Hdf5Wavefile(workspace, survey)
#             
#             from_top_node = ''
#             wavefiles_dict = h5wavefile.get_wavefiles(from_top_node)
#             for wave_id in sorted(wavefiles_dict):
#                 self.wavefile_combo.addItem(wave_id)
#         else:
#             self.wavefile_combo.clear()
    
    def plot_spectrogram(self):
        """ Use a thread to relese the user. """
        workspace = app_core.DesktopAppSync().get_workspace()
        survey = app_core.DesktopAppSync().get_selected_survey()
        item_id = app_core.DesktopAppSync().get_selected_item_id(item_type='wavefile')
        if not item_id:
            # Clear.
            self.axes.cla()
            self._canvas.draw()
            self.workspacedir_label.setText('Workspace: -     ')
            self.survey_label.setText('Survey: -')
            self.itemid_label.setText('Item id: -')
            return
        #
        self.workspacedir_label.setText('Workspace: <b>' + workspace + '</b>   ')
        self.survey_label.setText('Survey: <b>' + survey + '</b>')
        self.itemid_label.setText('Item id: <b>' + item_id + '</b>')
        #
        try:
            # Check if thread is running.
            if self.spectrogram_thread:
#                 while self.spectrogram_thread.is_alive():
#                     #print('DEBUG: Stop running thread.')
                self.spectrogram_thread_active = False
##################                threading.Timer(0.5, self.plot_spectrogram)
            else:
                
                
                self.axes.cla()
                self._canvas.draw()

                
                
                # Use a thread to relese the user.
                self.spectrogram_thread_active = True
                self.spectrogram_thread = threading.Thread(target = self.run_plot_spectrogram, 
                                                           args=(workspace, survey, item_id))
                self.spectrogram_thread.start()
        except Exception as e:
            print('EXCEPTION in plot_spectrogram_in_thread: ', e)
    
    def run_plot_spectrogram(self, workspace, survey, item_id):
        """ """
        try:
            self.axes.cla()
            #
            if not self.spectrogram_thread_active:
                return
            #
            h5wavefile = hdf54bats.Hdf5Wavefile(workspace, survey)
            try:
                signal = h5wavefile.get_wavefile(item_id, close=False)
                item_title = h5wavefile.get_title(item_id, close=False)
                item_metadata = h5wavefile.get_user_metadata(item_id, close=False)
            finally:
                h5wavefile.close()
            sampling_freq_hz = item_metadata.get('file_frame_rate_hz', '')
            if not sampling_freq_hz:
                sampling_freq = 384000
            else:
                sampling_freq = int(sampling_freq_hz)
            
            print('- Framerate: ', sampling_freq)
            
            if len(signal) > (10 * sampling_freq):
                signal = signal[0:10 * sampling_freq]
                print('Warning: Signal truncated to 10 sec.')
                    
            # File.
#             wave_file = self.wavefilepath_edit.text()
#             wave_file_path = pathlib.Path(wave_file)
    #         if not wave_file_path.is_file():
    #             print('DEBUG: File does not exists: ', wave_file)
    #             return
            # Settings.
            window_size = int(self.windowsize_combo.currentText())
            overlap = self.overlap_combo.currentText()
    #         window_size = 1024
    #         resolution = 'Highest'
            window_function = 'hann'
            jump = int(window_size / 2)
            if overlap == 'None':
                window_function = 'hann'
#                 jump = window_size
                jump = int(sampling_freq / 500)
            elif overlap == 'Low':
                window_function = 'hann'
#                 jump = int(window_size / 1.33) 
                jump = int(sampling_freq / 1000) # 1 ms.
            elif overlap == 'Medium':
    #             window_function = 'black'
                window_function = 'hann'
#                 jump = int(window_size / 2)
                jump = int(sampling_freq / 2000)
            elif overlap == 'High':
#                 window_function = 'blackh'
                window_function = 'hann'
#                 jump = int(window_size / 4)
                jump = int(sampling_freq / 4000)
            elif overlap == 'Highest':
#                 window_function = 'kaiser'
                window_function = 'hann'
#                 jump = int(window_size / 8)
                jump = int(sampling_freq / 8000)
            #
            
            
            
            #
            pos_in_sec_from = 0.0
            pos_in_sec_to = len(signal) / sampling_freq        
            #
            # Cut part from 1 sec signal.
            signal_short = signal[int(pos_in_sec_from * sampling_freq):int(pos_in_sec_to * sampling_freq)]
            # 
            if not self.spectrogram_thread_active:
                return
            # Create util.
            dbsf_util = dsp4bats.DbfsSpectrumUtil(window_size=window_size, 
                                                   window_function=window_function)
            #
            if not self.spectrogram_thread_active:
                return
            # Create matrix.
            ### jump = int(sampling_freq/1000/jumps_per_ms)
            size = int(len(signal_short) / jump)
            matrix = dbsf_util.calc_dbfs_matrix(signal_short, matrix_size=size, jump=jump)
            #
            if not self.spectrogram_thread_active:
                return
            # Plot.
            max_freq = sampling_freq / 1000 / 2 # kHz and Nyquist.
            ###f, ax = plt.subplots(figsize=(15, 5))
            self.axes.imshow(matrix.T, 
                      cmap='viridis', 
                      origin='lower',
                      extent=(pos_in_sec_from, pos_in_sec_to, 
                              0, max_freq)
                     )
            self.axes.axis('tight')
#             self.axes.set_title(wave_file_path.name)
#             self.axes.set_title(wavefile_id)
            self.axes.set_title(item_title)
            self.axes.set_ylabel('Frequency (kHz)')
            self.axes.set_xlabel('Time (s)')
            #ax.set_ylim([0,160])
            #
            if not self.spectrogram_thread_active:
                return
            #
            self._canvas.draw()
            
        finally:
            self.spectrogram_thread = None

    