# -*- coding: utf-8 -*-

# 风电预测界面
# 继承 Window_FD 的 Ui_MainWindow 类，添加该窗口的补充设置，为该窗口的控件编写槽函数（功能函数）

import sys
import os

from PyQt5 import QtWidgets
from PyQt5.QtGui import QRegExpValidator, QPixmap
from PyQt5.QtWidgets import QApplication, QMessageBox, QMainWindow
from PyQt5.QtCore import QRegExp

# 包内导入，用ui.表示当前模块，也可以删去ui直接用. ，但被其他模块导入使用时，相对导入会出问题
# 导入风电的窗口初始界面
from ui.Ui_Window_FD import Ui_MainWindow
# 导入模型训练，预测，文件保存 等功能 的函数
from fun.fun_change import model_training, write_tofile, point_predict

current_path = os.path.dirname(__file__)  # 先找到当前文件所在的目录ui
father_path = os.path.dirname(current_path)  # 往上倒一层目录,也就是 ui所在的文件夹，项目文件夹


# 在后面调整文件路径，可以解决 相对路径 在 其他模块调用时路径错误的问题

# 继承Ui，编写各ui的槽函数，实现各ui的功能
class MainWindow_FD(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow_FD, self).__init__(parent)

        self.setupUi(self)

        self.label_chart.setScaledContents(True)

        self.Ispredict_over = False
        self.filename_select = ''
        self.filename_select_copy = ''
        self.filename_save_chart = ''
        self.filename_save_excel = ''
        self.data_predict = []
        self.data_predict_copy = []

        # ui/控件 与槽函数链接
        self.pushButton_forFileDialog.clicked.connect(self.show_FileDialog_select)
        self.pushButton_predict_file.clicked.connect(self.pushButton_predict_file_clicked)
        self.pushButton_save_chart.clicked.connect(self.show_FileDialog_save_chart)
        self.pushButton_w_tofile.clicked.connect(self.pushButton_w_tofile_clicked)

    # 选择文件 按钮 槽函数    主要利用QFileDialog文件对话框获取待预测文件的文件名
    def show_FileDialog_select(self):
        self.filename_select, ftype = QtWidgets.QFileDialog. \
            getOpenFileName(self, 'Open file', os.path.join(father_path, 'test_example/FD'), "Excel(*xlsx;*.xls)")
        # 返回值是列表，文件名+文件类型 eg：('C:/Users/huanglian/Desktop/新建文本文档.txt', 'All Files (*)')
        if self.filename_select:
            self.filename_select_copy = self.filename_select
            self.label_chart.setText('')
            self.Ispredict_over = False  # Ispredict_over 判断文件选择完成后，是否完成预测的标志量
        else:
            # filename_select_copy 的作用是，当取消选择，可以保留上一次选择的文件
            self.filename_select = self.filename_select_copy

    # 保存图表 按钮 槽函数
    # 主要实现方法为：将预测结果的temp_FD.jpg文件复制一份
    def show_FileDialog_save_chart(self):
        if self.Ispredict_over:
            self.filename_save_chart = ''
            self.filename_save_chart, ftype = QtWidgets.QFileDialog.getSaveFileName \
                (self, 'Save file', os.path.join(father_path, 'result_save/result_chart'), "jig(*.jpg);;png(*.png)")
        else:
            QMessageBox.critical(self, 'Error', '请先完成预测')
        if self.filename_save_chart:
            chart_temp = open(os.path.join(father_path, 'temp/temp_FD.jpg'), "rb")
            chart_content = chart_temp.read()
            chart_save = open(self.filename_save_chart, "wb")
            chart_save.write(chart_content)
            chart_save.close()
            chart_temp.close()

    # 将结果写入文件 按键 槽函数
    def pushButton_w_tofile_clicked(self):
        if self.Ispredict_over:
            self.data_predict_copy = self.data_predict.copy()
            zero_list = [None] * 12
            zero_list.extend(self.data_predict_copy)  # 由于预测函数返回的值缺失前12个数据，添加12个空值从而保证写入文件时正常
            self.data_predict_copy = zero_list
            # print(len(self.data_predict_copy))
            # print(self.data_predict_copy)

            self.filename_save_excel = ''
            self.filename_save_excel, ftype = QtWidgets.QFileDialog.getSaveFileName \
                (self, 'Save file', os.path.join(father_path, 'result_save/result_excel'), "Excel(*.xlsx)")

            # 获取保存文件的名称后，调用保存文件函数
            if self.filename_save_excel:
                write_tofile(self.filename_select, self.filename_save_excel, self.data_predict_copy)
        else:
            QMessageBox.critical(self, 'Error', '请先完成预测')

    # 文件开始预测 按钮 槽函数
    def pushButton_predict_file_clicked(self):
        if self.filename_select:
            # 由于训练过程较长，显示图片，说明运行中
            self.label_chart.setPixmap(QPixmap(os.path.join(father_path, 'resource/waiting.png')))
            QtWidgets.QApplication.processEvents()  # 刷新，否则图片不显示
            self.data_predict = ''
            self.data_predict = model_training(self.filename_select, True)  # 调用训练预测函数，返回预测结果

            # 预测成功则展示预测结果图片，训练预测失败（程序出问题，有一定概率是文件问题）则提示“请选择规范的文件”
            if self.data_predict:
                self.label_chart.setPixmap(QPixmap(os.path.join(father_path, 'temp/temp_FD.jpg')))
                self.Ispredict_over = True
                QMessageBox.information(self, 'Message', '预测完成')
            else:
                self.label_chart.clear()
                QMessageBox.critical(self, 'Error', '请选择规范的文件')

        else:
            QMessageBox.critical(self, 'Error', '请先选择文件')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = MainWindow_FD()
    ui.show()
    sys.exit(app.exec_())
