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

@pytest.fixture(scope="module", autouse=True)
def connect_my_bitalino(data,request):
    pytest.device = bitalino_lsl.BitalinoLSL(pytest.mac_address)
    def end():
        pytest.device.close()
        time.sleep(1)
    request.addfinalizer(end)

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

@pytest.mark.dev_test
def test_stream(capsys):
    channels = {0: 'Fp1-Fp2', 1: 'T3-T5'}
    with capsys.disabled():
        stream_test(channels)
