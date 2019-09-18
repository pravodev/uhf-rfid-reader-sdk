from setuptools import setup

setup(
    name='uhf-rfid-reader-sdk',
    version='0.1',
    author="Rifqi Khoeruman Azam",
    author_email="pravodev@gmail.com",
    install_requires= [
        'pyserial',
        'crcmod'
    ],
    description="(Unofficial) UHF RFID Reader SDK",
    long_description=open('README.md').read(),
    license="MIT",
    keywords="rfid sdk",
    url="https://github.com/pravodev/uhf-rfid-reader-sdk",
    packages=['rfid_reader']
)