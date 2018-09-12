import threading
import time
import bitalino_lsl
from .sharedResources import SharedResources

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
            #TODO: Catch exception for read
            chunk = list(self._bitalino.read(self._N_SAMPLES))
            #for i in range(self._N_SAMPLES):
            for i in chunk:
                SharedResources.queue.put((chunk.pop(0)[1:len(self._channels_keys)+1], self._timestamp))
                self._timestamp += 1.0/self._sampling_rate
            #with SharedResources.flag_lock:
                #if not SharedResources.flag:
                    #self.shutdown_flag.set()
        self.stop()

    def stop(self):
        print("Stop reading")
        #threading.Thread.__stop(self)
