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

from desktop_app import app_framework
import dsp4bats

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
        # Wave file.
        self.wavefilepath_edit = QtWidgets.QLineEdit('')
        self.wavefilepath_button = QtWidgets.QPushButton('Browse...')
        self.wavefilepath_button.clicked.connect(self.wavefile_browse)
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
        self.windowsize_combo.setCurrentIndex(3)
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
        self.overlap_combo.setCurrentIndex(2)
        self.overlap_combo.currentIndexChanged.connect(self.plot_spectrogram)
        
        # Matplotlib figure and canvas for Qt5.
        self._figure = mpl_figure.Figure()
        self._canvas = mpl_backend.FigureCanvasQTAgg(self._figure) 
        self.axes = self._figure.add_subplot(111)       
        self._canvas.show()
        # Layout widgets.
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self._canvas)
        
        # Layout widgets.
        form1 = QtWidgets.QGridLayout()
        gridrow = 0
#         label = QtWidgets.QLabel('From directory:')
#         form1.addWidget(label, gridrow, 0, 1, 1)
#         form1.addWidget(self.sourcedir_edit, gridrow, 1, 1, 13)
#         form1.addWidget(self.sourcedir_button, gridrow, 14, 1, 1)
#         gridrow += 1
#         form1.addWidget(self.recursive_checkbox, gridrow, 1, 1, 13)
#         form1.addWidget(self.sourcecontent_button, gridrow, 14, 1, 1)
#         gridrow += 1
#         form1.addWidget(self.sourcefiles_tableview, gridrow, 0, 1, 15)
# #         form1.addWidget(self.loaded_datasets_listview, gridrow, 0, 1, 15)
#         gridrow += 1
# #         form1.addWidget(QtWidgets.QLabel(''), gridrow, 0, 1, 1) # Empty row.
#         form1.addWidget(app_framework.LeftAlignedQLabel('<b>View in browser:</b>'), gridrow, 0, 1, 1)
#         gridrow += 1
# #         form1.addWidget(self.showfileinbrowser_button, gridrow, 0, 1, 1)
# #         form1.addWidget(self.firstfile_button, gridrow, 1, 1, 1)
# #         form1.addWidget(self.previousfile_button, gridrow, 2, 1, 1)
# #         form1.addWidget(self.nextfile_button, gridrow, 3, 1, 1)
# #         form1.addWidget(self.lastfile_button, gridrow, 4, 1, 1)
        
        gridrow += 1
        label = QtWidgets.QLabel('Wave file:')
        form1.addWidget(label, gridrow, 0, 1, 1)
        form1.addWidget(self.wavefilepath_edit, gridrow, 1, 1, 13)
        form1.addWidget(self.wavefilepath_button, gridrow, 14, 1, 1)
        gridrow += 1
        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch(10)
        hbox.addWidget(app_framework.RightAlignedQLabel('Window size:'))
        hbox.addWidget(self.windowsize_combo)
        hbox.addWidget(app_framework.RightAlignedQLabel('Overlap:'))
        hbox.addWidget(self.overlap_combo)
#         hbox.addStretch(10)
        form1.addLayout(hbox, gridrow, 0, 1, 15)
        gridrow += 1
        form1.addWidget(self._canvas, gridrow, 0, 15, 15)
        #
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(form1)
        widget.setLayout(layout)
        #
        return widget        
    
    def wavefile_browse(self):
        """ """
        # Show select file dialog box. Multiple files can be selected.
        namefilter = 'Wave files (*.wav *.WAV);;All files (*.*)'
        filenames, _ = QtWidgets.QFileDialog.getOpenFileNames(
                            self,
                            'Import sample(s)',
                            '', # self._last_used_excelfile_name,
                            namefilter)
        # Check if user pressed ok or cancel.
        if filenames:
            for filename in filenames:
                print('DEBUG: ', filename)
                self.wavefilepath_edit.setText(filename)
                self.plot_spectrogram()
    
    
    # === Settings ===
