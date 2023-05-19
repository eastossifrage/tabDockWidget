# -*- coding:utf-8 -*-
# 自定义占位用的 splitter
# author: 东方鹗
# B站: https://space.bilibili.com/194359739
# 知乎: https://www.zhihu.com/people/eastossifrage
# CSDN: https://blog.csdn.net/os373

from PyQt5.Qt import QEvent, QSplitter


class Splitter(QSplitter):
    """ 自定义占位用的 splitter
    """
    instances = []

    def __init__(self, parent=None):
        super(Splitter, self).__init__(parent)
        Splitter.instances.insert(0, self)  # 添加当前实例到列表最开头

    def event(self, a0: QEvent) -> bool:
        if a0.type() == QEvent.DeferredDelete:
            # print("{} splitter delete".format(self))
            Splitter.instances.remove(self)

        return super(Splitter, self).event(a0)

