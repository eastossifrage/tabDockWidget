# -*- coding:utf-8 -*-
# 用于显示拖拽过程中的 tab 标签
# author: 东方鹗
# B站: https://space.bilibili.com/194359739
# 知乎: https://www.zhihu.com/people/eastossifrage
# CSDN: https://blog.csdn.net/os373

from PyQt5.Qt import QEvent, QPushButton
from PyQt5.QtCore import Qt


class FloatingTab(QPushButton):
    """ 用于显示拖拽过程中的 tab 标签
    """
    def __init__(self, parent=None):
        super(FloatingTab, self).__init__(parent)

        self.initUI()

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setStyleSheet("border-style: outset;background-color: whitesmoke;")
        self.hide()

    def event(self, a0: QEvent) -> bool:
        if a0.type() == QEvent.DeferredDelete:
            print("floatingTab delete")
        return super(FloatingTab, self).event(a0)

