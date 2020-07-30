#!/usr/bin/env python3
# coding: utf-8
import pytest


def test1():
    assert 3 == 3


def test2():
    with pytest.raises(AssertionError):
        assert 3 == 4
