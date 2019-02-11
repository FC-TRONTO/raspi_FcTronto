# coding: UTF-8

from serialCom import SerialController
import time
from enum import Enum
from debug import ERROR, WARN, INFO, DEBUG, TRACE

# ボール保持状態用列挙型
class BallStateE(Enum):
    HAVE_BALL = 0
    NOT_HAVE_BALL = 1

# モータ制御用クラス
class MotorController:
    # モータ制御用パラメータ群
    # ボール保持状態判定閾値
    THRESHOLD_BALL_DETECT = 0.05
    # ボールとの角度からモータ速度変換時の補正値
    CORRECTION_VALUE_BALL_ANGLE_TO_SPEED = 3
    # 敵陣ゴールとの角度からモータ速度変換時の補正値
    CORRECTION_VALUE_EGOAL_ANGLE_TO_SPEED = 3
    # 自陣ゴールとの角度からモータ速度変換時の補正値
    CORRECTION_VALUE_MGOAL_ANGLE_TO_SPEED = 5
    # ボールとの距離からモータ速度変換時の補正値
    CORRECTION_VALUE_DISTANCE_TO_SPEED = 100
    # 距離センサの値がinfinityの時のモータの値
    SPEED_DISTANCE_INFINITE = 30
    # ゴールが正面にある時のモータの値
    SPEED_FRONT_GOAL = 40
    # ボールが正面にある時のモータの値(距離センサを使わない場合のみ使用)
    SPEED_FRONT_BALL = 30
    # どうしようもない時用の値(ゆっくり旋回)
    SPEED_NOTHING_TO_DO = 5, -5

    # コンストラクタ
    def __init__(self):
        DEBUG('MotorController generated')
        # インスタンス変数初期化
        # ドリブル状態に入ったかを記憶する変数
        self.is_dribble_started = False
        # モータ制御後処理インスタンス生成
        self.motorControlPostProcessor = MotorControlPostProcessor()
    
    # 距離センサの値から現在のボール状態を取得する
    def getBallStateByDistance(self, distance):
        # すでにドリブル状態に入っていた場合
        if self.is_dribble_started:
            # 距離センサの値がinfinityの時もボール保持状態と判断する
            # (距離センサにボールが近づきすぎても値がinifinityになるため)
            if distance < MotorController.THRESHOLD_BALL_DETECT or distance == 100:
                return BallStateE.HAVE_BALL
            else:
                # 距離センサの値が閾値より大きくなっていたらドリブル状態は解除
                self.is_dribble_started = False
                DEBUG('dribble END')
                return BallStateE.NOT_HAVE_BALL
        # ドリブル状態に入っていない場合
        else:
            # 距離センサの値が閾値より小さかったらボール保持状態と判断
            # ドリブル状態に入る
            if distance < MotorController.THRESHOLD_BALL_DETECT:
                self.is_dribble_started = True
                DEBUG('dribble START')
                return BallStateE.HAVE_BALL
            else:
                return BallStateE.NOT_HAVE_BALL
    
    # タッチセンサの値から現在のボール状態を取得する
    def getBallStateByTouch(self, isTouched):
        # タッチされてない
        if isTouched == 0:
            TRACE('ball state : not touched')
            return BallStateE.NOT_HAVE_BALL
        # タッチされてる
        elif isTouched == 1:
            TRACE('ball state : touched')
            return BallStateE.HAVE_BALL
        # 不正値
        else:
            WARN('ball state : invalid value (isTouched)')
            return BallStateE.NOT_HAVE_BALL

    # ボールとの距離からモータの値を計算する
    def getMotorPowerByDistance(self, distance):
        # 距離センサの値がinfinityの場合は固定値
        if distance == 100:
            motorPower = MotorController.SPEED_DISTANCE_INFINITE
        else:
            motorPower = int(distance * MotorController.CORRECTION_VALUE_DISTANCE_TO_SPEED)
        return motorPower, motorPower

    # 数値の絶対値を100に丸める
    def roundOffWithin100(self, num):
        if abs(num) > 100:
            return num / abs(num) * 100
        else:
            return num

    # ゴール情報を使ってモータの値を計算する
    def calcMotorPowersByGoalAngle(self, eGoalAngle, mGoalAngle):
        # ゴールが正面にある場合
        if eGoalAngle == 0:
            TRACE('calcMotor patern : enemyGoalAngle = 0')
            # 前進
            return MotorController.SPEED_FRONT_GOAL, MotorController.SPEED_FRONT_GOAL
        # ゴールが正面にない場合
        elif eGoalAngle > -180 and eGoalAngle < 180:
            TRACE('calcMotor patern : -180 < enemyGoalAngle < 180')
            # モータの値は補正をかける
            speed = eGoalAngle / MotorController.CORRECTION_VALUE_EGOAL_ANGLE_TO_SPEED
            # 絶対値が100を超える場合は100に丸める
            speed = self.roundOffWithin100(speed)
            return (-speed), speed
        # ゴールとの角度が不正値の場合
        else:
            # 自分のゴールの角度を使う
            # 自分のゴールとの角度が取れている場合
            if mGoalAngle > -180 and mGoalAngle < 180:
                TRACE('calcMotor patern : -180 < mGoalAngle < 180')
                # とりあえず自軍のゴールの方向に旋回するのは危険そうなので逆に旋回する
                # モータの値は補正をかける
                speed = mGoalAngle / MotorController.CORRECTION_VALUE_MGOAL_ANGLE_TO_SPEED
                # 絶対値が100を超える場合は100に丸める
                speed = self.roundOffWithin100(speed)
                return speed, (-speed)
            # 自分のゴールとの角度も不正値の場合
            else:
                TRACE('calcMotor patern : cannot detect goal')
                # どうしようもない時用の値を使う
                return MotorController.SPEED_NOTHING_TO_DO

    # ボール情報を使ってモータの値を計算する
    def calcMotorPowersByBallAngleAndDis(self, ballAngle, ballDis):
        # ボールが正面にある場合
        if ballAngle == 0:
            TRACE('calcMotor patern : ballAngle = 0')
            # 距離センサの値をボールまでの距離としてモータの値を計算
            return self.getMotorPowerByDistance(ballDis)
        # ボールが正面にない場合
        else:
            TRACE('calcMotor patern : boalAngle != 0')
            # モータの値は補正をかける
            speed = ballAngle / MotorController.CORRECTION_VALUE_BALL_ANGLE_TO_SPEED
            # 絶対値が100を超える場合は100に丸める
            speed = self.roundOffWithin100(speed)
            return (-speed), speed
    
    # ボールとの角度のみを使ってモータの値を計算する
    def calcMotorPowersByBallAngle(self, ballAngle):
        # ボールが正面にある場合
        if ballAngle == 0:
            TRACE('calcMotor patern : ballAngle = 0')
            # モータの値は固定値で前進
            return MotorController.SPEED_FRONT_BALL, MotorController.SPEED_FRONT_BALL
        # ボールが正面にない場合
        else:
            TRACE('calcMotor patern : boalAngle != 0')
            # モータの値は補正をかける
            speed = ballAngle / MotorController.CORRECTION_VALUE_BALL_ANGLE_TO_SPEED
            # 絶対値が100を超える場合は100に丸める
            speed = self.roundOffWithin100(speed)
            return (-speed), speed
    
    # モータの値を計算する
    def calcMotorPowers(self, ballState, shmem):
        # ボール保持状態の場合
        if ballState == BallStateE.HAVE_BALL:
            # 画像処理結果を使ってゴールへ向かう
            return self.calcMotorPowersByGoalAngle(shmem.enemyGoalAngle, shmem.myGoalAngle)

        # ボールなし状態の場合
        else:
            # 赤外線センサと距離センサの情報を使ってボールへ向かう
            #return self.calcMotorPowersByBallAngleAndDis(shmem.irAngle, shmem.uSonicDis)
            # 距離センサは使用しない
            return self.calcMotorPowersByBallAngle(shmem.irAngle)

    # モータの値を計算しEV3へ送る
    def calcAndSendMotorPowers(self, shmem, serial):
        while 1:
            # ボール状態取得
            ballState = self.getBallStateByTouch(shmem.isTouched)
            DEBUG('ballState = ', ballState)
            # モータ値計算
            motorPowers = self.calcMotorPowers(ballState, shmem)
            # モーター値後処理(現在は首振り検知処理のみ)
            motorPowers = self.motorControlPostProcessor.escapeSwing(motorPowers)
            # モータ値記憶
            self.pre_motor_powers = motorPowers
            # 送信伝文生成
            sendText = str(motorPowers[0]) + "," + str(motorPowers[1]) + "\n"
            # モータ値送信
            serial.write(sendText)
            # 0.05sごとに実行
            # 本当は全力でぶん回したい
            # ラズパイ側はマルチプロセスを採用しているので問題ないと思うが
            # EV3側は計算資源を通信に占有される恐れがあるためとりあえず0.05sにしておく
            INFO('ball=' + str(ballState),
                 'motor=' + str(motorPowers[0]).rjust(4) + ',' + str(motorPowers[1]).rjust(4),
                 'touch=' + str(shmem.isTouched).rjust(4),
                 'enemy=' + str(shmem.enemyGoalAngle).rjust(4) + ',' + str(shmem.enemyGoalDis).rjust(4),
                 'my=' + str(shmem.myGoalAngle).rjust(4) + ',' + str(shmem.myGoalDis).rjust(4))
            time.sleep(0.05)
    
    # 起動処理
    def target(self, shmem, serial):
        DEBUG('MotorController target() start')
        self.calcAndSendMotorPowers(shmem, serial)

    # 停止処理(仮)
    def close():
        pass

