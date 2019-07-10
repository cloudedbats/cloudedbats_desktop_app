#!/usr/bin/python3
# -*- coding:utf-8 -*-

import time
import datetime
import threading
from cloudedbats_app import app_framework
from cloudedbats_app import app_utils
from cloudedbats_app import app_core

# Github repository included as a github submodule.
import dsp4bats
import sound4bats
import hdf54bats

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
                    app_utils.Logging.warning('Wave file scanner is already running. Please try again later.')
                    return
            # Use a thread to relese the user.
            item_id_list = param_dict.get('item_id_list', [])
            low_freq_hz = param_dict.get('low_frequency_hz', 15000.0)
            high_freq_hz = param_dict.get('high_frequency_hz', None)
            min_amp_level_dbfs = param_dict.get('min_amp_level_dbfs', None)
            min_amp_level_relative = param_dict.get('min_amp_level_relative', None)
            
            
            
            
            self._scan_files(item_id_list, 
                             low_freq_hz, high_freq_hz, 
                             min_amp_level_dbfs, min_amp_level_relative)
            
            
            
            
#             self.thread_object = threading.Thread(target=self._scan_files, 
#                                                   args=(item_id_list, 
#                                                         low_freq_hz, high_freq_hz, 
#                                                         min_amp_level_dbfs, min_amp_level_relative
#                                                       ))
#             self.thread_object.start()
        
        except Exception as e:
            app_utils.Logging.warning('Failed to scan wave files. Exception: ' + str(e))
            
    def _scan_files(self, item_id_list, low_freq_hz, high_freq_hz, min_amp_level_dbfs, min_amp_level_relative):
        """ """
        workspace = app_core.DesktopAppSync().get_workspace()
        survey = app_core.DesktopAppSync().get_selected_survey()
        h5wavefile = hdf54bats.Hdf5Wavefiles(workspace, survey)
        
        for item_id in item_id_list:
            
            app_utils.Logging().info('Scanning: ' + item_id)
            
            print('DEBUG:', item_id, '   ', low_freq_hz, '   ', high_freq_hz, '   ', min_amp_level_dbfs, '   ', min_amp_level_relative)
            
            signal = h5wavefile.get_wavefile(item_id=item_id, close=True)
            
            signal = signal / 32767 # To interval -1.0 to 1.0
            
            extractor = sound4bats.PulsePeaksExtractor(debug=True)
            extractor.setup(sampling_freq_hz=384000)
            signal_filtered = extractor.filter(signal, 
                                               filter_low_hz=low_freq_hz, filter_high_hz=high_freq_hz)
            extractor.new_result_table()
            extractor.extract_peaks(signal_filtered, 
                                    min_amp_level_dbfs=min_amp_level_dbfs, min_amp_level_relative=min_amp_level_relative)
            
            result_table = extractor.get_result_table()
            
            print('Debug: TABLE len:', len(result_table))
            
            h5wavefile.add_pulse_peaks_table(item_id, result_table)
            
            
#             extractor.save_result_table(file_path='debug_pulse_peaks' + item_id + '.txt')

#         # Plot.
#         import matplotlib.pyplot
#         
#         time = []
#         freq = []
#         amp = []
#         for row in extractor.get_result_table():
#             if row[0] == 1:
#                 if row[3] > -100: # -100 means silent.
#                     time.append(float(row[1]))
#                     freq.append(float(row[2]))
#                     amp.append(float(row[3]))
#         #
#         amp_min = abs(min(amp))
#         sizes = [((x+amp_min)**1.2) * 0.1 for x in amp]
#          
#     #     matplotlib.pyplot.scatter(time, freq, c=sizes, s=sizes, cmap='Blues')
# #         matplotlib.pyplot.scatter(time, freq, c=amp, s=sizes, cmap='Reds')
# #        matplotlib.pyplot.scatter(time, freq, c=amp, s=0.5, cmap='Reds') #, origin='lower')
#         matplotlib.pyplot.scatter(time, freq, s=0.5 )
#         matplotlib.pyplot.show()

        return #####################################################

