import pytest
from scripts.seed_data import _clean_str, _to_int, _to_float, _to_phone, _is_placeholder_row

def test_clean_str():
    assert _clean_str("  hello  ") == "hello"
    assert _clean_str("") is None
    assert _clean_str(None) is None

def test_to_int():
    assert _to_int("123") == 123
    assert _to_int("123.45") == 123
    assert _to_int("invalid") is None
    assert _to_int(None) is None

def test_to_float():
    assert _to_float("123.45") == 123.45
    assert _to_float("invalid") is None
    assert _to_float(None) is None

def test_to_phone():
    assert _to_phone("9876543210") == "9876543210"
    assert _to_phone("9876543210.0") == "9876543210"
    assert _to_phone("not a phone") is None

def test_is_placeholder_row():
    assert _is_placeholder_row({"col1": "Continue to next page"}) is True
    assert _is_placeholder_row({"col1": "Valid data"}) is False