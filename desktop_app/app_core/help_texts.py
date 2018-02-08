#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Project: http://cloudedbats.org
# Copyright (c) 2018 Arnold Andreasson 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

class HelpTexts(object):  
    """ Help texts for the desktop application. 
        Mostly displayed in util_qt.RichTextQLabel labels, basic HTML tags can be used. 
    """
    
    def __init__(self, parent = None):  
        """ """
        self._texts = {}
        self._add_texts()
    
    def get_text(self, key):
        """ """
        try:          
            return self._texts[key]
        except:
            pass
        return ''
    
    def _add_texts(self):
        """ """          

        # Start activity..

        self._texts['start_activity'] = """
        <p>&nbsp;</p>
        <h3>Welcome to CloudedBats - Desktop application</h3>
        <p>
        The <a href="http://cloudedbats.org">CloudedBats</a>
        software project is about trying to eleminate the need for desktop
        applications when working with bat sound and related data. 
        But the cloud part of CloudedBats is not yet developed, and it will 
        take some years (probably many) before all detectors have internet connection built in.
        </p>
        <p>
        The functionality available is mainly the same that later will be implemented 
        in the CloudedBats detector software and/or in the cloud.
        </p>
        <p>
        Features include in this version are:
        <ul>        
            <li>Automatic extraction of metrics from wave files. 
            Results are saved as tab separated text files and can be used in, 
            for example, Excel or R.
            </li>
            <li>Visualisation of metrics as diagrams, mainly scatter-plots.
            </li>
            <li>Extraction of metadata from Petterson M500X. 
            (I need this myself, more formats may be added on demand by users.)
            </li>
        </ul>
        </p>
        
        <h4>Usage instructions</h4>
        <p>
        The user interface contains <b>activities</b> and <b>extra tools</b>. 
        Activities are always placed in the central part and extra tools can be moved around. 
        Valid places for extra tool are side-by-side or stacked at the bottom or to the right. 
        It is also possible to put them outside the application window. 
        Click on the title bar to move them.
        All activites and tools keeps their content when hidden.
        </p>
        <p>
        All user actions are logged both in the logging tool window and in a text file placed in 
        the same directory (also called folder or map) as the executable application file. 
        This log file is cleared each time the application is started, and it is mainly used when 
        searching for errors in the application. 
        </p>

        <h4>Under development</h4>
        <p>
        CloudedBats is under development following a roughly defined roadmap. 
        Content is mainly defined by my own needs, but user feedback and suggestions are welcome...
        <p>
        Some more information is available via the menu "Help/About".
        </p>
        
        """
        
        # About.
        
        self._texts['about'] = """
        <p>
        <b>CloudedBats - Desktop application</b> <br>
        ###version###
        </p>
        <p>
        This desktop application is a part of the open source 
        <a href="http://cloudedbats.org">CloudedBats.org</a>
        software project.
        </p>
        <p>
        Single file executables are available for Windows, MacOS and Ubuntu (Linux).
        Users who want to run the latest development version can find more 
        information at the GitHub repository: 
        <a href="https://github.com/cloudedbats/cloudedbats_desktop_app">
        https://github.com/cloudedbats/cloudedbats_desktop_app</a>.
        </p>
        <p>
        All source code for the CloudedBats project is developed in Python 3 
        and released under the 
        <a href="http://opensource.org/licenses/mit">MIT license</a>.
        </p>
        <p>
        Developed by: Arnold Andreasson, Sweden.<br/>        
        Contact: info@cloudedbats.org
        </p>
        """


