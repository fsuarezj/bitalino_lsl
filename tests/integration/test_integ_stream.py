import pytest
import re
from context import bitalino_lsl
import logging
from pylsl import StreamInlet, resolve_stream
import time

## Marks are:
## dev_test: test used for developing purposes
## exc_test: test launching exceptions
## int_test: test using an integer as input for the channels
## list_test: test using a list as input for the channels
## dict_test: test using a dictionary as input for the channels

@pytest.fixture(scope="session")
def data():
    pytest.mac_address = "20:17:11:20:51:60"

#@pytest.fixture(scope="module", autouse=True)
#def connect_my_bitalino(data,request):
#    pytest.device = bitalino_lsl.BitalinoLSL(pytest.mac_address)
#    def end():
#        pytest.device.close()
#        time.sleep(1)
#    request.addfinalizer(end)

@pytest.yield_fixture(autouse=True)
def run_around_tests(data, capsys):
    pytest.device = bitalino_lsl.BitalinoLSL(pytest.mac_address)
    yield
    time.sleep(1)

def stream_test(channels, segs = 1):
    pytest.device.create_lsl_EEG(channels)
    sampling_rate = pytest.device.get_sampling_rate()
    pytest.device.start()
    data_len = len(channels)
    streams = resolve_stream('type', 'EEG')
    inlet = StreamInlet(streams[0])
    old_sample, old_timestamp = inlet.pull_sample()
    for i in range(sampling_rate*segs - 1):
        sample, timestamp = inlet.pull_sample()
        assert len(sample) == data_len
        assert timestamp == old_timestamp + 1.0/sampling_rate
        old_sample = sample
        old_timestamp = timestamp

    # Time delay calculation
    now = time.time()
    dif = now - timestamp
    logging.debug("Dif = {dif:10f}".format(dif = dif))
    pytest.device.stop()
    pytest.device.close()

@pytest.mark.no_exc
def test_stream_1c1s(capsys):
    channels = {0: 'Fp1-Fp2'}
    with capsys.disabled():
        stream_test(channels)

@pytest.mark.no_exc
def test_stream_2c5s(capsys):
    channels = [2,0]
    with capsys.disabled():
        stream_test(channels, 5)

@pytest.mark.no_exc
def test_stream_3c2s(capsys):
    channels = {0: 'Fp1-Fp2', 1: 'Pz-T5', 5: 'C3-O1'}
    with capsys.disabled():
        stream_test(channels)

@pytest.mark.no_exc
def test_stream_6c10s(capsys):
    channels = {3: 'F3-F7', 1: 'C4-T4', 2: 'Fz-F4', 5: 'O1-O2', 0: 'Fp2-Fp1', 4: 'Pz-P3'}
    with capsys.disabled():
        stream_test(channels)
