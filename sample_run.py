import sys

from PyQt5.QtWidgets import QApplication

from gift_wrapper.sample_pictures import WrappingCreator

if __name__ == '__main__':
    DPI = 72

    A = int(150 * DPI / 25.4)
    B = int(120 * DPI / 25.4)
    C = int(30 * DPI / 25.4)
    app = QApplication(sys.argv)
    ex = WrappingCreator(A, B, C)
    sys.exit(app.exec_())
