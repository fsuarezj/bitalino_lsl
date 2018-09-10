import bitalino
import sys
import time
import threading
#from pylsl import StreamInfo
from pylsl import StreamInfo, StreamOutlet, resolve_stream
from queue import Queue

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

class SharedResources():
    """This class stores the resources shared between threads
    """
    queue = Queue()
    flag = True
    flag_lock = threading.Lock()
    father = None

class BitaReader(threading.Thread):
    """This class is the thread reading from the BITalino device
    """
    _N_SAMPLES = 100

    def __init__(self, bitalino, sampling_rate, channels_keys):
        threading.Thread.__init__(self)
        self.shutdown_flag = threading.Event()
        self._bitalino = bitalino
        self._sampling_rate = sampling_rate
        self._channels_keys = channels_keys

    def run(self):
        self._bitalino.start(self._sampling_rate, self._channels_keys)
        self._timestamp = time.time()
        while not self.shutdown_flag.is_set():
            chunk = list(self._bitalino.read(self._N_SAMPLES))
            #for i in range(self._N_SAMPLES):
            for i in chunk:
                SharedResources.queue.put((chunk.pop(0)[1:len(self._channels_keys)+1], self._timestamp))
                self._timestamp += 1.0/self._sampling_rate
            with SharedResources.flag_lock:
                if not SharedResources.flag:
                    self.shutdown_flag.set()
        self.stop()

    def stop(self):
        print("Stop reading")
        #threading.Thread.__stop(self)

class LSLStreamer(threading.Thread):
    """This class is the thread pushing the data to the Lab Streaming Layer
    """
    def __init__(self, outlet):
        threading.Thread.__init__(self)
        self.shutdown_flag = threading.Event()
        self._outlet = outlet

    def run(self):
        ## This line fixes the timestamp data
        streams = resolve_stream('type', 'EEG')
        while not self.shutdown_flag.is_set():
            data, timestamp = SharedResources.queue.get()
            #TODO: Catch exception if data is not correct
            try:
                self._outlet.push_sample(data, timestamp)
            except:
                print(f"BAD DATA: {data}")
                SharedResources.father.stop()
                with SharedResources.flag_lock:
                    SharedResources.flag = False
            with SharedResources.flag_lock:
                if not SharedResources.flag:
                    self.shutdown_flag.set()
        self.stop()

    def stop(self):
        while not SharedResources.queue.empty():
            data, timestamp = SharedResources.queue.get()
            try:
                self._outlet.push_sample(data, timestamp)
            except:
                print(f"BAD DATA: {data}")
                SharedResources.father.stop()
                with SharedResources.flag_lock:
                    SharedResources.flag = False
            #print(data)
            #dif = time.time() - timestamp
            #print(f"Tiempos = {dif:10f}")
        print(f"BAD DATA: {data}")
        print("Stop streaming")
        #threading.Thread.__stop(self)

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
        with SharedResources.flag_lock:
            SharedResources.flag = True
        SharedResources.father = self
        self._bitaReader = BitaReader(self._bitalino, self._sampling_rate, list(self._eeg_channels.keys()))
        #self._bitaReader.daemon = True
        self._streamer = LSLStreamer(self._outlet)
        #self._streamer.daemon = True
        self._bitaReader.start()
        self._streamer.start()

    def stop(self):
        print("Stopping...")
        self._bitaReader.shutdown_flag.set()
        self._streamer.shutdown_flag.set()
        with SharedResources.flag_lock:
            SharedResources.flag = False
