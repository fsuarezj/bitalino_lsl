# BITalino-lsl

A python module called `bitalino_lsl` to stream BITalino data though the Lab Streaming Layer (LSL). This module gets data from the [BITalino](www.bitalino.com) device through the [bitalino python api](https://github.com/BITalinoWorld/revolution-python-api) and uses the [Lab Stream Layer](https://github.com/sccn/labstreaminglayer) to stream the data.

The module should work with python versions >= 2.7 although it has only been tested for:
* Python 2.7.15
* Python 3.6.5

## Getting started

### Installation
`pip install bitalino_lsl`

### Example

~~~python
import bitalino_lsl
from pylsl import StreamInlet, resolve_stream
import time

# MAC address of the BITalino device
MAC_ADDRESS_BITALINO_DEVICE = "20:17:11:1A:2B:3C"

# List with channels of the BITalino device to be streamed to the LSL
# This channels can be specified as a list or as a dictionary with their
# position in the 10-20 system. BITalino uses bipolar electrodes so the
# position will be defined by two points
# CHANNELS = {0: 'Fp1-Fp2', 1: 'P3-T5'}
CHANNELS = [0,1]

# Connect with the BITalino device
device = bitalino_lsl.BitalinoLSL(MAC_ADDRESS_BITALINO_DEVICE)

# Create the Stream with the channels information
device.create_lsl_EEG(CHANNELS)

# Start the stream getting data from the BITalino device
device.start()

# Get the Stream to read the data from
inlet = StreamInlet(resolve_stream('type', 'EEG')[0])

# Read the BITalino data for 5 seconds
t_end = time.time() + 5
while time.time() < t_end:
  sample, timestamp = inlet.pull_sample()
  print(sample)

# Stop the device
device.stop()

# Close the connection with the BITalino device
device.close()
~~~

## Documentation
Documentation is available [here](https://bitalino-lsl.readthedocs.io)

## License
This project is licensed under the [GNU GPL v3](LICENSE.md)
