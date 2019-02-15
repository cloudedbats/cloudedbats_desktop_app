#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: http://cloudedbats.org
# Copyright (c) 2018 Arnold Andreasson 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

"""
This module contains customized GUI-related classes.
"""

import pandas as pd
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5 import QtCore

class RichTextQLabel(QtWidgets.QLabel):
    """ Customized QLabel. Used for informative texts. """
    def __init__(self, parent = None):  
        QtWidgets.QLabel.__init__(self, parent)  
        self.setTextFormat(QtCore.Qt.RichText)
        self.setOpenExternalLinks(True) 
        self.setWordWrap(True)

class HeaderQLabel(QtWidgets.QLabel):  
    """ Customized QLabel. Used for informative texts. """
    def __init__(self, parent = None):  
        QtWidgets.QLabel.__init__(self, parent)  
        self.setTextFormat(QtCore.Qt.RichText)
        self.setAlignment(QtCore.Qt.AlignHCenter)
        self.setStyleSheet(""" 
            * { color: white; background-color: black; }
            """)
        
class RightAlignedQLabel(QtWidgets.QLabel):  
    """ Customized QLabel. """
    def __init__(self, parent = None):  
        QtWidgets.QLabel.__init__(self, parent)  
        self.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
 
class CenterAlignedQLabel(QtWidgets.QLabel):  
    """ Customized QLabel. """
    def __init__(self, parent = None):  
        QtWidgets.QLabel.__init__(self, parent)  
        self.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignCenter)

class LeftAlignedQLabel(QtWidgets.QLabel):  
    """ Customized QLabel. """
    def __init__(self, parent = None):  
        QtWidgets.QLabel.__init__(self, parent)  
        self.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)

class ClickableQLabel(QtWidgets.QLabel):  
    """ Customized QLabel. Emits signal when clicked, and change color when hovering. """
    # Static variables.
    # Create signal.
    label_clicked = QtCore.pyqtSignal()

    def __init__(self, parent = None):  
        QtWidgets.QLabel.__init__(self, parent)  
        # Set style.
        self.setProperty('ActivityStatus', 'Unselected') # TODO: Remove this when stylesheet fixed.
        self.updateStyleSheet()
  
    def mouseReleaseEvent(self, ev):  
        """ Overridden abstract method. """
        self.label_clicked.emit()
  
    def enterEvent(self, ev):
        """ Overridden abstract method. """
        self.setStyleSheet(""" 
            * [ActivityStatus="Selected"] { color: #d1581c; background-color: black; }
            * [ActivityStatus="Unselected"] { color: #d1581c; background-color: white; }
            """)
  
    def leaveEvent(self, ev):  
        """ Overridden abstract method. """
        self.setStyleSheet(""" 
            * [ActivityStatus="Selected"] { color: white; background-color: black; }
            * [ActivityStatus="Unselected"] { color: black; background-color: white; }
            """)

    def updateStyleSheet(self):  
        self.setStyleSheet(""" 
            * [ActivityStatus="Selected"] { color:  white; background-color: black; }
            * [ActivityStatus="Unselected"] { color:  black; background-color: white; }
            """)

class ClickableLinkQLabel(QtWidgets.QLabel):  
    """ Customized QLabel. Emits signal when clicked, and change color when hovering. """
    # Static variables.
    # Create signal.
    link_label_clicked = QtCore.pyqtSignal()
    
    def __init__(self, parent = None):  
        QtWidgets.QLabel.__init__(self, parent)
        #  
        self.setStyleSheet(""" 
            * { color: black; }
            """)
  
    def mouseReleaseEvent(self, ev):  
        """ Overridden abstract method. """
        self.link_label_clicked.emit()
  
    def enterEvent(self, ev):
        """ Overridden abstract method. """
        self.setStyleSheet(""" 
            * { color: #d1581c; }
            """)
  
    def leaveEvent(self, ev):  
        """ Overridden abstract method. """
        self.setStyleSheet(""" 
            * { color: black; }
            """)


class ActivityMenuQLabel(ClickableQLabel):  
    """ Customized QLabel. Contains a list of all ActivityMenuQLabel objects. Only one is marked as active.  """
    # Static variables.
    activityitems = []
    # Create signal.
    activity_menu_label_clicked = QtCore.pyqtSignal()
    
    def __init__(self, parent = None):  
        ClickableQLabel.__init__(self, parent)
        # Add to static variable:
        self.activityitems.append(self)
        self.markAsUnselected()
  
    def mouseReleaseEvent(self, ev):  
        """ Overridden abstract method. """
        self.activity_menu_label_clicked.emit()
        
    def markAsSelected(self):
        """ """
        # Mark all others as unselected.
        for label in self.activityitems:
            label.markAsUnselected() 
        # Mark this as selected.
        self.setProperty('ActivityStatus', 'Selected')
        self.updateStyleSheet()
          
    def markAsUnselected(self):
        """ """
        self.setProperty('ActivityStatus', 'Unselected')
        self.updateStyleSheet()


