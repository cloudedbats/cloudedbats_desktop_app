#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: http://cloudedbats.org
# Copyright (c) 2018 Arnold Andreasson 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import sys
import time
import queue
import threading
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
import matplotlib.backends.backend_qt5agg as mpl_backend
import matplotlib.figure as mpl_figure

from cloudedbats_app import app_framework
from cloudedbats_app import app_core
from cloudedbats_app import app_utils
import dsp4bats
import hdf54bats

class CallShapesTool(app_framework.ToolBase):
    """ CallShapes plotting tool. Zero Crossing style. """
    
    def __init__(self, name, parentwidget):
        """ """
        # Initialize parent. Should be called after other 
        # initialization since the base class calls _create_content().
        super(CallShapesTool, self).__init__(name, parentwidget)
        # Where is the tool allowed to dock in the main window.
        self.setAllowedAreas(QtCore.Qt.RightDockWidgetArea | 
                             QtCore.Qt.BottomDockWidgetArea)
        self.setBaseSize(600,600)        
        # Default position. Hide as default.
        self._parent.addDockWidget(QtCore.Qt.RightDockWidgetArea, self)
        self.hide()
        # Plot queue. Used to separate threads.
        self.callshapes_queue = queue.Queue(maxsize=100)
        self.callshapes_thread = None
#         self.callshapes_active = False
        self.callshapes_active = True
        self.last_used_callshapes_item_id = ''
#         self.last_used_window_size = -1
#         self.last_used_timeresolution = -1
#         self.last_used_viewpart = -1
        # Use sync object for workspaces and surveys. 
        app_core.DesktopAppSync().item_id_changed_signal.connect(self.plot_callshapes)
        # Also when visible.
        self.visibilityChanged.connect(self.visibility_changed)
    
    def _create_content(self):
        """ """
        content = self._create_scrollable_content()
        layout = QtWidgets.QVBoxLayout()
        # Add tabs.
        tabWidget = QtWidgets.QTabWidget()
        tabWidget.addTab(self._content_callshapes(), 'Call shapes')
        tabWidget.addTab(self._content_more(), '(More)')
        tabWidget.addTab(self._content_help(), '(Help)')
        # 
        layout.addWidget(tabWidget)
        content.setLayout(layout)
    
    def _content_callshapes(self):
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
        font = QtGui.QFont('Helvetica', pointSize=-1, weight=QtGui.QFont.Bold)
        self.survey_edit.setFont(font)
        self.itemid_edit.setFont(font)
        self.title_edit.setFont(font)
        
#         self.windowsize_combo = QtWidgets.QComboBox()
#         self.windowsize_combo.setEditable(False)
#         self.windowsize_combo.setMinimumWidth(80)
#         self.windowsize_combo.setMaximumWidth(150)
#         self.windowsize_combo.addItems(['128', 
#                                         '256', 
#                                         '512', 
#                                         '1024', 
#                                         '2048', 
#                                         '4096', 
#                                         ])
#         self.windowsize_combo.setCurrentIndex(3)
#         self.windowsize_combo.currentIndexChanged.connect(self.plot_spectrogram)
#         
#         self.timeresolution_combo = QtWidgets.QComboBox()
#         self.timeresolution_combo.setEditable(False)
#         self.timeresolution_combo.setMinimumWidth(80)
#         self.timeresolution_combo.setMaximumWidth(150)
#         self.timeresolution_combo.addItems(['2 ms', 
#                                              '1 ms', 
#                                              '1/2 ms', 
#                                              '1/4 ms', 
#                                              '1/8 ms', 
#                                              ])
#         self.timeresolution_combo.setCurrentIndex(1)
#         self.timeresolution_combo.currentIndexChanged.connect(self.plot_spectrogram)
#         
#         self.viewpart_combo = QtWidgets.QComboBox()
#         self.viewpart_combo.setEditable(False)
#         self.viewpart_combo.setMinimumWidth(80)
#         self.viewpart_combo.setMaximumWidth(150)
#         self.viewpart_combo.addItems(['All', 
#                                       '0-1 s', 
#                                       '1-2 s', 
#                                       '2-3 s', 
#                                       '3-4 s', 
#                                       '4-5 s', 
#                                       '5-6 s', 
#                                       '6-7 s', 
#                                       '7-8 s', 
#                                       '8-9 s', 
#                                       '9-10 s', 
#                                       ])
#         self.viewpart_combo.setCurrentIndex(0)
#         self.viewpart_combo.currentIndexChanged.connect(self.plot_spectrogram)
        
        # Matplotlib figure and canvas for Qt5.
        self._figure = mpl_figure.Figure()
        self._canvas = mpl_backend.FigureCanvasQTAgg(self._figure)
        self.axes = self._figure.add_subplot(111)
        self._figure.tight_layout()
        self._canvas.show()
        
        # Layout widgets.
        form1 = QtWidgets.QGridLayout()
        form1.setSpacing(5)
        form1.setContentsMargins(5,5,5,5)
        
        gridrow = 0
        form1.addWidget(self.survey_label, gridrow, 0, 1, 1)
        form1.addWidget(self.survey_edit, gridrow, 1, 1, 27)
