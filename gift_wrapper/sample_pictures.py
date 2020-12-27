#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time
import sys
import math
import numpy as np
from PyQt5.QtCore import *
from PyQt5.QtWidgets import (QWidget, QDialog, QHBoxLayout,
                             QLabel, QApplication, QProgressBar)
from PyQt5.QtGui import QPixmap, QIcon, QImage, QPainter, QFont, QColor, QPolygonF, QPen
from PyQt5.QtSvg import *
import cv2
from PIL import Image, ImageDraw, ImageOps
from PIL.ImageQt import ImageQt
import matplotlib.pyplot as plt
import numpy as np
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM, renderPDF

from .GiftBox import GiftBox, Dot
from .RenderStripeNet import render_stripe
from .RenderCubeNet import MAX_VERTICAL, MAX_HORIZON
from .InputStripeDetail import parameters

# parameters = parameters
# parameters.stripe_width = 10
# parameters.stripe_interval_width = 10
# parameters.offset = 5
# parameters.stripe_theta = 45.0
# parameters.background_color = '#FFFFFF'
# parameters.color_set = []
# parameters.image_fname = ""

DPI = 72


def p_dist(dot1, dot2):
    return math.sqrt((dot1.x - dot2.x) ** 2 + (dot1.y - dot2.y) ** 2)


def dint(num):
    if num * 10 % 10 < 5.0:
        return int(num)
    else:
        return int(num) + 1


def calc_diff(pixels1, pixels2):
    diff = 0
    for pixel1, pixel2 in zip(pixels1, pixels2):
        diff += math.sqrt((pixel1[0] - pixel2[0]) ** 2) + math.sqrt(
            (pixel1[1] - pixel2[1]) ** 2) + math.sqrt((pixel1[2] - pixel2[2]) ** 2)
    return diff


def hex2tuple(color16):
    return (int(color16[1:3], 16), int(color16[3:5], 16), int(color16[5:7], 16))


class Actions(QDialog):
    """
    Simple dialog that consists of a Progress Bar and a Button.
    Clicking on the button results in the start of a timer and
    updates the progress bar.
    """

    emit_image = pyqtSignal(int)

    def __init__(self, p_dataset):
        self.para = p_dataset
        self.paper_image = None
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('generating...')
        self.progress = QProgressBar(self)
        self.progress.setGeometry(0, 0, 300, 25)
        self.prog = WrappingCreator(self.para.get()[0:3])
        self.prog.processNum.connect(self.process_start)
        self.prog.emit_image.connect(self.emitImageArea)
        self.prog.countChanged.connect(self.onCountChanged)
        self.show()
        self.prog.start()

    def process_start(self, value):
        self.progress.setMaximum(value + 4)

    def onCountChanged(self, value):
        self.progress.setValue(value)

    def emitImageArea(self, num):
        self.paper_image = self.prog.paper_image
        self.emit_image.emit(0)


