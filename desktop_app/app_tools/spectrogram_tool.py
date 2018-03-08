#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: http://cloudedbats.org
# Copyright (c) 2018 Arnold Andreasson 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
import numpy as np
import matplotlib.backends.backend_qt5agg as mpl_backend
import matplotlib.figure as mpl_figure

import app_framework
from cloudedbats_dsp import dsp4bats

class SpectrogramTool(app_framework.ToolBase):
    """ Spectrogram plotting tool. """
    
    def __init__(self, name, parentwidget):
        """ """
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
        tabWidget.addTab(self._content_settings(), 'Settings')
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
    def _content_settings(self):
        """ """
        widget = QtWidgets.QWidget()
        #
        
        self.image = QtWidgets.QLabel()
        self.image.setPixmap(QtGui.QPixmap('/home/arnold/Desktop/develop/github_cloudedbats_dsp/dsp4bats/batfiles_done1_results/WurbAA03_20170731T221032+0200_N43.3148W2.0060_TE384_Plot.png'))
        self.image.setObjectName("image")
#         self.image.mousePressEvent = self.getPos
 

        
        
        # Active widgets and connections.
        self._nameedit = QtWidgets.QLineEdit('<Name>')
        self._emailedit = QtWidgets.QLineEdit('<Email>')
        self._customerlist = QtWidgets.QListWidget()
        # Layout.
        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow('&Name:', self._nameedit)
        form_layout.addRow('&Mail:', self._emailedit)
        form_layout.addRow('&Projects:', self._customerlist)
        # Test data.
        self._customerlist.addItem('<First project.>')
        self._customerlist.addItem('<Second project.>')
        #
        # Active widgets and connections.
        self._testbutton = QtWidgets.QPushButton('Write info to log')
#         self._testbutton.clicked.connect(self._test)                
        # Layout.
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self._testbutton)
        button_layout.addStretch(5)
        #
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(form_layout, 10)
        
        layout.addWidget(self.image)
        
        layout.addLayout(button_layout)
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
    
    



    def plot_spectrogram(self):
        """ """
        wave_file = self.wavefilepath_edit.text()
        # Settings.
        window_size = 256
#         window_function = 'kaiser'
        window_function = 'hann'
        jumps_per_ms = 2         
        #
        self.axes.cla()
        if wave_file is None:
            self._canvas.draw()
            return
        # Read signal from file. Length 1 sec.
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
         
        # Create util.
        dbsf_util = dsp4bats.DbfsSpectrumUtil(window_size=window_size, 
                                               window_function=window_function)
        # Create matrix.
        jump = int(sampling_freq/1000/jumps_per_ms)
        size = int(len(signal_short) / jump)
        matrix = dbsf_util.calc_dbfs_matrix(signal_short, matrix_size=size, jump=jump)
         
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
        self.axes.set_ylabel('Frequency (kHz)')
        self.axes.set_xlabel('Time (s)')
        #ax.set_ylim([0,160])
        #
        self._canvas.draw()
    
    