class MotorControlPostProcessor:
    # モータ制御後処理パラメータ群
    # 首振り検知方向転換間隔閾値[s]、この時間以内に方向転換を繰り返すと首振りと検知する
    THRESHOLD_TIME_SWING_DETECT = 2
    # 首振り検知方向転換回数閾値、この回数以上方向転換を繰り返すと首振りと検知する
    THRESHOLD_COUNT_SWING_DETECT = 3
    # 首振り回避時間[s]、首振り検知したらこの時間分直進する
    TIME_ESCAPE_FROM_SWING = 1
    # 首振り回避の際のモータの値
    SPEED_ESCAPE_FROM_SWING = 5, 5

    def __init__(self):
        # 前回モータ値
        self.pre_motor_powers = 0, 0
        # 前回方向転換時刻(首振り検知用)
        self.pre_direction_change_time = time.time()
        # 首振り検知用方向転換数
        self.count_direction_change_detect_swing = 0
        # 首振り回避状態
        self.is_escaping_swing = False
        # 首振り回避開始時刻
        self.escape_swing_start_time = time.time()
        TRACE('MotorControlPostProcessor generated')

    def escapeSwing(self, motorPowers):
        # 首振り回避する必要がある場合
        if self.isNeedToEscapeSwing(motorPowers):
            TRACE('escape from swing')
            # 首振り回避用のモータ値を返す
            return MotorControlPostProcessor.SPEED_ESCAPE_FROM_SWING
        # 首振り回避する必要がない場合
        else:
            TRACE('not escape from swing')
            # 入力値をそのまま返す
            return motorPowers

    def isNeedToEscapeSwing(self, motorPowers):
        # すでに首振り回避状態に入っている
        if self.is_escaping_swing:
            # 首振り回避開始時からの経過時間が閾値より大きかった場合
            if (time.time() - self.escape_swing_start_time) > MotorControlPostProcessor.TIME_ESCAPE_FROM_SWING:
                # 首振り回避終了
                DEBUG('swing end')
                self.is_escaping_swing = False
                return False
            # 首振り回避開始時から十分時間が経過していない場合
            else:
                # 首振り回避継続
                return True
        # 首振り回避中でない
        else:
            # 首振り開始?
            if self.isSwingStarted(motorPowers):
                # 首振り回避開始
                DEBUG('swing start')
                self.is_escaping_swing = True
                return True
            else:
                # 首振り回避引き続き必要なし
                return False
    
    def isSwingStarted(self, motorPowers):
        # 首振り検知用方向転換数更新
        self.updateCountDerectionChangeDetectSwing(motorPowers)
        # 首振り検知用方向転換数が閾値を超えていたら
        if self.count_direction_change_detect_swing > MotorControlPostProcessor.THRESHOLD_COUNT_SWING_DETECT:
            return True
        else:
            return False
    
    def updateCountDerectionChangeDetectSwing(self, motorPowers):
        # 方向転換した場合
        if motorPowers[0] * self.pre_motor_powers[0] < 0 and motorPowers[1] * self.pre_motor_powers[1] < 0 and motorPowers[0] != motorPowers[1]:
            # 前回方向転換検知時からの経過時間が閾値より小さかった場合
            if (time.time() - self.pre_direction_change_time) > MotorControlPostProcessor.THRESHOLD_TIME_SWING_DETECT:
                TRACE('count_direction_change_detect_swing : increment')
                # 首振り検知用方向転換数をインクリメントする
                self.count_direction_change_detect_swing += 1
            # 前回方向転換検知時から十分時間が経過していた場合
            else:
                TRACE('count_direction_change_detect_swing : reset')
                # 首振り検知用方向転換数をリセット
                self.count_direction_change_detect_swing = 1
            DEBUG('count_derection_change_detect_swing = ', self.count_direction_change_detect_swing)