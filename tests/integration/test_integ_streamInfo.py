import pytest
import re
from context import bitalino_lsl
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
def connect_my_bitalino(data, request):
    pytest.device = bitalino_lsl.BitalinoLSL(pytest.mac_address)
    def end():
        pytest.device.close()
        time.sleep(1)
    request.addfinalizer(end)

#@pytest.mark.dev_test
#def test_developing_test(data, capsys):
#    pytest.device.create_lsl_EEG([4,2])
#    with capsys.disabled():
#        print(pytest.device._info_eeg.as_xml())
#        ch = pytest.device._info_eeg.desc().child("channels").child("channel")
#        for i in range(pytest.device._info_eeg.channel_count()):
#            print(ch.child_value("label"))
#            print(ch.child_value("unit"))
#            print(ch.child_value("type"))
#            ch = ch.next_sibling()

@pytest.mark.int_test
def test_create_lsl_EEG_channel_int(data, capsys):
    pytest.device.create_lsl_EEG(2)
    assert pytest.device._info_eeg.__class__.__name__ == "StreamInfo"
    assert pytest.device._info_eeg.name() == "BITalino"
    assert pytest.device._info_eeg.type() == "EEG"
    assert pytest.device._info_eeg.channel_count() == 1
    #with capsys.disabled():
    #    print(pytest.device._eeg_channels)
    assert pytest.device._info_eeg.nominal_srate() == 1000
    assert pytest.device._info_eeg.desc().child_value("manufacturer") == "BITalino"
    ch = pytest.device._info_eeg.desc().child("channels").child("channel")
    for i in pytest.device.get_active_channels():
        assert ch.child_value("label") == ""
        assert ch.child_value("unit") == "microvolts"
        assert ch.child_value("type") == "EEG"
        ch = ch.next_sibling()

@pytest.mark.list_test
def test_create_lsl_EEG_channel_list(data, capsys):
    pytest.device.create_lsl_EEG([5])
    assert pytest.device._info_eeg.__class__.__name__ == "StreamInfo"
    assert pytest.device._info_eeg.name() == "BITalino"
    assert pytest.device._info_eeg.type() == "EEG"
    assert pytest.device._info_eeg.channel_count() == 1
    assert pytest.device._info_eeg.nominal_srate() == 1000
    assert pytest.device._info_eeg.desc().child_value("manufacturer") == "BITalino"
    ch = pytest.device._info_eeg.desc().child("channels").child("channel")
    for i in pytest.device.get_active_channels():
        assert ch.child_value("label") == ""
        assert ch.child_value("unit") == "microvolts"
        assert ch.child_value("type") == "EEG"
        ch = ch.next_sibling()

@pytest.mark.dict_test
def test_create_lsl_EEG_channel_dict(data):
    pytest.device.create_lsl_EEG({0: 'Pz-P4'})
    assert pytest.device._info_eeg.__class__.__name__ == "StreamInfo"
    assert pytest.device._info_eeg.name() == "BITalino"
    assert pytest.device._info_eeg.type() == "EEG"
    assert pytest.device._info_eeg.channel_count() == 1
    assert pytest.device._info_eeg.nominal_srate() == 1000
    assert pytest.device._info_eeg.desc().child_value("manufacturer") == "BITalino"
    ch = pytest.device._info_eeg.desc().child("channels").child("channel")
    for i in pytest.device.get_active_channels():
        assert ch.child_value("label") == str(pytest.device._eeg_channels[i])
        assert ch.child_value("unit") == "microvolts"
        assert ch.child_value("type") == "EEG"
        ch = ch.next_sibling()

@pytest.mark.list_test
def test_create_lsl_EEG_channels_list(data):
    pytest.device.create_lsl_EEG([0,1])
    assert pytest.device._info_eeg.__class__.__name__ == "StreamInfo"
    assert pytest.device._info_eeg.name() == "BITalino"
    assert pytest.device._info_eeg.type() == "EEG"
    assert pytest.device._info_eeg.channel_count() == 2
    assert pytest.device._info_eeg.nominal_srate() == 1000
    assert pytest.device._info_eeg.desc().child_value("manufacturer") == "BITalino"
    ch = pytest.device._info_eeg.desc().child("channels").child("channel")
    for i in pytest.device.get_active_channels():
        assert ch.child_value("label") == ""
        assert ch.child_value("unit") == "microvolts"
        assert ch.child_value("type") == "EEG"
        ch = ch.next_sibling()

