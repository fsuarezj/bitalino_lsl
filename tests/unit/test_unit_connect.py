import pytest
import bitalino
import re
from context import bitalino_lsl
import time

@pytest.fixture
def data():
    pytest.mac_address = "20:17:11:20:51:60"

@pytest.mark.no_exc
@pytest.mark.mock_test
def test_my_bitalino(mock, data):
    mock.patch.object(bitalino, 'BITalino')
    pytest.device = bitalino_lsl.BitalinoLSL(pytest.mac_address)
    device = bitalino_lsl.BitalinoLSL(pytest.mac_address)
    mock.patch.object(pytest.device._bitalino, 'close')
    device.close()
