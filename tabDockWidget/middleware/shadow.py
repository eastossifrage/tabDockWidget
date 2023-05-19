# -*- coding:utf-8 -*-
# 用于显示拖拽过程中的 tabWidget 上册的阴影遮罩
# author: 东方鹗
# B站: https://space.bilibili.com/194359739
# 知乎: https://www.zhihu.com/people/eastossifrage
# CSDN: https://blog.csdn.net/os373

from PyQt5.Qt import QWidget, QPainter, QEvent, QPen, QColor
from PyQt5.QtCore import Qt


class Shadow(QWidget):
    """ 用于显示拖拽过程中的 tabWidget 上册的阴影遮罩
    """
    def __init__(self):
        super(Shadow, self).__init__()

        self.initUI()

    def initUI(self):
        self.setContentsMargins(0, 0, 0, 0)
        # 设置窗口鼠标事件穿透，相当于不接收鼠标事件
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WA_TranslucentBackground)  # 设置窗口背景透明
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)  # 隐藏边框

    def paintEvent(self, event):
        """ 实现子窗体半透明效果 """
        painter = QPainter(self)
        painter.setOpacity(0.6)                         # 设置窗口透明度
        painter.setPen(QPen(Qt.gray, 1, Qt.NoPen))
        painter.setBrush(QColor("#cce8ff"))
        painter.drawRect(self.rect())

    def event(self, a0: QEvent) -> bool:
        if a0.type() == QEvent.DeferredDelete:
            print("shadow delete")
        return super(Shadow, self).event(a0)

    def drawRect(self, myRect):
        self.setGeometry(myRect)
        self.show()

