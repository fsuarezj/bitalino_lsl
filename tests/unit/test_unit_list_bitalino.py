import pytest
import bitalino
import re
from context import bitalino_lsl

def is_mac_address(mac_address):
    return re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", mac_address.lower())

@pytest.mark.no_exc
@pytest.mark.mock_test
def test_list_bitalino1(mock):
    mock.patch.object(bitalino, 'find')
    bitalino.find.return_value = [['12:23:34:FF:A1:B2', 'BITalino_A1B2']]
    devices = bitalino_lsl.list_bitalino()
    assert type(devices) == dict
    if devices == {}:
        assert True
    else:
        for dev in devices:
            assert is_mac_address(dev)
            assert devices[dev][:8] == "BITalino"

@pytest.mark.no_exc
@pytest.mark.mock_test
def test_list_bitalino1(mock):
    mock.patch.object(bitalino, 'find')
    bitalino.find.return_value = [['12:23:34:FF:A1:B2', 'BITalino_A1B2'], ['54:34:F1:A2:41:E2', 'BITalino_41E2']]
    devices = bitalino_lsl.list_bitalino()
    assert type(devices) == dict
    if devices == {}:
        assert True
    else:
        for dev in devices:
            assert is_mac_address(dev)
            assert devices[dev][:8] == "BITalino"
