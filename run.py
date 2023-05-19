# -*- coding:utf-8 -*-
# 主程序运行文件
# author: 东方鹗
# B站: https://space.bilibili.com/194359739
# 知乎: https://www.zhihu.com/people/eastossifrage
# CSDN: https://blog.csdn.net/os373

import sys
from PyQt5.Qt import QMainWindow, QTableWidget, QApplication
from tabDockWidget import TabDockWidget


class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.tab = TabDockWidget()

        self.initUI()

    def initUI(self):
        for i in range(5):
            tb = QTableWidget()
            tb.setRowCount(i + 5)
            tb.setColumnCount(i + 2)
            self.tab.addTab(tb, "Tab{}".format(i + 1))
        self.setCentralWidget(self.tab)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.resize(1024, 768)
    window.show()
    sys.exit(app.exec_())
