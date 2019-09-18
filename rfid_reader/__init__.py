from distutils.version import LooseVersion
from rfid_reader.reader import RFIDReader, BAUDRATE

__version__ = '1.0.0'
__version_info__ = tuple(LooseVersion(__version__).version)
__author__ = 'Rifqi Khoeruman Azam <pravodev@gmail.com>'
__all__ = [
    'RFID',
]
