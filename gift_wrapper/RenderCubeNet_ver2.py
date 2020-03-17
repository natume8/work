# -*- coding:utf-8 -*-
import numpy as np
from PyQt5.QtCore import *
from PyQt5.QtGui import QPainter, QFont, QColor, QPen
from PyQt5.QtSvg import *
import os
from GiftBox import GiftBox

default_paper_size = {
    'A4': [297.0, 210.0],
    'A3': [420.0, 297.0],
    'B3': [515.0, 364.0],
    'B4': [364.0, 257.0],
    'B5': [257.0, 182.0]
}

MAX_HORIZON = 800
MAX_VERTICAL = 400

os.makedirs("./.tmp/", exist_ok=True)


class NPainter(QPainter):
    def __init__(self):
        super(NPainter, self).__init__()

    def draw_Line(self, point1, point2):
        self.drawLine(point1[0], point1[1], point2[0], point2[1])


def render_net_no_image(vertical, horizon, high, theta, specify_ps):
    vertical = float(vertical)
    horizon = float(horizon)
    high = float(high)
    theta = theta * (np.pi / 180)
    g_box = GiftBox(vertical, horizon, high)
    minimum_p_s = g_box.getValidPaperSize(theta)   # (w, h)
    g_box.render(theta)
    dots_list_s = g_box.dots_to_render
    dots_list_ = [[i.x, i.y] for i in dots_list_s]
    specify_paper_size = []
    if specify_ps != '指定なし':
        specify_paper_size = default_paper_size[specify_ps]
    w = MAX_HORIZON
    h = MAX_VERTICAL
    if h / w < minimum_p_s[1] / minimum_p_s[0]:
        render_paper = [minimum_p_s[0] * (h / minimum_p_s[1]), h]
    else:
        render_paper = [w, minimum_p_s[1] * (w / minimum_p_s[0])]
    svg_gen = QSvgGenerator()
    svg_gen.setFileName("./.tmp/output_render.svg")
    svg_gen.setSize(QSize(render_paper[0], render_paper[1]))
    svg_gen.setViewBox(QRect(0, 0, render_paper[0], render_paper[1]))

    dots_list = [[i[0] * (render_paper[1] / minimum_p_s[1]),
                  -i[1] * (render_paper[1] / minimum_p_s[1]) + render_paper[1]]
                 for i in dots_list_]

    painter = NPainter()
    painter.begin(svg_gen)
    # thetaが有効 かつ 紙サイズの指定なし or thetaが有効で、最小サイズが指定紙より小さい
    if g_box.isValidThete(theta) and (specify_paper_size == []
                                      or (minimum_p_s[0] < specify_paper_size[0] and minimum_p_s[1] < specify_paper_size[1])):  # True 青
        pen = QPen(QColor(0, 0, 255))
    else:
        pen = QPen(QColor(255, 0, 0))
    # pen = QPen(QColor(255, 0, 0))
    pen_2 = QPen(QColor(144, 238, 144))
    pen.setWidth(3)
    pen_2.setWidth(2)
    painter.setPen(pen)

    painter.draw_Line(dots_list[0], dots_list[1])
    painter.draw_Line(dots_list[1], dots_list[2])
    painter.draw_Line(dots_list[2], dots_list[3])
    painter.draw_Line(dots_list[3], dots_list[0])
    painter.draw_Line(dots_list[0], dots_list[5])
    painter.draw_Line(dots_list[4], dots_list[5])
    painter.draw_Line(dots_list[4], dots_list[3])
    painter.draw_Line(dots_list[3], dots_list[9])
    painter.draw_Line(dots_list[4], dots_list[8])
    painter.draw_Line(dots_list[9], dots_list[8])
    painter.draw_Line(dots_list[9], dots_list[6])
    painter.draw_Line(dots_list[6], dots_list[7])
    painter.draw_Line(dots_list[7], dots_list[8])
    painter.draw_Line(dots_list[8], dots_list[11])
    painter.draw_Line(dots_list[11], dots_list[10])
    painter.draw_Line(dots_list[10], dots_list[7])
    painter.draw_Line(dots_list[6], dots_list[12])
    painter.draw_Line(dots_list[12], dots_list[13])
    painter.draw_Line(dots_list[13], dots_list[7])

    painter.setPen(pen_2)
    painter.drawRect(0, 0, render_paper[0], render_paper[1])

    painter.end()
    return minimum_p_s


