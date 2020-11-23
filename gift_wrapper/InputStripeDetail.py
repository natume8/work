# -*- coding: utf_8 -*-
# 入力：線の幅、線同士の間隔、オフセット、角度

import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import QPixmap, QIcon, QColor
from PyQt5.QtWidgets import *


debug_v = 0

color_scheme_sample = [
    ["#cc0000", "#ff99cc", "#ffcccc"],
    ["#ffffcc", "#ffffff", "#99cc99"],
    ["#0000cc", "#ffffcc", "#0099ff"]
]

demo_colors = [
    ["#6AA041", "#FCDFA4", "#B95341", "#F39744", "#85574A"],
    ["#ACA048", "#EFCCA7", "#835447", "#4F8934"],
    ["#7DB4C5", "#C5B5CC", "#E4D38E", "#EA91AA", "#35ACA5"],
    ["#5CB4B6", "#9C7FA5", "#91BC5C", "#E99361", "#ED838A"]
]


class SetParameters:
    def __init__(self):
        self.stripe_width = None
        self.stripe_interval_width = None
        self.offset = None
        self.stripe_theta = None
        self.background_color = 'white'
        self.color_set = []

    def all_valid(self):
        p_list = [True if i is not None and i != "" and i >= 0 else False
                  for i in [self.stripe_width, self.stripe_interval_width, self.offset, self.stripe_theta]]
        if all(p_list):
            return True
        else:
            return False

    def color_set_isValid(self):
        if self.color_set is not []:
            return True
        else:
            return False


parameters = SetParameters()


