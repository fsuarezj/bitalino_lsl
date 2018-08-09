import pytest
import re
from context import bitalino_lsl

@pytest.fixture(scope="session")
def data():
    pytest.mac_address = "20:17:11:20:51:60"

@pytest.fixture(scope="session", autouse=True)
def connect_my_bitalino(data):
    pytest.device = bitalino_lsl.BitalinoLSL(pytest.mac_address)

@pytest.mark.no_exc
def test_create_StreamInfo_channel(data):
    pytest.device.create_lsl_EEG(2)
    assert pytest.device._info_eeg.__class__.__name__ == "StreamInfo"
    assert pytest.device._info_eeg.name() == "BITalino"
    assert pytest.device._info_eeg.type() == "EEG"
    assert pytest.device._info_eeg.channel_count() == 1
    assert pytest.device._info_eeg.nominal_srate() == 1000

@pytest.mark.no_exc
def test_create_StreamInfo_channels(data):
    pytest.device.create_lsl_EEG([0,1])
    assert pytest.device._info_eeg.__class__.__name__ == "StreamInfo"
    assert pytest.device._info_eeg.name() == "BITalino"
    assert pytest.device._info_eeg.type() == "EEG"
    assert pytest.device._info_eeg.channel_count() == 2
    assert pytest.device._info_eeg.nominal_srate() == 1000

@pytest.mark.no_exc
def test_create_StreamInfo_channels2(data):
    pytest.device.create_lsl_EEG([5,0,1])
    assert pytest.device._info_eeg.__class__.__name__ == "StreamInfo"
    assert pytest.device._info_eeg.name() == "BITalino"
    assert pytest.device._info_eeg.type() == "EEG"
    assert pytest.device._info_eeg.channel_count() == 3
    assert pytest.device._info_eeg.nominal_srate() == 1000

def test_create_StreamInfo_exc1():
    with pytest.raises(Exception) as excinfo:
        pytest.device.create_lsl_EEG(6)
    assert "The specified channel/s is invalid." in str(excinfo.value)

def test_create_StreamInfo_exc2():
    with pytest.raises(Exception) as excinfo:
        pytest.device.create_lsl_EEG([0,1,2,3,4,6])
    assert "The specified channel/s is invalid." in str(excinfo.value)

def test_create_StreamInfo_exc3():
    with pytest.raises(Exception) as excinfo:
        pytest.device.create_lsl_EEG("a")
    assert "The specified channel/s is invalid." in str(excinfo.value)

def test_create_StreamInfo_exc4():
    with pytest.raises(Exception) as excinfo:
        pytest.device.create_lsl_EEG(["3", "2", 1])
    assert "The specified channel/s is invalid." in str(excinfo.value)

def test_create_StreamInfo_exc5():
    with pytest.raises(Exception) as excinfo:
        pytest.device.create_lsl_EEG([0,"a", "b", 1])
    assert "The specified channel/s is invalid." in str(excinfo.value)
