import bitalino
import sys
import time
import threading
#from pylsl import StreamInfo
from pylsl import StreamInfo, StreamOutlet, resolve_stream
from queue import Queue
from .bitaReader import BitaReader
from .lslStreamer import LSLStreamer
from .sharedResources import SharedResources

def list_bitalino():
    """returns a dict with detected bitalino devices where the key is the name and the value is the MAC address
    """
    print("Looking for BITalino devices...")
    devices = bitalino.find()
    bitalinos = {}
    for dev in devices:
        if dev[1][:8] == "BITalino":
            bitalinos[dev[0]] = dev[1]
    return bitalinos

class ExceptionCode():
    """This class stores the Exception codes
    """
    CHANNEL_NOT_INITIALIZED = "The specified channel has not been initialized."
    WRONG_CHANNEL = "The specified channel/s is invalid."
    WRONG_CHANNEL_LOCATION = "The specified channel/s is not complied with 10-20 system in bipolar configuration (e.g. F7-F3)."
    WRONG_SAMPLING_RATE = "The sampling rate is defined as an integer in Hz and can be 1, 10, 100 or 1000"

class BitalinoLSL(object):
    """This class is implements Lab Streaming Layer for BITalino
    """
    _eeg_positions = [       "Fp1",          "Fp2",
                    "F7",   "F3",   "Fz",   "F4",   "F8",
            "A1",   "T3",   "C3",   "Cz",   "C4",   "T4",   "A2",
                    "T5",   "P3",   "Pz",   "P4",   "T6",
                            "O1",           "O2"]
    _sampling_rate = 1000
    _eeg_channels = dict()
    _bitalino = None
    _info_eeg = None
    _outlet = None
    _bitalino_data = []
    _timestamps = []

    def __init__(self, mac_address, timeout = None):
        print(f"Connecting to BITalino with MAC {mac_address}")
        self._bitalino = bitalino.BITalino(mac_address, timeout)

    def _validate_eeg_bipolar_channels_dict(self, channels):
       for i in list(channels.keys()):
           if not i in range(6):
               raise Exception(ExceptionCode.WRONG_CHANNEL)
           if type(channels[i]) != str:
               raise Exception(ExceptionCode.WRONG_CHANNEL_LOCATION)
           else:
               ch_loc = channels[i].split('-')
               if len(ch_loc) != 2:
                   raise Exception(ExceptionCode.WRONG_CHANNEL_LOCATION)
               for j in ch_loc:
                   if j not in self._eeg_positions:
                       raise Exception(ExceptionCode.WRONG_CHANNEL_LOCATION)

    def create_lsl_EEG(self, channels):
        aux = dict()
        if type(channels) == dict:
            self._validate_eeg_bipolar_channels_dict(channels)
            self._eeg_channels = channels
        elif type(channels) == list:
            for i in channels:
                if not i in range(6):
                    raise Exception(ExceptionCode.WRONG_CHANNEL)
                else:
                    aux[i] = ""
            self._eeg_channels = aux
        else:
            if not channels in range(6):
                raise Exception(ExceptionCode.WRONG_CHANNEL)
            aux[channels] = ""
            self._eeg_channels = aux

        print("Creating LSL")
        # ToDo: Replace the name for a lookup in the devices dict
        self._info_eeg = StreamInfo("BITalino", "EEG", len(list(self._eeg_channels.keys())), self._sampling_rate, 'float32', "BITalino_5160_EEG")
        self._info_eeg.desc().append_child_value("manufacturer", "BITalino")
        chns = self._info_eeg.desc().append_child("channels")
        for i in self._eeg_channels.keys():
            ch = chns.append_child("channel")
            ch.append_child_value("label", str(self._eeg_channels[i]))
            ch.append_child_value("unit", "microvolts")
            ch.append_child_value("type", "EEG")

    def get_active_channels(self):
        return list(self._eeg_channels.keys())

    def locate_bipolar_EEG_channels(self, channels):
        if type(channels) == dict:
            self._validate_eeg_bipolar_channels_dict(channels)
        else:
            raise Exception(ExceptionCode.WRONG_CHANNEL_LOCATION)
        for i in list(channels.keys()):
            if i not in list(self._eeg_channels.keys()):
                raise Exception(ExceptionCode.CHANNEL_NOT_INITIALIZED)
        chns = self._info_eeg.desc().child("channels")
        self._eeg_channels.update(channels)
        #print(chns.remove_child.__doc__)
        #print(dir(chns))
        #print(self._info_eeg.as_xml())
        if sys.version_info[0] >= 3:
            self._info_eeg.desc().remove_child(chns)
        else:
            self._info_eeg.desc().remove_child("channels")
        chns = self._info_eeg.desc().append_child("channels")
        for i in list(self._eeg_channels.keys()):
            ch = chns.append_child("channel")
            ch.append_child_value("label", str(self._eeg_channels[i]))
            ch.append_child_value("unit", "microvolts")
            ch.append_child_value("type", "EEG")

    def set_sampling_rate(self, sampling_rate):
        if sampling_rate not in [1, 10, 100, 1000]:
            raise Exception(ExceptionCode.WRONG_SAMPLING_RATE)
        self._sampling_rate = sampling_rate

    def get_sampling_rate(self):
        return self._sampling_rate

    def _set_n_samples(self, num):
        BitaReader._N_SAMPLES = num

    def start(self):
        self._outlet = StreamOutlet(self._info_eeg)
        #with SharedResources.flag_lock:
            #SharedResources.flag = True
        SharedResources.father = self
        self._bitaReader = BitaReader(self._bitalino, self._sampling_rate, list(self._eeg_channels.keys()))
        #self._bitaReader.daemon = True
        self._streamer = LSLStreamer(self._outlet)
        #self._streamer.daemon = True
        self._bitaReader.start()
        self._streamer.start()

    def stop(self):
        print("Stopping...")
        if self._bitaReader.is_alive():
            print("Padre apaga bitaReader")
            self._bitaReader.shutdown_flag.set()
        if self._streamer.is_alive():
            print("Padre apaga streamer")
            self._streamer.shutdown_flag.set()
#        with SharedResources.flag_lock:
#            SharedResources.flag = False
        print("Sacabó")

    def raise_exception(self, e):
        self.stop()
        #time.sleep(1)
        #raise(e)

    def threads_alive(self):
        return self._bitaReader.is_alive() and self._streamer.is_alive()