class SelectableQListView(QtWidgets.QListView):  
    """ Customized QListView. Contains a single column and corresponding checkboxes. """
    def __init__(self, parent = None):
        """ """
        QtWidgets.QListView.__init__(self, parent)
        self._tablemodel = QtGui.QStandardItemModel()
        self.setModel(self._tablemodel)

    def clear(self):
        """ """
        self._tablemodel.clear()        
         
    def setList(self, data_list = None, default_check_state = True):
        """ """
        self._tablemodel.clear()        
        for tableitem in data_list:
            standarditem = QtGui.QStandardItem(tableitem)
            standarditem.setCheckState(QtCore.Qt.Checked)
            standarditem.setCheckable(default_check_state)
            self._tablemodel.appendRow(standarditem)
         
    def checkAll(self):
        """ """
        for rowindex in range(self._tablemodel.rowCount()):
            item = self._tablemodel.item(rowindex, 0)
            item.setCheckState(QtCore.Qt.Checked)
            
    def uncheckAll(self):
        """ """
        for rowindex in range(self._tablemodel.rowCount()):
            item = self._tablemodel.item(rowindex, 0)
            item.setCheckState(QtCore.Qt.Unchecked)

    def getSelectedDataList(self):
        """ """
        selecteddata = []
        self._selected_data_list = []
        for rowindex in range(self._tablemodel.rowCount()):
            item = self._tablemodel.item(rowindex, 0)
            if item.checkState() == QtCore.Qt.Checked:
                selecteddata.append(str(item.text()))
        #
        return selecteddata

    def getNotSelectedDataList(self):
        """ """
        selecteddata = []
        self._selected_data_list = []
        for rowindex in range(self._tablemodel.rowCount()):
            item = self._tablemodel.item(rowindex, 0)
            if item.checkState() != QtCore.Qt.Checked:
                selecteddata.append(str(item.text()))
        #
        return selecteddata

    def getSelectedIndexList(self):
        """ """
        selectedindexes = []
        self._selected_data_list = []
        for rowindex in range(self._tablemodel.rowCount()):
            item = self._tablemodel.item(rowindex, 0)
            if item.checkState() == QtCore.Qt.Checked:
                selectedindexes.append(rowindex)
        #
        return selectedindexes

    def getNotSelectedIndexList(self):
        """ """
        selectedindexes = []
        self._selected_data_list = []
        for rowindex in range(self._tablemodel.rowCount()):
            item = self._tablemodel.item(rowindex, 0)
            if item.checkState() != QtCore.Qt.Checked:
                selectedindexes.append(rowindex)
        #
        return selectedindexes


class ToolboxQTableView(QtWidgets.QTableView):  
    """ Customized QTableView. The table is automatically connected to an 
        instance of ToolboxTableModel.  """
    def __init__(self, parent = None, filter_column_index = None):
        """ """
        QtWidgets.QTableView.__init__(self, parent)
####        self._tablemodel = ToolboxTableModel(modeldata = plankton_core.DatasetTable()) 
        self._tablemodel = PandasModel() 
        self._selectionmodel = None # Created below.
        # Connect models.
        if filter_column_index is None:
            self.setModel(self._tablemodel)
            #
            self._selectionmodel = QtCore.QItemSelectionModel(self._tablemodel) 
            self.setSelectionModel(self._selectionmodel)
            self.resizeColumnsToContents()

            pass

        else:
            """ Use this method if the default model should be replaced by a filtered model. """
            # Filter proxy model.
            self.filterproxymodel = QtCore.QSortFilterProxyModel(self)
            self.filterproxymodel.setSourceModel(self._tablemodel)
            self.filterproxymodel.setFilterKeyColumn(filter_column_index)
            self.setModel(self.filterproxymodel)
            #
            self._selectionmodel = QtCore.QItemSelectionModel(self.filterproxymodel) 
            self.setSelectionModel(self._selectionmodel)
            self.resizeColumnsToContents()        
        # Default setup for tables.
        self.setAlternatingRowColors(True)
        self.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ContiguousSelection)
#         self.verticalHeader().setDefaultSectionSize(18)
           
    def clearModel(self):
        """ """
        if self._tablemodel.getModeldata():
            self._tablemodel.getModeldata().clear()
#         # Call same method in parent class.
#         super(ToolboxQTableView, self).clear()
          
    def resetModel(self):
        """ Used to repaint. """
        if self._tablemodel:
            self._tablemodel.beginResetModel()
