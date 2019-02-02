# -*- coding: utf8 -*-

import logging
from logging import getLogger, StreamHandler, Formatter

DEBUG_LEVEL_NONE = 0
DEBUG_LEVEL_INFO = 1
DEBUG_LEVEL_DEBUG = 2
DEBUG_LEVEL_TRACE = 3
DEBUG_LEVEL_ALL = 4

# ログ出力のレベルを指定する。
# 指定したレベル以上のログが出力される。
# 例：DEBUG_LEVEL_DEBUG を指定すると、INFOとDEBUGが出力される。
DEBUG_LEVEL = DEBUG_LEVEL_ALL

# ログ出力の初期設定
# todo: 関数化する
logger = getLogger('LogTest')
logger.setLevel(logging.DEBUG)
stream_handler = StreamHandler()
stream_handler.setLevel(logging.DEBUG)
handler_format = Formatter('[%(asctime)s][%(processName)s][%(levelname)s] %(message)s')
stream_handler.setFormatter(handler_format)
logger.addHandler(stream_handler)


def INFO(sentence):
    if DEBUG_LEVEL >= DEBUG_LEVEL_INFO:
        logger.info(sentence)


def DEBUG(sentence):
    if DEBUG_LEVEL >= DEBUG_LEVEL_DEBUG:
        logger.debug(sentence)


def TRACE(sentence):
    if DEBUG_LEVEL >= DEBUG_LEVEL_TRACE:
        logger.debug(sentence)


# main関数
# todo:ファイル分割する
if __name__ == "__main__":
    INFO('info test')
    DEBUG('debug test')
    TRACE('trace test')