class WrappingCreator(QThread):

    processNum = pyqtSignal(int)
    countChanged = pyqtSignal(int)
    emit_image = pyqtSignal(int)

    def __init__(self, data):
        super().__init__()

        self.lbl = None
        self.paper_image = None
        # self.initUI()
        self.A = int(data[0] * DPI / 25.4)
        self.B = int(data[1] * DPI / 25.4)
        self.C = int(data[2] * DPI / 25.4)

        # -----define variable-----
        self.gift_b = GiftBox(self.A, self.B, self.C)
        self.theta = self.gift_b.get_optimal_theta()
        print("wp size theta: ", self.theta)
        self.b_w = int(parameters.stripe_width * DPI / 25.4)
        self.stripe_angle = int(parameters.stripe_theta)
        self.b_interval = int(parameters.stripe_interval_width * DPI / 25.4)
        self.offset = int(parameters.offset * DPI / 25.4)
        self.gift_b.draw_continuous_picture(
            self.b_w, self.b_interval, self.offset, self.theta / 180 * np.pi, self.stripe_angle / 180 * np.pi)
        self.gift = self.gift_b.all_stripe
        self.gift_b.render(self.theta / 180 * np.pi)
        self.renderdots = self.gift_b.dots_to_render
        print("real size dots(design paper): ")
        for ii, gd in enumerate(self.renderdots):
            print(ii, ": ", gd.x, gd.y)
        print()
        # self.giftbox_render()

    def initUI(self):

        # self.imageArea = QHBoxLayout(self)
        # # QPixmapオブジェクト作成

        # # ラベルを作ってその中に画像を置く
        # self.setLayout(self.imageArea)
        # self.move(300, 50)
        # self.setWindowTitle('Imoyokan')
        # self.show()
        pass

    def run(self):
        self.processNum.emit(len(self.gift))
        th_count = 0

        # -----load pattern piece-----

        # separete pattern
        #o_pattern = Image.open('./pictures/picture1_1.png')
        o_pattern = Image.open(parameters.image_fname)
        # contenius pattern
        # o_pattern = Image.open('./pictures/sample2.png')

        # -----shape patterns-----
        pattern = o_pattern.resize(
            (self.b_w, int(self.b_w * o_pattern.width / o_pattern.height)))
        print(pattern.width, pattern.height)
        # ## select side pattern's size
        side_lr_pattern = pattern.resize((int(self.b_w / np.cos(self.stripe_angle / 180 *
                                                                np.pi)),
                                          int(pattern.width * self.b_w / pattern.height / np.cos(self.stripe_angle /
                                                                                                 180 * np.pi))))
        side_tb_pattern = pattern.resize((int(self.b_w / np.sin(self.stripe_angle / 180 *
                                                                np.pi)),
                                          int(pattern.width * self.b_w / pattern.height / np.sin(self.stripe_angle /
                                                                                                 180 * np.pi))))
        # side_lr_pattern = pattern.resize((int(self.b_w),
        #                                  int(pattern.width * self.b_w / pattern.height)))
        # side_tb_pattern = pattern.resize((int(self.b_w),
        #                                  int(pattern.width * self.b_w / pattern.height)))
        s_lr_h = side_lr_pattern.height
        s_tb_h = side_tb_pattern.height

        r_lr_p = side_lr_pattern.crop((side_lr_pattern.width / 2, 0,
                                       side_lr_pattern.width, side_lr_pattern.height))
        r_tb_p = side_tb_pattern.crop((side_tb_pattern.width / 2, 0,
                                       side_tb_pattern.width, side_tb_pattern.height))

        # -----define generating surface-----
        net_image = Image.new('RGBA',
                              (self.B * 3 + self.C * 2, self.A * 2 + self.C * 2),
                              parameters.background_color
                              )
        net_center_i = Image.new(
            'RGBA', (self.B + self.C, self.A + self.C), (200, 200, 200, 0))
        main_s = Image.new('RGBA', (self.B, self.A), (200, 200, 200, 0))
        top_s = Image.new('RGBA', (self.B, int(self.C / 2)),
                          (200, 200, 200, 0))
        bottom_s = Image.new(
            'RGBA', (self.B, int(self.C / 2)), (200, 200, 200, 0))
        left_s = Image.new(
            'RGBA', (int(self.C / 2), self.A), (200, 200, 200, 0))
        right_s = Image.new(
            'RGBA', (int(self.C / 2), self.A), (200, 200, 200, 0))
        th_count += 1
        self.countChanged.emit(th_count)

        # draw = ImageDraw.Draw(main_s)

        # -----iterate proccessing of dots of stripe-----
        for index, stripe in enumerate(self.gift):
            seg = stripe.get()[0]
            seg_dots = seg.get()
            if index == 0:
                seg_dots = [seg_dots[-1]] + seg_dots[:-1:]
            dot1, dot2 = [seg_dots[1], seg_dots[2]] if p_dist(seg_dots[1], seg_dots[2]) > p_dist(
                seg_dots[0], seg_dots[3]) else [seg_dots[0], seg_dots[3]]
            # icount = 30
            icount = int(p_dist(dot1, dot2) // pattern.width + 2)
            # print(seg_dots)
            border = Image.new(
                'RGBA', (pattern.width * icount, pattern.height), (0, 0, 0, 0))
            for i in range(icount):
                border.paste(pattern, (pattern.width * i, 0),
                             pattern.split()[3])
            border_w = border.rotate(
                self.stripe_angle, expand=True, fillcolor=(255, 255, 255))

            # -----create side surface-----
            t_side_seg = list()
            b_side_seg = list()
            l_side_seg = list()
            r_side_seg = list()
            state = self.state_segment(seg_dots)
            if state["top"]:
                t_side_seg = [
                    seg_dots[-1],
                    seg_dots[-2],
                    Dot(seg_dots[-2].x, self.C / 2),
                    Dot(seg_dots[-1].x, self.C / 2)
                ]
            if state["bottom"]:
                if len(seg_dots) == 4:
                    b_side_seg = [
                        Dot(seg_dots[0].x, 0),
                        Dot(seg_dots[1].x, 0),
                        Dot(seg_dots[1].x, self.C / 2),
                        Dot(seg_dots[0].x, self.C / 2),
                    ]
                else:
                    i1, i2 = [1, 2] if seg_dots[1].x == 0 and - \
                        seg_dots[1].y == self.A else [0, 1]
                    b_side_seg = [
                        Dot(seg_dots[i1].x, 0),
                        Dot(seg_dots[i2].x, 0),
                        Dot(seg_dots[i2].x, self.C / 2),
                        Dot(seg_dots[i1].x, self.C / 2),
                    ]
            if state["left"]:
                l_side_seg = [
                    Dot(seg_dots[0].x, -seg_dots[0].y),
                    Dot(seg_dots[1].x, -seg_dots[1].y),
                    Dot(self.C / 2, -seg_dots[1].y),
                    Dot(self.C / 2, -seg_dots[0].y)
                ]
            if state["right"]:
                if len(seg_dots) == 4:
                    r_side_seg = [
                        Dot(0, -seg_dots[-1].y),
                        Dot(0, -seg_dots[-2].y),
                        Dot(self.C / 2, -seg_dots[-2].y),
                        Dot(self.C / 2, -seg_dots[-1].y),
                    ]
                else:
                    i1, i2 = [-2, -3] if seg_dots[-2].x == self.B and seg_dots[-2].y == 0 else [-1, -2]
                    r_side_seg = [
                        Dot(0, -seg_dots[i1].y),
                        Dot(0, -seg_dots[i2].y),
                        Dot(self.C / 2, -seg_dots[i2].y),
                        Dot(self.C / 2, -seg_dots[i1].y),
                    ]

            if t_side_seg != []:    # create top side
                # print(t_side_seg[0].getl(), t_side_seg[1].getl())
                r_p = 0
                for ii in t_side_seg:
                    plt.plot(ii.x, -ii.y + self.C / 2, color="red",
                             marker='.', markersize=7)
                if (t_side_seg[1].x - t_side_seg[0].x) < r_tb_p.height:
                    print(t_side_seg[1].x, t_side_seg[1].y)
                    if t_side_seg[1].x == self.B and t_side_seg[1].y == 0:
                        r_p = t_side_seg[1].x - t_side_seg[0].x
                        # print("r_p", r_p)
                if r_tb_p.width >= self.C / 2:      # 模様の大きさよりCの大きさが小さかったら
                    p_b = r_tb_p.crop((0, r_p, self.C / 2, r_tb_p.height))
                    top_s.paste(p_b.transpose(Image.ROTATE_270),
                                (int(
                                    t_side_seg[0].x + (t_side_seg[1].x - t_side_seg[0].x) / 2 - s_tb_h / 2), 0),
                                p_b.transpose(Image.ROTATE_270).split()[3])
                else:   # 側面に模様が1つより多く並ぶとき
                    count = int((self.C / 2 - r_tb_p.width) //
                                side_tb_pattern.width + 1)
                    side_b = Image.new('RGBA', (int(self.C / 2),
                                                r_tb_p.height), (200, 200, 200, 0))
                    side_b.paste(r_tb_p, (0, 0), r_tb_p.split()[3])
                    for c in range(count):
                        side_b.paste(side_tb_pattern, (r_tb_p.width +
                                                       side_tb_pattern.width * c, 0), side_tb_pattern.split()[3])
                    side_b_r = side_b.transpose(Image.ROTATE_270)
                    s_crop = side_b_r.crop(
                        (0, r_p, side_b_r.width, side_b_r.height))
                    if r_p != 0:
                        top_s.paste(
                            s_crop, (int(t_side_seg[0].x), 0), s_crop.split()[3])
                    else:
                        top_s.paste(
                            s_crop, (int(
                                t_side_seg[0].x + (t_side_seg[1].x - t_side_seg[0].x) / 2 - s_tb_h / 2), 0),
                            s_crop.split()[3])
            if b_side_seg != []:    # create bottom side
                for ii in b_side_seg:
                    plt.plot(ii.x, -ii.y - self.A, color="red",
                             marker='.', markersize=7)

                left_p = 0
                # print([(b.x, b.y)for b in b_side_seg])
                if (b_side_seg[1].x - b_side_seg[0].x) <= r_tb_p.height:
                    if b_side_seg[0].x == 0 and b_side_seg[0].y == 0:
                        left_p = r_tb_p.height - \
                            (b_side_seg[1].x - b_side_seg[0].x)
                    elif b_side_seg[1].x == self.B and b_side_seg[1].y == 0:
                        pass
                    else:
                        pass
                        # print(b_side_seg, r_tb_p.height)
                        # exit("error: bottom side seg is wrong")

                if r_tb_p.width >= self.C / 2:
                    p_b = r_tb_p.crop((left_p, 0, self.C / 2, r_tb_p.height))
                    bottom_s.paste(p_b.transpose(Image.ROTATE_90),
                                   (int(
                                       b_side_seg[0].x + (b_side_seg[1].x - b_side_seg[0].x) / 2 - s_tb_h / 2), 0),
                                   p_b.transpose(Image.ROTATE_90).split()[3])
                else:
                    count = int((self.C / 2 - r_tb_p.width) //
                                side_tb_pattern.width + 1)
                    side_b = Image.new('RGBA', (int(self.C / 2),
                                                r_tb_p.height), (200, 200, 200, 0))
                    side_b.paste(r_tb_p, (0, 0), r_tb_p.split()[3])
                    for c in range(count):
                        side_b.paste(side_tb_pattern, (r_tb_p.width +
                                                       side_tb_pattern.width * c, 0), side_tb_pattern.split()[3])

                    side_b_r = side_b.transpose(Image.ROTATE_90)
                    s_crop = side_b_r.crop(
                        (left_p, 0, side_b_r.width, side_b_r.height))
                    bottom_s.paste(s_crop,
                                   (int(b_side_seg[0].x + (b_side_seg[1].x -
                                                           b_side_seg[0].x) / 2 - s_tb_h / 2), 0),
                                   s_crop.split()[3])

            if l_side_seg != []:    # create left side
                # print(l_side_seg[0].getl(), l_side_seg[1].getl())
                for ii in l_side_seg:
                    plt.plot(ii.x - self.C / 2, -ii.y, color="red",
                             marker='.', markersize=7)
                drawl = ImageDraw.Draw(left_s)
                if l_side_seg[1].y - l_side_seg[0].y < r_lr_p.height:
                    if l_side_seg[1].x == 0 and l_side_seg[1].y == self.A:
                        r_p = l_side_seg[1].y - l_side_seg[0].y
                else:
                    r_p = r_lr_p.height
                if r_lr_p.width >= self.C / 2:
                    p_b = r_lr_p.crop((0, 0, self.C / 2, r_p))
                    left_s.paste(
                        p_b, (0, int(l_side_seg[0].y + (l_side_seg[1].y - l_side_seg[0].y) / 2 - s_lr_h / 2)), p_b.split()[3])
                else:
                    count = int((self.C / 2 - r_lr_p.width) //
                                side_lr_pattern.width + 2)
                    side_b = Image.new('RGBA', (int(self.C / 2),
                                                r_lr_p.height), (200, 200, 200, 0))
                    side_b.paste(r_lr_p, (0, 0), r_lr_p.split()[3])
                    for c in range(count):
                        side_b.paste(side_lr_pattern, (r_lr_p.width +
                                                       side_lr_pattern.width * c, 0), side_lr_pattern.split()[3])
                    s_crop = side_b.crop(
                        (0, 0, side_b.width, r_p))
                    if r_p == l_side_seg[1].y - l_side_seg[0].y:
                        left_s.paste(
                            s_crop, (0, int(l_side_seg[0].y)),
                            s_crop.split()[3])
                    else:
                        left_s.paste(
                            s_crop, (0, int(
                                l_side_seg[0].y + (l_side_seg[1].y - l_side_seg[0].y) / 2 - s_lr_h / 2)),
                            s_crop.split()[3])
            if r_side_seg != []:    # create right side
                for ii in r_side_seg:
                    plt.plot(ii.x + self.B, -ii.y, color="red",
                             marker='.', markersize=7)

                upper_p = 0
                if r_side_seg[1].y - r_side_seg[0].y < r_lr_p.height:
                    if r_side_seg[0].x == 0 and r_side_seg[0].y == 0:
                        upper_p = r_lr_p.height - \
                            (r_side_seg[1].y - r_side_seg[0].y)
                    elif r_side_seg[1].x == self.A and r_side_seg[1].y == 0:
                        pass
                    else:
                        pass
                        # print(r_side_seg, r_lr_p.height)
                        # exit("error: right side seg is wrong")
                if r_lr_p.width >= self.C / 2:
                    p_b = r_lr_p.crop((0, upper_p, self.C / 2, r_lr_p.height))
                    right_s.paste(p_b.transpose(Image.ROTATE_180),
                                  (0, int(
                                      r_side_seg[0].y + (r_side_seg[1].y - r_side_seg[0].y) / 2 - s_lr_h / 2)),
                                  p_b.transpose(Image.ROTATE_180).split()[3])
                else:
                    count = int((self.C / 2 - r_lr_p.width) //
                                side_lr_pattern.width + 1)
                    side_b = Image.new('RGBA', (int(self.C / 2),
                                                r_lr_p.height), (200, 200, 200, 0))
                    side_b.paste(r_lr_p, (0, 0), r_lr_p.split()[3])
                    for c in range(count):
                        side_b.paste(side_lr_pattern, (r_lr_p.width +
                                                       side_lr_pattern.width * c, 0), side_lr_pattern.split()[3])

                    side_b_r = side_b.transpose(Image.ROTATE_180)
                    s_crop = side_b_r.crop(
                        (0, upper_p, side_b_r.width, side_b_r.height))
                    right_s.paste(
                        s_crop,
                        (0, int(
                            r_side_seg[0].y + (r_side_seg[1].y - r_side_seg[0].y) / 2 - s_lr_h / 2)),
                        s_crop.split()[3])

            # print("---")

            x_i = 1 / np.tan(self.stripe_angle / 180 * np.pi)
            diff_l = list()
            # todo: can optimize...
            for w_count in range(int(pattern.width * np.sin(self.stripe_angle / 180 * np.pi))):
                d_main_s = Image.new(
                    'RGBA', (self.B, self.A), (200, 200, 200, 0))
                # -----create main surface to calcurate difference-----
                if seg_dots[1].x == 0 and -seg_dots[1].y == self.A:
                    x_start = int(-(abs(seg_dots[1].y - seg_dots[0].y) * np.cos(
                        self.theta * np.pi / 180) * np.sin(self.theta * np.pi / 180))) - dint(x_i * w_count)
                    y_start = int(self.A - (border_w.height - abs(seg_dots[2].x - seg_dots[1].x) * np.cos(
                        self.theta * np.pi / 180) * np.sin(self.theta * np.pi / 180))) + w_count
                    # print("5 point: ", index, x_start, y_start)
                else:
                    if -seg_dots[1].y != self.A:
                        x_start = int(self.b_w * -np.sin(self.stripe_angle /
                                                         180 * np.pi)) - dint(x_i * w_count)
                        y_start = -int(border_w.height -
                                       (-seg_dots[1].y)) + w_count
                    else:
                        x_start = int(seg_dots[0].x) - dint(x_i * w_count)
                        y_start = self.A - \
                            int(border_w.height - (self.b_w *
                                                   np.cos(self.stripe_angle / 180 * np.pi))) + w_count

                # print("x start, y start: ", x_start, y_start)
                # print("segs: ", seg_dots[1].x, seg_dots[1].y)
                # print(border_w.width, border_w.height)
                for x in range(border_w.width):
                    for y in range(border_w.height):
                        if (0 <= x_start + x and x_start + x < self.B) and (0 <= y_start + y and y_start + y < self.A):
                            # if (x_start + x < self.B) and (y_start + y < self.A):
                            pixel = border_w.getpixel((x, y))
                            # if not (pixel[0] >= 250 and pixel[1] >= 250 and pixel[2] >= 250):
                            if pixel[3] != 0:
                                try:
                                    d_main_s.putpixel(
                                        (x_start + x, y_start + y), pixel)
                                except:
                                    print(sys.exc_info()[0])
                                    print(x_start + x, y_start + y)
                                    exit()
                                # pass

                # -----calcurate difference of pixel-----
                diff = list()
                if state["top"]:
                    diff.append([d_main_s.getpixel((x, 0)) for x in range(
                        int(t_side_seg[1].x) - int(t_side_seg[0].x))])
                    diff.append([top_s.getpixel((x, self.C / 2 - 1))
                                 for x in range(int(t_side_seg[1].x) - int(t_side_seg[0].x))])
                if state["bottom"]:
                    diff.append([d_main_s.getpixel((x, self.A - 1))
                                 for x in range(int(b_side_seg[1].x) - int(b_side_seg[0].x))])
                    diff.append([bottom_s.getpixel((x, 0)) for x in range(
                        int(b_side_seg[1].x) - int(b_side_seg[0].x))])
                if state["left"]:
                    diff.append([d_main_s.getpixel((self.C / 2 - 1, y))
                                 for y in range(int(l_side_seg[1].y) - int(l_side_seg[0].y))])
                    diff.append([left_s.getpixel((0, y)) for y in range(
                        int(l_side_seg[1].y) - int(l_side_seg[0].y))])
                if state["right"]:
                    diff.append([d_main_s.getpixel((self.B - 1, y))
                                 for y in range(int(r_side_seg[1].y) - int(r_side_seg[0].y))])
                    diff.append([right_s.getpixel((0, y)) for y in range(
                        int(r_side_seg[1].y) - int(r_side_seg[0].y))])
                diff_r = 0
                for d_i in range(int(len(diff) / 2)):
                    diff_r += calc_diff(diff[2 * d_i], diff[2 * d_i + 1])
                diff_l.append(diff_r)

            min_i = diff_l.index(min(diff_l))
            if seg_dots[1].x == 0 and -seg_dots[1].y == self.A:
                x_start = int(-(abs(seg_dots[1].y - seg_dots[0].y) * np.cos(
                    self.theta * np.pi / 180) * np.sin(self.theta * np.pi / 180))) - dint(x_i * min_i)
                y_start = int(self.A - (border_w.height - abs(seg_dots[2].x - seg_dots[1].x) * np.cos(
                    self.theta * np.pi / 180) * np.sin(self.theta * np.pi / 180))) + min_i
                # print("5 point: ", index, x_start, y_start)
            else:
                if -seg_dots[1].y != self.A:
                    x_start = int(self.b_w * -np.sin(self.stripe_angle /
                                                     180 * np.pi)) - dint(x_i * min_i)
                    y_start = -int(border_w.height - (-seg_dots[1].y)) + min_i
                else:
                    x_start = int(seg_dots[0].x) - dint(x_i * min_i)
                    y_start = self.A - \
                        int(border_w.height - (self.b_w *
                                               np.cos(self.stripe_angle / 180 * np.pi))) + min_i

            # print("x start, y start: ", x_start, y_start)
            # print("segs: ", seg_dots[1].x, seg_dots[1].y)
            # print("min: ", min_i, diff_l[min_i])

            # -----create main surface-----
            for x in range(border_w.width):
                for y in range(border_w.height):
                    if (0 <= x_start + x and x_start + x < self.B) and (0 <= y_start + y and y_start + y < self.A):
                        # if (x_start + x < self.B) and (y_start + y < self.A):
                        pixel = border_w.getpixel((x, y))
                        if not (pixel[0] >= 250 and pixel[1] >= 250 and pixel[2] >= 250):
                            try:
                                main_s.putpixel(
                                    (x_start + x, y_start + y), pixel)
                            except:
                                print(sys.exc_info()[0])
                                print(x_start + x, y_start + y)
                                exit()

            th_count += 1
            self.countChanged.emit(th_count)

            # -----debug part-----
            i = 0
            # print("create ", index, " / ", len(self.gift), "part")
            for dot in seg.get():
                # print(dot.x, dot.y)
                # draw.ellipse((dot.x -2, -dot.y-2, dot.x + 2, -dot.y + 2), fill=(stripe.r, stripe.g, stripe.b), outline=(0,0,0))
                plt.plot(dot.x, dot.y, color=[
                         stripe.r / 255, stripe.g / 255, stripe.b / 255], marker='.', markersize=7)
                i += 1
            # break
            # break

        # -----create wrapping paper's parts-----
        net_center_i.paste(
            main_s, (int(self.C / 2), int(self.C / 2)), main_s.split()[3])
        net_center_i.paste(top_s, (int(self.C / 2), 0), top_s.split()[3])
        net_center_i.paste(
            bottom_s, (int(self.C / 2), int(self.A + self.C / 2)), bottom_s.split()[3])
        net_center_i.paste(left_s, (0, int(self.C / 2)), left_s.split()[3])
        net_center_i.paste(
            right_s, (int(self.B + self.C / 2), int(self.C / 2)), right_s.split()[3])
        th_count += 1
        self.countChanged.emit(th_count)

        # -----create wrapping paper design-----
        net_left_i = Image.new(
            'RGBA', (int(self.B + self.C / 2), int(self.A + self.C)), (200, 200, 200, 0))
        net_bottom_i = Image.new('RGBA', (int(self.B), int(
            self.A + self.C / 2)), (200, 200, 200, 0))
        net_right_i = Image.new(
            'RGBA', (int(self.B + self.C / 2), int(self.A)), (200, 200, 200, 0))

        net_left_i.paste(top_s.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.FLIP_TOP_BOTTOM), (
            0, 0), top_s.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.FLIP_TOP_BOTTOM).split()[3])
        net_left_i.paste(top_s.transpose(Image.FLIP_LEFT_RIGHT), (0, int(
            self.C / 2)), top_s.transpose(Image.FLIP_LEFT_RIGHT).split()[3])
        net_left_i.paste(main_s.transpose(Image.FLIP_LEFT_RIGHT), (0, int(
            self.C)), main_s.transpose(Image.FLIP_LEFT_RIGHT).split()[3])
        net_left_i.paste(left_s.transpose(Image.FLIP_LEFT_RIGHT), (int(self.B), int(
            self.C)), left_s.transpose(Image.FLIP_LEFT_RIGHT).split()[3])

        net_bottom_i.paste(bottom_s.transpose(Image.FLIP_TOP_BOTTOM),
                           (0, 0), bottom_s.transpose(Image.FLIP_TOP_BOTTOM).split()[3])
        net_bottom_i.paste(main_s.transpose(Image.FLIP_TOP_BOTTOM), (0, int(
            self.C / 2)), main_s.transpose(Image.FLIP_TOP_BOTTOM).split()[3])

        net_right_i.paste(right_s.transpose(Image.FLIP_LEFT_RIGHT),
                          (0, 0), right_s.transpose(Image.FLIP_LEFT_RIGHT).split()[3])
        net_right_i.paste(main_s.transpose(Image.FLIP_LEFT_RIGHT), (int(
            self.C / 2), 0), main_s.transpose(Image.FLIP_LEFT_RIGHT).split()[3])

        net_image.paste(net_center_i,
                        (int(self.B + self.C / 2), int(self.C / 2)),
                        net_center_i.split()[3])
        net_image.paste(net_left_i,
                        (0, 0),
                        net_left_i.split()[3])
        net_image.paste(net_bottom_i,
                        (int(self.B + self.C), int(self.A + self.C * 3 / 2)),
                        net_bottom_i.split()[3])
        net_image.paste(net_right_i,
                        (int(self.B * 2 + self.C * 3 / 2), int(self.C)),
                        net_right_i.split()[3])
        th_count += 1
        self.countChanged.emit(th_count)

        # -----rotate and paste wrapping design to paper-----
        paper_w, paper_h = self.gift_b.get_valid_paper_size(
            self.theta / 180 * np.pi)
        paper = Image.new(
            'RGBA', (int(paper_w), int(paper_h)), parameters.background_color)
        self.rotate_paper(net_image, paper, self.theta)
        th_count += 1
        self.countChanged.emit(th_count)

        # -----view result-----
        # lbl = QLabel(self)
        net_image = net_image.resize((int(self.B * 2), int(self.A * 2)))
        net_image = net_image.resize(
            (int((self.B * 3 + self.C * 2) * 0.8), int((self.A * 2 + self.C * 2) * 0.8)))
        # net_image.show()
        # paper.save("sample_result.png")
        paper = ImageOps.mirror(paper)
        self.paper_image = ImageQt(paper)
        # qim = ImageQt(net_image)
        # pixmap01 = QPixmap.fromImage(qim)
        # lbl.setPixmap(pixmap01)
        # self.imageArea.addWidget(lbl)
        ax = plt.gca()
        ax.set_aspect(1)
        # plt.show(block=True)

        # net_center_i.show()
        self.emit_image.emit(0)

    def rotate_paper(self, net_image, paper, theta1):
        theta_np = theta1 / 180 * np.pi
        beta = self.C / 2
        p = 2 * self.A - 2 * self.B * \
            np.tan(theta_np) + (1 - np.tan(theta_np)) * self.C + beta
        q = p - self.C * np.tan(theta_np)
        l2 = q / 2
        w = (l2 + self.C) * np.sin(theta_np)
        h = p * np.cos(theta_np)
        # paper rotation
        default = np.array([[self.B * 3 / 2], [-self.A]])
        rotate_a = np.array(
            [[np.cos(theta_np), -np.sin(theta_np)], [np.sin(theta_np), np.cos(theta_np)]])

        t_l = rotate_a * \
            np.array([[0 - default[0, 0]], [self.C - default[1, 0]]]) + default
        top_left = Dot(t_l[0, 0], t_l[1, 0])
        t_o = rotate_a * \
            np.array([[0 - default[0, 0]], [0 - default[1, 0]]]) + default
        t_origin = Dot(t_o[0, 0], t_o[1, 0])
        # print("design paper origin: ", t_origin.x, t_origin.y)

        r_image = net_image.rotate(
            theta1, expand=True, fillcolor=hex2tuple(parameters.background_color))
        # r_image_o = Dot(
        #     top_left.x - t_origin.x + w,
        #     -(top_left.y - t_origin.y + net_image.width *
        #       np.sin(theta_np) + h) + paper.height
        # )
        r_image_o = Dot(
            self.renderdots[1].x,
            (-self.renderdots[1].y + paper.height) -
            net_image.width * np.sin(self.theta * np.pi / 180)
        )
        # print("design paper top left: ", top_left.x, top_left.y)

        for x in range(r_image.width):
            for y in range(r_image.height):
                if 0 <= int(r_image_o.x) + x < paper.width and 0 <= int(r_image_o.y) + y < paper.height:
                    pixel = r_image.getpixel((x, y))
                    # if not (pixel[0] >= 250 and pixel[1] >= 250 and pixel[2] >= 250):
                    try:
                        paper.putpixel(
                            (int(r_image_o.x) + x, int(r_image_o.y) + y), pixel)
                    except:
                        print(sys.exc_info()[0])
                        print(paper.width, paper.height)
                        print(r_image_o.x + x, r_image_o.y + y)
                        exit()

    def state_segment(self, dots):
        seg = {"top": False, "bottom": False, "left": False, "right": False}
        if len(dots) == 4:
            if dots[0].x == 0 and dots[1].x == 0:
                seg["left"] = True
            if dots[0].y == -self.A and dots[1].y == -self.A:
                seg["bottom"] = True
            if dots[-1].x == self.B and dots[-2].x == self.B:
                seg["right"] = True
            if dots[-1].y == 0 and dots[-2].y == 0:
                seg["top"] = True
        elif len(dots) >= 5:
            if dots[1].x == 0 and dots[1].y == -self.A:
                seg["left"] = True
                seg["bottom"] = True
                if dots[-1].x == self.B and dots[-2].x == self.B:
                    seg["right"] = True
                if dots[-1].y == 0 and dots[-2].y == 0:
                    seg["top"] = True
            if dots[-2].x == self.B and dots[-2].y == 0:
                seg["right"] = True
                seg["top"] = True
                if dots[0].x == 0 and dots[1].x == 0:
                    seg["left"] = True
                if dots[0].y == -self.A and dots[1].y == -self.A:
                    seg["bottom"] = True

        return seg
