#!/usr/bin/env python

from setuptools import setup

try:
    import unittest2  # noqa
except ImportError:
    test_loader = 'unittest:TestLoader'
else:
    test_loader = 'unittest2:TestLoader'


setup(
    name='YubiOTP',
    version='0.2.1',
    description='A library for verifying YubiKey OTP tokens, both locally and through a Yubico web service.',
    long_description=open('README').read(),
    author='Peter Sagerson',
    author_email='psagersccdwvgsz@ignorare.net',
    packages=['yubiotp'],
    scripts=['bin/yubikey', 'bin/yubiclient'],
    url='https://bitbucket.org/psagers/yubiotp',
    license='BSD',
    install_requires=[
        'six',
        'pycrypto',
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    test_suite='yubiotp.test',
    test_loader=test_loader,
)
