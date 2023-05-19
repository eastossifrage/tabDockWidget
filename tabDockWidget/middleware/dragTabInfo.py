# -*- coding:utf-8 -*-
# 用于保存要拖拽的 tabWidget 信息
# author: 东方鹗
# B站: https://space.bilibili.com/194359739
# 知乎: https://www.zhihu.com/people/eastossifrage
# CSDN: https://blog.csdn.net/os373


class DragTabInfo(object):
    """ 用于保存要拖拽的 tabWidget 信息
    """

    def __init__(self, thisTabRect=None, thisWidget=None,
                 tabText=None, tabIcon=None, tabToolTip=None, tabWhatsThis=None):
        self.thisTabRect = thisTabRect  # 保存原始标签的几何尺寸
        self.thisWidget = thisWidget  # 保存对应的 widget 实例
        self.tabText = tabText  # 保存原始标签的文字内容
        self.tabIcon = tabIcon  # 保存原始标签的图标
        self.tabToolTip = tabToolTip
        self.tabWhatsThis = tabWhatsThis