@pytest.mark.list_test
def test_create_lsl_EEG_channels_list2(data):
    pytest.device.create_lsl_EEG([5,0,1])
    assert pytest.device._info_eeg.__class__.__name__ == "StreamInfo"
    assert pytest.device._info_eeg.name() == "BITalino"
    assert pytest.device._info_eeg.type() == "EEG"
    assert pytest.device._info_eeg.channel_count() == 3
    assert pytest.device._info_eeg.nominal_srate() == 1000
    assert pytest.device._info_eeg.desc().child_value("manufacturer") == "BITalino"
    ch = pytest.device._info_eeg.desc().child("channels").child("channel")
    for i in pytest.device.get_active_channels():
        assert ch.child_value("label") == ""
        assert ch.child_value("unit") == "microvolts"
        assert ch.child_value("type") == "EEG"
        ch = ch.next_sibling()

@pytest.mark.dict_test
def test_create_lsl_EEG_channels_dict(data):
    pytest.device.create_lsl_EEG({3: 'F3-F7', 1: 'C4-T4'})
    assert pytest.device._info_eeg.__class__.__name__ == "StreamInfo"
    assert pytest.device._info_eeg.name() == "BITalino"
    assert pytest.device._info_eeg.type() == "EEG"
    assert pytest.device._info_eeg.channel_count() == 2
    assert pytest.device._info_eeg.nominal_srate() == 1000
    assert pytest.device._info_eeg.desc().child_value("manufacturer") == "BITalino"
    ch = pytest.device._info_eeg.desc().child("channels").child("channel")
    for i in pytest.device.get_active_channels():
        assert ch.child_value("label") == str(pytest.device._eeg_channels[i])
        assert ch.child_value("unit") == "microvolts"
        assert ch.child_value("type") == "EEG"
        ch = ch.next_sibling()

@pytest.mark.dict_test
def test_create_lsl_EEG_channels_dict2(data):
    pytest.device.create_lsl_EEG({3: 'F3-F7', 1: 'C4-T4', 2: 'Fz-F4', 5: 'O1-O2', 0: 'Fp2-Fp1', 4: 'Pz-P3'})
    assert pytest.device._info_eeg.__class__.__name__ == "StreamInfo"
    assert pytest.device._info_eeg.name() == "BITalino"
    assert pytest.device._info_eeg.type() == "EEG"
    assert pytest.device._info_eeg.channel_count() == 6
    assert pytest.device._info_eeg.nominal_srate() == 1000
    assert pytest.device._info_eeg.desc().child_value("manufacturer") == "BITalino"
    ch = pytest.device._info_eeg.desc().child("channels").child("channel")
    for i in pytest.device.get_active_channels():
        assert ch.child_value("label") == str(pytest.device._eeg_channels[i])
        assert ch.child_value("unit") == "microvolts"
        assert ch.child_value("type") == "EEG"
        ch = ch.next_sibling()

@pytest.mark.list_test
@pytest.mark.loc_chn
def test_locate_channel_list(data, capsys):
    chns = [2]
    pytest.device.create_lsl_EEG(chns)
    with capsys.disabled():
        pytest.device.locate_bipolar_EEG_channels({2: 'O1-P4'})
    ch = pytest.device._info_eeg.desc().child("channels").child("channel")
    for i in chns:
        assert ch.child_value("label") == str(pytest.device._eeg_channels[i])
    assert str(pytest.device._eeg_channels[2]) == 'O1-P4'

@pytest.mark.list_test
@pytest.mark.loc_chn
def test_locate_channels_list(data):
    chns = [0,1]
    pytest.device.create_lsl_EEG(chns)
    pytest.device.locate_bipolar_EEG_channels({1: 'F4-F3', 0: 'Cz-Pz'})
    ch = pytest.device._info_eeg.desc().child("channels").child("channel")
    labels = []
    for i in chns:
        labels.append(ch.child_value("label"))
    assert labels.sort() == list(pytest.device._eeg_channels.values()).sort()
    assert str(pytest.device._eeg_channels[0]) == 'Cz-Pz'
    assert str(pytest.device._eeg_channels[1]) == 'F4-F3'

