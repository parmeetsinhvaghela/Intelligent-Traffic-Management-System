from PyQt5.QtWidgets import QApplication
from package.mainwindow import MainWindow
import sys


def run():
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
