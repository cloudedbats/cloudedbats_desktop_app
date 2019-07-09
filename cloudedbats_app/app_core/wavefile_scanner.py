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
            high_freq_hz = param_dict.get('high_frequency_hz', 250000.0)
            
            
            
            self._scan_files(item_id_list, low_freq_hz, high_freq_hz)
            
            
            
            
#             self.thread_object = threading.Thread(target=self._scan_files, 
#                                                   args=(item_id_list, low_freq_hz, high_freq_hz, 
#                                                       )) # logrow_id, datatype_list, year_from, year_to, status, user ))
#             self.thread_object.start()
        except Exception as e:
            app_utils.Logging.warning('Failed to scan wave files. Exception: ' + str(e))
            
    def _scan_files(self, item_id_list, low_freq_hz, high_freq_hz):
        """ """
        
        print('DEBUG:', item_id_list, '   ', low_freq_hz, '   ', high_freq_hz)
        
        workspace = app_core.DesktopAppSync().get_workspace()
        survey = app_core.DesktopAppSync().get_selected_survey()
        
        item_id = item_id_list[0]
        
        h5wavefile = hdf54bats.Hdf5Wavefiles(workspace, survey)
        signal = h5wavefile.get_wavefile(item_id=item_id, close=False)
        
        extractor = sound4bats.PulsePeaksExtractor(debug=True)
        extractor.setup(sampling_freq_hz=384000)
        signal_filtered = extractor.filter(signal, filter_low_hz=20000, filter_high_hz=100000)
        extractor.new_result_table()
        extractor.extract_peaks(signal_filtered)
        extractor.save_result_table(file_path='debug_pulse_peaks.txt')

        # Plot.
        import matplotlib.pyplot
        
        time = []
        freq = []
        amp = []
        for row in extractor.get_result_table():
            if row[0] == 1:
                if row[3] > -100: # -100 means silent.
                    time.append(float(row[1]))
                    freq.append(float(row[2]))
                    amp.append(float(row[3]))
        #
        amp_min = abs(min(amp))
        sizes = [((x+amp_min)**1.2) * 0.1 for x in amp]
         
    #     matplotlib.pyplot.scatter(time, freq, c=sizes, s=sizes, cmap='Blues')
#         matplotlib.pyplot.scatter(time, freq, c=amp, s=sizes, cmap='Reds')
        matplotlib.pyplot.scatter(time, freq, c=amp, s=0.5, cmap='Reds')
        matplotlib.pyplot.show()

        return #####################################################



# ########## From pulse_peaks_extractor ##########
#     file_path = pathlib.Path('../data', 'test_chirp_generator.wav')
#     
#     with wave.open(str(file_path), 'r') as wave_file:
#         nchannels = wave_file.getnchannels() # 1=mono, 2=stereo.
#         sampwidth = wave_file.getsampwidth() # sample width in bytes.
#         framerate = wave_file.getframerate() # Sampling frequency.
#         nframes = wave_file.getnframes() # Number of audio frames.
#         
#         if int(framerate > 90000):
#             frame_rate_hz = framerate
#             lenght_s = int(nframes) / int(framerate)
#         else:
#             # Probably time division by a factor of 10.
#             frame_rate_hz = framerate * 10
#             lenght_s = int(nframes) / int(framerate) / 10
#             
#         buffer_raw = wave_file.readframes(frame_rate_hz) # Max 1 sec.
#         signal = numpy.fromstring(buffer_raw, dtype=numpy.int16) / 32767
#     
#     print('frame_rate_hz: ', frame_rate_hz, ' lenght_s: ', lenght_s)
#     
#     extractor = PulsePeaksExtractor(debug=True)
#     extractor.setup(frame_rate_hz)
#     signal_filtered = extractor.filter(signal, filter_low_hz=20000, filter_high_hz=100000)
#     extractor.new_result_table()
#     extractor.extract_peaks(signal_filtered)
#     extractor.save_result_table(file_path='../data/pulse_peaks.txt')
#     
#     # Plot.
#     time = []
#     freq = []
#     amp = []
#     for row in extractor.get_result_table():
#         if row[0] == 1:
#             if row[3] > -100: # -100 means silent.
#                 time.append(float(row[1]))
#                 freq.append(float(row[2]))
#                 amp.append(float(row[3]))
#     #
#     amp_min = abs(min(amp))
#     sizes = [((x+amp_min)**1.2) * 0.1 for x in amp]
#     
# #     matplotlib.pyplot.scatter(time, freq, c=sizes, s=sizes, cmap='Blues')
#     matplotlib.pyplot.scatter(time, freq, c=amp, s=sizes, cmap='Reds')
#     matplotlib.pyplot.show()
