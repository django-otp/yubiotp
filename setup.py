#!/usr/bin/env python

from distutils.core import setup


setup(
    name='YubiOTP',
    version='0.1.0',
    description='An implementation of the Yubico OTP algorithm, as used in YubiKey devices.',
    long_description=open('README').read(),
    author='Peter Sagerson',
    author_email='psagersccdwvgsz@ignorare.net',
    packages=['yubiotp'],
    scripts=['bin/yubikey'],
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