#         label = app_framework.RightAlignedQLabel('FFT window size:')
#         form1.addWidget(label, gridrow, 28, 1, 1)
#         form1.addWidget(self.windowsize_combo, gridrow, 29, 1, 1)
        gridrow += 1
        form1.addWidget(self.itemid_label, gridrow, 0, 1, 1)
        form1.addWidget(self.itemid_edit, gridrow, 1, 1, 27)
#         label = app_framework.RightAlignedQLabel('Time resolution:')
#         form1.addWidget(label, gridrow, 28, 1, 1)
#         form1.addWidget(self.timeresolution_combo, gridrow, 29, 1, 1)
        gridrow += 1
        form1.addWidget(self.title_label, gridrow, 0, 1, 1)
        form1.addWidget(self.title_edit, gridrow, 1, 1, 27)
#         label = app_framework.RightAlignedQLabel('View part:')
#         form1.addWidget(label, gridrow, 28, 1, 1)
#         form1.addWidget(self.viewpart_combo, gridrow, 29, 1, 1)
        gridrow += 1
        form1.addWidget(self._canvas, gridrow, 0, 100, 30)
        #
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(form1)
        widget.setLayout(layout)
        #
        return widget        
    
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
    
    def close(self):
        """ """
        try:
            # Terminate callshapes thread.
            self.callshapes_active = False
            #
            while self.callshapes_queue.qsize() > 5:
                try: self.callshapes_queue.get_nowait()
                except queue.Empty: break # Exits while loop.
            # Send on queue to release thread.
            self.callshapes_queue.put(False)
        except Exception as e:
            debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
            app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))
    
    def visibility_changed(self, visible):
        """ """
        try:
            if visible:
#                 self.last_used_window_size = -1
#                 self.last_used_timeresolution = -1
#                 self.last_used_viewpart = -1
                QtCore.QTimer.singleShot(100, self.plot_callshapes)
                 
        except Exception as e:
            debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
            app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))
    
    def plot_callshapes(self):
        """ Use a thread to relese the user. """
        try:
            workspace = app_core.DesktopAppSync().get_workspace()
            survey = app_core.DesktopAppSync().get_selected_survey()
            item_id = app_core.DesktopAppSync().get_selected_item_id(item_type='wavefile')
            item_metadata = app_core.DesktopAppSync().get_metadata_dict()
            item_title = item_metadata.get('item_title', '')
            # Don't redraw the same callshapes.
            if (item_id == self.last_used_callshapes_item_id): ### and \
#                (int(self.windowsize_combo.currentText()) == self.last_used_window_size) and \
#                (self.timeresolution_combo.currentText() == self.last_used_timeresolution) and \
#                (self.viewpart_combo.currentText() == self.last_used_viewpart):
                return
            #
            try:
                # Check if thread is running.
                if not self.callshapes_thread:
#                     self.callshapes_active = True
                    self.callshapes_thread = threading.Thread(target = self.run_callshapes_plotter, 
                                                               args=())
                    self.callshapes_thread.start()
            
            except Exception as e:
                debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
                app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))
            #
            callshapes_dict = {}
            callshapes_dict['workspace'] = workspace
            callshapes_dict['survey'] = survey
            callshapes_dict['item_id'] = item_id
            callshapes_dict['item_title'] = item_title
            #
            if self.callshapes_queue.qsize() > 5:
                app_utils.Logging().info('Items removed from the callshapes plotting queue.')
                while self.callshapes_queue.qsize() > 5:
                    try:
                        self.callshapes_queue.get_nowait()
                    except queue.Empty:
                        break # Exits while loop.
            #
