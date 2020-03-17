# -*- coding: utf_8 -*-
import shutil
import sys

import numpy as np
from PyQt5.QtSvg import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QPixmap, QIcon, QImage, QPainter, QFont, QColor, QPolygonF, QPen
from PyQt5.QtWidgets import *
import os.path
from GiftBox import GiftBox
from RenderCubeNet_ver2 import MAX_VERTICAL, MAX_HORIZON
from InputStripeDetail import parameters


def render_stripe(vertical, horizon, high, s, u, offset, b2s_angle, b_angle):
    vertical = float(vertical)
    horizon = float(horizon)
    high = float(high)
    s = float(s)
    u = float(u)
    offset = float(offset)
    g_box = GiftBox(vertical, horizon, high)
    g_box.drawStripe(s, u, offset, b2s_angle, b_angle)
    colors = parameters.color_set
    minimum_p_s = g_box.getValidPaperSize(b_angle)  # (w, h)
    w = MAX_HORIZON
    h = MAX_VERTICAL
    if h / w < minimum_p_s[1] / minimum_p_s[0]:
        render_paper = [minimum_p_s[0] * (h / minimum_p_s[1]), h]
    else:
        render_paper = [w, minimum_p_s[1] * (w / minimum_p_s[0])]
    svg_gen = QSvgGenerator()
    svg_gen.setFileName("./.tmp/output_render_wrap.svg")
    svg_gen.setSize(QSize(render_paper[0], render_paper[1]))
    svg_gen.setViewBox(QRect(0, 0, render_paper[0], render_paper[1]))
    painter = QPainter()
    painter.begin(svg_gen)
    pen = QPen(QColor(0, 0, 255))

    pen.setWidth(2)

    # painter.drawPoint(10, 10)

    box_corners = g_box.dots_to_render
    g_box_stripe = g_box.result
    dots_list = []

    painter.setPen(pen)
    sg = QPolygonF()
    print(colors)
    c_i = 0
    for unit_stripe_shape in g_box_stripe:
        print(type(unit_stripe_shape))
        for unit_stripe_seg in unit_stripe_shape.get():
            s_p = []
            for s_point in unit_stripe_seg.get():
                # 左右反転用
                # sp = QPointF(-s_point.x * (render_paper[1] / minimum_p_s[1]) + render_paper[0],
                sp = QPointF(s_point.x * (render_paper[1] / minimum_p_s[1]),
                             -s_point.y * (render_paper[1] / minimum_p_s[1]) + render_paper[1])
                s_p.append(sp)
            sg = QPolygonF(s_p)
            pen = QPen(Qt.NoPen)
            if not colors:
                painter.setBrush(QColor(unit_stripe_shape.r, unit_stripe_shape.g, unit_stripe_shape.b))
            else:
                print(colors[c_i])
                painter.setBrush(QColor(colors[c_i]))
            print(type(unit_stripe_seg))
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
        # dots_list.append(QPointF(-c_point.x * (render_paper[1] / minimum_p_s[1]) + render_paper[0],
        dots_list.append(QPointF(c_point.x * (render_paper[1] / minimum_p_s[1]),
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
    return g_box


os.makedirs("./.tmp/", exist_ok=True)


class SRenderStripe(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.setWindowTitle('test stripe')
        self.setGeometry(150, 100, 1300, 700)
        # 箱の縦横高さ，線の幅、線の間、オフセット、箱に対するストライプの角度、箱の角度
        # render_stripe(100, 60, 30, 10, 10, 10, 45 / 180 * np.pi, 45 / 180 * np.pi)
        render_stripe(300, 200, 50, 20, 10, 0, 45 / 180 * np.pi, 0.8779006137531478)
        renderer = QSvgRenderer('./.tmp/output_render_wrap.svg')
        w, h = renderer.defaultSize().width(), renderer.defaultSize().height()
        self.view_boxes = QVBoxLayout(self)
        self.lbl = QLabel()
        self.pixmap = QImage(renderer.defaultSize(), QImage.Format_ARGB32_Premultiplied)
        self.pixmap.fill(QColor("white").rgb())
        painter = QPainter(self.pixmap)
        painter.restore()
        renderer.render(painter)
        self.pixmap.scaled(MAX_HORIZON, MAX_VERTICAL)
        self.lbl.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.lbl.setPixmap(QPixmap.fromImage(self.pixmap))
        self.view_boxes.addWidget(self.lbl)

        self.setLayout(self.view_boxes)
        self.show()

    def closeEvent(self, event):
        shutil.rmtree('./.tmp/')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = SRenderStripe()
    w.raise_()
    app.exec_()