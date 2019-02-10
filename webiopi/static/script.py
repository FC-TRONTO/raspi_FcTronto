import webiopi
import sys
import os
import subprocess
from subprocess import Popen

@webiopi.macro
def start(data):
    # os.systemを使ってmain.pyを実行する
    #os.system('python /home/pi/Desktop/raspi_FcTronto/main.py')
    cmd = "python /home/pi/Desktop/raspi_FcTronto/main.py"
    #subprocess.call(cmd.strip().split(" "))
    output_file = '/home/pi/Desktop/raspi_FcTronto/debug.log'
    with open(output_file, 'w') as f:
        Popen(cmd.strip().split(" "), stdout=f)

@webiopi.macro
def stop(data):
    # os.systemを使ってstop_main_py.shを実行する
    #os.system('ps auxww | grep main.py | grep -v grep | awk '{ print "sudo kill -9", $2}' | sh')"
    #subprocess.call("/home/pi/Desktop/raspi_FcTronto/webiopi/static/stop_main_py.sh")
    Popen("/home/pi/Desktop/raspi_FcTronto/webiopi/static/stop_main_py.sh")

@webiopi.macro
def set_goal_mode(color):
    with open('/home/pi/Desktop/raspi_FcTronto/webiopi/goal_mode.txt', mode='w') as f:
        if color == 'yellow':
            f.write('yellow')
        elif color == 'blue':
            f.write('blue')
        else:
            f.write('none')

