import threading
from .sharedResources import SharedResources
from queue import Empty

class LSLStreamer(threading.Thread):
    """This class is the thread pushing the data to the LSL Stream
    """
    def __init__(self, outlet):
        """Creates the LSLStreamer

        :param outlet: a valid LSL outlet Stream
        """
        threading.Thread.__init__(self)
        self.shutdown_flag = threading.Event()
        self._outlet = outlet

    def run(self):
        """Method called to start the streamer thread
        """
        except_flag = False
        ## This line fixes the timestamp data
#        streams = resolve_stream('type', 'EEG')
        while not self.shutdown_flag.is_set():
            try:
                data, timestamp = SharedResources.queue.get(timeout = 0.5)
            except Empty as e:
                data, timestamp = None, 0
            if (type(data) != type(None)):
                try:
                    self._outlet.push_sample(data, timestamp)
                except ValueError as vf:
                    SharedResources.logger.debug("BAD DATA: {data}".format(data = data))
                    SharedResources.father.raise_exception(vf)
                    self.shutdown_flag.set()
                    except_flag = True
#            with SharedResources.flag_lock:
#                if not SharedResources.flag:
#                    self.shutdown_flag.set()
        self.stop(except_flag)

    def stop(self, except_flag = False):
        """Method called to stop the thread

        If there was not an exception this method will empty the queue sending
        all the data from the sensor to the LSL Stream

        :param except_flag: default False. A boolean only True when an exception was raised during the execution of the thread
        """
        if(not except_flag):
            while not SharedResources.queue.empty():
                data, timestamp = SharedResources.queue.get()
                #TODO: Catch exception if data is not correct
                try:
                    self._outlet.push_sample(data, timestamp)
                except ValueError as vf:
                    SharedResources.logger.debug("BAD DATA: {data}".format(data = data))
                    SharedResources.father.raise_exception(vf)
                    #SharedResources.father.stop()
                #print(data)
                #dif = time.time() - timestamp
                #print(f"Tiempos = {dif:10f}")
        #with SharedResources.flag_lock:
            #SharedResources.flag = False
        SharedResources.logger.debug("Stop streaming")
        #threading.Thread.__stop(self)
