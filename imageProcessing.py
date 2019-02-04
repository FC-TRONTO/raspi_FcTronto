# coding: UTF-8

import time
import cv2
import numpy as np
import picamera
import picamera.array


class ImageProcessing:
    def __init__(self):
        print 'ImageProcessing generated'

    def red_detect(self, img):
        # HSV色空間に変換
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # 赤色のHSVの値域1
        hsv_min = np.array([100, 127, 30])
        hsv_max = np.array([120, 255, 255])
        mask1 = cv2.inRange(hsv, hsv_min, hsv_max)

        return mask1

    def imageProcessingMain(self, shmem):
        # 画像処理を行う

        with picamera.PiCamera() as camera:
            with picamera.array.PiRGBArray(camera) as stream:
                camera.resolution = (640, 480)
                while True:
                    print 'imageProcessingMain'
                    # TODO: 画像を取得する
                    # stream.arrayにRGBの順で映像データを格納
                    camera.capture(stream, 'bgr', use_video_port=True)

                    # 赤色検出
                    mask = self.red_detect(stream.array)

                    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

                    rects = []
                    for contour in contours:
                        approx = cv2.convexHull(contour)
                        rect = cv2.boundingRect(approx)
                        rects.append(rect)

                    for rect in rects:
                        print rect[0]
                        print rect[1]
                        print rect[2]
                        print rect[3]
                        # print rect[4]


                        cv2.rectangle(stream.array, (rect[0], rect[1]),  (rect[0] + rect[2], rect[1] + rect[3]), (0, 0, 255), thickness=2)

                        # 結果表示
                    cv2.imshow("Frame", stream.array)
                    cv2.imshow("Mask", mask)


                    # # グレースケールに変換
                    # gray = cv2.cvtColor(stream.array, cv2.COLOR_BGR2GRAY)
                    #
                    # # カスケードファイルを利用して顔の位置を見つける
                    # cascade = cv2.CascadeClassifier(cascade_file)
                    # face_list = cascade.detectMultiScale(gray, minSize=(100, 100))
                    #
                    # for (x, y, w, h) in face_list:
                    #     print("face_position:", x, y, w, h)
                    #     color = (0, 255, 255)
                    #     pen_w = 1
                    #     cv2.rectangle(stream.array, (x, y), (x + w, y + h), color, thickness=pen_w)
                    # # system.arrayをウィンドウに表示
                    # cv2.imshow('frame', stream.array)
                    # # cv2.imshow('frame2', gray)#

                    # "q"でウィンドウを閉じる
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        break

                    # streamをリセット
                    stream.seek(0)
                    stream.truncate()
                cv2.destroyAllWindows()


            # TODO: ゴールの位置を解析する

            # TODO: 共有メモリに書き込む






            # cap = cv2.VideoCapture("input.mp4")
            #
            # while (cap.isOpened()):
            #     # フレームを取得
            #     ret, frame = cap.read()
            #
            #     # 赤色検出
            #     mask = red_detect(frame)
            #
            #     # 結果表示
            #     cv2.imshow("Frame", frame)
            #     cv2.imshow("Mask", mask)
            #
            #     # qキーが押されたら途中終了
            #     if cv2.waitKey(25) & 0xFF == ord('q'):
            #         break
            #
            #     time.sleep(1)
            #
            # cap.release()
            # cv2.destroyAllWindows()

    def target(self, shmem):
        print 'imageProcessingMain target() start'
        self.imageProcessingMain(shmem)

    def close():
        pass
