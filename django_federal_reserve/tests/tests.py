"""
Quick run with:

    export TESTNAME=.testJobRawCommand; tox -e py27-django17

"""
from __future__ import print_function

import warnings

from django.test import TestCase

warnings.simplefilter('error', RuntimeWarning)


class Tests(TestCase):

    fixtures = []

    def setUp(self):
        pass

    def test1(self):
        self.assertEqual(1, 1)
