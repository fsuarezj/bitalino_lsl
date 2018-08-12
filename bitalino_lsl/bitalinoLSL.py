import bitalino
from pylsl import StreamInfo
#from pylsl import StreamInfo, StreamOutlet

def list_bitalino():
    print("Looking for BITalino devices...")
    devices = bitalino.find()
    bitalinos = {}
    for dev in devices:
        if dev[1][:8] == "BITalino":
            bitalinos[dev[0]] = dev[1]
    return bitalinos

class ExceptionCode():
    WRONG_CHANNEL = "The specified channel/s is invalid."
    WRONG_CHANNEL_LOCATION = "The specified channel/s is not complied with 10-20 system in bipolar configuration (e.g. F7-F3)."

class BitalinoLSL(object):
    _eeg_positions = [       "Fp1",          "Fp2",
                    "F7",   "F3",   "Fz",   "F4",   "F8",
            "A1",   "T3",   "C3",   "Cz",   "C4",   "T4",   "A2",
                    "T5",   "P3",   "Pz",   "P4",   "T6",
                            "O1",           "O2"]
    _sampling_rate = 1000
    _eeg_channels = dict()

    def __init__(self, mac_address, timeout = None):
        print("Connecting to BITalino with MAC {mac_address}")
        self.bitalino = bitalino.BITalino(mac_address, timeout)

    def create_lsl_EEG(self, channels):
        aux = dict()
        if type(channels) == dict:
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

    def locate_bipolar_channels(self):
        print("Hey")

    def stream(self):
        print("Start streaming")