def render_net_on_image(vertical, horizon, high, theta, pixmap, specify_ps):
    vertical = float(vertical)
    horizon = float(horizon)
    high = float(high)
    theta = theta * (np.pi / 180)
    g_box = GiftBox(vertical, horizon, high)
    g_box.render(theta)
    dots_list_s = g_box.dots_to_render
    dots_list_ = [[i.x, i.y] for i in dots_list_s]
    minimum_p_s = g_box.getValidPaperSize(theta)  # w, h
    w = pixmap.width()
    h = pixmap.height()
    if h / w < minimum_p_s[1] / minimum_p_s[0]:
        render_paper = [minimum_p_s[0] * (h / minimum_p_s[1]), h]
    else:
        render_paper = [w, minimum_p_s[1] * (w / minimum_p_s[0])]
    if h / w < minimum_p_s[1] / minimum_p_s[0]:
        dots_list = [[-i[0] * (h / minimum_p_s[1]) + render_paper[0], -i[1] * (h / minimum_p_s[1]) + render_paper[1]]
                     for i in dots_list_]
    else:
        dots_list = [[-i[0] * (w / minimum_p_s[0]) + render_paper[0], -i[1] * (w / minimum_p_s[0]) + render_paper[1]]
                     for i in dots_list_]
    svg_gen = QSvgGenerator()
    svg_gen.setFileName("./.tmp/output_render.svg")
    svg_gen.setSize(QSize(render_paper[0], render_paper[1]))
    svg_gen.setViewBox(QRect(0, 0, render_paper[0], render_paper[1]))
    specify_paper_size = []
    if specify_ps != '指定なし':
        specify_paper_size = default_paper_size[specify_ps]
    painter = NPainter()
    painter.begin(svg_gen)
    if g_box.isValidThete(theta) and (specify_paper_size == []
                                      or (minimum_p_s[0] < specify_paper_size[0] and minimum_p_s[1] < specify_paper_size[1])):  # 未実装
        pen = QPen(QColor(0, 0, 255))
    else:
        pen = QPen(QColor(255, 0, 0))
    pen.setWidth(3)
    pen_2 = QPen(QColor(144, 238, 144))
    pen_2.setWidth(2)
    painter.setPen(pen)

    painter.draw_Line(dots_list[0], dots_list[1])
    painter.draw_Line(dots_list[1], dots_list[2])
    painter.draw_Line(dots_list[2], dots_list[3])
    painter.draw_Line(dots_list[3], dots_list[0])
    painter.draw_Line(dots_list[0], dots_list[5])
    painter.draw_Line(dots_list[4], dots_list[5])
    painter.draw_Line(dots_list[4], dots_list[3])
    painter.draw_Line(dots_list[3], dots_list[9])
    painter.draw_Line(dots_list[4], dots_list[8])
    painter.draw_Line(dots_list[9], dots_list[8])
    painter.draw_Line(dots_list[9], dots_list[6])
    painter.draw_Line(dots_list[6], dots_list[7])
    painter.draw_Line(dots_list[7], dots_list[8])
    painter.draw_Line(dots_list[8], dots_list[11])
    painter.draw_Line(dots_list[11], dots_list[10])
    painter.draw_Line(dots_list[10], dots_list[7])
    painter.draw_Line(dots_list[6], dots_list[12])
    painter.draw_Line(dots_list[12], dots_list[13])
    painter.draw_Line(dots_list[13], dots_list[7])

    painter.setPen(pen_2)
    painter.drawRect(0, 0, render_paper[0], render_paper[1])

    painter.end()
    return render_paper, minimum_p_s
