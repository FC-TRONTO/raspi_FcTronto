# coding: UTF-8

import unittest
from imageProcessing import ImageProcessing
from ctypes import Structure, c_int, c_double


# テスト用共有メモリの構造体
class TestPoint(Structure):
    _fields_ = [('irAngle', c_int), ('uSonicDis', c_double), ('enemyGoalAngle', c_int), ('enemyGoalDis', c_int), ('myGoalAngle', c_int), ('myGoalDis', c_int)]


if __name__ == '__main__':
    from multiprocessing import Process, Value

    print 'test main line'
    # テスト用共有メモリの準備
    shmem = Value(TestPoint, 0)

    # モータ制御インスタンスの生成
    imageProcessing = ImageProcessing()

    p_imageProcessing = Process(target=imageProcessing.target, args=(shmem,))

    p_imageProcessing.start()
    print 'p_imageProcessing started'
    p_imageProcessing.join()
