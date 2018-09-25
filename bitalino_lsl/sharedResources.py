from queue import Queue
import logging
import sys

class SharedResources():
    """This class stores the resources shared between threads
    """
    queue = Queue()
    father = None
    exc_info = None
    logger = logging.getLogger()
    log_level = logging.WARNING

    def __init__(self):
        SharedResources.queue = Queue()
        SharedResources.father = None
        SharedResources.exc_info = None

        SharedResources.logger.setLevel(SharedResources.log_level)
        #ch = logging.StreamHandler(sys.stdout)
        #ch = logging.FileHandler("prueba.log")
        ch = logging.StreamHandler()
        ch.setLevel(SharedResources.log_level)
        formatter = logging.Formatter('%(relativeCreated)6d %(threadName)s - %(levelname)s: %(message)s')
        ch.setFormatter(formatter)
        SharedResources.logger.addHandler(ch)
