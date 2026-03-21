# tests/test_models/test_photo.py
from src.models.photo import Photo


def test_photo_creation():
    photo = Photo(id=0, orientation='H', tags={'cat', 'beach', 'sun'})
    assert photo.id == 0
    assert photo.orientation == 'H'
    assert photo.tags == {'cat', 'beach', 'sun'}


def test_photo_is_horizontal():
    photo = Photo(id=0, orientation='H', tags=set())
    assert photo.is_horizontal == True
    assert photo.is_vertical == False


def test_photo_is_vertical():
    photo = Photo(id=1, orientation='V', tags=set())
    assert photo.is_vertical == True
    assert photo.is_horizontal == False


def test_photo_tag_count():
    photo = Photo(id=0, orientation='H', tags={'a', 'b', 'c'})
    assert photo.tag_count == 3
