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

    # p_imageProcessing = Process(target=imageProcessing.target, args=(shmem,))
    #
    # p_imageProcessing.start()
    # TRACE('p_imageProcessing started')
    file_list = glob.glob("./camera_distance/0degree/*jpg")
    TRACE(file_list)

    for file in file_list:
        TRACE(file)
        stream = cv2.imread(file)
        hsv_img = cv2.cvtColor(stream, cv2.COLOR_BGR2HSV)

        # 黄色領域の検知
        yellow_cx_t, yellow_cy_t, yellow_area_size, yellow_convex = imageProcessing.colorDetect(hsv_img, imageProcessing.YELLOW_HSV_RANGE_MIN,
                                                                                 imageProcessing.YELLOW_HSV_RANGE_MAX, 'Yellow')
        if yellow_cx_t > -1:
            imageProcessing.draw_marker(stream, yellow_cx_t, yellow_cy_t, (30, 255, 30))

        # 青色領域の検知
        blue_cx_t, blue_cy_t, blue_area_size, blue_convex = imageProcessing.colorDetect(hsv_img, imageProcessing.BLUE_HSV_RANGE_MIN,
                                                                           imageProcessing.BLUE_HSV_RANGE_MAX, 'Blue')
        if blue_cx_t > -1:
            imageProcessing.draw_marker(stream, blue_cx_t, blue_cy_t, (255, 30, 30))

        # 壁の検知
        wall_cx_t, wall_cy_t, wall_area_size, wall_convex = imageProcessing.wallDetect(hsv_img, imageProcessing.WALL_HSV_RANGE_MIN, imageProcessing.WALL_HSV_RANGE_MAX, 'Wall')
        cv2.drawContours(stream, [wall_convex], 0, (255, 255, 0), thickness=1)
        # 結果表示
        # 画角の前後左右と画像表示の上下左右を揃えるために画像を転置する。
        cv2.circle(stream, (imageProcessing.CAMERA_CENTER_CX_T, imageProcessing.CAMERA_CENTER_CY_T), imageProcessing.CAMERA_RANGE_R, (0, 0, 255), thickness=1)
        cv2.line(stream, (imageProcessing.CAMERA_CENTER_CX_T, 0), (imageProcessing.CAMERA_CENTER_CX_T, 480), (0, 0, 255), thickness=1)
        cv2.line(stream, (0, imageProcessing.CAMERA_CENTER_CY_T), (480, imageProcessing.CAMERA_CENTER_CY_T), (0, 0, 255),
                 thickness=1)
        cv2.imshow('Frame', stream.transpose((1, 0, 2)))
        cv2.moveWindow('Frame', 0, 30)
        cv2.moveWindow('MaskYellow', 482, 30)
        cv2.moveWindow('MaskBlue', 964, 30)
        cv2.moveWindow('MaskWall', 482, 502)
        cv2.waitKey(0)

    cv2.destroyAllWindows()
    # p_imageProcessing.join()
