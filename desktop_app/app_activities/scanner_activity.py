#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2010-2016 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
#
from __future__ import unicode_literals

import pandas as pd
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5 import QtCore
import app_framework
import app_core

class ScannerActivity(app_framework.ActivityBase):
    """ Used for screening of content of loaded datasets. """

# self.image = QLabel()
# self.image.setPixmap(QPixmap("C:\\myImg.jpg"))
# self.image.setObjectName("image")
# self.image.mousePressEvent = self.getPos
# 
# def getPos(self , event):
#     x = event.pos().x()
#     y = event.pos().y() 
    
    def __init__(self, name, parentwidget):
        """ """
        self._last_used_dir_path = None
        # Initialize parent. Should be called after other 
        # initialization since the base class calls _create_content().
        super(ScannerActivity, self).__init__(name, parentwidget)
    
    def _create_content(self):
        """ """
        content = self._create_scrollable_content()
        contentLayout = QtWidgets.QVBoxLayout()
        content.setLayout(contentLayout)
        # Add activity name at top.
        self._activityheader = app_framework.HeaderQLabel()
        self._activityheader.setText('<h2>' + self.objectName() + '</h2>')
        contentLayout.addWidget(self._activityheader)
        # Add content to the activity.
        contentLayout.addWidget(self._content_scanner_tabs())
    
    def _content_scanner_tabs(self):
        """ """
        # Active widgets and connections.
        selectdatabox = QtWidgets.QGroupBox('', self)
        tabWidget = QtWidgets.QTabWidget()
        tabWidget.addTab(self._content_scanner(), 'Scanner')
        tabWidget.addTab(self._content_adv_settings(), 'Advanced settings')
        tabWidget.addTab(self._content_help(), 'Help')
        # Layout widgets.
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(tabWidget)
        selectdatabox.setLayout(layout)        
        #
        return selectdatabox
    
    # === Scanner ===
    def _content_scanner(self):
        """ """
        widget = QtWidgets.QWidget()
        # From dir.
        self.sourcedir_edit = QtWidgets.QLineEdit('')
        self.sourcedir_button = QtWidgets.QPushButton('Browse...')
        self.sourcedir_button.clicked.connect(self.source_dir_browse)
        self.recursive_checkbox = QtWidgets.QCheckBox('Include subdirectories')
        self.recursive_checkbox.setChecked(False)
        # View from dir content as table.
        self.sourcecontent_button = QtWidgets.QPushButton('View files')
        self.sourcecontent_button.clicked.connect(self.load_data)
        
        
        self.sourcefiles_tableview = app_framework.SelectableQListView()
#         self.sourcefiles_tableview = QtWidgets.QTableView()
#        self.sourcefiles_tableview.setSortingEnabled(True)

        # Check files in tool window.
        self.showfileinbrowser_button = QtWidgets.QPushButton('Show in file browser')
        self.showfileinbrowser_button.clicked.connect(self.load_data)        
        self.firstfile_button = QtWidgets.QPushButton('|<')
        self.firstfile_button.setMaximumWidth(30)
        self.firstfile_button.clicked.connect(self.load_data)        
        self.previousfile_button = QtWidgets.QPushButton('<')
        self.previousfile_button.clicked.connect(self.load_data)        
        self.previousfile_button.setMaximumWidth(30)
        self.nextfile_button = QtWidgets.QPushButton('>')
        self.nextfile_button.clicked.connect(self.load_data)        
        self.nextfile_button.setMaximumWidth(30)
        self.lastfile_button = QtWidgets.QPushButton('>|')
        self.lastfile_button.clicked.connect(self.load_data)        
        self.lastfile_button.setMaximumWidth(30)

        
        
        
        
        # Frequencies.
        self.lowfreqfilter_edit = QtWidgets.QDoubleSpinBox()
        self.lowfreqfilter_edit.setRange(0.0, 250.0)
        self.lowfreqfilter_edit.setValue(15.0)
        self.highfreqfilter_edit = QtWidgets.QDoubleSpinBox()
        self.highfreqfilter_edit.setRange(0.0, 250.0)
        self.highfreqfilter_edit.setValue(250.0)
        # To dir.
        self.targetdir_edit = QtWidgets.QLineEdit('')
        self.targetdir_button = QtWidgets.QPushButton('Browse...')
        self.targetdir_button.clicked.connect(self.target_dir_browse)
        # Scan.
        self.scanfiles_button = QtWidgets.QPushButton("Scan all files")
        self.scanfiles_button.clicked.connect(self.scan_files)
        
        # Layout widgets.
        form1 = QtWidgets.QGridLayout()
        gridrow = 0
        label = QtWidgets.QLabel('From directory:')
        form1.addWidget(label, gridrow, 0, 1, 1)
        form1.addWidget(self.sourcedir_edit, gridrow, 1, 1, 13)
        form1.addWidget(self.sourcedir_button, gridrow, 14, 1, 1)
        gridrow += 1
        form1.addWidget(self.recursive_checkbox, gridrow, 1, 1, 13)
        form1.addWidget(self.sourcecontent_button, gridrow, 14, 1, 1)
        gridrow += 1
        form1.addWidget(self.sourcefiles_tableview, gridrow, 0, 1, 15)
#         form1.addWidget(self.loaded_datasets_listview, gridrow, 0, 1, 15)
        gridrow += 1
#         form1.addWidget(QtWidgets.QLabel(''), gridrow, 0, 1, 1) # Empty row.
        form1.addWidget(app_framework.LeftAlignedQLabel('<b>View in browser:</b>'), gridrow, 0, 1, 1)
        gridrow += 1
