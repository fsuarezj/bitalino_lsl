import bitalino
import pytest
import random
from context import bitalino_lsl
from pylsl import StreamInlet, resolve_stream
import time

## Marks are:
## dev_test: test used for developing purposes
## exc_test: test launching exceptions
## int_test: test using an integer as input for the channels
## list_test: test using a list as input for the channels
## dict_test: test using a dictionary as input for the channels

@pytest.fixture(scope="module")
def data():
    pytest.mac_address = "20:17:11:20:51:60"

@pytest.yield_fixture(autouse=True)
def run_around_tests():
    yield
    pytest.device.stop()
    # Sleep before each test to avoid getting previous data
    time.sleep(0.7)

#def teardown_function():
#    """ Stop the streaming"""
#    pytest.device.stop()

def stream_test(mocker, channels, read_data = [], segs = 1):
    """Main function to test the stream with several channels and data"""
    # Creates the mock read_data
    if (read_data == []):
        read_data = [[0] for i in range(10)]
        for i in channels:
            sample = random.sample(range(1024), len(read_data))
            for j in range(len(read_data)):
                read_data[j].append(sample[j])

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
            #index = stream_data[j].index(sample[j])
            #assert stream_data[j][index - 1] == old_sample[j]
            assert timestamp == old_timestamp + 1/sampling_rate
        old_sample = sample
        old_timestamp = timestamp

@pytest.mark.dict_test
def test_stream_2e_2s(data, capsys, mocker):
    """ Test with two mocked electrodes and two samples"""
    channels = {0: 'Fp1-Fp2', 1: 'T3-T5'}
    read_data = [[0,1,69], [0,2,70]]
    with capsys.disabled():
        stream_test(mocker, channels, read_data)

@pytest.mark.dict_test
def test_stream_1e_4s(data, capsys, mocker):
    """ Test with one mocked electrode and four samples"""
    channels = {0: 'Fp1-Fp2'}
    read_data = [[0,3], [0,4], [0,5], [0,6]]
    with capsys.disabled():
        stream_test(mocker, channels, read_data, segs = 3)

@pytest.mark.dict_test
def test_stream_4e_10s(data, capsys, mocker):
    """ Test with four mocked electrodes and ten samples"""
    channels = {0: 'Fp1-Fp2', 1: 'T3-T5', 2: 'F7-F3', 3: 'F4-F8'}
    with capsys.disabled():
        stream_test(mocker, channels, segs=5)

@pytest.mark.dict_test
def test_stream_1e_10s(data, capsys, mocker):
    """ Test with one mocked electrode and ten samples"""
    channels = {1: 'T3-T5'}
    with capsys.disabled():
        stream_test(mocker, channels, segs=5)

@pytest.mark.list_test
def test_stream_3e_10s_list(data, capsys, mocker):
    """ Test with three mocked electrodes as a list and ten samples"""
    channels = [0,2,5]
    with capsys.disabled():
        stream_test(mocker, channels, segs=5)

@pytest.mark.list_test
def test_stream_1e_10s_list(data, capsys, mocker):
    """ Test with one mocked electrode as a list and ten samples"""
    channels = [0]
    with capsys.disabled():
        stream_test(mocker, channels, segs=5)

@pytest.mark.exc_test
def test_stream_bad_data(data, capsys, mocker):
    """ Test launching bad data exception"""
    channels = [0,2,5]
    read_data = [[0,3], [0,4], [0,5], [0,6]]
    with capsys.disabled():
        stream_test(mocker, channels, segs=5)
