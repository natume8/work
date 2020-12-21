# -*- coding:utf-8 -*-
import os
import io

import numpy as np
from PyQt5.QtCore import *
from PyQt5.QtGui import QPainter, QColor, QPen, QPolygonF, QImage, QPixmap
from PyQt5.QtSvg import *
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF, renderPM
import PyPDF2
import img2pdf
from PIL import Image

from .GiftBox import GiftBox
from .RenderCubeNet import NPainter
from .InputStripeDetail import parameters

os.makedirs("./.tmp/", exist_ok=True)


def render_net_real_size(vertical, horizon, high, theta, save_path, flag=0):
    vertical = float(vertical)
    horizon = float(horizon)
    high = float(high)
    g_box = GiftBox(vertical, horizon, high)
    if flag == 0:
        theta = theta * (np.pi / 180)
    else:
        theta = g_box.get_optimal_theta() * (np.pi / 180)
    g_box.render(theta)
    dots_list_s = g_box.dots_to_render
    dots_list_ = [[i.x, i.y] for i in dots_list_s]
    minimum_p_s = g_box.get_valid_paper_size(theta)  # (w, h)
    svg_gen = QSvgGenerator()
    svg_gen.setFileName(save_path)  # output_file
    # px = x(mm) * dpi / 25.4
    output_p_s = [minimum_p_s[0] * svg_gen.logicalDpiX() / 25.4,
                  minimum_p_s[1] * svg_gen.logicalDpiY() / 25.4]
    svg_gen.setSize(QSize(output_p_s[0], output_p_s[1]))
    # svg_gen.setViewBox(QRect(0, 0, minimum_p_s[0], minimum_p_s[1]))

    dots_list = [[i[0] * svg_gen.logicalDpiX() / 25.4,
                  -i[1] * svg_gen.logicalDpiY() / 25.4 + output_p_s[1]]
                 for i in dots_list_]

    painter = NPainter()
    painter.begin(svg_gen)
    if g_box.is_valid_theta(theta):  # 未実装
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
    print("output: ", output_p_s)
    print("DPI: ", svg_gen.logicalDpiX())
    return minimum_p_s


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
    g_box.draw_stripe(s, u, offset, b2s_angle, b_angle)
    minimum_p_s = g_box.get_valid_paper_size(b_angle)  # (w, h)
    svg_gen = QSvgGenerator()
    svg_gen.setFileName(save_path)
    output_p_s = [minimum_p_s[0] * svg_gen.logicalDpiX() / 25.4,
                  minimum_p_s[1] * svg_gen.logicalDpiY() / 25.4]

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

    g_box_stripe = g_box.all_stripe

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
                painter.setBrush(QColor(unit_stripe_shape.r,
                                        unit_stripe_shape.g, unit_stripe_shape.b))
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
    painter.drawRect(0, 0, output_p_s[0], output_p_s[1])

    painter.end()


# pixmap_pは展開図, g_pathは保存する画像のパス
def save_wrap_paper(w, h, pw, ph, scaled_v, g_path, out_w, out_h):
    [w, h, pw, ph] = [i * scaled_v for i in [w, h, pw, ph]]

    im = Image.open(g_path[0])
    if 'dpi' in im.info:
        im_dpi = im.info['dpi']
    else:
        im_dpi = (300, 300)

    im_crop = im.crop((w, h, w + pw + 0.1, h + ph + 0.1))
    [out_w, out_h] = [i * im_dpi[0] / 25.4 for i in [out_w, out_h]]
    im_crop_resize = im_crop.resize((int(out_w), int(out_h)))
    im_crop_resize.save(".tmp/save_wrap_paper.png", dpi=(im_dpi[0], im_dpi[1]))


def render_wrap_paper_and_net_real_size(vertical, horizon, high, theta, save_path, g_path,
                                        w, h, pw, ph, scaled):
    tmp_box = ".tmp/save_box.svg"
    tmp_box_pdf = ".tmp/save_box.pdf"
    tmp_wrap_pdf = ".tmp/save_wrap.pdf"
    out = render_net_real_size(vertical, horizon, high, theta, tmp_box)
    save_wrap_paper(w, h, pw, ph, scaled, g_path, out[0], out[1])
    drawing = svg2rlg(tmp_box)
    renderPDF.drawToFile(drawing, tmp_box_pdf)
    try:
        with open(tmp_wrap_pdf, "wb") as f:
            f.write(img2pdf.convert(".tmp/save_wrap_paper.png"))
    except OSError:
        print("file is Opening")
    merger = PyPDF2.PdfFileMerger()
    merger.append(tmp_box_pdf)
    merger.append(tmp_wrap_pdf)
    merger.write(save_path)
    merger.close()
    os.remove(tmp_box)
    os.remove(tmp_box_pdf)
    os.remove(tmp_wrap_pdf)
    os.remove(".tmp/save_wrap_paper.png")


def render_wp_image_net_real_size(vertical, horizon, high, theta, save_path, simage):
    tmp_box = ".tmp/save_box.svg"
    tmp_box_pdf = ".tmp/save_box.pdf"
    tmp_wrap_pdf = ".tmp/save_wrap.pdf"
    out = render_net_real_size(vertical, horizon, high, theta, tmp_box, flag=1)
    buffer = QBuffer()
    buffer.open(QBuffer.ReadWrite)
    simage.save(buffer, "PNG")
    pil_im = Image.open(io.BytesIO(buffer.data()))
    pil_im = pil_im.convert("RGB")
    print("pil size: ", pil_im.size)
    pil_im.save(".tmp/save_wrap_paper.png")

    drawing = svg2rlg(tmp_box)
    renderPDF.drawToFile(drawing, tmp_box_pdf)
    output_s = (img2pdf.mm_to_pt(out[0]), img2pdf.mm_to_pt(out[1]))
    layout_fun = img2pdf.get_layout_fun(output_s)
    print("saved: ", Image.open(".tmp/save_wrap_paper.png").size)
    try:
        with open(tmp_wrap_pdf, "wb") as f:
            f.write(img2pdf.convert(
                ".tmp/save_wrap_paper.png", layout_fun=layout_fun))
    except OSError:
        print("file is Opening")
    merger = PyPDF2.PdfFileMerger()
    merger.append(tmp_box_pdf)
    merger.append(tmp_wrap_pdf)
    merger.write(save_path)
    merger.close()
    os.remove(tmp_box)
    os.remove(tmp_box_pdf)
    os.remove(tmp_wrap_pdf)
    os.remove(".tmp/save_wrap_paper.png")


def save_svg_to_pdf(vertical, horizon, high, theta, save_path, s=None, u=None, offset=None, b2s_angle=None):
    tmp_svg = "./.tmp/save_pdf_output.svg"
    tmp_pdf = "./.tmp/save_pdf_output.pdf"
    tmp_pdf_w = "./.tmp/save_pdf_output_w.pdf"
    if parameters.all_valid() and s is not None and u is not None and offset is not None and b2s_angle is not None:
        render_net_real_size(vertical, horizon, high, theta, tmp_svg)
        drawing = svg2rlg(tmp_svg)
        renderPDF.drawToFile(drawing, tmp_pdf)
        render_stripe_real_size(vertical, horizon, high,
                                s, u, offset, b2s_angle, theta, tmp_svg)
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
