from machine import UART
import ustruct as struct

class PMS7003:
    PMS_FRAME_LENGTH = 0
    PMS_PM1_0 = 1
    PMS_PM2_5 = 2
    PMS_PM10_0 = 3
    PMS_PM1_0_ATM = 4
    PMS_PM2_5_ATM = 5
    PMS_PM10_0_ATM = 6
    PMS_PCNT_0_3 = 7
    PMS_PCNT_0_5 = 8
    PMS_PCNT_1_0 = 9
    PMS_PCNT_2_5 = 10
    PMS_PCNT_5_0 = 11
    PMS_PCNT_10_0 = 12
    PMS_VERSION = 13
    PMS_ERROR = 14
    PMS_CHECKSUM = 15

    #command
    cmdReadData = b'\xe2\x00\x00'
    cmdModePassive = b'\xe1\x00\x00'
    cmdModeActive = b'\xe1\x00\x01'
    cmdSleep = b'\xe4\x00\x00'
    cmdWakeup = b'\xe4\x00\x01'
    passive = 0
    active = 1
    mode = None 

    def __init__(self,uart=0):
        self.uart = UART(uart)
        self.uart.init(9600, bits=8, parity=None, stop=1, rxbuf=32)
        self.setmode(self.passive)

    def setmode(self,mode):
        self.mode = mode
        if mode == self.passive:
            self.write(self.cmdModePassive)
        else:
            self.write(self.cmdModeActive)

    def sleep(self):
        self.write(self.cmdSleep)

    def wakeup(self):
        self.write(self.cmdWakeup)
           
    def write(self,cmd):
        command = b'BM'+cmd
        sum = 0
        for c in command:
            sum += c
        command += bytearray([sum>>8,sum&0xff])
        self.uart.write(command)

    def read(self):
        if self.mode == self.passive:
            self.write(self.cmdReadData)
        while not self.uart.any():
            pass
        if self.uart.read(1) != b'B':
            return False
        if self.uart.read(1) != b'M':
            return False

        read_buffer = self.uart.read(30)
        if len(read_buffer) < 30:
            return False

        data = struct.unpack('!HHHHHHHHHHHHHBBH', read_buffer)

        checksum = 0x42 + 0x4D
        for c in read_buffer[0:28]:
            checksum += c
        if checksum != data[self.PMS_CHECKSUM]:
            print('bad checksum')
            return False

        return {
            'FRAME_LENGTH': data[self.PMS_FRAME_LENGTH],
            'PM1_0': data[self.PMS_PM1_0],
            'PM2_5': data[self.PMS_PM2_5],
            'PM10_0': data[self.PMS_PM10_0],
            'PM1_0_ATM': data[self.PMS_PM1_0_ATM],
            'PM2_5_ATM': data[self.PMS_PM2_5_ATM],
            'PM10_0_ATM': data[self.PMS_PM10_0_ATM],
            'PCNT_0_3': data[self.PMS_PCNT_0_3],
            'PCNT_0_5': data[self.PMS_PCNT_0_5],
            'PCNT_1_0': data[self.PMS_PCNT_1_0],
            'PCNT_2_5': data[self.PMS_PCNT_2_5],
            'PCNT_5_0': data[self.PMS_PCNT_5_0],
            'PCNT_10_0': data[self.PMS_PCNT_10_0],
            'VERSION': data[self.PMS_VERSION],
            'ERROR': data[self.PMS_ERROR],
            'CHECKSUM': data[self.PMS_CHECKSUM],
        }