#     def _content_settings(self):
#         """ """
#         widget = QtWidgets.QWidget()
#         #
#         
#         self.image = QtWidgets.QLabel()
#         self.image.setPixmap(QtGui.QPixmap('/home/arnold/Desktop/develop/github_cloudedbats_dsp/dsp4bats/batfiles_done1_results/WurbAA03_20170731T221032+0200_N43.3148W2.0060_TE384_Plot.png'))
#         self.image.setObjectName("image")
# #         self.image.mousePressEvent = self.getPos
#         
#         # Active widgets and connections.
#         self._nameedit = QtWidgets.QLineEdit('<Name>')
#         self._emailedit = QtWidgets.QLineEdit('<Email>')
#         self._customerlist = QtWidgets.QListWidget()
#         # Layout.
#         form_layout = QtWidgets.QFormLayout()
#         form_layout.addRow('&Name:', self._nameedit)
#         form_layout.addRow('&Mail:', self._emailedit)
#         form_layout.addRow('&Projects:', self._customerlist)
#         # Test data.
#         self._customerlist.addItem('<First project.>')
#         self._customerlist.addItem('<Second project.>')
#         #
#         # Active widgets and connections.
#         self._testbutton = QtWidgets.QPushButton('Write info to log')
# #         self._testbutton.clicked.connect(self._test)                
#         # Layout.
#         button_layout = QtWidgets.QHBoxLayout()
#         button_layout.addWidget(self._testbutton)
#         button_layout.addStretch(5)
#         #
#         layout = QtWidgets.QVBoxLayout()
#         layout.addLayout(form_layout, 10)
#         
#         layout.addWidget(self.image)
#         
#         layout.addLayout(button_layout)
#         widget.setLayout(layout)                
#         #
#         return widget
    
    
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


    # === Core ===
    
    def plot_spectrogram(self):
        """ Use a thread to relese the user. """
        # Clear.
        self.axes.cla()
        self._canvas.draw()
        try:
            # Check if thread is running.
            if self.spectrogram_thread:
#                 while self.spectrogram_thread.is_alive():
#                     #print('DEBUG: Stop running thread.')
                self.spectrogram_thread_active = False
                threading.Timer(0.5, self.plot_spectrogram)
                    
            # Use a thread to relese the user.
            self.spectrogram_thread_active = True
            self.spectrogram_thread = threading.Thread(target = self.run_plot_spectrogram, 
                                                          args=())
            self.spectrogram_thread.start()
        except Exception as e:
            print('EXCEPTION in plot_spectrogram_in_thread: ', e)
    
    def run_plot_spectrogram(self):
        """ """
        # File.
        wave_file = self.wavefilepath_edit.text()
        wave_file_path = pathlib.Path(wave_file)
        if not wave_file_path.is_file():
            print('DEBUG: File does not exists: ', wave_file)
            return
        # Settings.
        window_size = int(self.windowsize_combo.currentText())
        overlap = self.overlap_combo.currentText()
#         window_size = 1024
#         resolution = 'Highest'
        window_function = 'hann'
        jump = int(window_size / 2)
        if overlap == 'None':
            window_function = 'hann'
            jump = window_size
        elif overlap == 'Low':
            window_function = 'hann'
            jump = int(window_size / 1.33) 
        elif overlap == 'Medium':
#             window_function = 'black'
            window_function = 'hann'
            jump = int(window_size / 2)
        elif overlap == 'High':
            window_function = 'blackh'
#             window_function = 'hann'
            jump = int(window_size / 4)
        elif overlap == 'Highest':
            window_function = 'kaiser'
#             window_function = 'hann'
            jump = int(window_size / 8)
        #
        if not self.spectrogram_thread_active:
            return
        # Read signal from file.
        wave_reader = dsp4bats.WaveFileReader(wave_file)
        sampling_freq = wave_reader.sampling_freq
        signal = np.array([])
        buffer = wave_reader.read_buffer()
        while len(buffer) > 0:
            signal = np.append(signal, buffer)
            buffer = wave_reader.read_buffer()  
        wave_reader.close()
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
        self.axes.set_title(wave_file_path.name)
        self.axes.set_ylabel('Frequency (kHz)')
        self.axes.set_xlabel('Time (s)')
        #ax.set_ylim([0,160])
        #
        if not self.spectrogram_thread_active:
            return
        #
        self._canvas.draw()
    
    