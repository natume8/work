import sys

from PyQt5.QtWidgets import QApplication

from gift_wrapper.sample_pictures import WrappingCreator

if __name__ == '__main__':
    DPI = 72

    A = int(150)
    B = int(120)
    C = int(30)
    # app = QApplication(sys.argv)
    ex = WrappingCreator([A, B, C])
    ex.run()
    # sys.exit(app.exec_())
