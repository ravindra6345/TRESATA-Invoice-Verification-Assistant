import pytest
from extractor import _extract_json

def test_parse_plain_json():
    assert _extract_json('{"supplier": "ABC"}') == {"supplier": "ABC"}

def test_parse_fenced_json():
    response = """```json
{"supplier": "ABC"}
```"""
    assert _extract_json(response) == {"supplier": "ABC"}

def test_reject_invalid_json():
    with pytest.raises(ValueError):
        _extract_json("not json")
