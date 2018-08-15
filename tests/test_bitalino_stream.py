import pytest
import re
from context import bitalino_lsl

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
def test_developing_test(data, capsys):
    pytest.device.create_lsl_EEG({0: 'Fp1-Fp2', 1: 'T3-T5'})
    with capsys.disabled():
        pytest.device.start()
