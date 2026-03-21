# tests/test_models/test_slideshow.py
import pytest
from src.models.photo import Photo
from src.models.slide import Slide
from src.models.slideshow import Slideshow


def test_slideshow_empty_score():
    slideshow = Slideshow(slides=[])
    assert slideshow.calculate_score() == 0


def test_slideshow_single_slide_score():
    slide = Slide([Photo(0, 'H', {'cat'})])
    slideshow = Slideshow(slides=[slide])
    assert slideshow.calculate_score() == 0  # No transitions


def test_slideshow_two_slides_score():
    s1 = Slide([Photo(0, 'H', {'a', 'b', 'c'})])
    s2 = Slide([Photo(1, 'H', {'a', 'b', 'd'})])
    slideshow = Slideshow(slides=[s1, s2])
    # common=2, only_s1=1, only_s2=1 -> min=1
    assert slideshow.calculate_score() == 1


def test_slideshow_to_output_string():
    s0 = Slide([Photo(0, 'H', {'cat'})])
    s1 = Slide([Photo(3, 'H', {'garden'})])
    s2 = Slide([Photo(1, 'V', {'a'}), Photo(2, 'V', {'b'})])
    slideshow = Slideshow(slides=[s0, s1, s2])

    output = slideshow.to_output_string()
    lines = output.strip().split('\n')
    assert lines[0] == '3'
    assert lines[1] == '0'
    assert lines[2] == '3'
    assert lines[3] == '1 2'


def test_slideshow_len():
    slideshow = Slideshow(slides=[Slide([Photo(0, 'H', {'a'})])])
    assert len(slideshow) == 1
