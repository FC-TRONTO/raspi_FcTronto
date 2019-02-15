import webiopi
import sys
import os
import subprocess
from subprocess import Popen
import ConfigParser

PARAMETER_INI_PATH = '/home/pi/Desktop/raspi_FcTronto/webiopi/parameter.ini'
PARAMETER_CUSTOM_SECTION = 'parameter'

@webiopi.macro
def reboot(data):
    # subprocess.Popenを使ってrebootを実行する
    cmd = "sudo reboot"
    Popen(cmd.strip().split(" "))

@webiopi.macro
def start(data):
    # subprocess.Popenを使ってmain.pyを実行する
    cmd = "python /home/pi/Desktop/raspi_FcTronto/main.py"
    output_file = '/home/pi/Desktop/raspi_FcTronto/debug.log'
    with open(output_file, 'w') as f:
        Popen(cmd.strip().split(" "), stdout=f)

@webiopi.macro
def stop(data):
    # subprocess.Popenを使ってstop_main_py.shを実行する
    Popen("/home/pi/Desktop/raspi_FcTronto/webiopi/static/stop_main_py.sh")

@webiopi.macro
def set_motor_setting(setting):
    read_file_path = os.path.join(os.path.dirname(__file__), '../motor_setting.txt')
    with open(read_file_path, mode='w') as f:
        f.write(setting)

@webiopi.macro
def set_goal_mode(color):
    with open('/home/pi/Desktop/raspi_FcTronto/webiopi/goal_mode.txt', mode='w') as f:
        if color == 'yellow':
            f.write('yellow')
        elif color == 'blue':
            f.write('blue')
        else:
            f.write('none')

@webiopi.macro
def set_shoot_algo(num):
    update_config_file('shoot_algo', num)

@webiopi.macro
def set_chase_algo(num):
    update_config_file('chase_algo', num)

@webiopi.macro
def set_shoot_speed(speed):
    update_config_file('shoot_speed', speed)

@webiopi.macro
def set_k_shoot_angle(k):
    update_config_file('k_shoot_angle', k)

@webiopi.macro
def set_chase_speed(speed):
    update_config_file('chase_speed', speed)

@webiopi.macro
def set_k_chase_angle(k):
    update_config_file('k_chase_angle', k)

@webiopi.macro
def set_go_center(speed):
    update_config_file('center_speed', speed)

@webiopi.macro
def set_k_go_center(k):
    update_config_file('k_center_angle', k)

def update_config_file(key, data):
    # ConfigParser を使って ini ファイルを編集
    config = ConfigParser.ConfigParser()
    config.read(PARAMETER_INI_PATH)
    
    # parameter セクションを編集
    if not config.has_section(PARAMETER_CUSTOM_SECTION):
        config.add_section(PARAMETER_CUSTOM_SECTION)
    
    config.set(PARAMETER_CUSTOM_SECTION, key, data)

    with open(PARAMETER_INI_PATH, 'w') as configfile:
        config.write(configfile)