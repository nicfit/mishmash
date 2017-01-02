# -*- coding: utf-8 -*-
import pytest
import mishmash
"""
test_mishmash
----------------------------------

Tests for `mishmash` module.
"""


def test_metadata():
    assert mishmash.version
    assert mishmash.__about__.__license__
    assert mishmash.__about__.__project_name__
    assert mishmash.__about__.__author__
    assert mishmash.__about__.__author_email__
    assert mishmash.__about__.__version_info__
    assert mishmash.__about__.__release__
    assert mishmash.__about__.__version_txt__
