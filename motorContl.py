# coding: UTF-8

from serialCom import SerialController
import time
from enum import Enum

class BallStateE(Enum):
    HAVE_BALL = 0
    NOT_HAVE_BALL = 1

class MotorController:
    THRESHOLD_BALL_DETECT = 0.05
    CORRECTION_VALUE_SPEED = 10

    def __init__(self):
        print('MotorController generated')

    # 現在のボール状態を取得する
    def getBallState(self, distance):
        # 距離センサの値が閾値より小さかったらボール保持状態と判断
        if distance < MotorController.THRESHOLD_BALL_DETECT:
            return BallStateE.HAVE_BALL
        else:
            return BallStateE.NOT_HAVE_BALL

    # モータの値を計算する
    def calcMotorPowers(self, ballState, angle):
        # ボール保持状態の場合
        if ballState == BallStateE.HAVE_BALL:
            # 前進(仮)
            return 30, 30
        # ボールなし状態の場合
        else:
            # ボールが正面にある場合
            if angle == 0:
                # 前進(仮)
                return 30, 30
            # ボールが正面にない場合
            else:
                # 絶対値が100を超える場合は100に丸める
                if abs(angle) > 100:
                    angle = angle / abs(angle) * 100
                # モータの値は補正をかける
                speed = angle / MotorController.CORRECTION_VALUE_SPEED
                return (-speed), speed
    
    def calcAndSendMotorPowers(self, shmem, serial):
        while 1:
            # ボール状態取得
            ballState = self.getBallState(shmem.uSonicDis)
            # モータ値計算
            motorPowers = self.calcMotorPowers(ballState, shmem.irAngle)
            # 送信伝文生成
            sendText = str(motorPowers[0]) + "," + str(motorPowers[1]) + "\n"
            # モータ値送信
            serial.write(sendText)
            # 1sごとに実行
            time.sleep(1)
    
    def target(self, shmem, serial):
        print('MotorController target() start')
        self.calcAndSendMotorPowers(shmem, serial)

    def close():
        pass