#             print('- To queue: ', item_id)
            self.callshapes_queue.put(callshapes_dict)
            #
            self.last_used_callshapes_item_id = item_id
#             self.last_used_window_size = int(self.windowsize_combo.currentText())
#             self.last_used_timeresolution = self.timeresolution_combo.currentText()
#             self.last_used_viewpart = self.viewpart_combo.currentText()


        
        except Exception as e:
            debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
            app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))
    
    def run_callshapes_plotter(self):
        """ """
        try:
            try:
                while self.callshapes_active:
                    queue_item = self.callshapes_queue.get()
                    if queue_item == False:
                        # Exit.
                        self.callshapes_active = False
                        continue
                    #
                    self.survey_edit.setText('')
                    self.itemid_edit.setText('')
                    self.title_edit.setText('')
                    #
                    if self.isVisible():
                        workspace = queue_item.get('workspace', '') 
                        survey = queue_item.get('survey', '') 
                        item_id = queue_item.get('item_id', '') 
                        item_title = queue_item.get('item_title', '') 
                        #
                        self.create_callshapes(workspace, survey, item_id)
                        #
                        self.survey_edit.setText(survey)
                        self.itemid_edit.setText(item_id)
                        self.title_edit.setText(item_title)
                        #
#                         time.sleep(0.3)
            finally:
                self.callshapes_thread = None
        
        except Exception as e:
            debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
            app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))
    
    def create_callshapes(self, workspace, survey, item_id):
        """ """
        try:
            if not item_id:
                self.axes.cla()
                self._canvas.draw()
                return
            #
            h5wavefile = hdf54bats.Hdf5Wavefiles(workspace, survey)
            try:
                item_metadata = h5wavefile.get_user_metadata(item_id=item_id, close=False)
                pulsepeaks_dict = h5wavefile.get_pulse_peaks_table(wavefile_id=item_id, close=False)
            finally:
                h5wavefile.close()
                
            sampling_freq_hz = item_metadata.get('rec_frame_rate_hz', '')
            max_freq = int(sampling_freq_hz) / 2 / 1000
            rec_nframes = item_metadata.get('rec_nframes', '')
            pos_in_sec_from = 0.0
            pos_in_sec_to = rec_nframes / int(sampling_freq_hz)

            # Plot.
            self.axes.cla()
            #
            time_s = pulsepeaks_dict['time_s']
            freq = pulsepeaks_dict['freq_khz']
            amp = pulsepeaks_dict['amp_dbfs']
            #
            amp_min = abs(min(amp))
            sizes = [((x+amp_min)**1.2) * 0.1 for x in amp]
              
#         #     matplotlib.pyplot.scatter(time_s, freq, c=sizes, s=sizes, cmap='Blues')
#     #         matplotlib.pyplot.scatter(time_s, freq, c=amp, s=sizes, cmap='Reds')
#     #        matplotlib.pyplot.scatter(time_s, freq, c=amp, s=0.2, cmap='Reds') #, origin='lower')
#             matplotlib.pyplot.scatter(time_s, freq, s=0.5 )
#             matplotlib.pyplot.show()

            self.axes.scatter(time_s, freq, s=0.2, alpha=0.5)
#             self.axes.scatter(time_s, freq, c=amp, s=0.2, cmap='Blues', alpha=0.5)
            
            self.axes.set_xlim(pos_in_sec_from, pos_in_sec_to)
            self.axes.set_ylim(0, max_freq)
#             self.axes.axis('tight')
#             self.axes.set_title(item_title)
            self.axes.set_ylabel('Frequency (kHz)')
            self.axes.set_xlabel('Time (s)')
            #ax.set_ylim([0,160])
             
            self.axes.minorticks_on()
            self.axes.grid(which='major', linestyle='-', linewidth='0.5', alpha=0.6)
            self.axes.grid(which='minor', linestyle='-', linewidth='0.5', alpha=0.3)
            self.axes.tick_params(which='both', top='off', left='off', right='off', bottom='off')
            #
            self._canvas.draw()
            
            
        except Exception as e:
            debug_info = self.__class__.__name__ + ', row  ' + str(sys._getframe().f_lineno)
            app_utils.Logging().error('Exception: (' + debug_info + '): ' + str(e))
