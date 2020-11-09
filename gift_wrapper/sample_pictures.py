#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time
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

from .GiftBox import GiftBox, Dot
from .RenderStripeNet import render_stripe
from .RenderCubeNet import MAX_VERTICAL, MAX_HORIZON
from .InputStripeDetail import parameters


DPI = 72

class Example(QWidget):

    def __init__(self):
        super().__init__()

        self.lbl = None
        self.initUI()
        self.A = int(150 * DPI / 25.4)
        self.B = int(120 * DPI / 25.4)
        self.C = int(30 * DPI / 25.4)
        self.theta = 45
        self.giftbox_render()

    def initUI(self):

        self.imageArea = QHBoxLayout(self)
        # QPixmapオブジェクト作成

        # ラベルを作ってその中に画像を置く
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
        b_w = int(10 * DPI / 25.4)
        stripe_angle = 45
        b_interval = int(10 * DPI / 25.4)
        offset = int(5 * DPI / 25.4)
        gift_b.draw_continuous_picture(b_w, b_interval, offset, self.theta / 180 * np.pi, stripe_angle / 180 * np.pi)
        #self.create_mask_svg(self.A, self.B, self.C, 10, 10, 10, stripe_angle / 180 * np.pi, 45 / 180 * np.pi)
        #gift = gift_b.dots_to_render
        gift = gift_b.all_stripe
        #print(len(gift))
        
        # load pattern piece
        o_pattern = Image.open('./pictures/sample2.png')
        pattern = o_pattern.resize((b_w, int(b_w * o_pattern.width / o_pattern.height)))
        side_lr_pattern = pattern.resize((int(b_w / np.cos(stripe_angle / 180 *
            np.pi)), 
            int(pattern.width * b_w / pattern.height / np.cos(stripe_angle /
                180 * np.pi))))
        side_tb_pattern = pattern.resize((int(b_w / np.sin(stripe_angle / 180 *
            np.pi)),
            int(pattern.width * b_w / pattern.height / np.sin(stripe_angle /
                180 * np.pi))))
        
        r_lr_p = side_lr_pattern.crop((side_lr_pattern.width / 2, 0, 
            side_lr_pattern.width, side_lr_pattern.height))
        r_tb_p = side_tb_pattern.crop((side_tb_pattern.width / 2, 0,
            side_tb_pattern.width, side_tb_pattern.height))

        # define generating surface
        net_image = Image.new('RGBA', 
                (self.B * 3 + self.C * 2, self.A * 2 + self.C * 2), 
                (200, 200, 200, 0))
        net_center_i = Image.new('RGBA', (self.B + self.C, self.A + self.C), (200, 200, 200, 0))
        main_s = Image.new('RGBA', (self.B, self.A), (200, 200, 200, 0))
        top_s = Image.new('RGBA', (self.B, int(self.C / 2)), (200, 200, 200, 0))
        bottom_s = Image.new('RGBA', (self.B, int(self.C / 2)), (200, 200, 200, 0))
        left_s = Image.new('RGBA', (int(self.C / 2), self.A), (200, 200, 200, 0))
        right_s = Image.new('RGBA', (int(self.C / 2), self.A), (200, 200, 200, 0))

        draw = ImageDraw.Draw(main_s)

        for index, stripe in enumerate(gift):
            seg = stripe.get()[0]
            icount = 30
            seg_dots = seg.get()

            #print(seg_dots)
            border = Image.new('RGBA', (pattern.width * icount, pattern.height), (0, 0, 0, 0))
            for i in range(icount):
                border.paste(pattern, (pattern.width * i, 0), pattern.split()[3])
            border_w = border.rotate(stripe_angle, expand=True, fillcolor=(255, 255, 255))

            # create main surface
            if index == 0:
                x_start = int(b_w * -np.sin(stripe_angle / 180 * np.pi))
                y_start = -int(border_w.height - (-seg_dots[0].y))
            elif -seg_dots[1].y != self.A:
                x_start = int(b_w * -np.sin(stripe_angle / 180 * np.pi))
                y_start = -int(border_w.height - (-seg_dots[1].y))
            else:
                x_start = int(seg_dots[0].x)
                y_start = self.A - int(border_w.height - (b_w * np.cos(stripe_angle)))
             
            #print(x_start, y_start, border_w.width, border_w.height)
            for x in range(border_w.width):
                for y in range(border_w.height):
                    if (0 <= x_start + x and x_start + x < self.B) and (0 <= y_start + y and y_start + y < self.A):
                    #if (x_start + x < self.B) and (y_start + y < self.A):
                        pixel = border_w.getpixel((x, y))
                        if not (pixel[0] >= 250 and pixel[1] >= 250 and pixel[2] >= 250):
                            try:
                                main_s.putpixel((x_start + x, y_start + y), pixel)
                            except:
                                print(sys.exc_info()[0])
                                print(x_start + x, y_start + y)
                                exit()
                            #pass
            
            # create side surface
            t_side_seg = list()
            b_side_seg = list()
            l_side_seg = list()
            r_side_seg = list()
            if index == 0:  # the order is different
                ##### offset not equal zero
                l_side_seg = [
                        Dot(0, -seg_dots[-1].y), 
                        Dot(0, -seg_dots[0].y), 
                        Dot(self.C / 2, -seg_dots[0].y),
                        Dot(self.C / 2, -seg_dots[-1].y)
                        ]
                t_side_seg = [
                        seg_dots[-2], 
                        seg_dots[-3], 
                        Dot(seg_dots[-3].x, self.C / 2), 
                        Dot(seg_dots[-2].x, self.C / 2)
                        ]
                if len(seg_dots) == 5:
                    r_side_seg = [
                            Dot(0, -seg_dots[2].y), 
                            Dot(0, -seg_dots[1].y), 
                            Dot(self.C / 2, -seg_dots[1].y),
                            Dot(self.C / 2, -seg_dots[0].y)
                            ]
                elif len(seg_dots) >= 6:
                    print("stripe index [1] segment is invalid")
            else:
                state = self.state_segment(seg_dots)
                #print("state: ", state)
                #print([[do.x, do.y]for do in seg_dots])
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
                        if seg_dots[1].x == 0 and -seg_dots[1].y == self.A:
                            i1 = 1
                            i2 = 2
                        else:
                            i1 = 0
                            i2 = 1
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
                            Dot(self.C / 2 ,-seg_dots[1].y),
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
                        if seg_dots[-2].x == self.B and seg_dots[-2].y == 0:
                            i1 = -2
                            i2 = -3
                        else:
                            i1 = -1
                            i2 = -2
                        r_side_seg = [
                                Dot(0, -seg_dots[i1].y),
                                Dot(0, -seg_dots[i2].y),
                                Dot(self.C / 2, -seg_dots[i2].y),
                                Dot(self.C / 2, -seg_dots[i1].y),
                                ]
            
            if t_side_seg != []:
                if r_tb_p.width >= self.C / 2:
                    p_b = r_tb_p.crop((0, 0, self.C / 2, r_tb_p.height))
                    top_s.paste(p_b.transpose(Image.ROTATE_270), 
                            (int(t_side_seg[0].x), 0), 
                            p_b.transpose(Image.ROTATE_270).split()[3])
                else:
                    count = int((self.C / 2 - r_tb_p.width) // side_tb_pattern.width + 1)
                    side_b = Image.new('RGBA', (int(self.C / 2),
                        r_tb_p.height), (200, 200, 200, 0))
                    side_b.paste(r_tb_p, (0, 0), r_tb_p.split()[3])
                    for c in range(count):
                        side_b.paste(side_tb_pattern, (r_tb_p.width +
                            side_tb_pattern.width * c, 0), side_tb_pattern.split()[3])
                    side_b_r = side_b.transpose(Image.ROTATE_270)
                    top_s.paste(side_b_r, (int(t_side_seg[0].x), 0), side_b_r.split()[3])
                #plt.plot(dot.x - self.C / 2, -dot.y, color='red', marker='.', markersize=10)
            if b_side_seg != []:
                if r_tb_p.width >= self.C / 2:
                    p_b = r_tb_p.crop((0, 0, self.C / 2, r_tb_p.height))
                    bottom_s.paste(p_b.transpose(Image.ROTATE_90), 
                            (int(b_side_seg[0].x), 0), 
                            p_b.transpose(Image.ROTATE_90).split()[3])
                else:
                    count = int((self.C / 2 - r_tb_p.width) // side_tb_pattern.width + 1)
                    side_b = Image.new('RGBA', (int(self.C / 2),
                        r_tb_p.height), (200, 200, 200, 0))
                    side_b.paste(r_tb_p, (0, 0), r_tb_p.split()[3])
                    for c in range(count):
                        side_b.paste(side_tb_pattern, (r_tb_p.width +
                            side_tb_pattern.width * c, 0), side_tb_pattern.split()[3])

                    side_b_r = side_b.transpose(Image.ROTATE_90)
                    bottom_s.paste(side_b_r, (int(b_side_seg[0].x), 0), side_b_r.split()[3])
                    #plt.plot(dot.x, -dot.y - self.A, color='red', marker='.', markersize=10)
            if l_side_seg != []: ## ok
                drawl = ImageDraw.Draw(left_s)
                #for dot in l_side_seg:
                if r_lr_p.width >= self.C / 2:
                    p_b = r_lr_p.crop((0, 0, self.C / 2, r_lr_p.height))
                    left_s.paste(p_b, (0, int(l_side_seg[0].y)), p_b.split()[3])
                else:
                    count = int((self.C / 2 - r_lr_p.width) // side_lr_pattern.width + 2)
                    side_b = Image.new('RGBA', (int(self.C / 2),
                        r_lr_p.height), (200, 200, 200, 0))
                    side_b.paste(r_lr_p, (0, 0), r_lr_p.split()[3])
                    for c in range(count):
                        side_b.paste(side_lr_pattern, (r_lr_p.width +
                            side_lr_pattern.width * c, 0), side_lr_pattern.split()[3])
                    left_s.paste(side_b, (0, int(l_side_seg[0].y)), side_b.split()[3])
                #plt.plot(dot.x - self.C / 2, -dot.y, color='red', marker='.', markersize=10)
                #pass
            if r_side_seg != []:
                if r_lr_p.width >= self.C / 2:
                    p_b = r_lr_p.crop((0, 0, self.C / 2, r_lr_p.height))
                    right_s.paste(p_b.transpose(Image.ROTATE_180), 
                            (0, int(r_side_seg[0].y)), 
                            p_b.transpose(Image.ROTATE_180).split()[3])
                else:
                    count = int((self.C / 2 - r_lr_p.width) // side_lr_pattern.width + 1)
                    side_b = Image.new('RGBA', (int(self.C / 2),
                        r_lr_p.height), (200, 200, 200, 0))
                    side_b.paste(r_lr_p, (0, 0), r_lr_p.split()[3])
                    for c in range(count):
                        side_b.paste(side_lr_pattern, (r_lr_p.width +
                            side_lr_pattern.width * c, 0), side_lr_pattern.split()[3])

                    side_b_r = side_b.transpose(Image.ROTATE_180)
                    right_s.paste(side_b_r, (0, int(r_side_seg[0].y)), side_b_r.split()[3])

                #plt.plot(dot.x + self.B, -dot.y, color='red', marker='.', markersize=10)
                #pass

            net_center_i.paste(main_s, (int(self.C / 2), int(self.C / 2)), main_s.split()[3])
            net_center_i.paste(top_s, (int(self.C / 2), 0), top_s.split()[3])
            net_center_i.paste(bottom_s, (int(self.C / 2), int(self.A + self.C / 2)), bottom_s.split()[3])
            net_center_i.paste(left_s, (0, int(self.C / 2)), left_s.split()[3])
            net_center_i.paste(right_s, (int(self.B + self.C / 2), int(self.C / 2)), right_s.split()[3])
            i = 0  ## debug
            for dot in seg.get():
                #print(dot.x, dot.y)
                #if i == 1:
                #    draw.ellipse((dot.x -2, -dot.y-2, dot.x + 2, -dot.y + 2), fill=(255, 0, 255), outline=(0,0,0))
                #else:
                #    draw.ellipse((dot.x -2, -dot.y-2, dot.x + 2, -dot.y + 2), fill=(stripe.r, stripe.g, stripe.b), outline=(0,0,0))
                #plt.plot(dot.x, dot.y, color=[stripe.r / 255, stripe.g / 255, stripe.b / 255], marker='.', markersize=15)
                i += 1
            #break
            #break
        
        # center
        net_image.paste(net_center_i, 
                (int(self.B + self.C / 2), int(self.C / 2)), 
                net_center_i.split()[3])
        net_image.paste(net_center_i, 
                (int(self.B + self.C / 2), int(self.C / 2)), 
                net_center_i.split()[3])
        net_image.paste(net_center_i, 
                (int(self.B + self.C / 2), int(self.C / 2)), 
                net_center_i.split()[3])
        net_image.paste(net_center_i, 
                (int(self.B + self.C / 2), int(self.C / 2)), 
                net_center_i.split()[3])
        net_image.paste(net_center_i, 
                (int(self.B + self.C / 2), int(self.C / 2)), 
                net_center_i.split()[3])
        net_image.paste(net_center_i, 
                (int(self.B + self.C / 2), int(self.C / 2)), 
                net_center_i.split()[3])
        net_image.paste(net_center_i, 
                (int(self.B + self.C / 2), int(self.C / 2)), 
                net_center_i.split()[3])
        net_image.paste(net_center_i, 
                (int(self.B + self.C / 2), int(self.C / 2)), 
                net_center_i.split()[3])
        
        lbl = QLabel(self)
        net_image = net_image.resize((int(self.B * 1), int(self.A * 1)))
        qim = ImageQt(net_image)
        pixmap01 = QPixmap.fromImage(qim)
        lbl.setPixmap(pixmap01)
        self.imageArea.addWidget(lbl)
        ax = plt.gca()
        ax.set_aspect(1)
        #plt.show(block=False)
        #net_center_i.show()

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

