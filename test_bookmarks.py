#!/home/linuxbrew/.linuxbrew/bin/python3.7

import pytest

from bookmarks import *

@pytest.fixture
def bookmarks():
    import json
    with open('test_data/bookmarks.json') as f:
        return json.load(f)


def test_next_id(bookmarks):
    assert next_id(bookmarks) == 230

def test_next_index(bookmarks):
    assert next_index([bookmarks]) == 1
