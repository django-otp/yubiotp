#!/usr/bin/env python

from distutils.core import setup


setup(
    name='YubiOTP',
    version='0.2.0',
    description='A library for verifying YubiKey OTP tokens, both locally and through a Yubico web service.',
    long_description=open('README').read(),
    author='Peter Sagerson',
    author_email='psagersccdwvgsz@ignorare.net',
    packages=['yubiotp'],
    scripts=['bin/yubikey', 'bin/yubiclient'],
    url='https://bitbucket.org/psagers/yubiotp',
    license='BSD',
    install_requires=['pycrypto'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
