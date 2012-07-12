from unittest import TestSuite, TextTestRunner
from doctest import DocTestSuite

from . import crc, modhex, otp


suite = TestSuite()

suite.addTest(DocTestSuite(crc))
suite.addTest(DocTestSuite(modhex))
suite.addTest(DocTestSuite(otp))

TextTestRunner().run(suite)
