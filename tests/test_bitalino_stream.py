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

@pytest.fixture(scope="session")
def data():
    pytest.mac_address = "20:17:11:20:51:60"

@pytest.fixture(scope="session", autouse=True)
def connect_my_bitalino(data):
    pytest.device = bitalino_lsl.BitalinoLSL(pytest.mac_address)

@pytest.mark.dev_test
def test_developing_test(capsys):
    pytest.device.create_lsl_EEG({0: 'Fp1-Fp2', 1: 'T3-T5'})
    with capsys.disabled():
        pytest.device.start()
        time.sleep(2)
        pytest.device.stop()

@pytest.mark.mock
def test_stream(capsys, mocker):
    channels = {0: 'Fp1-Fp2', 1: 'T3-T5'}
    pytest.device.create_lsl_EEG(channels)
    pytest.device._set_n_samples(2)
    mocker.patch.object(pytest.device._bitalino, 'read')
    pytest.device._bitalino.read.return_value = [[0,1,69], [0,1,70]]
    sampling_rate = pytest.device.get_sampling_rate()
    with capsys.disabled():
        pytest.device.start()
        streams = resolve_stream('type', 'EEG')
        inlet = StreamInlet(streams[0])
        datitos = inlet.pull_sample() ### Here is the problem!!!
        old_sample, old_timestamp = (datitos[0], datitos[1])
    for i in range(sampling_rate - 1):
        with capsys.disabled():
            print(i)
        sample, timestamp = inlet.pull_sample()
        with capsys.disabled():
            print(timestamp)
        assert sample[1] != old_sample[1]
        assert sample[1] in [69, 70]
        assert timestamp == old_timestamp + 1/sampling_rate
        old_sample = sample
        old_timestamp = timestamp
    pytest.device.stop()
