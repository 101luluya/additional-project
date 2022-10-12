# -*- coding: utf-8 -*-

# 光伏预测界面
# 继承 Widget_GF 的 Ui_Form 类，添加该窗口的补充设置，为该窗口的控件编写槽函数（功能函数）
# 其他与风电类似，注释参考即可

import os
import sys

from PyQt5 import QtWidgets
from PyQt5.QtGui import QRegExpValidator, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox
from PyQt5.QtCore import QRegExp

# 包内导入，用ui.表示当前模块，也可以删去ui直接用.，但当前文件作为main运行时是顶层模块，相对导入会出问题
from ui.Ui_Widget_GF import Ui_Form
from fun.fun_change import model_training, write_tofile, point_predict

current_path = os.path.dirname(__file__)  # 先找到当前文件所在的目录ui
father_path = os.path.dirname(current_path)  # 往上倒一层目录,也就是 ui所在的文件夹，项目文件夹


class MainWidget_GF(QWidget, Ui_Form):
    def __init__(self, parent=None):
        super(MainWidget_GF, self).__init__(parent)

        self.setupUi(self)

        self.Ispredict_over = False
        self.filename_select = ''
        self.filename_select_copy = ''
        self.filename_save_chart = ''
        self.filename_save_excel = ''
        self.data_add = []

        self.label_chart.setScaledContents(True)

        self.pushButton_forFileDialog.clicked.connect(self.show_FileDialog_select)
        self.pushButton_predict_file.clicked.connect(self.pushButton_predict_file_clicked)
        self.pushButton_save_chart.clicked.connect(self.show_FileDialog_save_chart)
        self.pushButton_w_tofile.clicked.connect(self.pushButton_w_tofile_clicked)

    def show_FileDialog_select(self):
        self.filename_select, ftype = QtWidgets.QFileDialog.getOpenFileName \
            (self, 'Open file', os.path.join(father_path, 'test_example/GF'), "Excel(*.xlsx;*.xls)")
        # 返回值是列表，文件名,文件类型 ('C:/Users/huanglian/Desktop/新建文本文档.txt', 'All Files (*)')
        if self.filename_select:
            self.filename_select_copy = self.filename_select
            self.label_chart.setText('')
            self.Ispredict_over = False
        else:
            self.filename_select = self.filename_select_copy

    def show_FileDialog_save_chart(self):

        if self.Ispredict_over:
            self.filename_save_chart = ''
            self.filename_save_chart, ftype = QtWidgets.QFileDialog.getSaveFileName \
                (self, 'Save file', os.path.join(father_path, 'result_save/result_chart'), "jig(*.jpg);;png(*.png)")
        else:
            QMessageBox.critical(self, 'Error', '请先完成预测')
        if self.filename_save_chart:
            chart_temp = open(os.path.join(father_path, 'temp/temp_GF.jpg'), "rb")
            chart_content = chart_temp.read()
            chart_save = open(self.filename_save_chart, "wb")
            chart_save.write(chart_content)
            chart_save.close()
            chart_temp.close()

    def pushButton_w_tofile_clicked(self):
        if self.Ispredict_over:
            self.data_add_copy = self.data_add.copy()
            zero_list = [None] * 12
            zero_list.extend(self.data_add_copy)
            self.data_add_copy = zero_list
            # print(len(self.data_add_copy))
            # print(self.data_add_copy)

            self.filename_save_excel = ''
            self.filename_save_excel, ftype = QtWidgets.QFileDialog.getSaveFileName \
                (self, 'Save file', os.path.join(father_path, 'result_save/result_excel'), "Excel(*.xlsx)")

            if self.filename_save_excel:
                write_tofile(self.filename_select, self.filename_save_excel, self.data_add_copy)
        else:
            QMessageBox.critical(self, 'Error', '请先完成预测')

    # 文件开始预测按钮响应
    def pushButton_predict_file_clicked(self):
        if self.filename_select:
            self.label_chart.setPixmap(QPixmap(os.path.join(father_path, 'resource/waiting.png')))
            QtWidgets.QApplication.processEvents()  # 刷新，否则图片不显示
            self.data_add = ''
            self.data_add = model_training(self.filename_select, False)
            if self.data_add:
                self.label_chart.setPixmap(QPixmap(os.path.join(father_path, 'temp/temp_GF.jpg')))
                self.Ispredict_over = True
                QMessageBox.information(self, 'Message', '预测完成')
            else:
                self.label_chart.clear()
                QMessageBox.critical(self, 'Error', '请选择规范的文件')
        else:
            QMessageBox.critical(self, 'Error', '请先选择文件')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = MainWidget_GF()
    ui.show()
    sys.exit(app.exec_())
