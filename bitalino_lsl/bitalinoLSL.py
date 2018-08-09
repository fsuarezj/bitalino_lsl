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

class BitalinoLSL(object):
    _sampling_rate = 1000
    _eeg_channels = []

    def __init__(self, mac_address, timeout = None):
        print("Connecting to BITalino with MAC {mac_address}")
        self.bitalino = bitalino.BITalino(mac_address, timeout)

    def create_lsl_EEG(self, channels):

        if type(channels) != list:
            if not channels in range(6):
                raise Exception(ExceptionCode.WRONG_CHANNEL)
            eeg_channels = [channels]
        else:
            for i in channels:
                if not i in range(6):
                    raise Exception(ExceptionCode.WRONG_CHANNEL)
            eeg_channels = channels

        print("Creating LSL")
        # ToDo: Replace the name for a lookup in the devices dict
        self._info_eeg = StreamInfo("BITalino", "EEG", len(eeg_channels), self._sampling_rate, 'float32', "BITalino_5160_EEG")

    def stream(self):
        print("Start streaming")
