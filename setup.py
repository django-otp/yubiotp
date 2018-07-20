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
    version='0.2.2',
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
        'pycryptodome',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python',
        'Topic :: Security',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    test_suite='yubiotp.test',
    test_loader=test_loader,
)
