from distutils import setup


setup(
    name='YubiOTP',
    version='0.1.0',
    description='An implementation of the Yubico OTP algorithm, as used in YubiKey devices.',
    long_description=open('README.rst').read(),
    author='Peter Sagerson',
    author_email='psagersccdwvgsz@ignorare.net',
    packages='yubiotp',
    scripts=['bin/yubiotp', 'bin/yubikey'],
    url='https://bitbucket.org/psagers/yubiotp',
    license='LICENSE',
    install_requires=['pycrypto']
)
