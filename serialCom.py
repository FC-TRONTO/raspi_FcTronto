# coding: UTF-8

import serial
import time
from debug import ERROR, WARN, INFO, DEBUG, TRACE

class SerialController:
    def __init__(self):
        # USBポートを使い、シリアル通信開始
        # 送信用と受信用で2つポートを使う
        self.ev3_recv_serial = serial.Serial('/dev/ttyUSB0', 115200, timeout=10)
        self.ev3_send_serial = serial.Serial('/dev/ttyUSB1', 115200, timeout=10)
        INFO(self.ev3_recv_serial.portstr)
        INFO(self.ev3_send_serial.portstr)
    
    def receiveDataLoop(self, shmem):
        while 1:
            read_data = self.ev3_recv_serial.readline()
            # 読み込んだ文字列を,区切りでリストに変換
            sensorValues = read_data.strip().split(",")
            # 共有メモリの値を更新
            if(len(sensorValues) == 2):
                if(self.is_int(sensorValues[0])):
                    shmem.irAngle = int(sensorValues[0])
                if(self.is_float(sensorValues[1])):
                    shmem.uSonicDis = float(sensorValues[1])
                TRACE('irAngle =', shmem.irAngle)
                TRACE('uSonicDis =', shmem.uSonicDis)
    
    def write(self, sendData):
        self.ev3_send_serial.write(sendData)
        DEBUG('write', sendData.rstrip())

    def target(self, shmem):
        self.receiveDataLoop(shmem)

    def close():
        pass

    def is_float(self, num):
        try:
            float(num)
        except ValueError:
            return False
        else:
            return True

    def is_int(self, num):
        try:
            int(num)
        except ValueError:
            return False
        else:
            return True
