# -*- coding:utf-8 -*-
from PyQt5.QtCore import *
from PyQt5.QtGui import QPainter, QColor, QPen, QPolygonF
from PyQt5.QtSvg import *
import os
import numpy as np
from GiftBox import GiftBox
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF, renderPM
from RenderCubeNet_ver2 import NPainter
from InputStripeDetail import parameters
import PyPDF2

os.makedirs("./.tmp/", exist_ok=True)


def render_net_real_size(vertical, horizon, high, theta, save_path):
    vertical = float(vertical)
    horizon = float(horizon)
    high = float(high)
    theta = theta * (np.pi / 180)
    g_box = GiftBox(vertical, horizon, high)
    g_box.render(theta)
    dots_list_s = g_box.dots_to_render
    dots_list_ = [[i.x, i.y] for i in dots_list_s]
    minimum_p_s = g_box.getValidPaperSize(theta)  # (w, h)
    svg_gen = QSvgGenerator()
    svg_gen.setFileName(save_path)  # output_file
    # px = x(mm) * dpi / 25.4
    output_p_s = [minimum_p_s[0] * svg_gen.logicalDpiX() / 25.4, minimum_p_s[1] * svg_gen.logicalDpiY() / 25.4]
    svg_gen.setSize(QSize(output_p_s[0], output_p_s[1]))
    # svg_gen.setViewBox(QRect(0, 0, minimum_p_s[0], minimum_p_s[1]))

    dots_list = [[i[0] * svg_gen.logicalDpiX() / 25.4,
                  -i[1] * svg_gen.logicalDpiY() / 25.4 + output_p_s[1]]
                 for i in dots_list_]

    painter = NPainter()
    painter.begin(svg_gen)
    if g_box.isValidThete(theta):  # 未実装
        pen = QPen(QColor(0, 0, 255))
    else:
        pen = QPen(QColor(255, 0, 0))
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
    painter.drawRect(0, 0, output_p_s[0], output_p_s[1])

    painter.end()


def render_stripe_real_size(vertical, horizon, high, s, u, offset, b2s_angle, b_angle, save_path):
    vertical = float(vertical)
    horizon = float(horizon)
    high = float(high)
    s = float(s)
    u = float(u)
    offset = float(offset)
    b_angle = b_angle * (np.pi / 180)
    b2s_angle = b2s_angle * (np.pi / 180)
    colors = parameters.color_set
    g_box = GiftBox(vertical, horizon, high)
    g_box.drawStripe(s, u, offset, b2s_angle, b_angle)
    minimum_p_s = g_box.getValidPaperSize(b_angle)  # (w, h)
    svg_gen = QSvgGenerator()
    svg_gen.setFileName(save_path)
    output_p_s = [minimum_p_s[0] * svg_gen.logicalDpiX() / 25.4, minimum_p_s[1] * svg_gen.logicalDpiY() / 25.4]

    svg_gen.setSize(QSize(output_p_s[0], output_p_s[1]))
    painter = QPainter()
    painter.begin(svg_gen)
    painter.setBrush(QColor(parameters.background_color))
    painter.drawRect(0, 0, output_p_s[0], output_p_s[1])
    painter.setBrush(Qt.NoBrush)
    pen = QPen(QColor(0, 0, 255))
    pen_3 = QPen(QColor(0, 0, 0))
    pen_3.setWidth(1)

    pen.setWidth(2)
    painter.setPen(pen_3)

    painter.drawPoint(20, 20)

    box_corners = g_box.dots_to_render
    g_box_stripe = g_box.result
    dots_list = []
    """for c_point in box_corners:
        # 左右反転用
        # dots_list.append(QPointF(-c_point.x * (render_paper[1] / minimum_p_s[1]) + render_paper[0],
        dots_list.append(QPointF(c_point.x * svg_gen.logicalDpiX() / 25.4,
                                 -c_point.y * svg_gen.logicalDpiX() / 25.4 + output_p_s[1]))
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
    # g.plot(c_point.x, c_point.y, marker='*') """
    painter.setPen(pen)
    c_i = 0
    sg = QPolygonF()
    for unit_stripe_shape in g_box_stripe:
        for unit_stripe_seg in unit_stripe_shape.get():
            s_p = []
            for s_point in unit_stripe_seg.get():
                # 左右反転用
                # sp = QPointF(s_point.x * svg_gen.logicalDpiX() / 25.4,
                sp = QPointF(-s_point.x * svg_gen.logicalDpiX() / 25.4 + output_p_s[0],
                             -s_point.y * svg_gen.logicalDpiY() / 25.4 + output_p_s[1])
                s_p.append(sp)
                # g.plot(s_point.x, s_point.y, marker='o', color=[aaa.r / 255, aaa.g / 255, aaa.b / 255])
            sg = QPolygonF(s_p)
            pen = QPen(Qt.NoPen)
            if not colors:
                painter.setBrush(QColor(unit_stripe_shape.r, unit_stripe_shape.g, unit_stripe_shape.b))
            else:
                print(colors[c_i])
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
    painter.drawRect(0, 0, output_p_s[0], output_p_s[1])

    painter.end()


def render_wrap_paper_and_net_real_size():
    # ######実装する
    pass


def save_svg_to_pdf(vertical, horizon, high, theta, save_path, s=None, u=None, offset=None, b2s_angle=None):
    tmp_svg = "./.tmp/save_pdf_output.svg"
    tmp_pdf = "./.tmp/save_pdf_output.pdf"
    tmp_pdf_w = "./.tmp/save_pdf_output_w.pdf"
    if parameters.all_valid() and s is not None and u is not None and offset is not None and b2s_angle is not None:
        render_net_real_size(vertical, horizon, high, theta, tmp_svg)
        drawing = svg2rlg(tmp_svg)
        renderPDF.drawToFile(drawing, tmp_pdf)
        render_stripe_real_size(vertical, horizon, high, s, u, offset, b2s_angle, theta, tmp_svg)
        drawing = svg2rlg(tmp_svg)
        renderPDF.drawToFile(drawing, tmp_pdf_w)
        merger = PyPDF2.PdfFileMerger()
        merger.append(tmp_pdf)
        merger.append(tmp_pdf_w)
        merger.write(save_path)
        merger.close()
        os.remove(tmp_svg)
        os.remove(tmp_pdf)
        os.remove(tmp_pdf_w)
    else:
        render_net_real_size(vertical, horizon, high, theta, tmp_svg)
        drawing = svg2rlg(tmp_svg)
        renderPDF.drawToFile(drawing, save_path)
        os.remove(tmp_svg)