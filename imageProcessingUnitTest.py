# coding: UTF-8

import unittest
from imageProcessing import ImageProcessing
from ctypes import Structure, c_int, c_double
from debug import ERROR, WARN, INFO, DEBUG, TRACE
import cv2
import time
import glob

# テスト用共有メモリの構造体
class TestPoint(Structure):
    _fields_ = [('irAngle', c_int), ('uSonicDis', c_double), ('enemyGoalAngle', c_int), ('enemyGoalDis', c_int), ('myGoalAngle', c_int), ('myGoalDis', c_int)]


if __name__ == '__main__':
    from multiprocessing import Process, Value

    TRACE('test main line')
    # テスト用共有メモリの準備
    shmem = Value(TestPoint, 0)

    # モータ制御インスタンスの生成
    imageProcessing = ImageProcessing()

    p_imageProcessing = Process(target=imageProcessing.target, args=(shmem,))

    file_list = glob.glob("./camera_distance/0degree/00000001.jpg")
    TRACE(file_list)

    for file in file_list:
        TRACE(file)
        stream = cv2.imread(file)

        yellow_goal_angle, yellow_goal_distance, blue_goal_angle, blue_goal_distance = imageProcessing.imageProcessingFrame(stream, shmem)

        time.sleep(5)

    p_imageProcessing.start()
    TRACE('p_imageProcessing started')

    cv2.destroyAllWindows()
    # p_imageProcessing.join()