#           pass
            self._tablemodel.endResetModel()
          
    def getTableModel(self):
        """ """
        return self._tablemodel.getModeldata()
        
    def setTableModel(self, tablemodeldata):
        """ """
        if self._tablemodel:
            self._tablemodel.beginResetModel()
            self._tablemodel.setModeldata(tablemodeldata)
            self._tablemodel.endResetModel()
          
    def getSelectionModel(self):
        """ """
        return self._selectionmodel
          
    def onFilterTextChanged(self, text):
        """ link the textChanged signal to this method for filtering. 
            In the constructor 'filter_column_index' must be defined. """          
        filterString = QtCore.QRegExp(str(text),
                                QtCore.Qt.CaseInsensitive,
#                                 QtCore.QRegExp.RegExp
                                )
        self.filterproxymodel.setFilterRegExp(filterString)
        

# class ToolboxTableModel(QtCore.QAbstractTableModel):
#     """ """
#     def __init__(self, modeldata = None):
#         """ """
#         self._modeldata = modeldata
#         # Initialize parent.
#         QtCore.QAbstractTableModel.__init__(self)
#         
#     def rowCount(self, parent=QtCore.QModelIndex()):
#         """ Overridden abstract method. """
#         if self._modeldata == None:
#             return 0
#         return self._modeldata.get_row_count()
# 
#     def columnCount(self, parent=QtCore.QModelIndex()):
#         """ Overridden abstract method. """
#         if self._modeldata == None:
#             return 0
#         return self._modeldata.get_column_count()
# 
#     def getModeldata(self):
#         """ """
#         return self._modeldata
# 
#     def setModeldata(self, tablemodeldata):
#         """ """
#         self._modeldata = tablemodeldata
# #         self.reset() 
# #         self.beginResetModel();
# # #         self._modeldata.clear();
# #         self.endResetModel(); 
# 
#     def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
#         """ Overridden abstract method. """
#         if self._modeldata == None:
#             return QtCore.QVariant()
#         if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
#             return QtCore.QVariant(str(self._modeldata.get_header_item(section)))
#         if orientation == QtCore.Qt.Vertical and role == QtCore.Qt.DisplayRole:
#             return QtCore.QVariant(str(section + 1))
#         return QtCore.QVariant()
# 
#     def data(self, index=QtCore.QModelIndex(), role=QtCore.Qt.DisplayRole):
#         """ Overridden abstract method. """
#         if self._modeldata == None:
#             return QtCore.QVariant()
#         if role == QtCore.Qt.DisplayRole:
#             if index.isValid():
#                 return QtCore.QVariant(str(self._modeldata.get_data_item(index.row(), index.column())))
#         return QtCore.QVariant()


class ToolboxEditableQTableView( QtWidgets.QTableView):  
    """ Customized QTableView for editing. The table is automatically connected to an 
        instance of ToolboxEditableTableModel.  """
    def __init__(self, parent = None):
        """ """
        try:
            QtWidgets.QTableView.__init__(self, parent)
            self._selectionmodel = None
             
            # Default setup for tables.
            self.setAlternatingRowColors(True)
            self.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
            #self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
            self.setSelectionMode(QtWidgets.QAbstractItemView.ContiguousSelection)
            # Default model, data and selection        
            self._tablemodel = ToolboxEditableTableModel()
            self.setModel(self._tablemodel)
            self._selectionmodel = QtCore.QItemSelectionModel(self._tablemodel)
            self.setSelectionModel(self._selectionmodel)
            self.resizeColumnsToContents()
        except Exception as e:
            print('DEBUG, Exception: ', e)
            raise
 
    def clearModel(self):
        """ """
        try:
            if self._tablemodel.getModeldata():
                self._tablemodel.getModeldata().clear()
        except Exception as e:
            print('DEBUG, Exception: ', e)
            raise
         
    def getTableModel(self):
        """ """
        return self._tablemodel.getModeldata()
          
    def setTableModel(self, tablemodeldata):
        """ """
        if self._tablemodel:
            self._tablemodel.beginResetModel()
            self._tablemodel.setModeldata(tablemodeldata)
            self._tablemodel.endResetModel()
          
    def getSelectionModel(self):
        """ """
        return self._selectionmodel


