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
        H = 2
        W = 6
        rscale = 0.3

        lbl = QLabel(self)
        im1 = Image.open('./pictures/sample.png')
        canvas = Image.new('RGBA', (im1.width * W, im1.height * H), (100, 100, 100))
        for h in range(H):
            row = Image.new('RGBA', (im1.width * W, im1.height), (60, 60, 60))
            for w in range(W):
                row.paste(im1, (im1.width * w, 0))
            canvas.paste(row, (0, im1.height * h))
        #im = im.rotate(45, expand=True)
        #canvas = canvas.rotate(30.5, expand=True)
        canvas.show()
        #im1.show()
        canvas = canvas.resize((int(im1.width * W * rscale), int(im1.height * H * rscale)))
        qim = ImageQt(canvas)
        pixmap01 = QPixmap.fromImage(qim)
        lbl.setPixmap(pixmap01)
        self.imageArea.addWidget(lbl)


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
