# coding: UTF-8

from serialCom import SerialController
import time

class MotorController:
    def __init__(self):
        print('MotorController generated')
    
    def calcAndSendMotorPowers(self, shmem, serial):
        while 1:
            # テスト用にモータの値は50,100固定
            serial.write("50,100\n")
            #print('write 50,100')
            # 1sごとに実行
            time.sleep(1)
    
    def target(self, shmem, serial):
        print('MotorController target() start')
        self.calcAndSendMotorPowers(shmem, serial)

    def close():
        pass