class ToolboxEditableTableModel(QtCore.QAbstractTableModel):
    """ Table model for editing. """
    def __init__(self, modeldata = None):
        """ """
        try:
            self._modeldata = modeldata
            # Initialize parent.
            QtCore.QAbstractTableModel.__init__(self)
        except Exception as e:
            print('DEBUG, Exception: ', e)
            raise
        
    def rowCount(self, parent=QtCore.QModelIndex()):
        """ Overridden abstract method. """
        try:
            if self._modeldata == None:
                return 0
            return self._modeldata.get_row_count()
        except Exception as e:
            print('DEBUG, Exception: ', e)
            raise

    def columnCount(self, parent=QtCore.QModelIndex()):
        """ Overridden abstract method. """
        try:
            if self._modeldata == None:
                return 0
            return self._modeldata.get_column_count()
        except Exception as e:
            print('DEBUG, Exception: ', e)
            raise

    def getModeldata(self):
        """ """
        return self._modeldata

    def setModeldata(self, tablemodeldata):
        """ """
        self._modeldata = tablemodeldata

    def headerData(self, section, orientation, role = QtCore.Qt.DisplayRole):
        """ Overridden abstract method. """
        try:
            if self._modeldata == None:
                return QtCore.QVariant()
            if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(str(self._modeldata.get_header_item(section)))
            if orientation == QtCore.Qt.Vertical and role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(str(section + 1))
            return QtCore.QVariant()
        except Exception as e:
            print('DEBUG, Exception: ', e)
            raise

    def data(self, index=QtCore.QModelIndex(), role = QtCore.Qt.DisplayRole):
        """ Overridden abstract method. """
        try:
            if self._modeldata == None:
                return QtCore.QVariant()
            # Also for editing.
            if (role == QtCore.Qt.DisplayRole) or (role == QtCore.Qt.EditRole):
                if index.isValid():
                    return QtCore.QVariant(str(self._modeldata.get_data_item(index.row(), index.column())))
            return QtCore.QVariant()
        except Exception as e:
            print('DEBUG, Exception: ', e)
            raise

    def setData(self, index, value, role = QtCore.Qt.EditRole):
        """ Overridden abstract method. For editing. """
        try:
            if role == QtCore.Qt.EditRole:
#                 self._modeldata.set_data_item(index.row(), index.column(), str(value.toString()))
                self._modeldata.set_data_item(index.row(), index.column(), value)
                self.dataChanged.emit(index, index)
                return True
            return False
        except Exception as e:
            print('DEBUG, Exception: ', e)
            raise

    def flags(self, index):
        """ Overridden abstract method. For editing. """
        try:
            return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        except Exception as e:
            print('DEBUG, Exception: ', e)
            raise


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



# === Style sheets: ===

#def set_app_style_sheet(app):
#    app.setStyleSheet("""
#        /* Default for all dock widgets.*/
#
#
#        /* QWidget, QWidget *  { color: black; background-color: #ffffff; }
#        */
#
#        QDockWidget, QDockWidget *  { color: black; background-color: #eeeeee; }
#        QDockWidget QPushButton:hover { color: #d1581c; }
#        
#        /* Default for all widgets used in tools. */        
#        ToolBase, ToolBase * { color: black; background-color: #eeeeee; } 
#        ToolBase QPushButton:hover { color: #d1581c; } 
#
#        /* Default for all widgets used in activities. */        
#        ActivityBase, ActivityBase * { color: black; background-color: #ffffff; } 
#        ActivityBase QPushButton:hover { color: #d1581c; } 
#        
#        QStatusBar { background-color: #eeeeee; }
#        
#        QLineEdit { background-color: #f8f8f8; }
#        
#        """)

#        QAbstractButton, 
#        QAbstractSlider, 
#        QAbstractSpinBox, 
#        QAxWidget, 
#        QCalendarWidget, 
#        QComboBox, 
#        QDesignerActionEditorInterface, 
#        QDesignerFormWindowInterface, 
#        QDesignerObjectInspectorInterface, 
#        QDesignerPropertyEditorInterface, 
#        QDesignerWidgetBoxInterface, 
#        QDesktopWidget, 
#        QDialog, 
#        QDialogButtonBox, 
#        QDockWidget, 
#        QFocusFrame, 
#        QFrame, 
#        QGLWidget, 
#        QGroupBox, 
#        QHelpSearchQueryWidget, 
#        QHelpSearchResultWidget, 
#        QLineEdit, 
#        QMainWindow, 
#        QMdiSubWindow, 
#        QMenu, 
#        QMenuBar, 
#        QPrintPreviewWidget, 
#        QProgressBar, 
#        QRubberBand, 
#        QSizeGrip, 
#        QSplashScreen, 
#        QSplitterHandle, 
#        QStatusBar, 
#        QSvgWidget, 
#        QTabBar, 
#        QTabWidget, 
#        QToolBar, 
#        QWebView, 
#        QWizardPage, 
#        QWorkspace 

def set_app_style_sheet(app):
    app.setStyleSheet("""
        
/*        QDockWidget .QWidget { background-color: whitesmoke; }
*/
        QAbstractButton:hover { color: #d1581c; }
        
        """)