#         form1.addWidget(self.showfileinbrowser_button, gridrow, 0, 1, 1)
#         form1.addWidget(self.firstfile_button, gridrow, 1, 1, 1)
#         form1.addWidget(self.previousfile_button, gridrow, 2, 1, 1)
#         form1.addWidget(self.nextfile_button, gridrow, 3, 1, 1)
#         form1.addWidget(self.lastfile_button, gridrow, 4, 1, 1)
        
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.showfileinbrowser_button)
        hlayout.addWidget(self.firstfile_button)
        hlayout.addWidget(self.previousfile_button)
        hlayout.addWidget(self.nextfile_button)
        hlayout.addWidget(self.lastfile_button)
        hlayout.addStretch(10)
        form1.addLayout(hlayout, gridrow, 0, 1, 15)
        
        
        gridrow += 1
        label = QtWidgets.QLabel('Low frequency limit (kHz):')
        form1.addWidget(label, gridrow, 0, 1, 2)
        form1.addWidget(self.lowfreqfilter_edit, gridrow, 2, 1, 5)
        gridrow += 1
        label = QtWidgets.QLabel('High frequency limit (kHz):')
        form1.addWidget(label, gridrow, 0, 1, 2)
        form1.addWidget(self.highfreqfilter_edit, gridrow, 2, 1, 5)
        gridrow += 1
#         form1.addWidget(QtWidgets.QLabel(''), gridrow, 0, 1, 1) # Empty row.
        form1.addWidget(app_framework.LeftAlignedQLabel('<b>Scan all:</b>'), gridrow, 0, 1, 1)

        gridrow += 1
        label = QtWidgets.QLabel('To directory:')
        form1.addWidget(label, gridrow, 0, 1, 1)
        form1.addWidget(self.targetdir_edit, gridrow, 1, 1, 13)
        form1.addWidget(self.targetdir_button, gridrow, 14, 1, 1)
        gridrow += 1
        form1.addWidget(self.scanfiles_button, gridrow, 0, 1, 1)
        #
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(form1)
        widget.setLayout(layout)
        #
        return widget        
        
        
        
###################        
#         self.dataframe_path = QtWidgets.QLineEdit()
#         self.load_dataframe = QtWidgets.QPushButton("Select dataframe")
#         self.load_dataframe.clicked.connect(self.load_data)
#         self.dataframe_tableview = QtWidgets.QTableView()
#         self.dataframe_tableview.setSortingEnabled(True)
#         
#         loaded_datasets_listview = QtWidgets.QListView()
#         self._loaded_datasets_model = QtGui.QStandardItemModel()
#         loaded_datasets_listview.setModel(self._loaded_datasets_model)
#         #
#         self._clear_metadata_button = app_framework.ClickableQLabel('Clear all')
# ###        self.connect(self._clear_metadata_button, QtCore.SIGNAL('clicked()'), self._uncheck_all_datasets)                
#         self._markall_button = app_framework.ClickableQLabel('Mark all')
# ###        self.connect(self._markall_button, QtCore.SIGNAL('clicked()'), self._check_all_datasets)  
#         self.scanfiles_button = QtWidgets.QPushButton("Scan files")
#         self.scanfiles_button.clicked.connect(self.scan_files)
#               
#         # Layout widgets.
#         hbox1 = QtWidgets.QHBoxLayout()
#         hbox1.addWidget(self._clear_metadata_button)
#         hbox1.addWidget(self._markall_button)
#         hbox1.addStretch(10)
#         #
#         layout = QtWidgets.QVBoxLayout()
# #         layout.addWidget(loaded_datasets_listview, 10)
#         layout.addWidget(self.dataframe_path)
#         layout.addWidget(self.load_dataframe)
#         layout.addWidget(self.dataframe_tableview, 10)
#         layout.addLayout(hbox1)
#         layout.addWidget(self.scanfiles_button)
#         widget.setLayout(layout)                
#         #
#         return widget
 
    def source_dir_browse(self):
        """ """
        dirdialog = QtWidgets.QFileDialog(self)
        dirdialog.setFileMode(QtWidgets.QFileDialog.Directory)
        dirdialog.setOptions(QtWidgets.QFileDialog.ShowDirsOnly |
                             QtWidgets.QFileDialog.DontResolveSymlinks)
        dirdialog.setDirectory(str(self.sourcedir_edit.text()))
        dirpath = dirdialog.getExistingDirectory()
        if dirpath:
            self.sourcedir_edit.setText(dirpath)
            self.targetdir_edit.setText(dirpath + '_results')

    def target_dir_browse(self):
        """ """
        dirdialog = QtWidgets.QFileDialog(self)
        dirdialog.setFileMode(QtWidgets.QFileDialog.Directory)
        dirdialog.setOptions(QtWidgets.QFileDialog.ShowDirsOnly |
                             QtWidgets.QFileDialog.DontResolveSymlinks)
        dirdialog.setDirectory(str(self.targetdir_edit.text()))
        dirpath = dirdialog.getExistingDirectory()
        if dirpath:
            self.targetdir_edit.setText(dirpath)

    def load_data(self):
        """ """
        dir_path = str(self.sourcedir_edit.text())
        scanner = app_core.WaveFileScanner()
        dataframe = scanner.get_file_info_as_dataframe(dir_path)
                
        model = PandasModel(dataframe[['file_name']])
        self.sourcefiles_tableview.setModel(model)

#         self.sourcefiles_tableview.resizeColumnsToContents()
            
    def scan_files(self):
        """ """
        scanner = app_core.WaveFileScanner()            
        params = {}
        params['source_dir_path'] = str(self.sourcedir_edit.text())
        params['target_dir_path'] = str(self.targetdir_edit.text())
        params['low_frequency_hz'] = float(self.lowfreqfilter_edit.text()) * 1000.0
        params['high_frequency_hz'] = float(self.highfreqfilter_edit.text()) * 1000.0
        scanner.scan_files_in_thread(params)
            
            
            
            
            
            
#         #
#         header = self.dataframe_tableview.horizontalHeader()
#         header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
#         #
#         header = self.dataframe_tableview.horizontalHeader()
#         for column in range(header.count()):
#             header.setSectionResizeMode(column, QtWidgets.QHeaderView.ResizeToContents)
#             width = header.sectionSize(column)
#             header.setSectionResizeMode(column, QtWidgets.QHeaderView.Interactive)
#             header.resizeSection(column, width)

    
    
    
    def getPos(self , event):
        x = event.pos().x()
        y = event.pos().y()
        print('x: ', x, ' y: ', y) 
    
    
    # === Advanced settings ===
    def _content_adv_settings(self):
        """ """
        widget = QtWidgets.QWidget()
        #
        
        self.image = QtWidgets.QLabel()
        self.image.setPixmap(QtGui.QPixmap('/home/arnold/Desktop/develop/github_cloudedbats_dsp/dsp4bats/batfiles_done1_results/WurbAA03_20170731T221032+0200_N43.3148W2.0060_TE384_Plot.png'))
        self.image.setObjectName("image")
        self.image.mousePressEvent = self.getPos
 

        
        
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
        label.setText(self.get_help_text())
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
 
    def get_help_text(self):
        """ """
        return """
        <p>&nbsp;</p>
        <h3>Scanner</h3>
        <p>
        The scanner...
        </p>
        
        """



