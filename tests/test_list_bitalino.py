import pytest
import re
from context import bitalino_lsl

def is_mac_address(mac_address):
    return re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", mac_address.lower())

def test_list_bitalino(capsys):
    devices = bitalino_lsl.list_bitalino()
    captured = capsys.readouterr()
    assert captured.out == "Looking for BITalino devices...\n"
    assert captured.err == ""
    assert type(devices) == dict
    if devices == {}:
        assert True
    else:
        for dev in devices:
            assert is_mac_address(dev)
            assert devices[dev][:8] == "BITalino"
    with capsys.disabled():
        print("Non captured output")
