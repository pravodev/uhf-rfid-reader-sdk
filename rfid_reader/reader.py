from rfid_reader.exceptions import InvalidConfig
import socket, serial, re, crcmod, crcmod.predefined, binascii, time
from binascii import hexlify

BAUDRATE = {
    5600: 0
}

#EPC C1 G2（ISO18000-6C）COMMAND
INVENTORY=0x01
READ_DATA=0x02
WRITE_DATA=0x03
KILL_TAG=0x05
LOCK=0x06
BLOCK_ERASE=0x07
READ_PROTECT=0x08
READ_PROTECT_WITHOUT_EPC=0x09
RESET_READ_PROTECT=0x0A
CHECK_READ_PROTECT=0x0B
EAS_ALARM=0x0C
CHECK_EAS_ALARM=0x0D
BLOCK_LOCK=0x0E
INVENTORY_SINGLE=0x0F
BLOCK_WRITE=0x10

#READER DEFINED COMMAND
GET_READER_INFORMATION=0x21
SET_REGION=0x22
SET_ADDRESS=0x24
SET_SCANTIME=0x25
SET_BAUDRATE=0x28
SET_POWER=0x2F
ACOUSTO_OPTIC_CONTROL=0x33
SET_WIEGAND=0x34
SET_WORK_MODE=0x35
GET_WORK_MODE=0x36
SET_EAS_ACCURACY=0x37
SYRIS_RESPONSE_OFFSET=0x38
TRIGGER_OFFSET=0x3B

class RFIDReader:
    communication = 'socket'
    addr = '00'
    baudrate = BAUDRATE[5600]
    buffer_size = 8192
    connection = None
    timeout = 5.0
    host = None
    port = 6000
    config = {
        'read_interval_timeout': 10,
        'read_total_timeout_constant': 10,
        'read_total_timeout_multiplier': 20,
        'write_total_timeout_constant': 20,
        'write_total_timeout_multiplier': 20
    }


    def __init__(self, *args, **kwargs):
        if len(args):
            self.communication = args[0]
        
        if len(kwargs):
            self.addr = kwargs.get('addr', self.addr)
            self.baudrate = kwargs.get('baudrate', self.baudrate)
            self.timeout = kwargs.get('timeout', self.timeout)
            self.host = kwargs.get('host', self.host)
            self.port = kwargs.get('port', self.port)
            self.config = kwargs.get('config', self.config)
    
    def connect(self):
        self.validateConfig()

        if self.communication is 'socket':
            # connect socket
            self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connection.settimeout(self.timeout)
            self.connection.connect((self.host, self.port))
        elif self.communication is 'serial':
            # connect port
            self.connection = serial.Serial()
            self.connection.port = self.port
            self.connection.baudrate = self.baudrate

            self.connection.parity = serial.PARITY_NONE
            self.connection.timeout = 5
            self.connection.stopbits = serial.STOPBITS_ONE
            self.connection.ReadIntervalTimeout = self.config.get('read_interval_timeout')
            self.connection.ReadTotalTimeoutConstant = self.config.get('read_total_timeout_constant')
            self.connection.ReadTotalTimeoutMultiplier = self.config.get('read_total_timeout_multiplier')
            self.connection.WriteTotalTimeoutConstant = self.config.get('write_total_timeout_constant')
            self.connection.WriteTotalTimeoutMultiplier = self.config.get('write_total_timeout_multiplier')
            self.connection.open()

        return self.connection
        
    def disconnect(self):
        self.connection.close()

    def validateConfig(self):
        if self.communication not in ['socket', 'serial']:
            raise InvalidConfig("invalid communication type, please use socket or port")
        elif self.baudrate not in BAUDRATE.values():
            raise InvalidConfig("invalid baudrate")
    
    def parseTag(self, rawtag, parse_all = True):
        """get tag from byte data"""
        sisa = 4 # 2 byte terakhir pada response
        rawtag = rawtag.decode('utf-8')
        tags = []
        try:
            index_awal = rawtag.index('e200')

            if parse_all == False:
                tag = rawtag[index_awal:(24+index_awal)]
                return tag
                
            tag = rawtag[index_awal:(len(rawtag)-sisa)]
            tags = re.findall("e2\w{22}", tag)
            return tags
        except Exception:
            return tags if parse_all else None

    def getResponse(self, parse=False):
        """retrive data from connection"""
        data = None

        deadline = time.time() + self.timeout
        while data is None:
            if time.time() >= deadline:
                raise Exception()
            
            if self.communication == "socket":
                self.connection.settimeout(deadline - time.time())
                data = self.connection.recv(self.buffer_size)
            elif self.communication == 'serial':
                data = self.connection.readline()

        if parse:
            data = hexlify(data)
            
            return {
                'len': int(data[0:2], 16),
                'addr': data[2:4].decode('utf-8'),
                'reCmd': data[4:6].decode('utf-8'),
                'data': data[6:-4],
                'lsb': data[-4:-2],
                'msb': data[-2:],
            }
        
        return data

    def sendCommand(self, cmd, **kwargs):
        raw_data = kwargs.get('data', [])
        addr = bytearray.fromhex(self.addr)
        cmd = bytearray([cmd])
        data = bytearray(raw_data)
        raw_length = str(len(addr+cmd+data) + 2)
        length = bytearray.fromhex(raw_length if len(raw_length) >=2 else '0' + raw_length)
        if len(data):
            crc = self.calculateCRC(length + addr + cmd + data)
        else:
            crc = self.calculateCRC(length + addr + cmd)

        lsb = bytearray.fromhex(str(crc[2:4]))
        msb = bytearray.fromhex(str(crc[0:2]))

        
        if len(data):
            request = length + addr + cmd + data + lsb + msb
        else:
            request = length + addr + cmd + lsb + msb
        
        if self.communication == "socket":
            self.connection.sendall(request)
        elif self.communication == "serial":
            self.connection.write(request)

    def calculateCRC(self, data):
        crc16 = crcmod.predefined.Crc('crc-16-mcrf4xx')
        crc16.update(data)
        return crc16.hexdigest()

    def inventory(self):
        data = None
        while data is None:
            self.sendCommand(INVENTORY)
            response = binascii.hexlify(self.getResponse())
            data = self.parseTag(response)
        return data

    def singleInventory(self):
        data = None
        while data is None:
            self.sendCommand(INVENTORY_SINGLE)
            response = binascii.hexlify(self.getResponse())
            data = self.parseTag(response)
        return data[0] if len(data) == 1 else None
        
    def scantags(self):
        return self.inventory()

    def scantag(self):
        return self.singleInventory()

    def getInfo(self):
        self.sendCommand(GET_READER_INFORMATION)
        resp = self.getResponse(True)
        data = resp.get('data')
        print('resp', data)