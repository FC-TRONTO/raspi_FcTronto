# coding: UTF-8

from enum import IntEnum
from debug import ERROR, WARN, INFO, DEBUG, TRACE

import cv2
import numpy as np
import picamera
import picamera.array
import os

from math import atan2, degrees, hypot


# ボール保持状態用列挙型
class EnemyGoalColorE(IntEnum):
    YELLOW = 0
    BLUE = 1


class ImageProcessing:
    # 画像出力の有効無効
    ENABLE = 1
    DISABLE = 0
    DEBUG_IMSHOW = DISABLE

    BLUE_HSV_RANGE_MIN = [55, 70, 10]
    BLUE_HSV_RANGE_MAX = [120, 150, 40]
    YELLOW_HSV_RANGE_MIN = [15, 127, 30]
    YELLOW_HSV_RANGE_MAX = [30, 255, 255]
    WALL_HSV_RANGE_MIN = [25, 70, 0]
    WALL_HSV_RANGE_MAX = [120, 255, 255]

    CAMERA_CENTER_CX_T = 220
    CAMERA_CENTER_CY_T = 240
    CAMERA_CENTER_CX = CAMERA_CENTER_CY_T
    CAMERA_CENTER_CY = CAMERA_CENTER_CX_T
    CAMERA_RANGE_R = 170

    KARNEL_R = 5
    KARNEL_SIZE = 2 * KARNEL_R + 1

    GOAL_DISTANCE_TABLE = []

    # @brief コンスタラクタ
    # @detail 初期化処理を行う
    def __init__(self):
        TRACE('ImageProcessing generated')

        # テーブルの読み込み
        # TODO: テーブル情報は仮。csvファイルから読み込むようにする
        self.GOAL_DISTANCE_TABLE = range(241)
        self.enemy_goal_color = EnemyGoalColorE.YELLOW
        self.goal_mode = 'none'
        self.pre_goal_mode = 'none'

    # @brief 敵ゴールの色をsetする(旧)
    # @param set_color setする相手ゴールの色
    # @detail 引数にはEnemyGoalColorEの値を指定する
    """
    def setEnemyGoalColor(self, set_color):
        color_name = ['YELLOW', 'BLUE']
        old_enemy_goal_color = self.ENEMY_GOAL_COLOR
        self.ENEMY_GOAL_COLOR = set_color
        INFO('Set Enemy Goal Color :', color_name[old_enemy_goal_color], '->', color_name[set_color])
    """

    # @brief 敵ゴールの色をsetする
    # @param set_color setする相手ゴールの色
    # @detail ファイルから読み込む
    def setEnemyGoalColorFromFile(self):
        # ゴールモード設定ファイルを読み込み
        try:
            with open('/home/pi/Desktop/raspi_FcTronto/webiopi/goal_mode.txt') as f:
                self.goal_mode = f.read()
        # ファイル読み込み失敗
        except:
            WARN('goal mode file read failure')
        # 前回読み込み時から変更があれば設定
        if self.goal_mode != self.pre_goal_mode:
            if self.goal_mode == 'yellow':
                self.enemy_goal_color = EnemyGoalColorE.YELLOW
            elif self.goal_mode == 'blue':
                self.enemy_goal_color = EnemyGoalColorE.BLUE
            else:
                WARN('invalid goal mode')
            INFO('goal_mode changed:', self.pre_goal_mode, '->', self.goal_mode)
        # ゴールモードを記憶
        self.pre_goal_mode = self.goal_mode

    # @brief 指定色の最大領域を検知する
    # @param hsv_img HSV変換後の処理対象画像
    # @param hsv_range_min 検知する色範囲の最小値
    # @param hsv_range_max 検知する色範囲の最大値
    # @param color_name 検知する色の名前
    # @detail
    def colorDetect(self, hsv_img, hsv_range_min, hsv_range_max, color_name):
        mask_0 = np.zeros((480, 480, 1), np.uint8)
        cv2.circle(mask_0, (self.CAMERA_CENTER_CX_T, self.CAMERA_CENTER_CY_T), self.CAMERA_RANGE_R, 255, thickness=-1)

        mask = cv2.inRange(hsv_img, np.array(hsv_range_min), np.array(hsv_range_max))
        mask = cv2.bitwise_and(mask, mask, mask=mask_0)

        # 画角の前後左右と画像表示の上下左右を揃えるために画像を転置する。
        if self.DEBUG_IMSHOW == self.ENABLE:
            cv2.imshow('Mask' + color_name, mask.transpose((1, 0)))

        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        convex_hull_list = []
        for contour in contours:
            approx = cv2.convexHull(contour)

            M = cv2.moments(approx)
            convex_hull_list.append({'approx': approx, 'moment': M})

        if len(convex_hull_list) > 0:
            max_convex_hull = max(convex_hull_list, key=(lambda x: x['moment']['m00']))
            if max_convex_hull['moment']['m00'] > 0:
                area_size = max_convex_hull['moment']['m00']

                cx = int(max_convex_hull['moment']['m10'] / max_convex_hull['moment']['m00'])
                cy = int(max_convex_hull['moment']['m01'] / max_convex_hull['moment']['m00'])

                return cx, cy, area_size, max_convex_hull['approx']
            return -1, -1, 0.0, []
        else:
            return -1, -1, 0.0, []

    # @brief フィールド領域を検知する
    # @param hsv_img HSV変換後の処理対象画像
    # @param hsv_range_min 検知する色範囲の最小値
    # @param hsv_range_max 検知する色範囲の最大値
    # @param color_name 検知する色の名前
    # @detail
    def wallDetect(self, hsv_img, hsv_range_min, hsv_range_max, color_name):
        mask_0 = np.zeros((480, 480, 1), np.uint8)
        cv2.circle(mask_0, (self.CAMERA_CENTER_CX_T, self.CAMERA_CENTER_CY_T), self.CAMERA_RANGE_R, 255,
                   thickness=-1)

        mask = cv2.inRange(hsv_img, np.array(hsv_range_min), np.array(hsv_range_max))
        mask = cv2.bitwise_and(mask, mask, mask=mask_0)
        # TODO: initに移動する
        kernel = np.zeros((self.KARNEL_SIZE, self.KARNEL_SIZE), np.uint8)
        cv2.circle(kernel, (self.KARNEL_R, self.KARNEL_R), self.KARNEL_R, 1, thickness=-1)
        mask = cv2.dilate(mask, kernel, iterations=1)
        TRACE(kernel)
        # 画角の前後左右と画像表示の上下左右を揃えるために画像を転置する。
        cv2.imshow('Mask' + color_name, mask.transpose((1, 0)))
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        convex_hull_list = []
        for contour in contours:
            approx = cv2.convexHull(contour)

            M = cv2.moments(approx)
            convex_hull_list.append({'approx': approx, 'moment': M})

        if len(convex_hull_list) > 0:
            max_convex_hull = max(convex_hull_list, key=(lambda x: x['moment']['m00']))
            if max_convex_hull['moment']['m00'] > 0:
                area_size = max_convex_hull['moment']['m00']

                cx = int(max_convex_hull['moment']['m10'] / max_convex_hull['moment']['m00'])
                cy = int(max_convex_hull['moment']['m01'] / max_convex_hull['moment']['m00'])

                return cx, cy, area_size, max_convex_hull['approx']
            return -1, -1, 0.0, []
        else:
            return -1, -1, 0.0, []

    # @brief 十字マーカーを描画する
    # @param x 十字マーカーのx座標
    # @param y 十字マーカーのy座標
    # @param marker_color 十字マーカーの色
    def draw_marker(self, img, x, y, marker_color):
        cv2.line(img, (x - 7, y), (x + 7, y), color=(255, 255, 255), thickness=2)
        cv2.line(img, (x, y - 7), (x, y + 7), color=(255, 255, 255), thickness=2)
        cv2.line(img, (x - 7, y), (x + 7, y), color=marker_color, thickness=1)
        cv2.line(img, (x, y - 7), (x, y + 7), color=marker_color, thickness=1)

    # @brief 画像処理によって検知した領域からゴールの方向と距離を計算する
    # @param cx 領域のx座標
    # @param cy 領域のy座標
    # @param area_size 領域の面積
    def calcGoalDirection(self, cx, cy, area_size):
        # TODO: cx = -1のときはどうする？
        vx = self.CAMERA_CENTER_CY - cy
        vy = self.CAMERA_CENTER_CX - cx

        try:
            goal_distance = self.GOAL_DISTANCE_TABLE[int(hypot(vx, vy))]
            goal_angle = degrees(atan2(vy, vx))
        except:
            goal_distance = -1
            goal_angle = 360

        return int(goal_angle), int(goal_distance)

    def imageProcessingFrame(self, frame, shmem):
        # HSV色空間に変換
        hsv_img = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        cv2.circle(frame, (self.CAMERA_CENTER_CX_T, self.CAMERA_CENTER_CY_T),
                   self.CAMERA_RANGE_R, (0, 0, 255), thickness=1)
        cv2.line(frame, (self.CAMERA_CENTER_CX_T, 0), (self.CAMERA_CENTER_CX_T, 480),
                 (0, 0, 255), thickness=1)
        cv2.line(frame, (0, self.CAMERA_CENTER_CY_T), (480, self.CAMERA_CENTER_CY_T),
                 (0, 0, 255), thickness=1)
        # 黄色領域の検知
        yellow_cx_t, yellow_cy_t, yellow_area_size, yellow_convex = self.colorDetect(hsv_img, self.YELLOW_HSV_RANGE_MIN,
                                                                                     self.YELLOW_HSV_RANGE_MAX,
                                                                                     'Yellow')
        if yellow_cx_t > -1:
            self.draw_marker(frame, yellow_cx_t, yellow_cy_t, (30, 255, 30))

        # 青色領域の検知
        blue_cx_t, blue_cy_t, blue_area_size, blue_convex = self.colorDetect(hsv_img, self.BLUE_HSV_RANGE_MIN,
                                                                             self.BLUE_HSV_RANGE_MAX,
                                                                             'Blue')
        if blue_cx_t > -1:
            self.draw_marker(frame, blue_cx_t, blue_cy_t, (255, 30, 30))

        # 壁の検知
        wall_cx_t, wall_cy_t, wall_area_size, wall_convex = self.colorDetect(hsv_img, self.WALL_HSV_RANGE_MIN, self.WALL_HSV_RANGE_MAX, 'Wall')

        DEBUG('Yellow :' + str(yellow_area_size).rjust(8), 'Blue :' + str(blue_area_size).rjust(8))

        # 画角の前後左右と画像表示の上下左右を揃えるためにx座標とy座標を交換する。
        yellow_cx = yellow_cy_t
        yellow_cy = yellow_cx_t
        blue_cx = blue_cy_t
        blue_cy = blue_cx_t

        yellow_goal_angle, yellow_goal_distance = self.calcGoalDirection(yellow_cx, yellow_cy, yellow_area_size)
        blue_goal_angle, blue_goal_distance = self.calcGoalDirection(blue_cx, blue_cy, blue_area_size)
        DEBUG('Yellow : Angle=' + str(yellow_goal_angle).rjust(4), 'Dis=' + str(yellow_goal_distance).rjust(3),
              'Blue : Angle=' + str(blue_goal_angle).rjust(4), 'Dis=' + str(blue_goal_distance).rjust(3))

        return yellow_goal_angle, yellow_goal_distance, blue_goal_angle, blue_goal_distance




    # @brief 画像処理のmain処理
    # @param shmem 共有メモリ
    def imageProcessingMain(self, shmem):
        # 画像処理を行う

        with picamera.PiCamera() as camera:
            with picamera.array.PiRGBArray(camera) as stream:
                camera.resolution = (480, 480)
                cap = cv2.VideoCapture('test.avi')

                while cap.isOpened():
                    # 画像を取得し、stream.arrayにRGBの順で映像データを格納
                    camera.capture(stream, 'bgr', use_video_port=True)

                    yellow_goal_angle, yellow_goal_distance, blue_goal_angle, blue_goal_distance = self.imageProcessingFrame(stream.array, shmem)

                    # 結果表示
                    # 画角の前後左右と画像表示の上下左右を揃えるために画像を転置する。

                    if self.DEBUG_IMSHOW == self.ENABLE:
                        cv2.imshow('Frame', stream.array.transpose((1, 0, 2)))
                        cv2.moveWindow('Frame', 0, 30)
                        cv2.moveWindow('MaskYellow', 482, 30)
                        cv2.moveWindow('MaskBlue', 964, 30)
                        cv2.moveWindow('MaskWall', 482, 502)
                    
                    # ゴールモード更新
                    self.setEnemyGoalColorFromFile()
                    
                    # 共有メモリに書き込む
                    if self.enemy_goal_color == EnemyGoalColorE.YELLOW:
                        shmem.enemyGoalAngle = int(yellow_goal_angle)
                        shmem.enemyGoalDis = int(yellow_goal_distance)
                        shmem.myGoalAngle = int(blue_goal_angle)
                        shmem.myGoalDis = int(blue_goal_distance)
                    elif self.enemy_goal_color == EnemyGoalColorE.BLUE:
                        shmem.enemyGoalAngle = int(blue_goal_angle)
                        shmem.enemyGoalDis = int(blue_goal_distance)
                        shmem.myGoalAngle = int(yellow_goal_angle)
                        shmem.myGoalDis = int(yellow_goal_distance)
                    else:
                        ERROR('Invalid Error : ENEMY_GOAL_COLOR =', self.enemy_goal_color)

                    # "q"でウィンドウを閉じる
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        break

                    # streamをリセット
                    stream.seek(0)
                    stream.truncate()
                cv2.destroyAllWindows()

    def target(self, shmem):
        TRACE('imageProcessingMain target() start')
        self.imageProcessingMain(shmem)

    def close():
        pass
