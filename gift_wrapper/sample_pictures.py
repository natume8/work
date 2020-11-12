#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time
import sys
import math
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


def p_dist(dot1, dot2):
    return math.sqrt((dot1.x - dot2.x) ** 2 + (dot1.y - dot2.y) ** 2)        


class Example(QWidget):

    def __init__(self):
        super().__init__()

        self.lbl = None
        self.initUI()
        self.A = int(150 * DPI / 25.4)
        self.B = int(120 * DPI / 25.4)
        self.C = int(30 * DPI / 25.4)
        #self.theta = 45.5
        self.giftbox_render()

    def initUI(self):

        self.imageArea = QHBoxLayout(self)
        # QPixmapオブジェクト作成

        # ラベルを作ってその中に画像を置く
        self.setLayout(self.imageArea)
        self.move(300, 50)
        self.setWindowTitle('Imoyokan')
        self.show()

    def giftbox_render(self):
        gift_b = GiftBox(self.A, self.B, self.C)
        #gift_b.render(self.theta / 180 * np.pi)
        self.theta = gift_b.get_optimal_theta()
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
            seg_dots = seg.get()
            if index == 0:
                dot1, dot2 = [seg_dots[0], seg_dots[1]] if p_dist(seg_dots[0], seg_dots[1]) > p_dist(seg_dots[2], seg_dots[3]) else [seg_dots[2], seg_dots[3]]
            else:
                dot1, dot2 = [seg_dots[1], seg_dots[2]] if p_dist(seg_dots[1], seg_dots[2]) > p_dist(seg_dots[0], seg_dots[3]) else [seg_dots[0], seg_dots[3]]
            #icount = 30
            icount = int(p_dist(dot1, dot2) // pattern.width + 2)
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
        net_left_i = Image.new('RGBA', (int(self.B + self.C / 2), int(self.A + self.C)), (200, 200, 200, 0))
        net_bottom_i = Image.new('RGBA', (int(self.B), int(self.A + self.C / 2)), (200, 200, 200, 0))
        net_right_i = Image.new('RGBA', (int(self.B + self.C / 2), int(self.A)), (200, 200, 200, 0))
        
        net_left_i.paste(top_s.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.FLIP_TOP_BOTTOM), (0, 0), top_s.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.FLIP_TOP_BOTTOM).split()[3])
        net_left_i.paste(top_s.transpose(Image.FLIP_LEFT_RIGHT), (0, int(self.C / 2)), top_s.transpose(Image.FLIP_LEFT_RIGHT).split()[3])
        net_left_i.paste(main_s.transpose(Image.FLIP_LEFT_RIGHT), (0, int(self.C)), main_s.transpose(Image.FLIP_LEFT_RIGHT).split()[3])
        net_left_i.paste(left_s.transpose(Image.FLIP_LEFT_RIGHT), (int(self.B), int(self.C)), left_s.transpose(Image.FLIP_LEFT_RIGHT).split()[3])

        net_bottom_i.paste(bottom_s.transpose(Image.FLIP_TOP_BOTTOM), (0, 0), bottom_s.transpose(Image.FLIP_TOP_BOTTOM).split()[3])
        net_bottom_i.paste(main_s.transpose(Image.FLIP_TOP_BOTTOM), (0, int(self.C / 2)), main_s.transpose(Image.FLIP_TOP_BOTTOM).split()[3])

        net_right_i.paste(right_s.transpose(Image.FLIP_LEFT_RIGHT), (0, 0), right_s.transpose(Image.FLIP_LEFT_RIGHT).split()[3])
        net_right_i.paste(main_s.transpose(Image.FLIP_LEFT_RIGHT), (int(self.C / 2), 0), main_s.transpose(Image.FLIP_LEFT_RIGHT).split()[3])

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

        paper_w, paper_h = gift_b.get_valid_paper_size(self.theta / 180 * np.pi)
        paper = Image.new('RGBA', (int(paper_w), int(paper_h)), (200, 200, 200, 0))
        self.rotate_paper(net_image, paper, self.theta)
                
        lbl = QLabel(self)
        #net_image = net_image.resize((int(self.B * 2), int(self.A * 2)))
        net_image = net_image.resize((int((self.B * 3 + self.C * 2) * 0.8), int((self.A * 2 + self.C * 2) * 0.8)))
        paper.save("sample_result.png")
        qim = ImageQt(paper)
        #qim = ImageQt(net_image)
        pixmap01 = QPixmap.fromImage(qim)
        lbl.setPixmap(pixmap01)
        self.imageArea.addWidget(lbl)
        #ax = plt.gca()
        #ax.set_aspect(1)
        #plt.show(block=False)
        #net_center_i.show()

    def rotate_paper(self, net_image, paper, theta1):
        theta_np = theta1 / 180 * np.pi
        beta = self.C / 2
        p = 2 * self.A - 2 * self.B * np.tan(theta_np) + (1 - np.tan(theta_np)) * self.C + beta
        q = p - self.C * np.tan(theta_np)
        l2 = q / 2
        w = (l2 + self.C) * np.sin(theta_np)
        h = p * np.cos(theta_np)
        ############# paper rotation
        default = np.array([[self.B * 3 / 2], [-self.A]])
        rotate_a = np.array([[np.cos(theta_np), -np.sin(theta_np)], [np.sin(theta_np), np.cos(theta_np)]])

        t_l = rotate_a * np.array([[0 - default[0, 0]], [self.C - default[1, 0]]]) + default
        top_left = Dot(t_l[0, 0], t_l[1, 0])
        t_o = rotate_a * np.array([[0 - default[0, 0]], [0 - default[1, 0]]]) + default
        t_origin = Dot(t_o[0, 0], t_o[1, 0])

        r_image = net_image.rotate(theta1, expand=True)
        r_image_o = Dot(
                top_left.x - t_origin.x + w,
                -(top_left.y - t_origin.y + net_image.width * np.sin(theta_np) + h) + paper.height
                )

        #draw = ImageDraw.Draw(paper)
        #draw.ellipse((int(r_image_o.x - 2), -int(r_image_o.y - 2), int(r_image_o.x + 2), -int(r_image_o.y + 2)), fill=(255, 0, 255), outline=(0,0,0))
        #draw.ellipse((int(r_image_o.x + r_image.width - 2), -int(r_image_o.y - 2), int(r_image_o.x + r_image.width + 2), -int(r_image_o.y + 2)), fill=(255, 0, 255), outline=(0,0,0))
        #plt.plot(r_image_o.x, r_image_o.y, color='blue', marker='.', markersize=10)
        #plt.plot(0, 0, color='red', marker='.', markersize=10)
        #plt.plot(0, paper.height, color='red', marker='.', markersize=10)
        #plt.plot(paper.width, paper.height, color='red', marker='.', markersize=10)
        #plt.plot(paper.width, 0, color='red', marker='.', markersize=10)
        #ax = plt.gca()
        #ax.set_aspect(1)
        #plt.show(block=False)
        
        #paper.paste(r_image, (int(r_image_o.x), int(-r_image_o.y + paper.height)), r_image.split()[3])        
        for x in range(r_image.width):
            for y in range(r_image.height):
                if 0 <= int(r_image_o.x) + x < paper.width and 0 <= int(r_image_o.y) + y < paper.height:
                    pixel = r_image.getpixel((x, y))
                    if not (pixel[0] >= 250 and pixel[1] >= 250 and pixel[2] >= 250):
                        try:
                            paper.putpixel((int(r_image_o.x) + x, int(r_image_o.y) + y), pixel)
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


