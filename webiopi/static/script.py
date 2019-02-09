import webiopi
import sys
import os

@webiopi.macro
def start(data):
    # os.systemを使ってmain.pyを実行する
    os.system('python /home/pi/Desktop/raspi_FcTronto/main.py')

@webiopi.macro
def stop(data):
    # os.systemを使ってstop_main_py.shを実行する
    os.system('./stop_main_py.sh')

@webiopi.macro
def set_goal_mode(color):
    with open('/home/pi/Desktop/raspi_FcTronto/webiopi/goal_mode.txt', mode='w') as f:
        if color == 'yellow':
            f.write('yellow')
        elif color == 'blue':
            f.write('blue')
        else:
            f.write('none')

