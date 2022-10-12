# -*- coding: utf-8 -*-

# 主界面启动文件
# 继承 Window_begin 的Ui_Window_begin 类，作为主窗口

import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox
from ui.Ui_Window_begin import Ui_Window_begin
from ui.fun_window_FD import MainWindow_FD
from ui.fun_widget_GF import MainWidget_GF


class MainWindow_begin(QMainWindow, Ui_Window_begin):
    def __init__(self, parent=None):
        super(MainWindow_begin, self).__init__(parent)

        self.setupUi(self)

        # 设置应用图标，下同
        self.setWindowIcon(QIcon('resource/jpg1.jpg'))
        self.ui_GF = MainWidget_GF()
        self.ui_FD = MainWindow_FD()
        # 子窗口在初始化时构建会保存窗口数据，在后面构建就不会保存
        self.ui_FD.setWindowIcon(QIcon('resource/jpg1.jpg'))
        self.ui_GF.setWindowIcon(QIcon('resource/jpg1.jpg'))
        self.pushButton_GF.clicked.connect(self.ui_GF_show)
        self.pushButton_FD.clicked.connect(self.ui_FD_show)

    def ui_GF_show(self):
        # self.ui_GF = MainWidget_GF()
        self.ui_GF.show()

    def ui_FD_show(self):
        # self.ui_FD = MainWindow_FD()
        self.ui_FD.show()

    # 设计退出提示
    def closeEvent(self, event):
        reply = QMessageBox.question(self, '提示',
                                     "是否要关闭所有窗口?",
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
            sys.exit(0)  # 退出程序
        else:
            event.ignore()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui_begin = MainWindow_begin()
    ui_begin.show()
    sys.exit(app.exec_())

    # 没有使用
    #     ui_GF = MainWidget_GF()
    #     ui_FD = MainWindow_FD()
    #     ui_begin.pushButton_GF.clicked.connect(ui_GF.show)
    #     ui_begin.pushButton_FD.clicked.connect(ui_FD.show)
    # 这种写法 （生成与主窗口完全不相关的ui界面）（会暂存子窗口信息，但是不能在关闭主窗口时关闭）
