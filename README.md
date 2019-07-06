# CloudedBats - Desktop app

This is a part of CloudedBats: http://cloudedbats.org


**Note: Under development. No stable release yet.**


![CloudedBats - Desktop application](images/CloudedBats-DesktopApp_2019-03-10.jpg?raw=true  "CloudedBats - Desktop application")
Early example of the user interface for the desktop application. CloudedBats.org / [CC-BY](https://creativecommons.org/licenses/by/3.0/)


## Installation

Install Python3, venv, and HDF5 on your computer. 

HDF5 can be downloaded from this page: "https://www.hdfgroup.org/downloads/hdf5/". 
It seems like version 1.8.20 is the last one with installer for Windows 32 bits. 
Use the latest version for all other 64 bits operating systems. 
On macOS it is possible to use Homebrew to install HDF5. Use the command "brew install hdf5". 
For Ubuntu, etc., use "sudo apt-get install libhdf5-serial-dev".

	mkdir work_cloudedbats
	cd work_cloudedbats    
	python -m venv venv
	source venv/bin/activate # On Linux and macOS.
	# venv\Scripts\activate # On Windows.
	git clone https://github.com/cloudedbats/cloudedbats_desktop_app.git
	cd cloudedbats_desktop_app
	pip install -r rquirements.txt
	pip install tables
	pip install h5py
	pip install git+https://github.com/cloudedbats/cloudedbats_dsp
	pip install git+https://github.com/cloudedbats/cloudedbats_hdf5
	pip install git+https://github.com/cloudedbats/cloudedbats_metadata

To run the desktop application:

	python cloudedbats_app_main.py

To bild a single file executabel. Check http://pyinstaller.org for more info.

	pyinstaller cloudedbats_app_main.spec 
	
Contact me if you are not familiar with the stuff above. I have prebuild single file executables for macOS and Windows (called "cloudedbats_desktop_app.exe"). But you have to install HDF5 on your computer yourself before that. 

## Contact

Arnold Andreasson, Sweden.

info@cloudedbats.org
