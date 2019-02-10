# coding: UTF-8

from multiprocessing import Process, Value
from ctypes import Structure, c_int, c_double
import os
from serialCom import SerialController
from motorContl import MotorController
from imageProcessing import ImageProcessing

# 共有メモリの構造体
class Point(Structure):
    _fields_ = [('irAngle', c_int), ('uSonicDis', c_double), ('enemyGoalAngle', c_int), ('enemyGoalDis', c_int), ('myGoalAngle', c_int), ('myGoalDis', c_int)]

def info(title):
    print(title)
    print('module name:', __name__)
    print('parent process:', os.getppid())
    print('process id:', os.getpid())

if __name__ == '__main__':
    info('main line')
    # 共有メモリの準備
    shmem = Value(Point, 0)
    # シリアル通信制御インスタンスの生成
    serialController = SerialController()
    # モータ制御インスタンスの生成
    motorController = MotorController()
    # 画像処理インスタンスの生成
    imageProcessing = ImageProcessing()

    p_serialCon = Process(target=serialController.target, args=(shmem,))
    p_motorContl = Process(target=motorController.target, args=(shmem, serialController))
    p_imageProcessing = Process(target=imageProcessing.target, args=(shmem,))

    p_serialCon.start()
    print('p_serialCon started')
    p_motorContl.start()
    print('p_motorContl started')
    p_imageProcessing.start()
    TRACE('p_imageProcessing started')

    p_motorContl.join()
    p_serialCon.join()
    p_imageProcessing.join()