@pytest.mark.dict_test
@pytest.mark.loc_chn
def test_locate_channels_dict(data):
    chns = {3: 'F3-F7', 1: 'C4-T4'}
    pytest.device.create_lsl_EEG(chns)
    chns2 = {1: 'F4-F3', 3: 'Cz-Pz'}
    pytest.device.locate_bipolar_EEG_channels(chns2)
    ch = pytest.device._info_eeg.desc().child("channels").child("channel")
    labels = []
    for i in chns:
        labels.append(ch.child_value("label"))
    assert labels.sort() == list(pytest.device._eeg_channels.values()).sort()
    assert str(pytest.device._eeg_channels[3]) == 'Cz-Pz'
    assert str(pytest.device._eeg_channels[1]) == 'F4-F3'

@pytest.mark.dict_test
@pytest.mark.loc_chn
def test_locate_channels_dict2(data):
    chns = {3: 'F3-F7', 1: 'C4-T4'}
    pytest.device.create_lsl_EEG(chns)
    pytest.device.locate_bipolar_EEG_channels({1: 'F4-F3'})
    ch = pytest.device._info_eeg.desc().child("channels").child("channel")
    labels = []
    for i in chns:
        labels.append(ch.child_value("label"))
        ch.next_sibling()
    assert labels.sort() == list(pytest.device._eeg_channels.values()).sort()
    assert str(pytest.device._eeg_channels[3]) == 'F3-F7'
    assert str(pytest.device._eeg_channels[1]) == 'F4-F3'

@pytest.mark.exc_test
@pytest.mark.int_test
def test_create_lsl_EEG_wrong_channel():
    with pytest.raises(Exception) as excinfo:
        pytest.device.create_lsl_EEG(6)
    assert "The specified channel/s is invalid." in str(excinfo.value)

@pytest.mark.exc_test
def test_create_lsl_EEG_wrong_channel2():
    with pytest.raises(Exception) as excinfo:
        pytest.device.create_lsl_EEG("a")
    assert "The specified channel/s is invalid." in str(excinfo.value)

@pytest.mark.exc_test
@pytest.mark.list_test
def test_create_lsl_EEG_wrong_list():
    with pytest.raises(Exception) as excinfo:
        pytest.device.create_lsl_EEG([0,1,2,3,4,6])
    assert "The specified channel/s is invalid." in str(excinfo.value)

@pytest.mark.exc_test
@pytest.mark.list_test
def test_create_lsl_EEG_wrong_list2():
    with pytest.raises(Exception) as excinfo:
        pytest.device.create_lsl_EEG(["3", "2", 1])
    assert "The specified channel/s is invalid." in str(excinfo.value)

@pytest.mark.exc_test
@pytest.mark.list_test
def test_create_lsl_EEG_wrong_list3():
    with pytest.raises(Exception) as excinfo:
        pytest.device.create_lsl_EEG([0,"a", "b", 1])
    assert "The specified channel/s is invalid." in str(excinfo.value)

@pytest.mark.exc_test
@pytest.mark.dict_test
def test_create_lsl_EEG_wrong_dict_channel(data):
    with pytest.raises(Exception) as excinfo:
        pytest.device.create_lsl_EEG({3: 'F3-F7', 6: 'C4-T4'})
    assert "The specified channel/s is invalid." in str(excinfo.value)

@pytest.mark.exc_test
@pytest.mark.dict_test
def test_create_lsl_EEG_wrong_dict_channel2(data):
    with pytest.raises(Exception) as excinfo:
        pytest.device.create_lsl_EEG({9: 'Fp2-Fp1'})
    assert "The specified channel/s is invalid." in str(excinfo.value)

