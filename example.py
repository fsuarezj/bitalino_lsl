import bitalino_lsl
from pylsl import StreamInlet, resolve_stream
import time

# MAC address of the BITalino device
MAC_ADDRESS_BITALINO_DEVICE = "20:17:09:18:60:36"

# List with channels of the BITalino device to be streamed to the LSL
# This channels can be specified as a list or as a dictionary with their
# position in the 10-20 system. BITalino uses bipolar electrodes so the
# position will be defined by two points
# CHANNELS = {0: 'Fp1-Fp2', 1: 'P3-T5'}
CHANNELS = [5]

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
