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

        # Start activity.

        self._texts['start_activity'] = """
        <p>&nbsp;</p>
        <h2>Welcome to CloudedBats - Desktop application</h2>
        <p>
        This desktop application is a free tool to be used when working with data collected during 
        bat surveys. 
        The software is based on a simple hierarchical data model where metadata (= data about data) 
        can be assigned at each level in that hierarchy.
        Ultrasonic recordings of bat sound can be imported from various types of detectors, and for some 
        of them, metadata can be extracted automatically. When imported, and pre-processed, it should 
        be easy and fast to browse through the recordings. 
        </p>
        
        <p>
        <i>Note: The software is under development. 
        Planned, but unfinished parts in the software are marked with parentheses.</i>
        </p>
        
        <h3>Data storage</h3>
        <p>
        Data and metadata for one survey is stored in a single HDF5 file (with the extension .h5). 
        HDF5 is a file format commonly used for scientific data; to store, work with and share data.
        It is also possible to do deeper analysis of data stored in a HDF5 file by using tools like 
        R and Python, and there are generic free browsers available for HDF5 files.
        For this application it is used as a replacement for a relational database, and it is chosen 
        because it is fast and can store huge amounts of data.
        </p>
        
        <h3>Types of nodes in the hierarchical data model are:</h3>
        <p>
        
        </p>
        
        <h4>- Workspace</h4>
        <p>
        A workspace is a directory where the HDF5 files are located. Each HDF5 file contains everything 
        for a specific survey, and therefore they can be moved to different hard drives and USB flash drives.
        Just point out the directory where they are located and use that as a workspace.
        </p>
        
        <h4>- Surveys</h4>
        <p>
        Survey is the top node in each HDF5 file. There are no specific limits for the size of a survey; 
        it depends on computer performance, etc. 
        Start with, for example, a small survey with 5000 recordings, 10 seconds each, and check what's
        works best for you.
        From a metadata perspective it is important to assign enough metadata to describe the survey 
        for future use. For example purpose of the survey, if it is a part of a program, contact information, 
        usage licenses for data, etc. 
        
        <br>One survey contains a number of events. 
        </p>
        
        <h4>- Events</h4>
        <p>
        A sampling event is a place, or area, at a certain time, or period. Results from the manual or 
        semi-automated analysis of recordings should be possible to store on the event node in a tabular form. 
        <br>One event contains a number of detectors.
        </p>
        
        <h4>- Detectors</h4>
        <p>
        Detectors are placed at different locations during an event. For transects, each recorded wavefile 
        will have the location stored and the bounding box can automatically be calculated from that 
        information. Important metadata is how the detector is deployed.
        <br>One detector contains a number of wavefiles.
        </p>
        
        <h4>- Wavefiles</h4>
        <p>
        A lot of metadata can automatically be extracted when importing the files. The files are stored in
        an internal format that makes it possible to export the wavefiles to a uniformed format even if
        different types of detectors are used.
        <br>Imported wavefiles can be scanned and visualised in various tool, for example as Spectrograms, 
        as Call shapes or as Metric plots.
        </p>
        
        <h3>Metadata</h3>
        <p>
        Internally metadata are stored as key-value lists at each note. Keys are always made up of lowercase
        characters where words are separated by underscore, for example: 'frame_rate_hz'. 
        For some types of exports, like Darwin Core, a lot of metadata items are mandatory and follows
        other rules for key names and values. Translation lists and routines will be available to handle 
        those exports.  
        </p>
        
        <h3>Ultrasonic recordings</h3>
        <p>
        During import it is possible to apply some processing. For example cut up longer files into smaller 
        parts and remove silent parts. Metadata that is possible to extract automatically will be converted
        to a format compatible with the GUANO metadata format.
        </p>
        
        <h3>User interface</h3>
        <p>
        The user interface contains <b>activities</b> and <b>extra tools</b>. 
        Activities are always placed in the central part and extra tools can be moved around. 
        Valid places for extra tools are side-by-side or stacked at the bottom or to the right. 
        It is also possible to put them outside the application window. 
        Click on the title bar to move them.
        All activites and tools keeps their content when hidden.
        </p>
        <p>
        The main hierarchy <i>survey - event - detector - wavefile</i> is organised as <b>activities</b>.
        Metadata, spectrograms, maps, etc., are handled as <b>extra tools</b>. Open the extra tools you are
        interested in to work with. The content in the extra tools are automatically synchronised with
        selected parts in the activities, when possible.
        </p>
        <p>
        User settings are stored in a file 'cloudedbats_app_config/desktop_app_settings.txt' located in the 
        same directory as this desktop application. (For macOS users it will be located in the users home 
        folder). Remove that file if you want to reset the system to the default state.  
        </p>
        <p>
        All user actions are logged both in the logging tool window and in a text file placed in 
        the same directory as this desktop application. 
        This log file is cleared each time the application is started, and it's mainly used when 
        searching for errors in the application. 
        </p>
        
        <h3>Open source software</h3>
        <p>
        The software is open and free under the MIT license. That means that you are free to use it as 
        you want, as it is, and with no warranties at all. But if you want to modify the code you are not 
        allowed to remove the license part that makes it open and free. Personally, I hope that you 
        use the system to produce open and free data that you share, but you are not obligated to do that. 
        </p>
        
        <p>
        The software is possible to run on Windows, macOS and Linux computers. Either by running 
        Python3/PyQt5 or by running generated single files executables for each operating system.
        The source code can be found here: <br>
        https://github.com/cloudedbats/cloudedbats_desktop_app
        </p>
        
        <h3>Under development</h3>
        <p>
        CloudedBats is under development following a roughly defined roadmap, and strongly depends on
        how much spare time I have for this and how fun I think it is. 
        Positive feedback is always welcome, and helps me to keep up the speed...
        </p>
        <p>
        Check the "Help/About" menu for contact information.
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
        information at GitHub: 
        <a href="https://github.com/cloudedbats/cloudedbats_desktop_app">
        cloudedbats_desktop_app</a>.
        </p>
        <p>
        All source code for the CloudedBats project is developed in Python 3 
        and released under the 
        <a href="http://opensource.org/licenses/mit">MIT license</a>.
        </p>
        <p>
        Developed by: Arnold Andreasson, Sweden.<br/>        
        Contact and feedback: info@cloudedbats.org
        </p>
        """


