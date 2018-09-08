import bitalino
import pytest
import re
from context import bitalino_lsl
from pylsl import StreamInlet, resolve_stream
import time

## Marks are:
## dev_test: test used for developing purposes
## exc_test: test not launching exceptions
## int_test: test using an integer as input for the channels
## list_test: test using a list as input for the channels
## dict_test: test using a dictionary as input for the channels

@pytest.fixture(scope="module")
def data():
    pytest.mac_address = "20:17:11:20:51:60"

def stream_test(mocker, channels, read_data, segs = 1):
    # Init device
    mocker.patch.object(bitalino, 'BITalino')
    pytest.device = bitalino_lsl.BitalinoLSL(pytest.mac_address)
    pytest.device.create_lsl_EEG(channels)
    len_data = len(read_data)
    pytest.device._set_n_samples(len_data)
    mocker.patch.object(pytest.device._bitalino, 'start')
    mocker.patch.object(pytest.device._bitalino, 'read')
    pytest.device._bitalino.read.return_value = read_data
    sampling_rate = pytest.device.get_sampling_rate()
    stream_data = list(map(lambda x: x[1:], read_data))
    # transpose
    stream_data = [list(i) for i in zip(*stream_data)]

    # Start streaming
    pytest.device.start()
    streams = resolve_stream('type', 'EEG')
    inlet = StreamInlet(streams[0])
    first_data = inlet.pull_sample()
    old_sample, old_timestamp = (first_data[0], first_data[1])

    # Getting the stream and asserting
    for i in range(sampling_rate*segs):
        sample, timestamp = inlet.pull_sample()
        for j in range(len(sample)):
            assert sample[j] in stream_data[j]
            assert timestamp == old_timestamp + 1/sampling_rate
        old_sample = sample
        old_timestamp = timestamp

    # Time delay calculation
    now = time.time()
    dif = now - timestamp
    print(f"Dif = {dif:10f}")
    pytest.device.stop()

@pytest.mark.mock
def test_stream1(data, capsys, mocker):
    channels = {0: 'Fp1-Fp2', 1: 'T3-T5'}
    output_data = [[0,1,69], [0,1,70]]
    with capsys.disabled():
        stream_test(mocker, channels, output_data)

@pytest.mark.mock
def test_stream2(data, capsys, mocker):
    channels = {0: 'Fp1-Fp2'}
    output_data = [[0,3], [0,4], [0,5], [0,6]]
    with capsys.disabled():
        stream_test(mocker, channels, output_data, segs = 3)
