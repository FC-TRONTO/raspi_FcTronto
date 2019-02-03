# coding: UTF-8

import time


class ImageProcessing:
    def __init__(self):
        print 'ImageProcessing generated'


    def imageProcessingMain(self, shmem):
        while 1:
            # 画像処理を行う
            print 'imageProcessingMain'

            # TODO: 画像を取得する
            
            # TODO: ゴールの位置を解析する

            # TODO: 共有メモリに書き込む

            # 1sごとに実行
            time.sleep(1)


    def target(self, shmem):
        print 'imageProcessingMain target() start'
        self.imageProcessingMain(shmem)


    def close():
        pass

