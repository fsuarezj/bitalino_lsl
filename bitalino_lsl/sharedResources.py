from queue import Queue

class SharedResources():
    """This class stores the resources shared between threads
    """
    queue = Queue()
    father = None
    exc_info = None

    def __init__(self):
        SharedResources.queue = Queue()
        SharedResources.father = None
        SharedResources.exc_info = None
