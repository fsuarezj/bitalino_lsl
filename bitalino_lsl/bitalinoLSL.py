import bitalino
import sys
import time
import threading
import logging
#from pylsl import StreamInfo
from pylsl import StreamInfo, StreamOutlet, resolve_stream
from queue import Queue
from future.utils import raise_
from .bitaReader import BitaReader
from .lslStreamer import LSLStreamer
from .sharedResources import SharedResources

if (sys.version_info > (3, 0)):
     # Python 3 code in this block
     from threading import get_ident
else:
    from thread import get_ident

def list_bitalino():
    """returns a dict with detected bitalino devices where the key is the name and the value is the MAC address
    """
    SharedResources.logger.info("Looking for BITalino devices...")
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
        """Constructor connects with BITalino device through bluetooth

        :param mac_address: MAC Address of the BITalino device
        :param timeout: defines a timeout for the connection
        """
        th_id = get_ident()
        SharedResources.logger.info("{th_id}: Connecting to BITalino with MAC {mac_address}".format(th_id = th_id, mac_address = mac_address))
        self._bitalino = bitalino.BITalino(mac_address, timeout)
        SharedResources()

    def close(self):
        """Closes the bluetooth or serial port socket
        """
        self._bitalino.close()

    def _validate_eeg_bipolar_channels_dict(self, channels):
        """Private method to validate the channels dictionary

        This method validates if the keys in the dictionary are in the way
        Str1 + "-" Str2 where Str1 and Str2 are elements of the array _eeg_positions,
        i.e. are valid positions in the 10-20 system. It also validates if the values
        in the dictionary are valid channels for BITalino, i.e. are int numbers
        between 0 and 5 corresponding to the 6 analog channels of BITalino. If the
        channels dictionray is not valid the method raises an exception with the
        appropiate message.

        :param channels: the channels dictionary
        """
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
        """Creates the LSL Stream Info according to the specified channels

        Creates the StreamInfo object with the information specified in the
        argument channels.

        :param channels: the channels to create the StreamInfo, it can be a list with the numbers of BITalino channels or a dictionary where the values are the BITalino channels number (from 0 to 5) and the keys are the bipolar EEG channels in the system 10-20
        """
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

        th_id = get_ident()
        SharedResources.logger.debug("{th_id}: Creating LSL".format(th_id = th_id))
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
        """Gets the active channels for the BITalino configuration
        """
        return list(self._eeg_channels.keys())

    def locate_bipolar_EEG_channels(self, channels):
        """Locates the channels in the EEG 10-20 system

        This method configures the StreamInfo object with the location of the
        channels in the EEG 10-20 system. It returns an exception if one of the
        channels to locate has not been initialized before.

        :param channels: the channels to create the StreamInfo, it can be a list with the numbers of BITalino channels or a dictionary where the values are the BITalino channels number (from 0 to 5) and the keys are the bipolar EEG channels in the system 10-20
        """
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
        """Set the sampling rate of BITalino

        :param sampling_rate: this param is the sampling rate in Hz, it can only be set to 1, 10, 100 or 1000
        """
        if sampling_rate not in [1, 10, 100, 1000]:
            raise Exception(ExceptionCode.WRONG_SAMPLING_RATE)
        self._sampling_rate = sampling_rate

    def get_sampling_rate(self):
        """Get the sampling rate
        """
        return self._sampling_rate

    def _set_n_samples(self, num):
        """Set the number of samples BITalino will get in a row

        :param num: the number of samples that BITalino will get in a row when
        the method read of the bitalino object is called. By default is 100
        """
        BitaReader._N_SAMPLES = num

    def start(self):
        """Start the BITalino LML Stream

        This method will init and start the threads to read from the BITalino
        device and to send the data to the LML Stream
        """
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

    def _shut_down_threads(self):
        """Private method to shut down the reading and streaming threads

        This private method is called to shut down the reading and streaming
        threads. It should only be called internally, if not it could break the
        program or failing stopping some of the threads.
        """
        th_id = get_ident()
        SharedResources.logger.debug("{th_id}: Shutting down threads...".format(th_id = th_id))
        if self._bitaReader.is_alive():
            SharedResources.logger.debug("{th_id}: Main thread shuts down bitaReader".format(th_id = th_id))
            self._bitaReader.shutdown_flag.set()
        if self._streamer.is_alive():
            SharedResources.logger.debug("{th_id}: Main thread shuts down streamer".format(th_id = th_id))
            self._streamer.shutdown_flag.set()
#        with SharedResources.flag_lock:
#            SharedResources.flag = False
        SharedResources.logger.debug("{th_id}: Threads shut down".format(th_id = th_id))

    def stop(self):
        """Stop the BitalinoLSL stream

        This method is called to stop the BITalino reading and streaming threads,
        if some thread raised an exception it raises it to the next level so it can
        be catched.
        """
        th_id = get_ident()
        SharedResources.logger.info("{th_id}: Stopping".format(th_id = th_id))
        self._shut_down_threads()
        SharedResources.logger.debug("{th_id}: Exception: {SharedResources.exc_info}".format(th_id = th_id, SharedResources = SharedResources))
        if SharedResources.exc_info:
            temp_exc_info = SharedResources.exc_info
            SharedResources.exc_info = None
            SharedResources.logger.debug("{th_id}: raising exception".format(th_id = th_id))
            raise_(temp_exc_info[0], temp_exc_info[1], temp_exc_info[2])

    def raise_exception(self, e):
        """Raises exceptions that occurred in the reading and streaming threads
        """
        th_id = get_ident()
        SharedResources.logger.debug("{th_id}: Including exception in SharedResources".format(th_id = th_id))
        if not SharedResources.exc_info:
            SharedResources.exc_info = sys.exc_info()
        self._shut_down_threads()
        #time.sleep(1)

    def threads_alive(self):
        """Check if the reading and streaming threads are alive

        :returns: True if both threads are alive
        """
        return self._bitaReader.is_alive() and self._streamer.is_alive()