class PandasModel(QtCore.QAbstractTableModel): 
    def __init__(self, df = pd.DataFrame(), parent=None): 
        QtCore.QAbstractTableModel.__init__(self, parent=parent)
        self._df = df
    
    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()

        if orientation == QtCore.Qt.Horizontal:
            try:
                return self._df.columns.tolist()[section]
            except (IndexError, ):
                return QtCore.QVariant()
        elif orientation == QtCore.Qt.Vertical:
            try:
                # return self.df.index.tolist()
                return self._df.index.tolist()[section]
            except (IndexError, ):
                return QtCore.QVariant()
    
    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()

        if not index.isValid():
            return QtCore.QVariant()

#         return QtCore.QVariant(str(self._df.ix[index.row(), index.column()]))
        return QtCore.QVariant(str(self._df.iat[index.row(), index.column()])) # More speed (iat).
    
    def setData(self, index, value, role):
        row = self._df.index[index.row()]
        col = self._df.columns[index.column()]
        if hasattr(value, 'toPyObject'):
            # PyQt4 gets a QVariant
            value = value.toPyObject()
        else:
            # PySide gets an unicode
            dtype = self._df[col].dtype
            if dtype != object:
                value = None if value == '' else dtype.type(value)
        self._df.set_value(row, col, value)
        return True
    
    def rowCount(self, parent=QtCore.QModelIndex()): 
        return len(self._df.index)
    
    def columnCount(self, parent=QtCore.QModelIndex()): 
        return len(self._df.columns)

    def sort(self, column, order):
        colname = self._df.columns.tolist()[column]
        self.layoutAboutToBeChanged.emit()
        self._df.sort_values(colname, ascending= order == QtCore.Qt.AscendingOrder, inplace=True)
        self._df.reset_index(inplace=True, drop=True)
        self.layoutChanged.emit()






