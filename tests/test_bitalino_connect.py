import pytest
import re
from context import bitalino_lsl
import time

@pytest.fixture
def data():
    pytest.mac_address = "20:17:11:20:51:60"

@pytest.mark.no_exc
def test_my_bitalino(data):
    device = bitalino_lsl.BitalinoLSL(pytest.mac_address)
    device.close()

def test_bitalino_no_device():
    with pytest.raises(Exception) as excinfo:
        device = bitalino_lsl.BitalinoLSL("23:12:14:A0:E1:69")
        device.close()
    assert "Host is down" in str(excinfo.value)

def test_bitalino_no_mac():
    with pytest.raises(Exception) as excinfo:
        device = bitalino_lsl.BitalinoLSL("wrong_mac")
        device.close()
    assert "The specified address is invalid." in str(excinfo.value)
