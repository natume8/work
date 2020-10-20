#!/usr/bin/python3
# -*- coding: utf-8 -*-


import sys
import numpy as np
from PyQt5.QtWidgets import (QWidget, QHBoxLayout,
                             QLabel, QApplication)
from PyQt5.QtGui import QPixmap, QImage
import cv2


class Example(QWidget):

    def __init__(self):
        super().__init__()

        self.lbl = None
        self.initUI()

    def initUI(self):

        self.hbox = QHBoxLayout(self)
        # QPixmapオブジェクト作成

        # ラベルを作ってその中に画像を置く
        self.gazou()
        self.setLayout(self.hbox)
        self.move(300, 200)
        self.setWindowTitle('Imoyokan')
        self.show()

    def gazou(self):
        cvImg = cv2.imread("./pictures/sample.png")
        print(cvImg)
        height, width, channel = cvImg.shape
        bytesPerLine = 3 * width
        qImg = QImage(cvImg.data, width, height,
                      bytesPerLine, QImage.Format_RGB888).rgbSwapped()
        pixmap01 = QPixmap.fromImage(qImg)
        lbl = QLabel(self)

        lbl.setPixmap(pixmap01)
        self.hbox.addWidget(lbl)


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
