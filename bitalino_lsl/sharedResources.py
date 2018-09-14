from queue import Queue

class SharedResources():
    """This class stores the resources shared between threads
    """
    queue = Queue()
    #flag = True
    #flag_lock = threading.Lock()
    father = None
    exc_info = None
