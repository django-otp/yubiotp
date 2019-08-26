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
    version='0.2.2.post1',
    description='A library for verifying YubiKey OTP tokens, both locally and through a Yubico web service.',
    author='Peter Sagerson',
    author_email='psagers@ignorare.net',
    url='https://github.com/django-otp/yubiotp',
    project_urls={
        "Documentation": 'https://yubiotp.readthedocs.io/',
        "Source": 'https://github.com/django-otp/yubiotp',
    },
    license='BSD',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python',
        'Topic :: Security',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

    packages=[
        'yubiotp',
    ],
    scripts=[
        'bin/yubikey',
        'bin/yubiclient',
    ],
    install_requires=[
        'six',
        'pycryptodome',
    ],

    test_suite='yubiotp.test',
    test_loader=test_loader,
)
