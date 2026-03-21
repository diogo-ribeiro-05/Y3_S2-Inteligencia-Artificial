# tests/test_models/test_slide.py
import pytest
from src.models.photo import Photo
from src.models.slide import Slide


def test_slide_single_horizontal():
    photo = Photo(id=0, orientation='H', tags={'cat', 'beach'})
    slide = Slide(photos=[photo])
    assert slide.tags == {'cat', 'beach'}
    assert slide.is_horizontal_slide == True


def test_slide_two_vertical():
    photo1 = Photo(id=1, orientation='V', tags={'selfie', 'smile'})
    photo2 = Photo(id=2, orientation='V', tags={'garden', 'selfie'})
    slide = Slide(photos=[photo1, photo2])
    assert slide.tags == {'selfie', 'smile', 'garden'}
    assert slide.is_vertical_slide == True


def test_slide_invalid_vertical_single():
    photo = Photo(id=1, orientation='V', tags={'a'})
    with pytest.raises(ValueError, match="Vertical photos must be paired"):
        Slide(photos=[photo])


def test_slide_invalid_two_horizontal():
    photo1 = Photo(id=0, orientation='H', tags={'a'})
    photo2 = Photo(id=1, orientation='H', tags={'b'})
    with pytest.raises(ValueError, match="Cannot combine two horizontal photos"):
        Slide(photos=[photo1, photo2])


def test_slide_invalid_mixed():
    photo1 = Photo(id=0, orientation='H', tags={'a'})
    photo2 = Photo(id=1, orientation='V', tags={'b'})
    with pytest.raises(ValueError, match="Cannot mix horizontal and vertical"):
        Slide(photos=[photo1, photo2])


def test_slide_photo_ids():
    photo1 = Photo(id=1, orientation='V', tags={'a'})
    photo2 = Photo(id=2, orientation='V', tags={'b'})
    slide = Slide(photos=[photo1, photo2])
    assert slide.photo_ids == [1, 2]
