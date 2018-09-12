import threading
from .sharedResources import SharedResources

class LSLStreamer(threading.Thread):
    """This class is the thread pushing the data to the Lab Streaming Layer
    """
    def __init__(self, outlet):
        threading.Thread.__init__(self)
        self.shutdown_flag = threading.Event()
        self._outlet = outlet

    def run(self):
        except_flag = False
        ## This line fixes the timestamp data
#        streams = resolve_stream('type', 'EEG')
        while not self.shutdown_flag.is_set():
            data, timestamp = SharedResources.queue.get()
            #TODO: Catch exception if data is not correct
            try:
                self._outlet.push_sample(data, timestamp)
            except ValueError as vf:
                print(f"BAD DATA: {data}")
                SharedResources.father.raise_exception(vf)
                self.shutdown_flag.set()
                except_flag = True
#            with SharedResources.flag_lock:
#                if not SharedResources.flag:
#                    self.shutdown_flag.set()
        self.stop(except_flag)

    def stop(self, except_flag = False):
        if(not except_flag):
            while not SharedResources.queue.empty():
                data, timestamp = SharedResources.queue.get()
                #TODO: Catch exception if data is not correct
                try:
                    self._outlet.push_sample(data, timestamp)
                except ValueError as vf:
                    print(f"BAD DATA: {data}")
                    SharedResources.father.raise_exception(vf)
                    #SharedResources.father.stop()
                #print(data)
                #dif = time.time() - timestamp
                #print(f"Tiempos = {dif:10f}")
        #with SharedResources.flag_lock:
            #SharedResources.flag = False
        print("Stop streaming")
        #threading.Thread.__stop(self)
