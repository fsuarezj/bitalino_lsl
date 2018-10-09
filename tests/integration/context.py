import os
import sys
#sys.path.insert(0, os.path.abspath(__file__+"/.."))
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
myPath = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, myPath + '/../../')

import bitalino_lsl
import logging
import sys
