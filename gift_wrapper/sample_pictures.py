#!/usr/bin/python3
# -*- coding: utf-8 -*-


import sys
import numpy as np
from PyQt5.QtWidgets import (QWidget, QHBoxLayout,
                             QLabel, QApplication)
from PyQt5.QtGui import QPixmap, QImage, QTransform
import cv2
from PIL import Image
from PIL.ImageQt import ImageQt


class Example(QWidget):

    def __init__(self):
        super().__init__()

        self.lbl = None
        self.initUI()

    def initUI(self):

        self.imageArea = QHBoxLayout(self)
        # QPixmapオブジェクト作成

        # ラベルを作ってその中に画像を置く
        self.gazou()
        self.setLayout(self.imageArea)
        self.move(300, 200)
        self.setWindowTitle('Imoyokan')
        self.show()

    def gazou(self):
        lbl = QLabel(self)
        #cvImg = cv2.imread("./pictures/sample.png")
        #print(cvImg)
        #height, width, channel = cvImg.shape
        #bytesPerLine = 3 * width
        #qImg = QImage(cvImg.data, width, height,
        #              bytesPerLine, QImage.Format_RGB888).rgbSwapped()
        #pixmap01 = QPixmap.fromImage(qImg)
        #trans = QTransform()
        #pixmap0 = 1
        im1 = Image.open('./pictures/sample.png')
        canvas = Image.new('RGB', (im1.width * 6, im1.height), (255, 255, 255))
        for i in range(6):
            canvas.paste(im1, (im1.width * i, 0))
        #im = im.rotate(45, expand=True)
        canvas = canvas.rotate(30.5, expand=True)
        canvas.show()
        #im1.show()
        #qim = ImageQt(canvas)
        #
        #pixmap01 = QPixmap.fromImage(qim)
        #lbl.setPixmap(pixmap01)
        self.imageArea.addWidget(lbl)


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
