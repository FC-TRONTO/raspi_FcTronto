# coding: UTF-8

import time
import cv2
import numpy as np
import picamera
import picamera.array


class ImageProcessing:
    def __init__(self):
        print 'ImageProcessing generated'

    def yellow_detect(self, hsv_img):
        # 黄色のHSVの値域
        hsv_min = np.array([20, 127, 0])
        hsv_max = np.array([40, 255, 255])
        mask = cv2.inRange(hsv_img, hsv_min, hsv_max)

        return mask

    def blue_detect(self, hsv_img):
        # 青色のHSVの値域
        hsv_min = np.array([100, 127, 30])
        hsv_max = np.array([120, 255, 255])
        mask = cv2.inRange(hsv_img, hsv_min, hsv_max)

        return mask

    def draw_marker(self, img, x, y, marker_color):
        cv2.line(img, (x - 7, y), (x + 7, y), color=(255, 255, 255), thickness=2)
        cv2.line(img, (x, y - 7), (x, y + 7), color=(255, 255, 255), thickness=2)
        cv2.line(img, (x - 7, y), (x + 7, y), color=marker_color, thickness=1)
        cv2.line(img, (x, y - 7), (x, y + 7), color=marker_color, thickness=1)

    def imageProcessingMain(self, shmem):
        # 画像処理を行う

        with picamera.PiCamera() as camera:
            with picamera.array.PiRGBArray(camera) as stream:
                camera.resolution = (640, 480)
                cap = cv2.VideoCapture('test.avi')

                while cap.isOpened():
                    print 'imageProcessingMain'
                    # TODO: 画像を取得する
                    # stream.arrayにRGBの順で映像データを格納
                    camera.capture(stream, 'bgr', use_video_port=True)
                    #stream = cv2.imread('sample_match.jpg')

                    # HSV色空間に変換
                    hsv_img = cv2.cvtColor(stream.array, cv2.COLOR_BGR2HSV)

                    # 青色検出
                    mask_blue = self.blue_detect(hsv_img)
                    mask_yellow = self.yellow_detect(hsv_img)
                    cv2.imshow("Mask blue", mask_blue)
                    cv2.imshow("Mask yellow", mask_yellow)
                    contours_blue, _ = cv2.findContours(mask_blue, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                    contours_yellow, _ = cv2.findContours(mask_yellow, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

                    convex_hull_blue_list = []
                    for contour in contours_blue:
                        approx = cv2.convexHull(contour)
                        rect = cv2.boundingRect(approx)
                        cv2.rectangle(stream.array, (rect[0], rect[1]),  (rect[0] + rect[2], rect[1] + rect[3]), (255, 150, 100), thickness=1)
                        # cv2.drawContours(stream.array, contour, -1, (255, 0, 0), 2)

                        M = cv2.moments(approx)
                        convex_hull_blue_list.append(M)
                        print 'ConvexHull Area = ' + str(M['m00'])

                    if len(convex_hull_blue_list) > 0:
                        max_convex_hull_blue = max(convex_hull_blue_list, key=(lambda x: x['m00']))

                        if max_convex_hull_blue['m00'] > 0 :
                            cx = int(max_convex_hull_blue['m10'] / max_convex_hull_blue['m00'])
                            cy = int(max_convex_hull_blue['m01'] / max_convex_hull_blue['m00'])
                            self.draw_marker(stream.array, cx, cy, (255, 30, 30))


                    # 結果表示
                    cv2.imshow("Frame", stream.array)

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
        print 'imageProcessingMain target() start'
        self.imageProcessingMain(shmem)

    def close():
        pass
