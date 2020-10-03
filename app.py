import sys

from PyQt5.QtWidgets import QApplication

from gift_wrapper.GiftWrapperInterface import GWMainWindow


app = QApplication(sys.argv)
main_window = GWMainWindow()
sys.exit(app.exec_())
