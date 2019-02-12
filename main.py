# coding: UTF-8

from multiprocessing import Process, Value
from ctypes import Structure, c_int
import os
from serialCom import SerialController
from motorContl import MotorController
from imageProcessing import ImageProcessing, EnemyGoalColorE
from debug import ERROR, WARN, INFO, DEBUG, TRACE

# 共有メモリの構造体
class Point(Structure):
    _fields_ = [('irAngle', c_int), ('isTouched', c_int), ('enemyGoalAngle', c_int), ('enemyGoalDis', c_int), ('myGoalAngle', c_int), ('myGoalDis', c_int)]

def info(title):
    INFO(title)
    INFO('module name:', __name__)
    INFO('parent process:', os.getppid())
    INFO('process id:', os.getpid())

# ゴール色文字列からImageProcessing.EnemyGoalEの値に変換する
def getEnemyGoalColorValueFromStr(goal_mode_str):
    if goal_mode_str == 'yellow':
        return EnemyGoalColorE.YELLOW
    elif goal_mode_str == 'blue':
        return EnemyGoalColorE.BLUE
    else:
        return -1

if __name__ == '__main__':
    WORK_DIR = '/home/pi/Desktop/raspi_FcTronto'
    info('main line')
    # 共有メモリの準備
    shmem = Value(Point, 0)
    # シリアル通信制御インスタンスの生成
    serialController = SerialController()
    # モータ制御インスタンスの生成
    motorController = MotorController()
    # 画像処理インスタンスの生成
    imageProcessing = ImageProcessing()

    p_serialCon = Process(target=serialController.target, args=(shmem,))
    p_motorContl = Process(target=motorController.target, args=(shmem, serialController))
    p_imageProcessing = Process(target=imageProcessing.target, args=(shmem,))

    p_serialCon.start()
    DEBUG('p_serialCon started')
    p_motorContl.start()
    DEBUG('p_motorContl started')
    p_imageProcessing.start()
    DEBUG('p_imageProcessing started')

    pre_goal_mode = 'none'
    goal_mode = 'none'
    while 1:
        # ゴールモード設定ファイルを読み込み
        try:
            with open(WORK_DIR + '/webiopi/goal_mode.txt') as f:
                goal_mode = f.read()
        # ファイル読み込み失敗
        except:
            WARN('goal mode file read failure')
        # 前回読み込み時から変更があり、かつ不正な値でなければImageProcessingに通知
        if goal_mode != pre_goal_mode and getEnemyGoalColorValueFromStr(goal_mode) != -1:
            imageProcessing.setEnemyGoalColor(getEnemyGoalColorValueFromStr(goal_mode))
            INFO('goal_mode changed:', pre_goal_mode, '->', goal_mode)
        # ゴールモードを記憶
        pre_goal_mode = goal_mode
        # TODO: 終了処理追加
        # 終了処理は必須ではないが、現状は^C等による強制終了でしか
        # プログラムを停止できない

    p_motorContl.join()
    p_serialCon.join()
    p_imageProcessing.join()