class SetDetailWindow(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        # quit = QAction("Quit", self)
        # quit.triggered.connect(self.close)

        self.setWindowTitle('input detail')
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.resize(500, 800)
        self.center_frame()
        self.initUI()
        self.init_color_UI()

        self.setLayout(self.layout)
        # self.show()

    def initUI(self):
        self.input_group = QGroupBox("&ストライプ情報入力")
        warinig_label = QLabel('* は必須 (数値で入力)')
        warinig_label.setStyleSheet('color: red')
        label_s_w = QLabel('* 線の幅 (mm)')
        label_s_w.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.label_s_w_t = QLineEdit()
        self.label_s_w_t.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.label_s_w_t.editingFinished.connect(self.fill_value)

        label_s_i_w = QLabel('* 線の間隔 (mm)')
        label_s_i_w.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.label_s_i_w_t = QLineEdit()
        self.label_s_i_w_t.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.label_s_i_w_t.editingFinished.connect(self.fill_value)

        label_offset = QLabel('* オフセット(mm)')
        label_offset.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.label_offset_t = QLineEdit()
        self.label_offset_t.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.label_offset_t.editingFinished.connect(self.fill_value)

        label_s_angle = QLabel('* ストライプの角度 (度)')
        label_s_angle.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.label_s_angle_t = QLineEdit("45.0")
        self.label_s_angle_t.setSizePolicy(
            QSizePolicy.Fixed, QSizePolicy.Fixed)
        parameters.stripe_theta = 45.0
        # self.label_s_angle_t.textChanged.connect(self.fill_value)
        # self.label_s_angle_t.editingFinished.connect(self.fill_value)
        self.angle_slider = QSlider(Qt.Horizontal)
        self.angle_slider.setFocusPolicy(Qt.NoFocus)
        self.angle_slider.setMinimum(0)
        self.angle_slider.setMaximum(900)
        self.angle_slider.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.angle_slider.setValue(450)

        edit_detail = QGridLayout()
        edit_detail.setSpacing(10)
        self.layout = QVBoxLayout(self)
        edit_detail.addWidget(warinig_label, 0, 1, 1, 2,
                              alignment=Qt.AlignHCenter)
        edit_detail.addWidget(label_s_w, 1, 1, alignment=Qt.AlignHCenter)
        edit_detail.addWidget(self.label_s_w_t, 1, 2)
        edit_detail.addWidget(label_s_i_w, 2, 1, alignment=Qt.AlignHCenter)
        edit_detail.addWidget(self.label_s_i_w_t, 2, 2)
        edit_detail.addWidget(label_offset, 3, 1, alignment=Qt.AlignHCenter)
        edit_detail.addWidget(self.label_offset_t, 3, 2)
        edit_detail.addWidget(label_s_angle, 4, 1, 2, 1,
                              alignment=Qt.AlignHCenter)
        edit_detail.addWidget(self.label_s_angle_t, 4, 2)
        edit_detail.addWidget(self.angle_slider, 5, 2)
        self.input_group.setLayout(edit_detail)
        self.layout.addWidget(self.input_group)
        self.layout.addSpacing(20)

    def init_color_UI(self):
        self.bg_color_set = QGroupBox("背景色の選択")
        self.select_back_color = QHBoxLayout(self)
        self.b_c = QColor('white')
        select_b_label = QLabel("背景色: ")
        self.select_c_label = QLineEdit()
        self.select_c_label.setReadOnly(True)
        self.select_c_label.resize(30, 10)
        self.select_c_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        select_color_button = QPushButton("選択")
        select_color_button.clicked.connect(self.select_back_ground_color)
        select_color_button.setFocusPolicy(Qt.NoFocus)
        self.select_back_color.addWidget(
            select_b_label, alignment=Qt.AlignRight)
        self.select_back_color.addWidget(self.select_c_label)
        self.select_back_color.addWidget(select_color_button)
        self.bg_color_set.setLayout(self.select_back_color)
        self.layout.addWidget(self.bg_color_set)
        self.layout.addSpacing(20)

        self.select_buttons_g = QGroupBox("モード選択")
        self.select_buttons = QHBoxLayout(self)
        self.select_detail = QButtonGroup()
        self.plane_b = QRadioButton('無地ストライプ')
        self.plane_b.toggled.connect(lambda: self.change_mode(0))
        self.image_b = QRadioButton('画像の利用')
        self.image_b.toggled.connect(lambda: self.change_mode(1))
        self.select_detail.addButton(self.plane_b, 0)
        self.select_detail.addButton(self.image_b, 1)
        self.select_buttons.addWidget(self.plane_b)
        self.select_buttons.addWidget(self.image_b)
        self.select_buttons_g.setLayout(self.select_buttons)
        self.layout.addWidget(self.select_buttons_g)
        self.layout.addSpacing(20)
        
        #-----color select area-----
        self.sc_frame = QFrame()
        self.color_selector = QVBoxLayout(self)
        self.color_palette = QGroupBox("ストライプカラーの選択")
        self.c_palette = QVBoxLayout(self)
        self.c_palette.setSpacing(20)
        self.c_palette_list = QListWidget(self)
        self.c_palette_list.setSelectionMode(
            QAbstractItemView.ExtendedSelection)
        self.add_num = 0

        self.c_palette.addWidget(self.c_palette_list)
        self.red_b = QPushButton("赤系色sample")
        self.green_b = QPushButton("緑系色sample")
        self.blue_b = QPushButton("青系色sample")
        color_buttons = QHBoxLayout()
        self.red_b.clicked.connect(self.scheme_color)
        self.green_b.clicked.connect(self.scheme_color)
        self.blue_b.clicked.connect(self.scheme_color)
        self.scheme_valid_r = False
        self.scheme_valid_g = False
        self.scheme_valid_b = False
        color_buttons.addWidget(self.red_b)
        color_buttons.addWidget(self.green_b)
        color_buttons.addWidget(self.blue_b)
        self.c_palette.addLayout(color_buttons)

        demo_color_buttons = QHBoxLayout()
        self.demo1 = QPushButton("デモ1: MK")
        self.demo2 = QPushButton("デモ2: TS")
        self.demo3 = QPushButton("デモ3: PC")
        self.demo4 = QPushButton("デモ4: SG")
        demo_color_buttons.addWidget(self.demo1)
        demo_color_buttons.addWidget(self.demo2)
        demo_color_buttons.addWidget(self.demo3)
        demo_color_buttons.addWidget(self.demo4)
        self.demo1.clicked.connect(self.import_demo_scheme)
        self.demo2.clicked.connect(self.import_demo_scheme)
        self.demo3.clicked.connect(self.import_demo_scheme)
        self.demo4.clicked.connect(self.import_demo_scheme)
        self.c_palette.addLayout(demo_color_buttons)

        self.color_palette.setLayout(self.c_palette)
        self.color_selector.addWidget(self.color_palette)
        self.color_selector.addSpacing(20)

        buttons = QHBoxLayout()
        add_button = QPushButton("追加")
        add_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        add_button.setFocusPolicy(Qt.NoFocus)
        add_button.clicked.connect(self.add_color_column)
        delete_button = QPushButton("削除")
        delete_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        delete_button.setFocusPolicy(Qt.NoFocus)
        delete_button.clicked.connect(self.delete_column)
        switch_button = QPushButton("入れ替え")
        switch_button.setToolTip("1つ下の色と入れ替えます")
        switch_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        switch_button.setFocusPolicy(Qt.NoFocus)
        switch_button.clicked.connect(self.switch_column)
        buttons.addWidget(add_button)
        buttons.addWidget(delete_button)
        buttons.addWidget(switch_button)
        self.color_selector.addLayout(buttons)

        self.c_palette_list.itemDoubleClicked.connect(self.change_color_column)
        self.sc_frame.setLayout(self.color_selector)
        self.layout.addWidget(self.sc_frame)
        
        #-----image selector area-----
        self.si_frame = QFrame()
        self.image_selector = QVBoxLayout()
        self.file_button = QPushButton()    

        # TODO: load image file 

        self.image_selector.addWidget(self.file_button)
        self.si_frame.setLayout(self.image_selector)
        self.layout.addWidget(self.si_frame)

        self.plane_b.setChecked(True)   # plane button checked

    # ヘルプ書かなきゃ
    def change_mode(self, mode):
        if mode == 0:
            self.sc_frame.show()
            self.si_frame.hide()
        elif mode == 1:
            self.sc_frame.hide()
            self.si_frame.show()

    def add_color_column(self, c=None):
        if c is False:
            c = self.select_color()
        color_icon_p = QPixmap(40, 40)
        color_icon_p.fill(QColor(c))
        color_icon = QIcon(color_icon_p)
        if c:
            self.add_num += 1
            view_color = QListWidgetItem(color_icon, c)
            self.c_palette_list.insertItem(self.add_num, view_color)
            parameters.color_set.append(c)

    def change_color_column(self):
        c = self.select_color()
        index = self.c_palette_list.currentRow()
        color_icon_p = QPixmap(40, 40)
        color_icon_p.fill(QColor(c))
        color_icon = QIcon(color_icon_p)
        if c:
            view_color = QListWidgetItem(color_icon, c)
            self.c_palette_list.takeItem(index)
            self.c_palette_list.insertItem(index, view_color)
            parameters.color_set[index] = c

    def delete_column(self, colors=None):
        selected = self.c_palette_list.selectedItems()
        if selected is not [] and (colors is False):
            for item in selected:
                i = self.c_palette_list.row(item)
                self.c_palette_list.takeItem(i)
                parameters.color_set.pop(i)
        elif colors is not None:
            for c in colors:
                d_c = self.c_palette_list.findItems(c, Qt.MatchFixedString)
                i = self.c_palette_list.row(d_c[0])
                self.c_palette_list.takeItem(i)
                parameters.color_set.pop(i)

    def switch_column(self):
        i = self.c_palette_list.currentRow()
        if i != self.c_palette_list.count() - 1:
            s_1 = self.c_palette_list.item(i)
            s_2 = self.c_palette_list.item(i + 1)

            self.c_palette_list.takeItem(i)
            self.c_palette_list.takeItem(i)
            self.c_palette_list.insertItem(i, s_1)
            self.c_palette_list.insertItem(i, s_2)
            parameters.color_set[i], parameters.color_set[i +
                                                          1] = parameters.color_set[i + 1], parameters.color_set[i]

    def select_back_ground_color(self, c=None):
        if c is False:
            c = self.select_color()
        if c:
            parameters.background_color = c
            self.select_c_label.setStyleSheet(
                f'background-color:{parameters.background_color}')

    def select_color(self):
        color = QColorDialog.getColor(Qt.white, self)
        if color.isValid():
            return color.name()
        else:
            return False

    def scheme_color(self):
        send = self.sender()
        if self.scheme_valid_r is True:
            self.delete_column(color_scheme_sample[0])
            self.scheme_valid_r = False
        if self.scheme_valid_g is True:
            self.delete_column(color_scheme_sample[1])
            self.scheme_valid_g = False
        if self.scheme_valid_b is True:
            self.delete_column(color_scheme_sample[2])
            self.scheme_valid_b = False

        if send == self.red_b:
            for c in color_scheme_sample[0]:
                self.add_color_column(c)
            self.scheme_valid_r = True
        elif send == self.green_b:
            for c in color_scheme_sample[1]:
                self.add_color_column(c)
            self.scheme_valid_g = True
        else:
            for c in color_scheme_sample[2]:
                self.add_color_column(c)
            self.scheme_valid_b = True

    def import_demo_scheme(self):
        if self.sender() == self.demo1:
            color_set = demo_colors[0]
            self.select_back_ground_color("#CE5840")
        elif self.sender() == self.demo2:
            color_set = demo_colors[1]
            self.select_back_ground_color("#ED5940")
        elif self.sender() == self.demo3:
            color_set = demo_colors[2]
        else:
            color_set = demo_colors[3]
            self.select_back_ground_color("#F0E08D")
        for c in color_set:
            self.add_color_column(c)

    def fill_value(self, send=None):
        """キー押す
        →fill_valueの呼び出し(フォーカスが再度つく)
        →文字種が違うとウインドウの呼び出し
        →LineEditがフォーカスが落ちて再びfill_value呼び出し
        """
        if send is None:
            send = self.sender()

        value = send.text().replace(".", "")
        if value != "":
            if value.isdecimal():
                if send == self.label_s_w_t:
                    parameters.stripe_width = float(send.text())
                if send == self.label_s_i_w_t:
                    parameters.stripe_interval_width = float(send.text())
                if send == self.label_offset_t:
                    parameters.offset = float(send.text())
                if send == self.label_s_angle_t:
                    parameters.stripe_theta = float(send.text())
            else:
                send.setText("数値で入力")
                send.selectAll()
        else:
            if send == self.label_s_w_t:
                parameters.stripe_width = ""
            if send == self.label_s_i_w_t:
                parameters.stripe_interval_width = ""
            if send == self.label_offset_t:
                parameters.offset = ""
            if send == self.label_s_angle_t:
                parameters.stripe_theta = ""

    def closeEvent(self, event):
        pass

    def center_frame(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # paras = SetParameters()
    main_window = SetDetailWindow()
    sys.exit(app.exec_())