@pytest.mark.exc_test
@pytest.mark.dict_test
def test_create_lsl_EEG_wrong_dict_location(data):
    with pytest.raises(Exception) as excinfo:
        pytest.device.create_lsl_EEG({3: 'F3-F7', 1: 'C4-T7', 2: 'Fz-F4', 5: 'O1-O2', 0: 'Fp2-Fp1', 4: 'Pz-P3'})
    assert "The specified channel/s is not complied with 10-20 system in bipolar configuration (e.g. F7-F3)." in str(excinfo.value)

@pytest.mark.exc_test
@pytest.mark.dict_test
def test_create_lsl_EEG_wrong_dict_location2(data):
    with pytest.raises(Exception) as excinfo:
        pytest.device.create_lsl_EEG({3: 'F3-F7', 5: 'O1-O2', 0: 'Fp2 Fp1', 4: 'Pz-P3'})
    assert "The specified channel/s is not complied with 10-20 system in bipolar configuration (e.g. F7-F3)." in str(excinfo.value)

@pytest.mark.exc_test
@pytest.mark.dict_test
def test_create_lsl_EEG_wrong_dict_location3(data):
    with pytest.raises(Exception) as excinfo:
        pytest.device.create_lsl_EEG({3: 'F3-F7', 1: 'C4-T4', 2: 'FZ-F4'})
    assert "The specified channel/s is not complied with 10-20 system in bipolar configuration (e.g. F7-F3)." in str(excinfo.value)

@pytest.mark.exc_test
@pytest.mark.dict_test
def test_create_lsl_EEG_wrong_dict_location4(data):
    with pytest.raises(Exception) as excinfo:
        pytest.device.create_lsl_EEG({3: 'F3-F7', 1: 'C4-T4-O1'})
    assert "The specified channel/s is not complied with 10-20 system in bipolar configuration (e.g. F7-F3)." in str(excinfo.value)

@pytest.mark.exc_test
@pytest.mark.dict_test
def test_create_lsl_EEG_wrong_dict_location4(data):
    with pytest.raises(Exception) as excinfo:
        pytest.device.create_lsl_EEG({3: 'F3'})
    assert "The specified channel/s is not complied with 10-20 system in bipolar configuration (e.g. F7-F3)." in str(excinfo.value)

@pytest.mark.dict_test
def test_locate_chnnels_wrong_dict(data):
    pytest.device.create_lsl_EEG({3: 'F3-F7', 1: 'C4-T4'})
    with pytest.raises(Exception) as excinfo:
        pytest.device.locate_bipolar_EEG_channels({1: 'F4 F3'})
    assert "The specified channel/s is not complied with 10-20 system in bipolar configuration (e.g. F7-F3)." in str(excinfo.value)

@pytest.mark.dict_test
def test_locate_chnnels_wrong_dict2(data):
    pytest.device.create_lsl_EEG({3: 'F3-F7', 1: 'C4-T4'})
    with pytest.raises(Exception) as excinfo:
        pytest.device.locate_bipolar_EEG_channels({1: 'F4'})
    assert "The specified channel/s is not complied with 10-20 system in bipolar configuration (e.g. F7-F3)." in str(excinfo.value)

@pytest.mark.dict_test
def test_locate_chnnels_wrong_dict3(data):
    pytest.device.create_lsl_EEG({3: 'F3-F7', 1: 'C4-T4'})
    with pytest.raises(Exception) as excinfo:
        pytest.device.locate_bipolar_EEG_channels(['F4-F3'])
    assert "The specified channel/s is not complied with 10-20 system in bipolar configuration (e.g. F7-F3)." in str(excinfo.value)

@pytest.mark.dict_test
def test_locate_chnnels_wrong_channel(data):
    pytest.device.create_lsl_EEG({3: 'F3-F7', 1: 'C4-T4'})
    with pytest.raises(Exception) as excinfo:
        pytest.device.locate_bipolar_EEG_channels({6: 'F4-F3'})
    assert "The specified channel/s is invalid." in str(excinfo.value)

@pytest.mark.dict_test
def test_locate_chnnels_not_initialized_channel(data):
    pytest.device.create_lsl_EEG({3: 'F3-F7', 1: 'C4-T4'})
    with pytest.raises(Exception) as excinfo:
        pytest.device.locate_bipolar_EEG_channels({2: 'F4-F3'})
    assert "The specified channel has not been initialized." in str(excinfo.value)
