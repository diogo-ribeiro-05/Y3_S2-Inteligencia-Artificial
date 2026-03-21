# tests/test_io/test_parser.py
import pytest
from src.io.parser import parse_input


def test_parse_input_example():
    content = """4
H 3 cat beach sun
V 2 selfie smile
V 2 garden selfie
H 2 garden cat
"""
    photos = parse_input(content)

    assert len(photos) == 4

    assert photos[0].id == 0
    assert photos[0].orientation == 'H'
    assert photos[0].tags == {'cat', 'beach', 'sun'}

    assert photos[1].id == 1
    assert photos[1].orientation == 'V'
    assert photos[1].tags == {'selfie', 'smile'}

    assert photos[2].id == 2
    assert photos[2].orientation == 'V'
    assert photos[2].tags == {'garden', 'selfie'}

    assert photos[3].id == 3
    assert photos[3].orientation == 'H'
    assert photos[3].tags == {'garden', 'cat'}


def test_parse_input_from_file(tmp_path):
    content = """2
H 1 dog
V 2 cat mouse
"""
    filepath = tmp_path / "test.txt"
    filepath.write_text(content)

    photos = parse_input(filepath.read_text())
    assert len(photos) == 2


def test_parse_input_invalid_format():
    content = "invalid"
    with pytest.raises(ValueError):
        parse_input(content)
