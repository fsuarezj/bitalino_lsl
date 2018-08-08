import pytest
from context import bitalino_lsl

def test_empty_list():
    assert bitalino_lsl.list_bitalino() == []
