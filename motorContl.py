# coding: UTF-8

from serialCom import SerialController
import time
from enum import Enum

# ボール保持状態用列挙型
class BallStateE(Enum):
    HAVE_BALL = 0
    NOT_HAVE_BALL = 1

# モータ制御用クラス
class MotorController:
    # ボール保持状態判定閾値
    THRESHOLD_BALL_DETECT = 0.05
    # ボールとの角度からモータ速度変換時の補正値
    CORRECTION_VALUE_ANGLE_TO_SPEED = 5
    # ボールとの距離からモータ速度変換時の補正値
    CORRECTION_VALUE_DISTANCE_TO_SPEED = 100

    # コンストラクタ
    def __init__(self):
        print('MotorController generated')
        # インスタンス変数初期化
        # ドリブル状態に入ったかを記憶する変数
        self.is_dribble_started = False

    # 現在のボール状態を取得する
    def getBallState(self, distance):
        # すでにドリブル状態に入っていた場合
        if self.is_dribble_started:
            # 距離センサの値がinfinityの時もボール保持状態と判断する
            # (距離センサにボールが近づきすぎても値がinifinityになるため)
            if distance < MotorController.THRESHOLD_BALL_DETECT or distance == 100:
                return BallStateE.HAVE_BALL
            else:
                # 距離センサの値が閾値より大きくなっていたらドリブル状態は解除
                self.is_dribble_started = False
                return BallStateE.NOT_HAVE_BALL
        # ドリブル状態に入っていない場合
        else:
            # 距離センサの値が閾値より小さかったらボール保持状態と判断
            # ドリブル状態に入る
            if distance < MotorController.THRESHOLD_BALL_DETECT:
                self.is_dribble_started = True
                return BallStateE.HAVE_BALL
            else:
                return BallStateE.NOT_HAVE_BALL

    # モータの値を計算する
    def calcMotorPowers(self, ballState, angle, distance):
        # ボール保持状態の場合
        if ballState == BallStateE.HAVE_BALL:
            # 前進(仮)
            # 本来は画像処理結果を使ってゴールへ向かう
            return 20, 20
        # ボールなし状態の場合
        else:
            # ボールが正面にある場合
            if angle == 0:
                # 距離センサの値をボールまでの距離としてモータの値を計算
                return getMotorPowerByDistance(distance)
            # ボールが正面にない場合
            else:
                # 絶対値が100を超える場合は100に丸める
                if abs(angle) > 100:
                    angle = angle / abs(angle) * 100
                # モータの値は補正をかける
                speed = angle / MotorController.CORRECTION_VALUE_ANGLE_TO_SPEED
                return (-speed), speed
    
    # モータの値を計算しEV3へ送る
    def calcAndSendMotorPowers(self, shmem, serial):
        while 1:
            # ボール状態取得
            ballState = self.getBallState(shmem.uSonicDis)
            # モータ値計算
            motorPowers = self.calcMotorPowers(ballState, shmem.irAngle, shmem.uSonicDis)
            # 送信伝文生成
            sendText = str(motorPowers[0]) + "," + str(motorPowers[1]) + "\n"
            # モータ値送信
            serial.write(sendText)
            # 0.1sごとに実行
            # 本当は全力でぶん回したい
            # ラズパイ側はマルチプロセスを採用しているので問題ないと思うが
            # EV3側は計算資源を通信に占有される恐れがあるためとりあえず0.1sにしておく
            time.sleep(0.1)
    
    # ボールとの距離からモータの値を計算する
    def getMotorPowerByDistance(distance):
        motorPower = distance * CORRECTION_VALUE_DISTANCE_TO_SPEED
        return motorPower, motorPower
    
    # 起動処理
    def target(self, shmem, serial):
        print('MotorController target() start')
        self.calcAndSendMotorPowers(shmem, serial)

    # 停止処理(仮)
    def close():
        pass
