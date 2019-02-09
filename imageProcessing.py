# coding: UTF-8

import cv2
import numpy as np
import picamera
import picamera.array
from debug import ERROR, WARN, INFO, DEBUG, TRACE


class ImageProcessing:
    def __init__(self):
        TRACE('ImageProcessing generated')

    def colorDetect(self, hsv_img, hsv_range_min, hsv_range_max, color_name):
        mask = cv2.inRange(hsv_img, np.array(hsv_range_min), np.array(hsv_range_max))
        cv2.imshow('Mask' + color_name, mask)
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        convex_hull_list = []
        for contour in contours:
            approx = cv2.convexHull(contour)
            # rect = cv2.boundingRect(approx)
            # cv2.rectangle(stream.array, (rect[0], rect[1]), (rect[0] + rect[2], rect[1] + rect[3]), (255, 150, 100),
            #               thickness=1)

            M = cv2.moments(approx)
            convex_hull_list.append(M)

        if len(convex_hull_list) > 0:
            max_convex_hull_blue = max(convex_hull_list, key=(lambda x: x['m00']))

            if max_convex_hull_blue['m00'] > 0:
                area_size = max_convex_hull_blue['m00']

                cx = int(max_convex_hull_blue['m10'] / max_convex_hull_blue['m00'])
                cy = int(max_convex_hull_blue['m01'] / max_convex_hull_blue['m00'])

                return cx, cy, area_size
            return -1, -1, 0.0
        else:
            return -1, -1, 0.0

    def draw_marker(self, img, x, y, marker_color):
        cv2.line(img, (x - 7, y), (x + 7, y), color=(255, 255, 255), thickness=2)
        cv2.line(img, (x, y - 7), (x, y + 7), color=(255, 255, 255), thickness=2)
        cv2.line(img, (x - 7, y), (x + 7, y), color=marker_color, thickness=1)
        cv2.line(img, (x, y - 7), (x, y + 7), color=marker_color, thickness=1)

    def imageProcessingMain(self, shmem):
        # 画像処理を行う

        with picamera.PiCamera() as camera:
            with picamera.array.PiRGBArray(camera) as stream:
                camera.resolution = (480, 480)
                cap = cv2.VideoCapture('test.avi')

                while cap.isOpened():
                    # 画像を取得する
                    # stream.arrayにRGBの順で映像データを格納
                    camera.capture(stream, 'bgr', use_video_port=True)
                    #stream = cv2.imread('sample_match.jpg')

                    # HSV色空間に変換
                    hsv_img = cv2.cvtColor(stream.array, cv2.COLOR_BGR2HSV)


                    # 青色
                    cx, cy, area_size_blue = self.colorDetect(hsv_img, [100, 127, 30], [120, 255, 255], 'Blue')
                    if cx > -1:
                        self.draw_marker(stream.array, cx, cy, (255, 30, 30))

                    cx, cy, area_size_yellow = self.colorDetect(hsv_img, [20, 127, 0], [40, 255, 255], 'Yellow')
                    if cx > -1:
                        self.draw_marker(stream.array, cx, cy, (30, 255, 30))

                    DEBUG('Blue :' + str(area_size_blue).rjust(8) + ' Yellow :' + str(area_size_yellow).rjust(8))

                    # 結果表示
                    cv2.imshow('Frame', stream.array)
                    cv2.moveWindow('Frame', 0, 30)
                    cv2.moveWindow('MaskBlue', 482, 30)
                    cv2.moveWindow('MaskYellow', 964, 30)

                    # "q"でウィンドウを閉じる
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        break

                    # streamをリセット
                    stream.seek(0)
                    stream.truncate()
                cv2.destroyAllWindows()


            # TODO: ゴールの位置を解析する

            # TODO: 共有メモリに書き込む

    def target(self, shmem):
        TRACE('imageProcessingMain target() start')
        self.imageProcessingMain(shmem)

    def close():
        pass
