#!/usr/bin/python3
# -*- coding:utf-8 -*-

import time
import datetime
import threading
from cloudedbats_app import app_framework

# Github repository included as a github submodule.
import dsp4bats
from dsp4bats import batfiles_scanner

class WaveFileScanner():
    """ Used for screening of content of loaded datasets. """
        
    def __init__(self):
        """ """
        self.thread_object = None
        self.thread_active = False
    
    def get_file_info_as_dataframe(self, 
                                   dir_path):
        """ """
        wurb_file_util = dsp4bats.WurbFileUtils()
        wurb_file_util.find_sound_files(dir_path=dir_path, 
                                        recursive=False, 
                                        wurb_files_only=False)
        return wurb_file_util.get_dataframe() 
    
    def is_active(self):
        """ """
        return self.thread_active 
    
    def stop_thread(self):
        """ """
        self.thread_active = False
    
    def scan_files_in_thread(self, param_dict):
        """ """
        try:
            # Check if thread is running.
            if self.thread_object:
                if self.thread_object.is_alive():
                    app_framework.Logging.warning('Wave file scanner is already running. Please try again later.')
                    return
            # Use a thread to relese the user.
            source_dir = param_dict.get('source_dir_path', '')
            target_dir = param_dict.get('target_dir_path', '')
            low_freq_hz = param_dict.get('low_frequency_hz', 15.0)
            high_freq_hz = param_dict.get('high_frequency_hz', 250.0)
            
            self.thread_object = threading.Thread(target=self._scan_files, 
                                                  args=(source_dir, target_dir, 
                                                        low_freq_hz, high_freq_hz, 
                                                      )) # logrow_id, datatype_list, year_from, year_to, status, user ))
            self.thread_object.start()
        except Exception as e:
            app_framework.Logging.warning('Failed to scan wave files. Exception: ' + str(e))
            
    def _scan_files(self, source_dir, target_dir, low_freq_hz, high_freq_hz):
        """ """
#         app_framework.Logging().log('Wave file scanner started.')
#  
#         print(aaa, bbb, ccc, ddd)
#          
#         self.thread_active = True
#         time.sleep(5)
#         self.thread_active = False
#  
#         app_framework.Logging().log('Wave file scanner ended.')
 
        return #####################################################


        app_framework.Logging().log('Wave file scanner started.')

         
#         scanner = batfiles_scanner.BatfilesScanner(
#                     batfiles_dir=source_dir,
#                     scanning_results_dir=target_dir,
# #                     batfiles_dir='/home/arnold/Desktop/bats_armstrong',
# #                     scanning_results_dir='/home/arnold/Desktop/bats_armstrong_results',
# #                     batfiles_dir='batfiles',
# #                     scanning_results_dir='batfiles_results',
#                     sampling_freq= 500000, #384000, # True sampling frequency (before TE). 
#                     debug=True) # True: Print progress information.
             
        # Get files.
        scanner.create_list_of_files()
         
        # Scan all files and extract metrics.
        print('\n', 'Scanning files. ',  datetime.datetime.now(), '\n')
        scanner.scan_files(
                    # Time domain parameters.
                    time_filter_low_limit_hz=low_freq_hz, # Lower limit for highpass or bandpass filter.
                    time_filter_high_limit_hz=None,  # Upper limit for lowpass or bandpass filter.
                    localmax_noise_threshold_factor=2.0, # Multiplies the detected noise level by this factor. 
                    localmax_jump_factor=1000, # 1000 gives 1 ms jumps, 2000 gives 0.5 ms jumps.
                    localmax_frame_length=1024, # Frame size to smooth the signal.
                    # Frequency domain parameters.
                    freq_window_size=128, # 
                    freq_filter_low_hz=low_freq_hz, # Don't use peaks below this limit. 
                    freq_threshold_below_peak_db=20.0, # Threshold calculated in relation to chirp peak level.
                    freq_threshold_dbfs =-50.0, # Absolute threshold in dbms. 
                    freq_jump_factor=2000, # 1000 gives 1 ms jumps, 2000 gives 0.5 ms jumps.  
                    freq_max_frames_to_check=100, # Max number of jump steps to calculate metrics.  
                    freq_max_silent_slots=8, # Number of jump steps to detect start/end of chirp.
                    )
         
        # Plot the content of the "*_Metrics.txt" files as Matplotlib plots.
        print('\n', 'Creates plots. ',  datetime.datetime.now(), '\n')
        scanner.plot_results(
                    # Figure settings.
                    figsize_width=16, 
                    figsize_height=10, 
                    dpi=80,
                    # Plot settings.
                    plot_min_time_s=0, # None: Automatic. 
                    plot_max_time_s=1.0, # None: Automatic. 
                    plot_max_freq_khz=200, # None: Automatic.  
                    plot_max_interval_s=0.2, # None: Automatic.  
                    plot_max_duration_ms=20, # None: Automatic.  
                    )
         
        # If the file names contains latitude/longitude information an 
        # interactive map (html) will be generated.
        print('\n', 'Creates map. ',  datetime.datetime.now(), '\n')
        scanner.plot_positions_on_map()
         
        app_framework.Logging().log('Wave file scanner ended.')
    
    