#     def __init__(self, name, parentwidget):
#         """ """
#         # Initialize parent. Should be called after other 
#         # initialization since the base class calls _create_content().
#         super(ScannerActivity, self).__init__(name, parentwidget)
# #         # Listen for changes in the toolbox dataset list.
# #         self.connect(toolbox_datasets.ToolboxDatasets(), 
# #                      QtCore.SIGNAL('datasetListChanged'), 
# #                      self.update)
#         # Data object used for plotting.
#         self._graph_plot_data = None
# 
#     def update(self):
#         """ """
#         # Selectable list of loaded datasets.
#         self._loaded_datasets_model.clear()        
# ###        for rowindex, dataset in enumerate(toolbox_datasets.ToolboxDatasets().get_datasets()):
# ###            item = QtCore.QStandardItem('Import-' + str(rowindex + 1) + 
# ###                                       '.   Source: ' + dataset.get_metadata('file_name'))
# ###            item.setCheckState(QtCore.Qt.Checked)
# ####            item.setCheckState(QtCore.Qt.Unchecked)
# ###            item.setCheckable(True)
# ###            self._loaded_datasets_model.appendRow(item)
#         #
#         self.update_column_list()
#         self.update_parameter_list()
#         
#     def _create_content(self):
#         """ """
#         content = self._create_scrollable_content()
#         contentLayout = QtWidgets.QVBoxLayout()
#         content.setLayout(contentLayout)
#         # Add activity name at top.
#         self._activityheader = app_framework.HeaderQLabel()
#         self._activityheader.setText('<h2>' + self.objectName() + '</h2>')
#         contentLayout.addWidget(self._activityheader)
#         # Add content to the activity.
#         contentLayout.addWidget(self._content_screening_tabs())
# 
#     def _content_screening_tabs(self):
#         """ """
#         # Active widgets and connections.
#         selectdatabox = QtWidgets.QGroupBox('', self)
#         tabWidget = QtWidgets.QTabWidget()
#         tabWidget.addTab(self._content_select_datasets(), 'Select datasets')
#         tabWidget.addTab(self._content_structure_screening(), 'Check structure')
#         tabWidget.addTab(self._content_codes_species_screening(), 'Check species') # 'Check code lists and species')
#         tabWidget.addTab(self._content_check_column_values(), 'Check column values')
#         tabWidget.addTab(self._content_plot_parameters(), 'Plot parameters')
#         # Layout widgets.
#         layout = QtWidgets.QVBoxLayout()
#         layout.addWidget(tabWidget)
#         selectdatabox.setLayout(layout)        
#         #
#         return selectdatabox
# 
#     # === Select datasets ===
#     def _content_select_datasets(self):
#         """ """
#         widget = QtWidgets.QWidget()
#         #
#         loaded_datasets_listview = QtWidgets.QListView()
#         self._loaded_datasets_model = QtGui.QStandardItemModel()
#         loaded_datasets_listview.setModel(self._loaded_datasets_model)
#         #
#         self._clear_metadata_button = app_framework.ClickableQLabel('Clear all')
# ###        self.connect(self._clear_metadata_button, QtCore.SIGNAL('clicked()'), self._uncheck_all_datasets)                
#         self._markall_button = app_framework.ClickableQLabel('Mark all')
# ###        self.connect(self._markall_button, QtCore.SIGNAL('clicked()'), self._check_all_datasets)                
#         # Layout widgets.
#         hbox1 = QtWidgets.QHBoxLayout()
#         hbox1.addWidget(self._clear_metadata_button)
#         hbox1.addWidget(self._markall_button)
#         hbox1.addStretch(10)
#         #
#         layout = QtWidgets.QVBoxLayout()
#         layout.addWidget(loaded_datasets_listview, 10)
#         layout.addLayout(hbox1)
#         widget.setLayout(layout)                
#         #
#         return widget
# 
#     def _check_all_datasets(self):
#         """ """
#         for rowindex in range(self._loaded_datasets_model.rowCount()):
#             item = self._loaded_datasets_model.item(rowindex, 0)
#             item.setCheckState(QtCore.Qt.Checked)
#             
#     def _uncheck_all_datasets(self):
#         """ """
#         for rowindex in range(self._loaded_datasets_model.rowCount()):
#             item = self._loaded_datasets_model.item(rowindex, 0)
#             item.setCheckState(QtCore.Qt.Unchecked)
# 
#     # === Content structure ===
#     def _content_structure_screening(self):
#         """ """
#         widget = QtWidgets.QWidget()
#         # Active widgets and connections.
# #         introlabel = utils_qt.RichTextQLabel()
# #         introlabel.setText(help_texts.HelpTexts().getText('ScreeningActivity_intro_0'))
#         #
#         self._checkdatasets_button = QtWidgets.QPushButton('View\ndatasets')
# ###        self.connect(self._checkdatasets_button, QtWidgets.SIGNAL('clicked()'), self._check_datasets)                
#         self._checkvisits_button = QtWidgets.QPushButton('View\nsampling events')
# ###        self.connect(self._checkvisits_button, QtWidgets.SIGNAL('clicked()'), self._check_visits) 
#         self._checksamples_button = QtWidgets.QPushButton('View\nsamples')
# ###        self.connect(self._checksamples_button, QtCore.SIGNAL('clicked()'), self._check_samples) 
#         #                
#         self._checkduplicates_button = QtWidgets.QPushButton('Scan for\nduplicates')
# ###        self.connect(self._checkduplicates_button, QtCore.SIGNAL('clicked()'), self._scan_for_duplicates)                
# 
#         # Result content.
#         self._structureresult_list = QtWidgets.QTextEdit()
#         # Layout widgets.
#         form1 = QtWidgets.QGridLayout()
#         gridrow = 0
#         label1 = QtWidgets.QLabel('Result:')
#         form1.addWidget(label1, gridrow, 1, 1, 1)
#         gridrow += 1
#         form1.addWidget(self._checkdatasets_button, gridrow, 0, 1, 1)
#         form1.addWidget(self._structureresult_list, gridrow, 1, 30, 1)
#         gridrow += 1
#         form1.addWidget(self._checkvisits_button, gridrow, 0, 1, 1)
#         gridrow += 1
#         form1.addWidget(self._checksamples_button, gridrow, 0, 1, 1)
#         gridrow += 1
#         form1.addWidget(self._checkduplicates_button, gridrow, 0, 1, 1)
#         #
#         layout = QtWidgets.QVBoxLayout()
# #         layout.addWidget(introlabel)
#         layout.addLayout(form1, 10)
#         layout.addStretch(5)
#         widget.setLayout(layout)                
#         #
#         return widget
# 
#     def _check_datasets(self):
#         """ """
#         self._structureresult_list.clear()
# #         datasets = toolbox_datasets.ToolboxDatasets().get_datasets()
# #         #
# #         countvisits = 0
# #         countsamples = 0
# #         countvariables = 0
# #         #
# #         if datasets and (len(datasets) > 0):
# #             for rowindex, dataset in enumerate(datasets):
# #                 #
# #                 item = self._loaded_datasets_model.item(rowindex, 0)
# #                 if item.checkState() == QtCore.Qt.Checked:        
# #                     #
# #                     row = 'Dataset: ' + dataset.get_metadata('file_name')
# #                     self._structureresult_list.append(row)
# #                     countvisits = 0
# #                     countsamples = 0
# #                     countvariables = 0
# #                     for visitnode in dataset.get_children():
# #                         countvisits += 1
# #                         for samplenode in visitnode.get_children():
# #                             countsamples += 1
# #                             countvariables += len(samplenode.get_children())
# #                     #
# #                     row = '   - Sampling events: ' + str(countvisits) + \
# #                           ', samples: ' + str(countsamples) + \
# #                           ', variable rows: ' + str(countvariables) 
# #                     self._structureresult_list.append(row)
# 
#     def _check_visits(self):
#         """ """
#         self._structureresult_list.clear()
# #         datasets = toolbox_datasets.ToolboxDatasets().get_datasets()
# #         #
# #         countsamples = 0
# #         countvariables = 0
# #         #
# #         if datasets and (len(datasets) > 0):
# #             for rowindex, dataset in enumerate(datasets):
# #                 #
# #                 item = self._loaded_datasets_model.item(rowindex, 0)
# #                 if item.checkState() == QtCore.Qt.Checked:        
# #                     #
# #                     row = 'Dataset: ' + dataset.get_metadata('file_name')
# #                     self._structureresult_list.append(row)
# #                     countsamples = 0
# #                     countvariables = 0
# #                     for visitnode in dataset.get_children():
# #                         row = '   - Sampling event: ' + visitnode.get_data('station_name') + \
# #                               ', ' + visitnode.get_data('sample_date')
# #                         self._structureresult_list.append(row)
# #                         countsamples = 0
# #                         countvariables = 0
# #                         for samplenode in visitnode.get_children():
# #                             countsamples += 1
# #                             countvariables += len(samplenode.get_children())
# #                         #
# #                         row = '      - Samples: ' + str(countsamples) + \
# #                           ', variable rows: ' + str(countvariables) 
# #                         self._structureresult_list.append(row)
# 
#     def _check_samples(self):
#         """ """
#         self._structureresult_list.clear()
# #         datasets = toolbox_datasets.ToolboxDatasets().get_datasets()
# #         #
# #         if datasets and (len(datasets) > 0):
# #             for rowindex, dataset in enumerate(datasets):
# #                 #
# #                 item = self._loaded_datasets_model.item(rowindex, 0)
# #                 if item.checkState() == QtCore.Qt.Checked:        
# #                     #
# #                     row = 'Dataset: ' + dataset.get_metadata('file_name')
# #                     self._structureresult_list.append(row)
# #                     for visitnode in dataset.get_children():
# #                         row = '   - Sampling event: ' + \
# #                               str(visitnode.get_data('station_name')) + ' ' + \
# #                               str(visitnode.get_data('sample_date'))
# #                         self._structureresult_list.append(row)
# #                         for samplenode in visitnode.get_children():
# #                             row = '      - Sample: ' + \
# #                                   str(samplenode.get_data('sample_min_depth_m')) + '-' + \
# #                                   str(samplenode.get_data('sample_max_depth_m'))
# #                             self._structureresult_list.append(row)
# #                             countvariables = len(samplenode.get_children())
# #                             #
# #                             row = '         - Variable rows: ' + str(countvariables) 
# #                             self._structureresult_list.append(row)
# #                             #
# #                             parameter_set = set()
# #                             taxonname_set = set()
# #                             taxonsizestagesex_set = set()
# #                             for variablenode in samplenode.get_children():
# #                                 parameter = variablenode.get_data('parameter')
# #                                 unit = variablenode.get_data('unit')
# #                                 taxonname = variablenode.get_data('scientific_name')
# #                                 sizeclass = variablenode.get_data('size_class')
# #                                 stage = variablenode.get_data('stage')
# #                                 sex = variablenode.get_data('sex')
# #                                 if parameter:
# #                                     parameter_set.add(parameter + '+' + unit)
# #                                 if taxonname:
# #                                     taxonname_set.add(taxonname)
# #                                     taxonsizestagesex_set.add(taxonname + '+' + sizeclass + '+' + stage + '+' + sex)
# #                             row = '         - Unique parameters/units: ' + str(len(parameter_set)) 
# #                             self._structureresult_list.append(row)
# #                             row = '         - Unique taxon names: ' + str(len(taxonname_set)) 
# #                             self._structureresult_list.append(row)
# #                             row = '         - Unique taxon-names/size-classes/stages/sex: ' + str(len(taxonsizestagesex_set)) 
# #                             self._structureresult_list.append(row)
# 
#     def _scan_for_duplicates(self):
#         """ """
#         self._structureresult_list.clear()
# #         datasets = toolbox_datasets.ToolboxDatasets().get_datasets()
# #         #
# #         dataset_descr = ''
# #         visit_descr = ''
# #         sample_descr = ''
# #         #
# #         check_duplicates_list = []
# #         #
# #         if datasets and (len(datasets) > 0):
# #             for rowindex, dataset in enumerate(datasets):
# #                 #
# #                 item = self._loaded_datasets_model.item(rowindex, 0)
# #                 if item.checkState() == QtCore.Qt.Checked:        
# #                     #
# #                     dataset_descr = dataset.get_metadata('file_name')
# #                     for visitnode in dataset.get_children():
# #                         visit_descr = str(visitnode.get_data('station_name')) + ', ' + \
# #                                       str(visitnode.get_data('sample_date'))
# #                         for samplenode in visitnode.get_children():
# #                             sample_descr = str(samplenode.get_data('sample_min_depth_m')) + '-' + \
# #                                            str(samplenode.get_data('sample_max_depth_m'))
# #                             check_duplicates_list = [] # Duplicates can occur inside one sample.
# #                             sample_description = dataset_descr + ', ' + visit_descr + ', ' + sample_descr
# #                             for variablenode in samplenode.get_children():
# #                                 scientific_name = str(variablenode.get_data('scientific_name'))
# #                                 size_class = str(variablenode.get_data('size_class'))
# #                                 stage = str(variablenode.get_data('stage'))
# #                                 sex = str(variablenode.get_data('sex'))
# #                                 parameter = str(variablenode.get_data('parameter'))
# #                                 unit = str(variablenode.get_data('unit'))
# #                                 #
# #                                 unique_items = (scientific_name, size_class, stage, sex, parameter, unit)
# #                                 if unique_items in check_duplicates_list:
# #                                     if sample_description:
# #                                         # Print first time for sample.
# #                                         self._structureresult_list.append(sample_description)
# #                                         sample_description = ''
# #                                     row = '   - Duplicate found: ' + \
# #                                           scientific_name + ', ' + \
# #                                           size_class + ', ' + \
# #                                           stage + ', ' + \
# #                                           sex + ', ' + \
# #                                           parameter + ', ' + \
# #                                           unit                                        
# #                                     self._structureresult_list.append(row)
# #                                 else:
# #                                     check_duplicates_list.append(unique_items)
# 
#     # === Content code lists and species ===
#     def _content_codes_species_screening(self):
#         """ """
#         widget = QtWidgets.QWidget()
#         # Active widgets and connections.
# #         introlabel_1 = utils_qt.RichTextQLabel()
# #         introlabel_1.setText(help_texts.HelpTexts().getText('ScreeningActivity_intro_1'))
# #         introlabel_2 = utils_qt.RichTextQLabel()
# #         introlabel_2.setText(help_texts.HelpTexts().getText('ScreeningActivity_intro_2'))
# #         introlabel_3 = utils_qt.RichTextQLabel()
# #         introlabel_3.setText(help_texts.HelpTexts().getText('ScreeningActivity_species'))
# #         introlabel_4 = utils_qt.RichTextQLabel()
# #         introlabel_4.setText(help_texts.HelpTexts().getText('ScreeningActivity_sizeclasses'))
#         #
# #         self._checkcodes_button = QtGui.QPushButton('Check\ncode lists')
# #         self.connect(self._checkcodes_button, QtCore.SIGNAL('clicked()'), self._code_list_screening)                
#         self._checkspecies_button = QtWidgets.QPushButton('Check\nspecies')
# ###        self.connect(self._checkspecies_button, QtCore.SIGNAL('clicked()'), self._species_screening) 
#         self._checksizeclasses_button = QtWidgets.QPushButton('Check\nsize classes')
# ###        self.connect(self._checksizeclasses_button, QtCore.SIGNAL('clicked()'), self._bvol_screening) 
# 
#         # Result content.
#         self._codesspeciesresult_list = QtWidgets.QTextEdit()
#         # Layout widgets.
#         form1 = QtWidgets.QGridLayout()
#         gridrow = 0
#         label1 = QtWidgets.QLabel('Result:')
#         form1.addWidget(label1, gridrow, 1, 1, 1)
# #         gridrow += 1
# #         form1.addWidget(self._checkcodes_button, gridrow, 0, 1, 1)
#         gridrow += 1
#         form1.addWidget(self._checkspecies_button, gridrow, 0, 1, 1)
#         form1.addWidget(self._codesspeciesresult_list, gridrow, 1, 30, 1)
#         gridrow += 1
#         form1.addWidget(self._checksizeclasses_button, gridrow, 0, 1, 1)
#         #
#         layout = QtWidgets.QVBoxLayout()
# #         layout.addWidget(introlabel_1)
# #         layout.addWidget(introlabel_2)
# #         layout.addWidget(introlabel_3)
# #         layout.addWidget(introlabel_4)
#         layout.addLayout(form1, 10)
#         layout.addStretch(5)
#         widget.setLayout(layout)                
#         #
#         return widget
# 
# #     def _code_list_screening(self):
# #         """ """
# #         # Screening results is also shown in the toolbox log.
# #         tool_manager.ToolManager().show_tool_by_name('Application log')
# #         #
# #         self._codesspeciesresult_list.clear()
# #         #
# #         try:
# #             app_framework.Logging().log('') # Empty line.
# #             app_framework.Logging().log('Code list screening started...')
# #             app_framework.Logging().start_accumulated_logging()
# #             self._write_to_status_bar('Code list screening in progress...')
# #             # Perform screening.
# #             codetypes_set = plankton_core.ScreeningManager().code_list_screening(toolbox_datasets.ToolboxDatasets().get_datasets())
# #         finally:
# #             # Log in result window.
# #             self._codesspeciesresult_list.append('Screening was done on these code types: ' + 
# #                                               str(sorted(codetypes_set)))
# #             self._codesspeciesresult_list.append('')
# #             #
# #             inforows = app_framework.Logging().get_all_info_rows()
# #             if inforows:
# #                 for row in inforows:
# #                     self._codesspeciesresult_list.append('- ' + row)                
# #             warningrows = app_framework.Logging().getAllWarnings()
# #             if warningrows:
# #                 for row in warningrows:
# #                     self._codesspeciesresult_list.append('- ' + row)
# #             errorrows = app_framework.Logging().get_all_errors()
# #             if errorrows:
# #                 for row in errorrows:
# #                     self._codesspeciesresult_list.append('- ' + row)
# #             # Also add to the logging tool.
# #             app_framework.Logging().log_all_accumulated_rows()
# #             app_framework.Logging().log('Screening was done on these code types: ' + 
# #                                     str(sorted(codetypes_set)))
# #             app_framework.Logging().log('Code list screening done.')
# #             self._write_to_status_bar('')
# 
#     def _species_screening(self):
#         """ """
#         # Screening results is also shown in the toolbox log.
#         app_framework.ToolManager().show_tool_by_name('Application log')
#         #
#         self._codesspeciesresult_list.clear()
#         #
#         try:
#             app_framework.Logging().log('') # Empty line.
#             app_framework.Logging().log('Species screening started...')
#             app_framework.Logging().start_accumulated_logging()
#             self._write_to_status_bar('Species screening in progress...')
#             # Perform screening.
# ###            plankton_core.ScreeningManager().species_screening(toolbox_datasets.ToolboxDatasets().get_datasets())
#         finally:
#             # Log in result window.
# #             self._codesspeciesresult_list.append('Screening was done on these code types: ' + 
# #                                               str(sorted(codetypes_set)))
# #             self._codesspeciesresult_list.append('')
#             #
#             inforows = app_framework.Logging().get_all_info_rows()
#             if inforows:
#                 for row in inforows:
#                     self._codesspeciesresult_list.append('- ' + row)                
#             warningrows = app_framework.Logging().get_all_warnings()
#             if warningrows:
#                 for row in warningrows:
#                     self._codesspeciesresult_list.append('- ' + row)
#             errorrows = app_framework.Logging().get_all_errors()
#             if errorrows:
#                 for row in errorrows:
#                     self._codesspeciesresult_list.append('- ' + row)
#             # Also add to the logging tool.
#             app_framework.Logging().log_all_accumulated_rows()
#             app_framework.Logging().log('Species screening done.')
#             self._write_to_status_bar('')
# 
#     def _bvol_screening(self):
#         """ """
#         # Screening results is also shown in the toolbox log.
#         app_framework.ToolManager().show_tool_by_name('Application log')
#         #
#         self._codesspeciesresult_list.clear()
#         #
#         try:
#             app_framework.Logging().log('') # Empty line.
#             app_framework.Logging().log('BVOL Species screening started...')
#             app_framework.Logging().start_accumulated_logging()
#             self._write_to_status_bar('BVOL Species screening in progress...')
#             # Perform screening.
# ###            plankton_core.ScreeningManager().bvol_species_screening(toolbox_datasets.ToolboxDatasets().get_datasets())
#         finally:
#             # Log in result window.
# #             self._codesspeciesresult_list.append('Screening was done on these code types: ' + 
# #                                               str(sorted(codetypes_set)))
# #             self._codesspeciesresult_list.append('')
#             #
#             inforows = app_framework.Logging().get_all_info_rows()
#             if inforows:
#                 for row in inforows:
#                     self._codesspeciesresult_list.append('- ' + row)                
#             warningrows = app_framework.Logging().get_all_warnings()
#             if warningrows:
#                 for row in warningrows:
#                     self._codesspeciesresult_list.append('- ' + row)
#             errorrows = app_framework.Logging().get_all_errors()
#             if errorrows:
#                 for row in errorrows:
#                     self._codesspeciesresult_list.append('- ' + row)
#             # Also add to the logging tool.
#             app_framework.Logging().log_all_accumulated_rows()
#             app_framework.Logging().log('BVOL Species screening done.')
#             self._write_to_status_bar('')
# 
#     # === Content column values ===
#     def _content_check_column_values(self):
#         """ """
#         widget = QtWidgets.QWidget()
#         # Active widgets and connections.
# #         introlabel = utils_qt.RichTextQLabel()
# #         introlabel.setText(help_texts.HelpTexts().getText('ScreeningActivity_intro_3'))
#         #
#         self._column_list = QtWidgets.QComboBox()
#         self._column_list.setMinimumContentsLength(30)
#         self._column_list.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
#         self._column_list.setEnabled(False)
#         #
# ###        self.connect(self._column_list, QtCore.SIGNAL('currentIndexChanged(int)'), self._update_column_content)                
#         # Column content.
# ##        self._content_list = utils_qt.SelectableQListView()
# ##        self._content_list = QtGui.QListWidget()
#         self._content_list = QtWidgets.QTextEdit()
# #        self._content_list.setMaximumHeight(200)
#         # Layout widgets.
#         form1 = QtWidgets.QGridLayout()
#         gridrow = 0
#         label1 = QtWidgets.QLabel('Column:')
#         label2 = QtWidgets.QLabel('Content:')
#         form1.addWidget(label1, gridrow, 0, 1, 1)
#         form1.addWidget(label2, gridrow, 1, 1, 1)
#         gridrow += 1
#         form1.addWidget(self._column_list, gridrow, 0, 1, 1)
#         form1.addWidget(self._content_list, gridrow, 1, 30, 1)
#         #
#         layout = QtWidgets.QVBoxLayout()
# #         layout.addWidget(introlabel)
#         layout.addLayout(form1, 10)
#         layout.addStretch(5)
#         widget.setLayout(layout)                
#         #
#         return widget
# 
#     def update_column_list(self):
#         """ """
#         self._column_list.clear()
#         self._content_list.clear()
# #         datasets = toolbox_datasets.ToolboxDatasets().get_datasets()
# #         if datasets and (len(datasets) > 0):        
# #             columns_set = set()
# #             for rowindex, dataset in enumerate(datasets):
# #                 #
# #                 item = self._loaded_datasets_model.item(rowindex, 0)
# #                 if item.checkState() == QtCore.Qt.Checked:        
# #                     #
# #                     for column in dataset.get_export_table_columns():
# #                         columns_set.add(column['header']) 
# #             #    
# #             self._column_list.addItems(sorted(columns_set))
# #             self._column_list.setEnabled(True)
# #         else:
# #             self._column_list.clear()
# #             self._column_list.setEnabled(False)
#                                
#     def _update_column_content(self, selected_row):
#         """ """
# #         datasets = toolbox_datasets.ToolboxDatasets().get_datasets()
# #         self._content_list.clear()
# #         if not (datasets and (len(datasets) > 0)):        
# #             return # Empty data.
# #         #
# #         columncontent_set = set()
# #         selectedcolumn = str(self._column_list.currentText())
# #         # Search for export column corresponding model element.
# #         nodelevel = ''
# #         key = ''
# #         for rowindex, dataset in enumerate(datasets):
# #             #
# #             item = self._loaded_datasets_model.item(rowindex, 0)
# #             if item.checkState() == QtCore.Qt.Checked:        
# #                 #
# #                 for info_dict in dataset.get_export_table_columns():
# #                     if info_dict['header'] == selectedcolumn:
# #                         nodelevel = info_dict['node']
# #                         key = info_dict['key']
# #                         break # Break loop.
# #             if nodelevel:
# #                 break # Also break next loop.
# #         #
# #         for rowindex, dataset in enumerate(datasets):
# #             #
# #             item = self._loaded_datasets_model.item(rowindex, 0)
# #             if item.checkState() == QtCore.Qt.Checked:        
# #                 #
# #                 if nodelevel == 'dataset':
# #                     if key in dataset.get_data_dict().keys():
# #                         columncontent_set.add(str(dataset.get_data(key)))
# #                     else:
# #                         columncontent_set.add('') # Add empty field.
# #                 #
# #                 for visitnode in dataset.get_children():
# #                     if nodelevel == 'visit':
# #                         if key in visitnode.get_data_dict().keys():
# #                             columncontent_set.add(str(visitnode.get_data(key)))
# #                         else:
# #                             columncontent_set.add('') # Add empty field.
# #                         continue    
# #                     #
# #                     for samplenode in visitnode.get_children():
# #                         if nodelevel == 'sample':
# #                             if key in samplenode.get_data_dict().keys():
# #                                 columncontent_set.add(str(samplenode.get_data(key)))
# #                             else:
# #                                 columncontent_set.add('') # Add empty field.
# #                             continue    
# #                         #
# #                         for variablenode in samplenode.get_children():
# #                             if nodelevel == 'variable':
# #                                 if key in variablenode.get_data_dict().keys():
# #                                     columncontent_set.add(str(variablenode.get_data(key)))
# #                                 else:
# #                                     columncontent_set.add('') # Add empty field.
# #                                 continue    
# #         # Content list.
# # #        self._content_list.addItems(sorted(columncontent_set))
# #         for row in sorted(columncontent_set): 
# #             self._content_list.append(row)
# 
#     # === Content plot ===
#     def _content_plot_parameters(self):
#         """ """
#         widget = QtWidgets.QWidget()
#         # Active widgets and connections.
# #         introlabel = utils_qt.RichTextQLabel()
# #         introlabel.setText(help_texts.HelpTexts().getText('ScreeningActivity_plotting'))
#         #
#         self._parameter_list = app_framework.SelectableQListView()       
#         #
#         clearall_label = app_framework.ClickableQLabel('Clear all')
#         markall_label = app_framework.ClickableQLabel('Mark all')
# ###        self.connect(clearall_label, QtCore.SIGNAL('clicked()'), self._parameter_list.uncheckAll)                
# ###        self.connect(markall_label, QtCore.SIGNAL('clicked()'), self._parameter_list.checkAll)                
#         #
#         self._plotparameters_button = QtWidgets.QPushButton('Plot parameter values')
# ###        self.connect(self._plotparameters_button, QtCore.SIGNAL('clicked()'), self._plot_screening)                
#         self._plotparameterperdate_button = QtWidgets.QPushButton('Plot parameters values per date')
# ###        self.connect(self._plotparameterperdate_button, QtCore.SIGNAL('clicked()'), self._plot_screening_per_date)                
#         # Layout widgets.
#         form1 = QtWidgets.QGridLayout()
#         gridrow = 0
#         label1 = QtWidgets.QLabel('Parameters:')
#         form1.addWidget(label1, gridrow, 0, 1, 2)
#         gridrow += 1
#         form1.addWidget(self._parameter_list, gridrow, 0, 1, 30)
#         gridrow += 5
#         form1.addWidget(clearall_label, gridrow, 0, 1, 1)
#         form1.addWidget(markall_label, gridrow, 1, 1, 1)
#         #
#         hbox1 = QtWidgets.QHBoxLayout()
# #         hbox1.addStretch(10)
#         hbox1.addWidget(self._plotparameters_button)
#         hbox1.addWidget(self._plotparameterperdate_button)
#         hbox1.addStretch(10)
#         #
#         layout = QtWidgets.QVBoxLayout()
# #         layout.addWidget(introlabel)
#         layout.addLayout(form1, 10)
#         layout.addLayout(hbox1)
#         layout.addStretch(5)
#         widget.setLayout(layout)                
#         #
#         return widget
# 
#     def update_parameter_list(self):
#         """ """
#         self._parameter_list.clear()
# #         datasets = toolbox_datasets.ToolboxDatasets().get_datasets()
# #         if datasets and (len(datasets) > 0):        
# #             parameter_set = set()
# #             for rowindex, dataset in enumerate(datasets):
# #                 #
# #                 item = self._loaded_datasets_model.item(rowindex, 0)
# #                 if item.checkState() == QtCore.Qt.Checked:        
# #                     #
# #                     for visitnode in dataset.get_children():
# #                         for samplenode in visitnode.get_children():
# #                             for variablenode in samplenode.get_children():
# #                                 parameter_set.add(variablenode.get_data('parameter') + ' (' + variablenode.get_data('unit') + ')')
# #                 self._parameter_list.setList(sorted(parameter_set))
# 
#     def _plot_screening(self):
#         """ """
#         # Show the Graph plotter tool if hidden. 
#         app_framework.ToolManager().show_tool_by_name('Graph plotter')
#         graphtool = app_framework.ToolManager().get_tool_by_name('Graph plotter')
#         graphtool.clear_plot_data()
#         # Set up plot data for this type.
# ###        self._graph_plot_data = toolbox_utils.GraphPlotData(
# ###                        title = 'Parameter values in sequence', 
# ###                        y_type = 'float',
# ###                        x_label = 'Sequence position in dataset(s)',
# ###                        y_label = 'Value')        
#         # One plot for each selected parameter.
#         for parameter in self._parameter_list.getSelectedDataList():
#             self._add_plot(parameter)
#         # View in the graph-plot tool.    
#         graphtool.set_chart_selection(chart = 'Line chart',
#                                     combined = True, stacked = False, y_log_scale = True)
#         graphtool.set_plot_data(self._graph_plot_data)   
# 
#     def _add_plot(self, parameter):
#         """ """
# #         datasets = toolbox_datasets.ToolboxDatasets().get_datasets()
# #         #
# #         yarray = []
# # #        unit_set = set() # In case of different units on the same parameter.
# #         #
# #         if datasets and (len(datasets) > 0):
# #             for rowindex, dataset in enumerate(datasets):
# #                 #
# #                 item = self._loaded_datasets_model.item(rowindex, 0)
# #                 if item.checkState() == QtCore.Qt.Checked:        
# #                     #
# #                     for visitnode in dataset.get_children():
# #                         for samplenode in visitnode.get_children():
# #                             for variablenode in samplenode.get_children():
# #                                 if (variablenode.get_data('parameter') + ' (' + variablenode.get_data('unit') + ')') == parameter:
# #     #                                 unit_set.add(variablenode.get_data('unit'))
# #                                     value = variablenode.get_data('value')
# #                                     yarray.append(value)                  
# #         #
# # #         units = ' --- '.join(sorted(unit_set))
# # #         parameter_unit = parameter + ' (' + units + ')' 
# #         #
# # #         self._graph_plot_data.add_plot(plot_name = parameter_unit, y_array = yarray)
# #         try:
# #             self._graph_plot_data.add_plot(plot_name = parameter, y_array = yarray)
# #         except UserWarning as e:
# #             QtWidgets.QMessageBox.warning(self, "Warning", str(e))
# 
#     def _plot_screening_per_date(self):
#         """ """
# #         # Show the Graph plotter tool if hidden. 
# #         tool_manager.ToolManager().show_tool_by_name('Graph plotter')
# #         graphtool = tool_manager.ToolManager().get_tool_by_name('Graph plotter')
# #         graphtool.clear_plot_data()
# #         # Set up plot data for this type.
# # ###        self._graph_plot_data = toolbox_utils.GraphPlotData(
# # ###                        title = 'Parameter values per date', 
# # ###                        x_type = 'date',
# # ###                        y_type = 'float',
# # ###                        y_label = 'Value')        
# #         # One plot for each selected parameter.
# #         for parameter in self._parameter_list.getSelectedDataList():
# #             self._add_plot_per_date(parameter)
# #         # View in the graph-plot tool.    
# #         graphtool.set_chart_selection(chart = 'Scatter chart',
# #                                     combined = True, stacked = False, y_log_scale = True)
# #         graphtool.set_plot_data(self._graph_plot_data)   
# 
#     def _add_plot_per_date(self, parameter):
#         """ """
# #         datasets = toolbox_datasets.ToolboxDatasets().get_datasets()
# #         #
# #         xarray = []
# #         yarray = []
# # #        unit_set = set() # In case of different units on the same parameter.
# #         #
# #         if datasets and (len(datasets) > 0):
# #             for rowindex, dataset in enumerate(datasets):
# #                 #
# #                 item = self._loaded_datasets_model.item(rowindex, 0)
# #                 if item.checkState() == QtCore.Qt.Checked:        
# #                     #
# #                     for visitnode in dataset.get_children():
# #                         date = visitnode.get_data('sample_date')
# #                         for samplenode in visitnode.get_children():
# #                             for variablenode in samplenode.get_children():
# #                                 if (variablenode.get_data('parameter') + ' (' + variablenode.get_data('unit') + ')') == parameter:
# #     #                                 unit_set.add(variablenode.get_data('unit'))
# #                                     value = variablenode.get_data('value')
# #                                     xarray.append(date)                  
# #                                     yarray.append(value)                  
# #             #
# # #         units = ' --- '.join(sorted(unit_set))
# # #         parameter_unit = parameter + ' (' + units + ')' 
# #         #
# # #         self._graph_plot_data.add_plot(plot_name = parameter_unit, y_array = yarray)
# #         try:
# #             self._graph_plot_data.add_plot(plot_name = parameter, x_array = xarray, y_array = yarray)
# #         except UserWarning as e:
# #             QtWidgets.QMessageBox.warning(self, "Warning", str(e))

