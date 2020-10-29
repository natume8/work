#!/usr/bin/python3
# -*- coding: utf-8 -*-


import sys
import numpy as np
from PyQt5.QtCore import *
from PyQt5.QtWidgets import (QWidget, QHBoxLayout,
                             QLabel, QApplication)
from PyQt5.QtGui import QPixmap, QIcon, QImage, QPainter, QFont, QColor, QPolygonF, QPen
from PyQt5.QtSvg import *
import cv2
from PIL import Image, ImageDraw
from PIL.ImageQt import ImageQt
import matplotlib.pyplot as plt
import numpy as np
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM, renderPDF

from .GiftBox import GiftBox
from .RenderStripeNet import render_stripe
from .RenderCubeNet import MAX_VERTICAL, MAX_HORIZON
from .InputStripeDetail import parameters



class Example(QWidget):

    def __init__(self):
        super().__init__()

        self.lbl = None
        self.initUI()
        self.A = 150
        self.B = 120
        self.C = 30
        self.theta = 45
        self.giftbox_render()

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
        #canvas.show()
        #im1.show()
        canvas = canvas.resize((int(im1.width * W * rscale), int(im1.height * H * rscale)))
        qim = ImageQt(canvas)
        #pixmap01 = QPixmap.fromImage(qim)
        #lbl.setPixmap(pixmap01)
        #self.imageArea.addWidget(lbl)

    def giftbox_render(self):
        gift_b = GiftBox(self.A, self.B, self.C)
        #gift_b.render(self.theta / 180 * np.pi)
        b_w = 10
        gift_b.draw_continuous_picture(b_w, 10, 5, self.theta / 180 * np.pi, 45 / 180 * np.pi)
        self.create_mask_svg(self.A, self.B, self.C, 10, 10, 10, 45 / 180 * np.pi, 45 / 180 * np.pi)
        #gift = gift_b.dots_to_render
        gift = gift_b.all_stripe
        #print(len(gift))

        o_pattern = Image.open('./pictures/sample.png')
        pattern = o_pattern.resize((10, int(10 * o_pattern.width / o_pattern.height)))
        icount = 15
        main_canvas = Image.new('RGBA', (self.B, self.A), (200, 200, 200))
        draw = ImageDraw.Draw(main_canvas)
        for stripe in gift:
            for seg in stripe.get():
                a = seg.get()
                border = Image.new('RGBA', (pattern.width * icount, pattern.height), (0, 0, 0))
                for i in range(icount):
                    border.paste(pattern, (pattern.width * i, 0))
                border_w = border.rotate(45, center=(0, pattern.height), expand=1)
                a_border = Image.new('RGBA', (border_w.width, border_w.height))
                for x in range(border_w.width):
                    for y in range(border_w.height):
                        pixel = border_w.getpixel((x, y))
                        if pixel != 255 or pixel != 255 or pixel != 255:
                            a_border.putpixel((x, y), pixel)

                print(border.width, border.height)
                main_canvas.paste(a_border, (int(b_w * -np.sin(45 / 180 * np.pi), int(-a[0].y)))
                #print(len(seg.get()))
                #for i, dot in enumerate(seg.get()):
                for dot in seg.get():
                    draw.ellipse((dot.x, -dot.y, dot.x + 3, -dot.y + 3), fill=(stripe.r, stripe.g, stripe.b), outline=(0,0,0))
                    #plt.plot(dot.x, dot.y, color=[stripe.r / 255, stripe.g / 255, stripe.b / 255], marker='.', markersize=15)
                    
                break

        lbl = QLabel(self)
        main_canvas = main_canvas.resize((int(self.B * 4), int(self.A * 4)))
        qim = ImageQt(main_canvas)
        pixmap01 = QPixmap.fromImage(qim)
        lbl.setPixmap(pixmap01)
        self.imageArea.addWidget(lbl)
        ax = plt.gca()
        ax.set_aspect(1)
        #plt.show(block=False)

    def create_mask_svg(self, vertical, horizon, high, s, u, offset, b2s_angle, b_angle):
        vertical = float(vertical)
        horizon = float(horizon)
        high = float(high)
        s = float(s)
        u = float(u)
        offset = float(offset)
        g_box = GiftBox(vertical, horizon, high)
        g_box.draw_continuous_picture(s, u, offset, b2s_angle, b_angle)
        colors = None #parameters.color_set
        minimum_p_s = g_box.get_valid_paper_size(b_angle)  # (w, h)
        w = MAX_HORIZON
        h = MAX_VERTICAL
        if h / w < minimum_p_s[1] / minimum_p_s[0]:
            render_paper = [minimum_p_s[0] * (h / minimum_p_s[1]), h]
        else:
            render_paper = [w, minimum_p_s[1] * (w / minimum_p_s[0])]
        svg_gen = QSvgGenerator()
        svg_gen.setFileName("./.tmp/output_render_wrap.svg")
        svg_gen.setSize(QSize(render_paper[0] + 500, render_paper[1] + 500))
        svg_gen.setViewBox(QRect(0, 0, render_paper[0] + 500, render_paper[1] + 500))
        painter = QPainter()
        painter.begin(svg_gen)
        pen = QPen(QColor(0, 0, 255))

        pen.setWidth(2)

        box_corners = g_box.dots_to_render  
        g_box_stripe = g_box.all_stripe
        dots_list = []

        painter.setPen(pen)
        sg = QPolygonF()
        c_i = 0
        for unit_stripe_shape in g_box_stripe:
            for unit_stripe_seg in unit_stripe_shape.get():
                s_p = []
                for s_point in unit_stripe_seg.get():
                    # 左右反転用
                    # sp = QPointF(s_point.x * (render_paper[1] / minimum_p_s[1]),
                    sp = QPointF(-s_point.x * (render_paper[1] / minimum_p_s[1]) + render_paper[0],
                                 -s_point.y * (render_paper[1] / minimum_p_s[1]) + render_paper[1])
                    s_p.append(sp)
                sg = QPolygonF(s_p)
                pen = QPen(Qt.NoPen)
                if not colors:
                    painter.setBrush(QColor(0, 0, 0))
                else:
                    painter.setBrush(QColor(colors[c_i]))
                painter.setPen(pen)
                # 図形の描画
                painter.drawPolygon(sg, len(sg))
                painter.setBrush(Qt.NoBrush)
            if colors:
                c_i = (c_i + 1) % len(colors)

        pen_2 = QPen(QColor(144, 238, 144))
        pen_2.setWidth(1)
        painter.setPen(pen_2)
        painter.drawRect(0, 0, render_paper[0], render_paper[1])

        pen_3 = QPen(QColor(0, 0, 0))
        pen_3.setWidth(1)
        painter.setPen(pen_3)

        for c_point in box_corners:
            # 左右反転用
            # dots_list.append(QPointF(c_point.x * (render_paper[1] / minimum_p_s[1]),
            dots_list.append(QPointF(-c_point.x * (render_paper[1] / minimum_p_s[1]) + render_paper[0],
                                     -c_point.y * (render_paper[1] / minimum_p_s[1]) + render_paper[1]))
        # 以下，展開図描画
        painter.drawLine(dots_list[0], dots_list[1])
        painter.drawLine(dots_list[1], dots_list[2])
        painter.drawLine(dots_list[2], dots_list[3])
        painter.drawLine(dots_list[3], dots_list[0])
        painter.drawLine(dots_list[0], dots_list[5])
        painter.drawLine(dots_list[4], dots_list[5])
        painter.drawLine(dots_list[4], dots_list[3])
        painter.drawLine(dots_list[3], dots_list[9])
        painter.drawLine(dots_list[4], dots_list[8])
        painter.drawLine(dots_list[9], dots_list[8])
        painter.drawLine(dots_list[9], dots_list[6])
        painter.drawLine(dots_list[6], dots_list[7])
        painter.drawLine(dots_list[7], dots_list[8])
        painter.drawLine(dots_list[8], dots_list[11])
        painter.drawLine(dots_list[11], dots_list[10])
        painter.drawLine(dots_list[10], dots_list[7])
        painter.drawLine(dots_list[6], dots_list[12])
        painter.drawLine(dots_list[12], dots_list[13])
        painter.drawLine(dots_list[13], dots_list[7])

        painter.end()

        mask = svg2rlg("./.tmp/output_render_wrap.svg")
        renderPM.drawToFile(mask, "./.tmp/mask.png", fmt="PNG")

