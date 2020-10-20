# -*- coding:utf-8 -*-

import shutil
import sys
import numpy as np

from PyQt5.QtSvg import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QPixmap, QIcon, QImage, QPainter, QFont, QColor
from PyQt5.QtWidgets import *

from .InputStripeDetail import SetDetailWindow, parameters
from .GiftBox import GiftBox
from .RenderCubeNet import render_net_on_image, render_net_no_image, MAX_HORIZON, MAX_VERTICAL
from .RenderStripeNet import render_stripe
from .Save2DGraphicsInterface import (render_net_real_size,
                                      render_stripe_real_size,
                                      render_wrap_paper_and_net_real_size,
                                      save_svg_to_pdf)

SHOKI_GAZO = ""

default_paper_size = {
    'A4': [297.0, 210.0],
    'A3': [420.0, 297.0],
    'B3': [515.0, 364.0],
    'B4': [364.0, 257.0],
    'B5': [257.0, 182.0]
}


class GWMainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(GWMainWindow, self).__init__(parent)
        dq = QDesktopWidget().availableGeometry()
        self.resize(1200, dq.size().height() - 50)
        self.form_widget = GiftWrapperForm(self)
        self.fname = None
        self.initUI()
        self.setCentralWidget(self.form_widget)
        self.center_frame()
        self.setWindowTitle('Main')
        self.show()

    def initUI(self):
        # status bar
        self.statusBar()
        openFile = QAction(QIcon(SHOKI_GAZO), '画像読み込み', self)
        # ショートカット設定
        openFile.setShortcut('Ctrl+O')
        # ステータスバー設定
        openFile.setStatusTip('フォルダにある画像を開いて読み込みます')
        openFile.triggered.connect(self.show_file_Dialog)

        saveImage = QAction('画像を保存', self)
        saveImage.setShortcut('Ctrl+s')
        saveImage.setStatusTip('画像をpdfまたはsvgで出力します')
        saveImage.triggered.connect(self.show_filesave_dialog)

        # メニューバー作成
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&ファイル')
        fileMenu.addAction(openFile)
        fileMenu.addAction(saveImage)

    def center_frame(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry()
        cp.setTopLeft(QPoint(cp.left(), cp.top() - 50))

        qr.moveCenter(cp.center())
        self.move(qr.topLeft())

    def show_file_Dialog(self):
        permitted_format = ["jpg", "png", "bpm", "gif", "tif", "jpeg"]
        op = QMessageBox.Ok
        if self.form_widget.exec_flag:
            op = QMessageBox.warning(
                self, "警告！", "展開図がリセットされます", QMessageBox.Ok, QMessageBox.No)
        if op == QMessageBox.Ok:
            self.fname = QFileDialog.getOpenFileName(self, '画像を開く', '/home')
            if self.fname[0].split(".")[-1].lower() in permitted_format:
                self.form_widget.draw_pict(self.fname[0])
                self.form_widget.exec_flag = False
            elif self.fname[0] == "":
                pass
            else:
                QMessageBox.warning(
                    self, "エラー！", "対応していない拡張子です\n(jpg, png, gif を推奨)", QMessageBox.Ok, QMessageBox.Ok)

    def show_filesave_dialog(self):
        # ディレクトリ選択ダイアログを表示
        if self.form_widget.g_w_can_hover:
            path = QFileDialog.getSaveFileName(
                self, '名前を付けて保存', '/home', 'pdf(*.pdf)')
            if path[0] != "":
                self.form_widget.save_wrap_pdf(path[0], self.fname)
        else:
            path = QFileDialog.getSaveFileName(
                self, '名前を付けて保存', '/home', 'svg(*.svg);;pdf(*.pdf)')
            if path[0] != "":
                self.form_widget.save_svg_graphic(path[0])

    def closeEvent(self, event):
        self.form_widget.d_w.close()
        shutil.rmtree('./.tmp/')


class GiftWrapperForm(QWidget):
    def __init__(self, parent):
        super(GiftWrapperForm, self).__init__(parent)
        self.exec_flag = False
        self.g_exec_flag = False
        self.s_exec_flag = False
        self.g_w_can_hover = False
        self.lastPoint = None
        self.scribbling = False
        self.b_x = 0
        self.b_y = 0
        self.m_x = 0
        self.m_y = 0
        self.magnification = 1
        self.giftbox = None
        self.b_theta = None
        self.initUI()

    def initUI(self):
        quit = QAction("Quit", self)
        quit.triggered.connect(self.close)

        self.vLay = QGridLayout(self)
        self.vLay.setContentsMargins(10, 10, 10, 10)
        self.vLay.setSpacing(20)
        self.inputLayout = QVBoxLayout(self)
        self.vMenuT = QGroupBox('メニュー')
        self.vMenu = QVBoxLayout(self)
        self.vMenu.setSpacing(13)
        self.vMenu.setContentsMargins(10, 10, 10, 10)
        self.vMenu.setSizeConstraint(QLayout.SetFixedSize)
        # self.vMenu.setSpacing(10)
        self.frameMenu = QFrame()
        self.frameMenu.setFrameShape(QFrame.Box)
        self.frameDraw = QFrame()
        self.frameDraw.setFrameShape(QFrame.Box)

        # ############3辺の入力
        title = QLabel('包装する箱の大きさ')
        title.setFont(QFont("Times", weight=QFont.Bold))
        title.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        ve = QLabel('  縦 (mm)')
        ve.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        ho = QLabel('  横 (mm)')
        ho.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        hi = QLabel('高さ (mm)')
        hi.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.inputVertical = QLineEdit()
        self.inputVertical.returnPressed.connect(self.call_function)
        self.inputVertical.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.inputHorizon = QLineEdit()
        self.inputHorizon.returnPressed.connect(self.call_function)
        self.inputHorizon.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.inputHigh = QLineEdit()
        self.inputHigh.returnPressed.connect(self.call_function)
        self.inputHigh.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.input_values = QGridLayout(self)
        self.input_values.addWidget(ve, 1, 1, 1, 1)
        self.input_values.addWidget(self.inputVertical, 1, 2, 1, 1)
        self.input_values.addWidget(ho, 2, 1, 1, 1)
        self.input_values.addWidget(self.inputHorizon, 2, 2, 1, 1)
        self.input_values.addWidget(hi, 3, 1, 1, 1)
        self.input_values.addWidget(self.inputHigh, 3, 2, 1, 1)
        self.inputLayout.setSpacing(10)
        self.inputLayout.addWidget(title)
        self.inputLayout.addLayout(self.input_values)
        self.vMenu.addLayout(self.inputLayout)

        # #############インターフェースオプションの選択
        self.select_option = QVBoxLayout()
        self.select_option.setSpacing(10)
        l_title = QLabel("オプション")
        l_title.setFont(QFont("Times", weight=QFont.Bold))
        l_title.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.seamless_pattern = QCheckBox("模様が連続になる包装紙を生成する", self)
        self.seamless_pattern.stateChanged.connect(self.enable_detail_button)
        self.detail_bottun = QPushButton('詳細設定', self)
        self.detail_bottun.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.detail_bottun.clicked.connect(self.call_detail_window)
        self.detail_bottun.hide()
        self.d_w = SetDetailWindow()

        # ############# detail_window
        self.d_w.angle_slider.valueChanged[int].connect(
            lambda value: self.d_w.label_s_angle_t.setText(str(value / 10)))
        self.d_w.label_s_angle_t.textChanged.connect(self.adjust_text_box)

        boxes = QVBoxLayout()
        boxes.setSpacing(5)
        boxes.addWidget(self.seamless_pattern)
        self.select_option.addWidget(l_title)
        self.select_option.addLayout(boxes)
        self.select_option.addWidget(self.detail_bottun)
        self.vMenu.addLayout(self.select_option)

        # ################用紙サイズのプルダウン
        self.papersize = QVBoxLayout()
        self.papersize.setSpacing(10)
        papersize_label = QLabel('用紙サイズ')
        papersize_label.setFont(QFont("Times", weight=QFont.Bold))
        papersize_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.paper_size = QComboBox(self)
        self.paper_size.addItem("指定なし")
        self.paper_size.addItem("B3 (縦: 364.0[mm], 横: 515.0[mm])")
        self.paper_size.addItem("A3 (縦: 297.0[mm], 横: 420.0[mm])")
        self.paper_size.addItem("B4 (縦: 257.0[mm], 横: 364.0[mm])")
        self.paper_size.addItem("A4 (縦: 210.0[mm], 横: 297.0[mm])")
        self.paper_size.addItem("B5 (縦: 182.0[mm], 横: 257.0[mm])")
        self.paper_size.setEditable(True)
        self.paper_size.lineEdit().setAlignment(Qt.AlignCenter)
        self.paper_size.lineEdit().setReadOnly(True)
        self.paper_size.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.paper_size.activated.connect(self.call_function)
        self.papersize.addWidget(papersize_label)
        self.papersize.addWidget(self.paper_size)
        self.vMenu.addLayout(self.papersize)

        # ###############Θのスライダー
        theta_slider = QVBoxLayout()
        theta_slider.setSpacing(10)
        slider = QHBoxLayout()
        self.theta_value = QLineEdit('0')
        self.theta_value.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        theta = QLabel('展開図の傾き')
        theta.setFont(QFont("Times", weight=QFont.Bold))
        theta.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.sld = QSlider(Qt.Horizontal, self)
        self.sld.setFocusPolicy(Qt.NoFocus)
        self.sld.setMinimum(0)
        self.sld.setMaximum(900)
        self.sld.resize(80, 20)
        self.sld.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        theta_slider.addWidget(theta)
        slider.addWidget(self.sld)
        slider.addWidget(self.theta_value)
        theta_slider.addLayout(slider)
        self.vMenu.addLayout(theta_slider)
        self.theta_value.editingFinished.connect(self.call_function)
        self.sld.valueChanged[int].connect(self.change_slider_value)

        self.vMenu.setSpacing(20)
        # ############初期画面に戻すボタン
        d_button = QHBoxLayout(self)
        delete_button = QPushButton('画像消去', self)
        delete_button.clicked.connect(self.delete_graphic)
        delete_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        delete_button.setToolTip("画像をクリアして初期画面に戻します")
        d_button.addSpacing(20)
        d_button.addWidget(delete_button)
        d_button.addSpacing(20)
        self.vMenu.addLayout(d_button)

        self.vMenu.setSpacing(17)

        # ########最適化ボタン
        self.optimise_button = QPushButton('最適化', self)
        self.optimise_button.setStyleSheet('background-color: #a8ffff;'
                                           'font-size: 11pt;'
                                           'border-width: 2px;'
                                           'font-weight:bold;')
        self.optimise_button.clicked.connect(self.call_function)
        self.optimise_button.setToolTip("最適化を実行して結果を表示します")
        self.optimise_button.resize(10, 15)
        self.vMenu.addWidget(self.optimise_button)

        display_paper_size = QVBoxLayout(self)
        display_paper_size.setSpacing(10)
        self.s_label = QLabel("必要用紙サイズ")
        self.s_label.setFont(QFont("Times", weight=QFont.Bold))
        self.s_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.d_label = QLabel("[縦 0mm, 横 0mm]")
        self.d_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        display_paper_size.addWidget(self.s_label, alignment=Qt.AlignRight)
        display_paper_size.addWidget(self.d_label, alignment=Qt.AlignRight)
        self.vMenu.addSpacing(20)
        self.vMenu.addLayout(display_paper_size)

        # 結果表示

        # 画像描画
        self.view_boxes = QVBoxLayout(self)
        # ######上画面
        lbl_gb = QGroupBox("展開図(裏)")
        lbl_gb.setStyleSheet('font-size: 11pt;'
                             'font-weight: bold;'
                             )
        lbl_b = QVBoxLayout()
        self.dev_pict = SHOKI_GAZO
        self.lbl = QLabel()
        self.lbl.resize(self.sizeHint().width() - self.vMenu.sizeHint().width() - 20,
                        self.sizeHint().height() - 20)
        self.lbl.setToolTip("実行すると展開図を表示します")
        lbl_b.addWidget(self.lbl, alignment=Qt.AlignCenter)
        lbl_gb.setLayout(lbl_b)
        self.view_boxes.addWidget(lbl_gb)

        # ########下画面
        w_lbl_gb = QGroupBox("包装紙(表)")
        w_lbl_gb.setStyleSheet('font-size: 11pt;'
                               'font-weight: bold;'
                               )
        w_lbl_b = QVBoxLayout()
        self.wrap_hbox = QHBoxLayout(self)
        self.wrap_pict = SHOKI_GAZO
        self.w_lbl = QLabel()
        self.w_lbl.resize(self.sizeHint().width() - 20,
                          self.sizeHint().height() - self.vMenu.sizeHint().height() - 20)
        self.w_lbl.setToolTip("実行すると包装紙の表面を表示します")
        w_lbl_b.addWidget(self.w_lbl, alignment=Qt.AlignCenter)
        w_lbl_gb.setLayout(w_lbl_b)
        self.w_lbl.installEventFilter(self)
        self.view_boxes.addWidget(w_lbl_gb)
        self.view_boxes.setContentsMargins(10, 10, 10, 10)

        line = QFrame(self, Qt.Widget)
        line.setFrameShape(QFrame.VLine)
        line.setLineWidth(2)

        self.vLay.addLayout(self.vMenu, 0, 1, 6, 1)
        self.vLay.addWidget(line, 0, 2, 6, 1)
        self.vLay.addWidget(lbl_gb, 0, 3, 3, 4)
        self.vLay.addWidget(w_lbl_gb, 3, 3, 3, 4)

        self.setLayout(self.vLay)

    def draw_pict(self, file_name):
        self.dev_pict = file_name
        self.pixmap = QImage(file_name)
        self.w_lbl.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        pMap = QPixmap.fromImage(self.pixmap)
        pMap = pMap.scaled(QSize(MAX_HORIZON, MAX_VERTICAL),
                           Qt.KeepAspectRatio)
        self.w_lbl.setPixmap(pMap)
        self.w_lbl.move(int(self.width() / 2 - self.lbl.width() / 2),
                        int(self.height() / 2 - self.lbl.height() / 2))

    def enable_detail_button(self, state):
        if state == Qt.Checked:
            self.detail_bottun.show()
        else:
            self.detail_bottun.hide()

    def call_detail_window(self):
        self.d_w.show()

    def delete_graphic(self):
        if self.exec_flag:
            op = QMessageBox.warning(
                self, "警告！", "初期画面に戻しますか？", QMessageBox.Ok, QMessageBox.No)
            if op == QMessageBox.Ok:
                self.dev_pict = SHOKI_GAZO
                self.draw_pict(SHOKI_GAZO)
                self.pixmap = QImage(SHOKI_GAZO)
                self.lbl.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
                self.lbl.setPixmap(QPixmap.fromImage(self.pixmap))
                self.lbl.move(int(self.width() / 2 - self.lbl.width() / 2),
                              int(self.height() / 2 - self.lbl.height() / 2))
                self.exec_flag = False
            if self.g_w_can_hover:
                self.g_w_can_hover = False

    def render_guide_line_with_wrap_paper(self, vertical, horizon, high, theta, w=0, h=0):
        self.pixmap = QImage(self.dev_pict)
        pMap = QPixmap.fromImage(self.pixmap)
        if pMap.width() / MAX_HORIZON < pMap.height() / MAX_VERTICAL:
            self.magnification = pMap.height() / MAX_VERTICAL
        else:
            self.magnification = pMap.width() / MAX_HORIZON
        self.pixmap_r = pMap.scaled(
            QSize(MAX_HORIZON, MAX_VERTICAL), Qt.KeepAspectRatio)
        r_m_ps = render_net_on_image(vertical, horizon, high, theta, self.pixmap_r,
                                     self.paper_size.itemText(self.paper_size.currentIndex()).split()[0])
        self.p_size = r_m_ps[0]
        renderer = QSvgRenderer('./.tmp/output_render.svg')
        painter = QPainter(self.pixmap_r)
        painter.restore()
        renderer.render(painter, QRectF(w, h, self.p_size[0], self.p_size[1]))

        self.w_lbl.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.w_lbl.setPixmap(self.pixmap_r)
        self.d_label.setText(
            f"[縦 {r_m_ps[1][1]:.1f}mm, 横 {r_m_ps[1][0]:.1f}mm]")
        self.d_label.adjustSize()

    def render_seamless_wrap_paper(self, vertical, horizon, high, line_w, interval_w, offset, s2b_angle, b_angle):
        render_stripe(vertical, horizon, high, line_w,
                      interval_w, offset, s2b_angle, b_angle)
        renderer = QSvgRenderer('./.tmp/output_render_wrap.svg')
        w, h = renderer.defaultSize().width() * 4 / \
            5, renderer.defaultSize().height() * 4 / 5
        self.w_pixmap = QImage(QSize(w, h), QImage.Format_ARGB32_Premultiplied)
        b_color = QColor(parameters.background_color)
        self.w_pixmap.fill(b_color)
        painter = QPainter(self.w_pixmap)
        painter.restore()
        renderer.render(painter)
        self.w_lbl.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.w_lbl.setPixmap(QPixmap.fromImage(self.w_pixmap))

    def render_guide_line_with_no_paper(self, vertical, horizon, high, theta):
        theta = theta * (np.pi / 180)
        # if self.giftbox is None:
        self.giftbox = GiftBox(vertical, horizon, high)
        m_ps = render_net_no_image(self.giftbox, theta,
                                   self.paper_size.itemText(self.paper_size.currentIndex()).split()[0])
        renderer = QSvgRenderer('./.tmp/output_render.svg')
        w, h = renderer.defaultSize().width() * 4 / \
            5, renderer.defaultSize().height() * 4 / 5
        self.pixmap = QImage(QSize(w, h), QImage.Format_ARGB32_Premultiplied)
        self.pixmap.fill(QColor("white").rgb())
        painter = QPainter(self.pixmap)
        painter.restore()
        renderer.render(painter)
        self.lbl.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.lbl.setPixmap(QPixmap.fromImage(self.pixmap))
        self.d_label.setText(f"[縦 {m_ps[1]:.1f}mm, 横 {m_ps[0]:.1f}mm]")
        self.d_label.adjustSize()

    def call_function(self, index_l=None):  # 関数の呼び出し
        what_call = self.sender()
        vertical = self.inputVertical.text()
        horizon = self.inputHorizon.text()
        high = self.inputHigh.text()
        theta = float(self.theta_value.text())
        error_message = ""
        if vertical != "" and horizon != "" and high != "":
            if not (vertical.replace(".", "").isdecimal()
                    and horizon.replace(".", "").isdecimal()
                    and high.replace(".", "").isdecimal()):
                error_message += "・3辺は数値で入力してください\n"
            elif float(vertical) <= 0 or float(horizon) <= 0 or float(high) <= 0:
                error_message += "・3辺は0より大きい値で入力してください\n"
            if what_call in [self.paper_size,
                             self.optimise_button,
                             self.inputVertical,
                             self.inputHorizon,
                             self.inputHigh
                             ]:
                if index_l is None:
                    index_l = self.paper_size.currentIndex()
                can_wrap = self.judge_can_wrap_paper(index_l)
                if not can_wrap:
                    error_message += '・指定した用紙サイズは小さすぎます\n'
                elif can_wrap == -1:
                    pass
                else:
                    theta = can_wrap
            if self.seamless_pattern.checkState() == Qt.Checked and not parameters.all_valid():
                error_message += '・詳細設定に空欄があります\n'
        else:
            error_message += "・3辺を数値で入力してください\n"

        if theta < 0 or 90 < theta:
            error_message += "・傾きΘの値が不正です(0~90度で入力してください)\n"

        if error_message != "":  # エラーを表示
            self.d_w.setWindowFlag(Qt.WindowStaysOnTopHint, on=False)
            a = QMessageBox()
            a.setWindowFlag(Qt.WindowStaysOnTopHint)
            a.warning(self, "エラー！", error_message,
                      QMessageBox.Ok, QMessageBox.Ok)
            self.d_w.setWindowFlag(Qt.WindowStaysOnTopHint)
        else:  # レンダリング実行
            vertical = float(vertical)
            horizon = float(horizon)
            high = float(high)
            if self.sld.value() != theta * 10:
                self.sld.setValue(int(theta * 10))
                self.theta_value.setText(str(theta))
                self.theta_value.adjustSize()
            if theta == 90.0:
                theta = 89.9
            self.exec_flag = True
            if self.dev_pict == SHOKI_GAZO:  # 展開図のレンダリング or シームレスのレンダリング
                self.render_guide_line_with_no_paper(
                    vertical, horizon, high, theta)
                if self.seamless_pattern.checkState() == Qt.Checked:
                    self.s_exec_flag = True
                    self.render_seamless_wrap_paper(vertical, horizon, high,
                                                    parameters.stripe_width,
                                                    parameters.stripe_interval_width,
                                                    parameters.offset,
                                                    parameters.stripe_theta / 180 * np.pi,
                                                    theta / 180 * np.pi)
                if self.g_w_can_hover:
                    self.g_w_can_hover = False

            else:  # 読み込み画像込みのレンダリング
                if self.seamless_pattern.checkState() == Qt.Checked:
                    self.d_w.setWindowFlag(Qt.WindowStaysOnTopHint, on=False)
                    op = QMessageBox.warning(
                        self, "警告！", "包装紙のデザインが変わります", QMessageBox.Ok, QMessageBox.No)
                    if op == QMessageBox.Ok:
                        self.draw_pict(SHOKI_GAZO)
                        self.call_function()
                    self.d_w.setWindowFlag(Qt.WindowStaysOnTopHint)
                    if self.g_w_can_hover:
                        self.g_w_can_hover = False
                else:
                    self.g_exec_flag = True
                    self.render_guide_line_with_no_paper(
                        vertical, horizon, high, theta)
                    self.render_guide_line_with_wrap_paper(
                        vertical, horizon, high, theta)
                    self.g_w_can_hover = True

    def change_slider_value(self, value):
        self.theta_value.setText(str(value / 10))
        self.theta_value.adjustSize()
        if self.exec_flag:
            self.call_function()

    def adjust_text_box(self):
        self.d_w.label_s_angle_t.adjustSize()
        self.d_w.fill_value(self.d_w.label_s_angle_t)
        if self.exec_flag:
            self.call_function()

    def save_wrap_pdf(self, path, g_path):
        vertical = float(self.inputVertical.text())
        horizon = float(self.inputHorizon.text())
        high = float(self.inputHigh.text())
        theta = float(self.theta_value.text())
        # ######## 壁紙アリpdf
        render_wrap_paper_and_net_real_size(vertical, horizon, high, theta, path, g_path,
                                            self.b_x, self.b_y, self.p_size[0], self.p_size[1],
                                            self.magnification)

    def save_svg_graphic(self, path):
        vertical = float(self.inputVertical.text())
        horizon = float(self.inputHorizon.text())
        high = float(self.inputHigh.text())
        theta = float(self.theta_value.text())
        if path.split(".")[-1] == "svg":
            render_net_real_size(vertical, horizon, high, theta, path)
            if self.seamless_pattern.checkState() == Qt.Checked:
                path2 = path.replace(".svg", "") + "_2.svg"
                render_stripe_real_size(vertical, horizon, high,
                                        parameters.stripe_width,
                                        parameters.stripe_interval_width,
                                        parameters.offset,
                                        parameters.stripe_theta,
                                        theta,
                                        path2)

        elif path.split(".")[-1] == "pdf":
            if self.seamless_pattern.checkState() == Qt.Checked:
                save_svg_to_pdf(vertical, horizon, high, theta,
                                path,
                                parameters.stripe_width,
                                parameters.stripe_interval_width,
                                parameters.offset,
                                parameters.stripe_theta)
            else:
                save_svg_to_pdf(vertical, horizon, high, theta, path)
        else:
            QMessageBox.warning(self, "エラー！", "対応していない拡張子です",
                                QMessageBox.Ok, QMessageBox.Ok)

    def judge_can_wrap_paper(self, row):  # 指定した用紙サイズで包めるか
        text = self.paper_size.itemText(row).split()[0]
        if self.inputVertical.text().replace(".", "").isdecimal() \
                and self.inputHorizon.text().replace(".", "").isdecimal() \
                and self.inputHigh.text().replace(".", "").isdecimal():
            g_box = GiftBox(float(self.inputVertical.text()), float(self.inputHorizon.text()),
                            float(self.inputHigh.text()))
            g_box_theta = g_box.get_optimal_theta()
            minimum_ps = g_box.get_valid_paper_size(
                g_box_theta * (np.pi / 180))
            if text != '指定なし' and (
                    default_paper_size[text][0] < minimum_ps[0] or default_paper_size[text][1] < minimum_ps[1]):
                return False
            else:
                return g_box_theta
        else:
            return -1

    # #####画像ラベルにHoverEnterしたらマウスが効くようにする。マウス押した位置から移動距離によって、rendererのQRectの座標を動かす
    def eventFilter(self, object, event):
        if event.type() == QEvent.Enter:
            self.stop = True
            return True
        elif event.type() == QEvent.Leave:
            self.stop = False
        return False

    def mousePressEvent(self, event):
        if self.g_w_can_hover and (self.stop is True) and event.button() == Qt.LeftButton:
            self.lastPoint = event.pos()
            self.scribbling = True

    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.LeftButton) and self.scribbling:
            self.m_x = (event.pos().x() - self.lastPoint.x())
            self.m_y = (event.pos().y() - self.lastPoint.y())
            self.render_guide_line_with_wrap_paper(self.inputVertical.text(),
                                                   self.inputHorizon.text(),
                                                   self.inputHigh.text(),
                                                   float(
                                                       self.theta_value.text()),
                                                   self.b_x + self.m_x, self.b_y + self.m_y)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.scribbling:
            self.b_x = self.b_x + event.pos().x() - self.lastPoint.x()
            self.b_y = self.b_y + event.pos().y() - self.lastPoint.y()
            if self.b_x < 0:
                self.b_x = 0
            if self.b_x > self.pixmap_r.width() - self.p_size[0]:
                self.b_x = self.pixmap_r.width() - self.p_size[0]
            if self.b_y < 0:
                self.b_y = 0
            if self.b_y > self.pixmap_r.height() - self.p_size[1]:
                self.b_y = self.pixmap_r.height() - self.p_size[1]
            self.render_guide_line_with_wrap_paper(self.inputVertical.text(),
                                                   self.inputHorizon.text(),
                                                   self.inputHigh.text(),
                                                   float(
                                                       self.theta_value.text()),
                                                   self.b_x, self.b_y)
            self.scribbling = False


# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     main_window = GWMainWindow()
#     sys.exit(app.exec_())
