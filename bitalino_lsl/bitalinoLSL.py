import bitalino
#from pylsl import StreamInfo, StreamOutlet

def list_bitalino():
    devices = bitalino.find()
    bitalinos = []
    for dev in devices:
        if dev[1][:8] == "BITalino":
            bitalinos.append(dev)
    return bitalinos

class BITalinoLSL(object):
    def __init__(self, macAddress, timeout = None):
        self.bitalino = BITalino(macAddress, timeout)

    def create_lsl():
        print("Creating LSL")

    def stream():
        print("Start streaming")
