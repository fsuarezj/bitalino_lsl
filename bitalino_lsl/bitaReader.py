import threading
import time
import bitalino_lsl
from .sharedResources import SharedResources

class BitaReader(threading.Thread):
    """This class is the thread reading from the BITalino device
    """
    _N_SAMPLES = 100

    def __init__(self, bitalino, sampling_rate, channels_keys):
        """Creates the BitaReader which starts reading from BITalino sensor

        This methods creates the BitaReader configuring the bitalino sensor and
        start reading from it.

        :param bitalino: The BITalino object correspondent to the BITalino sensor
        :param sampling_rate: The sampling rate for the bitalino sensor in Hz.
        Will be 1, 10, 100 or 1000
        :param channels_keys: The numbers of channels to read from
        """
        threading.Thread.__init__(self)
        self.shutdown_flag = threading.Event()
        self._bitalino = bitalino
        self._sampling_rate = sampling_rate
        self._channels_keys = channels_keys

    def run(self):
        """Method called to start the reading thread
        """
        except_flag = False
        self._bitalino.start(self._sampling_rate, self._channels_keys)
        self._timestamp = time.time()
        while not self.shutdown_flag.is_set():
            #TODO: Catch exception for read
            try:
                data = self._bitalino.read(self._N_SAMPLES)
                chunk = list(data)
                for i in chunk:
                    SharedResources.queue.put((chunk.pop(0)[1:len(self._channels_keys)+1], self._timestamp))
                    self._timestamp += 1.0/self._sampling_rate
            except Exception as vf:
                SharedResources.logger.debug("BAD READ: {data}".format(data = data))
                SharedResources.father.raise_exception(vf)
                self.shutdown_flag.set()
                except_flag = True
            #for i in range(self._N_SAMPLES):
            #with SharedResources.flag_lock:
                #if not SharedResources.flag:
                    #self.shutdown_flag.set()
        self.stop(except_flag)

    def stop(self, except_flag = False):
        """Method called to stop the thread
        """
        SharedResources.logger.debug("Stop reading")
        #threading.Thread.__stop(self)
