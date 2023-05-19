# -*- coding:utf-8 -*-
# 制作可拖拽，可 Dock 的 tabWidget
# author: 东方鹗
# B站: https://space.bilibili.com/194359739
# 知乎: https://www.zhihu.com/people/eastossifrage
# CSDN: https://blog.csdn.net/os373

from PyQt5.Qt import QTabWidget, QWidget, QCursor, QRect, QRegion, QPoint, QHBoxLayout, QApplication, \
     QMouseEvent, QEvent, QObject, QIcon
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import qApp
from tabDockWidget.middleware import DragTabInfo, FloatingTab, Shadow, Splitter


class TabWidget(QTabWidget):
    """ 自定义 tabWidget
    """
    instances = []

    dragTabInfo = DragTabInfo()  # 保存当前要拖动的 tab 的信息
    floatingTab = None     # 用以保存 tab 标签拖出 tabBar 区域后的浮动标签实例
    floatingWidget = None  # 用以保存 tab 标签拖出 tabBar 区域后的浮动 widget 实例
    splitter = None        # 用以保存 tabWidget 外围的分割器
    shadow = None          # 用以保存阴影中显示的 widget 实例
    flag = None            # 用以保存鼠标在 tabWidget 中的位置

    def __init__(self, parent=None):
        super(TabWidget, self).__init__(parent)
        self.parent = parent
        self.clickPoint = QPoint()
        self.canDrag = False
        self.floatingFlag = False  # False 时显示 tab，True 显示 widget

        self.initUI()

    def initUI(self):
        self.tabBar().installEventFilter(self)
        self.setMovable(True)  # 设置允许在 tabBar 内部移动的功能
        self.setTabsClosable(True)  # tab 显示关闭按钮
        self.tabCloseRequested.connect(self.closeTab)

        TabWidget.instances.insert(0, self)  # 添加当前实例到列表最开头

    def event(self, a0: QEvent) -> bool:
        if a0.type() == QEvent.DeferredDelete:
            # print("{} tabWidget delete".format(self))
            TabWidget.instances.remove(self)  # 删除当前实例
        return super(TabWidget, self).event(a0)

    def closeTab(self, index):
        if self.count() > 1:
            self.widget(index).deleteLater()  # 调用顺序不能换
            self.removeTab(index)
        else:
            self.close()
            self.parentWidget().setParent(None)  # 注意顺序，该项优先
            self.setParent(None)                 # 注意顺序，该项靠后
            self.tabBar().deleteLater()
            self.deleteLater()
            self.destroyUnnecessaryWindow()

    def eventFilter(self, a0: 'QObject', a1: 'QEvent') -> bool:
        if a0 == self.tabBar() and a1.type() == a1.MouseButtonPress:
            self.mouseInTabBarPress(QMouseEvent(a1))
        elif a0 == self.tabBar() and a1.type() == a1.MouseButtonRelease:
            self.mouseInTabBarRelease(QMouseEvent(a1))
        elif a0 == self.tabBar() and a1.type() == a1.MouseMove:
            self.mousePressedMove(QMouseEvent(a1))

        return super(TabWidget, self).eventFilter(a0, a1)

    @staticmethod
    def theseRegion(a0: QTabWidget):
        """
        自定义实现得到当前 tabWidget 以及子控件 tabBar 的 Region 操作。
        :param a0:
        :return: tabBarRegion, tabWidgetRegion, tabWidgetWholeRegion
        """
        tabBarRegion = a0.tabBar().visibleRegion()
        tabBarRegion.translate(a0.tabBar().mapToGlobal(QPoint(0, 0)))  # 获取该 tabBar 实例在屏幕中的可见区域
        tabWidgetRect = a0.contentsRect()  # 获取该 tabWidget 实例在屏幕中的全部区域
        tabWidgetRect.translate(a0.mapToGlobal(QPoint(0, 0)))
        tabWidgetWholeRegion = QRegion(tabWidgetRect)
        tabWidgetRegion = tabWidgetWholeRegion.xored(tabBarRegion)  # 获取 tabWidget 区域以及tabBar区域的差集

        return tabBarRegion, tabWidgetRegion, tabWidgetWholeRegion

    def mouseInTabBarPress(self, a1: QMouseEvent):
        self.beTop()
        if a1.button() == Qt.LeftButton:
            currentIdx = self.tabBar().tabAt(a1.pos())  # 鼠标按下时，对应的标签的 index
            if TabWidget.floatingTab is None and TabWidget.floatingWidget is None:
                # print("鼠标在当前实例的 tabBar 区域按下，并且没有浮动标签")
                self.setCurrentIndex(currentIdx)  # 鼠标按下时，显示当前标签对应的界面内容
                TabWidget.dragTabInfo = DragTabInfo(  # 保存当前拖拽的 tab 的信息
                    self.tabBar().tabRect(currentIdx),
                    self.currentWidget(),
                    self.tabText(currentIdx),
                    self.tabIcon(currentIdx),
                    self.tabToolTip(currentIdx),
                    self.tabWhatsThis(currentIdx)
                )
                self.clickPoint = a1.globalPos()
            else:
                # print("鼠标在当前实例的 tabBar 区域按下，并且存在浮动标签")
                TabWidget.floatingTab = None
                TabWidget.floatingWidget = None

                self.insertTab(currentIdx,
                               TabWidget.dragTabInfo.thisWidget,
                               TabWidget.dragTabInfo.tabIcon,
                               TabWidget.dragTabInfo.tabText)
                self.setTabToolTip(currentIdx, TabWidget.dragTabInfo.tabToolTip)
                self.setTabWhatsThis(currentIdx, TabWidget.dragTabInfo.tabWhatsThis)
                self.setCurrentWidget(TabWidget.dragTabInfo.thisWidget)

            self.tabBar().grabMouse()  # 从 tabBar 开始按下鼠标，仅仅 tabBar 捕获鼠标

    def mouseInTabBarRelease(self, a1: QMouseEvent):
        if a1.button() == Qt.LeftButton:
            # print("鼠标在当前实例的 tabBar 区域松开")
            TabWidget.floatingTab = None
            TabWidget.floatingWidget = None
            TabWidget.shadow = None
            TabWidget.dragTabInfo = DragTabInfo()
            TabWidget.flag = None
            self.destroyUnnecessaryWindow()  # 鼠标松开后，删除无用控件的实例
            self.clickPoint = QPoint()
            self.canDrag = False
            self.tabBar().releaseMouse()  # tabBar 区域释放鼠标

    def mousePressedMove(self, a1: QMouseEvent):
        # print("鼠标在当前实例的 tabBar 区域移动")
        if TabWidget.dragTabInfo.thisWidget is None:
            return

        if not self.canDrag:
            movedLength = (a1.globalPos() - self.clickPoint).manhattanLength()
            self.canDrag = movedLength > qApp.startDragDistance()

        if TabWidget.floatingTab is None or TabWidget.floatingWidget is None and self.canDrag:
            tabBarRegion, tabWidgetRegion, _ = self.theseRegion(self)
            if tabBarRegion.contains(a1.globalPos()):
                return
            else:
                tabWidgetPressEvent = self.createMouseEvent(  # 创建 mousePress 事件，从 tab 标签拖出重新进入 tabWidget 区域开始
                    QEvent.MouseButtonPress, self.mapFromGlobal(a1.globalPos()))
                QApplication.postEvent(self, tabWidgetPressEvent)  # 通过 tabWidget 的 mousePress 事件来进行拖出操作
                return

    def mousePressEvent(self, a0: QMouseEvent) -> None:
        self.beTop()
        if a0.button() == Qt.LeftButton and TabWidget.floatingTab is None and TabWidget.floatingWidget is None \
                and TabWidget.dragTabInfo.thisWidget:
            # print("鼠标在当前实例的 tabWidget 区域按下，并且没有浮动标签")
            TabWidget.dragTabInfo.thisWidget.setParent(None)  # 删除对应标签， 将标签脱离母体
            if self.count() == 0:  # 如果当前 tabWidget 的标签数为 0
                if self.parentWidget().count() == 2:    # 且原来处在包含有 2 个控件的 splitter 中
                    # 以下内容是获取旁边的 tabWidget 实例 ====================
                    if self.parentWidget().indexOf(self) == 0:
                        inst = self.parentWidget().widget(1)
                    else:
                        inst = self.parentWidget().widget(0)
                    # ============================================
                    grandpa = self.parentWidget().parentWidget()
                    # 以下一行语句是获取原来包含有两个控件的 splitter 在外层 splitter 中的位置
                    index = grandpa.indexOf(self.parentWidget())   # 必须在 setParent 函数之前
                    self.parentWidget().setParent(None)
                    self.setParent(None)  # 脱离原有的 splitter
                    inst.setParent(None)  # 脱离原有的 splitter
                    grandpa.insertWidget(index, inst)  # 插入上层 splitter 中
                    grandpa.setSizes([60000, 60000])
                elif self.parentWidget().count() == 1:   # 处理最外层的 splitter
                    self.parentWidget().setParent(None)
                    self.setParent(None)  # 脱离原有的 splitter
                self.move(QPoint(-self.width(), -self.height()))

                # 以下是为了设置对应的拖拽标签图标、大小和内容
            TabWidget.floatingTab = FloatingTab()
            TabWidget.floatingTab.setIcon(TabWidget.dragTabInfo.tabIcon)
            TabWidget.floatingTab.setText(TabWidget.dragTabInfo.tabText)
            TabWidget.floatingTab.setGeometry(TabWidget.dragTabInfo.thisTabRect)

            # 以下是为了设置对应的拖拽 widget，也就是 tabWidget 区域外显示的拖拽控件
            TabWidget.floatingWidget = TabWidget.dragTabInfo.thisWidget
            TabWidget.floatingWidget.setWindowFlags(Qt.FramelessWindowHint)
            TabWidget.splitter = Splitter()
            TabWidget.shadow = Shadow()
            # ====================================================
        elif a0.button() == Qt.LeftButton and TabWidget.floatingTab and TabWidget.floatingWidget:
            # print("鼠标在当前实例的 tabWidget 区域按下，并且存在浮动标签")
            TabWidget.flag = None   # 刚开始点击 tabWidget 区域, shadow 要隐藏
        self.grabMouse()  # 从 tabWidget 开始按下鼠标，仅仅 tabWidget 捕获鼠标
        super(TabWidget, self).mousePressEvent(a0)

    def mouseMoveEvent(self, a0: QMouseEvent) -> None:
        # print("鼠标在当前实例的 tabWidget 内移动")
        if TabWidget.floatingTab and TabWidget.floatingWidget:  # 如果存在浮动控件
            for tabWidgetInst in TabWidget.instances:  # 遍历所有实例，实现跨实例拖拽的功能
                if tabWidgetInst.parent.region().contains(a0.globalPos()):
                    self.floatingFlag = False
                else:
                    self.floatingFlag = True

                tabBarRegion, tabWidgetRegion, _ = self.theseRegion(tabWidgetInst)

                if tabBarRegion.contains(a0.globalPos()):
                    TabWidget.shadow.hide()         # 鼠标进入 tabBar 区域，阴影不显示
                    tabBarPressEvent = self.createMouseEvent(  # 创建 mousePress 事件，
                                                               # 从 tabWidget 区域拖出重新进入 tab 标签区域开始
                        QEvent.MouseButtonPress, tabWidgetInst.tabBar().mapFromGlobal(a0.globalPos()))
                    QApplication.postEvent(tabWidgetInst.tabBar(), tabBarPressEvent)  # 通过 tabBar 的 mousePress 事件来进行拖入操作
                    return
                elif tabWidgetRegion.contains(a0.globalPos()):
                    if tabWidgetInst == self:
                        TabWidget.shadow.activateWindow()
                        self.displayShadow()
                        break
                    else:
                        tabWidgetPressEvent = self.createMouseEvent(  # 创建 mousePress 事件
                            QEvent.MouseButtonPress, tabWidgetInst.mapFromGlobal(a0.globalPos()))
                        QApplication.postEvent(tabWidgetInst,
                                               tabWidgetPressEvent)  # 通过 tabWidget 的 mousePress 事件来进行界面切换
                        return
                else:
                    if tabWidgetInst == self:
                        TabWidget.shadow.hide()  # 鼠标离开 tabWidget 本实例区域，阴影不显示

            TabWidget.floatingTab.move(
                a0.globalPos() - TabWidget.floatingTab.rect().center())  # 浮动 tab 标签跟随鼠标
            TabWidget.floatingWidget.move(a0.globalPos())  # widget 控件跟随鼠标
            if self.floatingFlag:
                TabWidget.floatingTab.hide()
                TabWidget.floatingWidget.show()
            else:
                TabWidget.floatingWidget.hide()
                TabWidget.floatingTab.show()

    def mouseReleaseEvent(self, a0: QMouseEvent) -> None:
        if a0.button() == Qt.LeftButton and TabWidget.floatingTab and TabWidget.floatingWidget:
            tabBarRegion, tabWidgetRegion, _ = self.theseRegion(self)
            if tabBarRegion.contains(a0.globalPos()):
                pass
            elif tabWidgetRegion.contains(a0.globalPos()):
                # print("鼠标在当前实例的 tabWidget 内松开")
                if self.count() < 1:
                    parentRect = self.parent.geometry()
                    gPos = QCursor.pos() - TabWidget.floatingTab.rect().center()
                    winRct = QRect(gPos.x(), gPos.y(), parentRect.width(), parentRect.height())
                    self.createNewWindow(winRct, TabWidget.dragTabInfo)
                else:
                    self.createNewDock(TabWidget.flag, TabWidget.dragTabInfo)
            else:
                parentRect = self.parent.geometry()
                gPos = QCursor.pos() - TabWidget.floatingTab.rect().center()
                winRct = QRect(gPos.x(), gPos.y(), parentRect.width(), parentRect.height())
                self.createNewWindow(winRct, TabWidget.dragTabInfo)
                # print("鼠标在当前实例的 tabWidget 外松开")

            TabWidget.floatingTab = None
            TabWidget.floatingWidget = None
            TabWidget.dragTabInfo = DragTabInfo()
            TabWidget.shadow = None
            TabWidget.flag = None
            self.destroyUnnecessaryWindow()  # 鼠标松开后，删除无用控件的实例
            self.clickPoint = QPoint()
            self.canDrag = False
        self.releaseMouse()  # tabWidget 区域释放鼠标
        super(TabWidget, self).mouseReleaseEvent(a0)

    def beTop(self):
        """ 如果鼠标经过的 tabWidget 的区域，将 tabWidget 控件置顶
        """
        if TabWidget.instances.index(self) != 0:
            TabWidget.instances.remove(self)
            TabWidget.instances.insert(0, self)
            if not self.parent.isActiveWindow():
                self.parent.activateWindow()        # 控件置顶

    def displayShadow(self):
        if self.count() > 0:
            widgetRect = self.currentWidget().contentsRect()
            widgetRect.translate(self.currentWidget().mapToGlobal(QPoint(0, 0)))  # 获取该 Widget 实例在屏幕中的区域
            topArea = QRect(widgetRect.x(), widgetRect.y(),
                            widgetRect.width(), int(widgetRect.height() * 0.2))
            rightArea = QRect(widgetRect.x() + int(widgetRect.width() * 0.8),
                              widgetRect.y() + int(widgetRect.height() * 0.2),
                              int(widgetRect.width() * 0.2),
                              widgetRect.height() - int(widgetRect.height() * 0.4))
            bottomArea = QRect(widgetRect.x(),
                               widgetRect.y() + int(widgetRect.height() * 0.8),
                               widgetRect.width(), int(widgetRect.height() * 0.2))
            leftArea = QRect(widgetRect.x(),
                             widgetRect.y() + int(widgetRect.height() * 0.2),
                             int(widgetRect.width() * 0.2),
                             widgetRect.height() - int(widgetRect.height() * 0.4))
            if topArea.contains(QCursor.pos()):
                topRect = QRect(widgetRect.x(),
                                widgetRect.y(),
                                widgetRect.width(),
                                int(widgetRect.height() / 2))
                TabWidget.shadow.drawRect(topRect)
                TabWidget.flag = "top"
            elif rightArea.contains(QCursor.pos()):
                rightRect = QRect(widgetRect.x() + int(widgetRect.width() / 2),
                                  widgetRect.y(),
                                  int(widgetRect.width() / 2),
                                  widgetRect.height())
                TabWidget.shadow.drawRect(rightRect)
                TabWidget.flag = "right"
            elif bottomArea.contains(QCursor.pos()):
                bottomRect = QRect(widgetRect.x(),
                                   widgetRect.y() + int(widgetRect.height() / 2),
                                   int(widgetRect.width()),
                                   int(widgetRect.height() / 2))
                TabWidget.shadow.drawRect(bottomRect)
                TabWidget.flag = "bottom"
            elif leftArea.contains(QCursor.pos()):
                leftRect = QRect(widgetRect.x(),
                                 widgetRect.y(),
                                 int(widgetRect.width() / 2),
                                 widgetRect.height())
                TabWidget.shadow.drawRect(leftRect)
                TabWidget.flag = "left"
            else:
                TabWidget.shadow.drawRect(widgetRect)
                TabWidget.flag = "all"

    @staticmethod
    def destroyUnnecessaryWindow():
        for tabWidgetInst in TabWidget.instances:
            if tabWidgetInst.count() == 0:  # 如果 tabWidget 的标签项的个数为 0
                tabWidgetInst.tabBar().deleteLater()
                tabWidgetInst.deleteLater()
        for splitterInst in Splitter.instances:
            if splitterInst.count() == 0:
                splitterInst.deleteLater()  # 注意先子控件后主控件顺序
        for tabDockInst in TabDockWidget.instances:
            if tabDockInst.hLayout.count() == 0:
                tabDockInst.deleteLater()

    def createMouseEvent(self, eventType, pos=QPoint()):
        if pos.isNull():
            gPos = QCursor.pos()
        else:
            gPos = self.mapToGlobal(pos)
        modifiers = QApplication.keyboardModifiers()

        event = QMouseEvent(eventType, pos, gPos,
                            Qt.LeftButton, Qt.LeftButton, modifiers)
        return event

    def createNewWindow(self, winRect, tabInfo):
        newWin = self.parent.__class__()
        newWin.addTab(tabInfo.thisWidget,
                      tabInfo.tabIcon,
                      tabInfo.tabText)
        newWin.setTabToolTip(0, tabInfo.tabToolTip)
        newWin.setTabWhatsThis(0, tabInfo.tabWhatsThis)
        newWin.setGeometry(winRect)
        newWin.show()

    def createNewDock(self, flag, tabInfo):
        if flag == "all":
            idx = self.addTab(TabWidget.dragTabInfo.thisWidget,
                              TabWidget.dragTabInfo.tabIcon,
                              TabWidget.dragTabInfo.tabText)
            self.setTabToolTip(idx, TabWidget.dragTabInfo.tabToolTip)
            self.setTabWhatsThis(idx, TabWidget.dragTabInfo.tabWhatsThis)
            self.setCurrentIndex(idx)
        else:
            newTabWidget = self.__class__(self.parent)
            newTabWidget.addTab(tabInfo.thisWidget,
                                tabInfo.tabIcon,
                                tabInfo.tabText)
            newTabWidget.setTabToolTip(0, tabInfo.tabToolTip)
            newTabWidget.setTabWhatsThis(0, tabInfo.tabWhatsThis)
            splitter = self.parentWidget()
            index = splitter.indexOf(self)

            if flag == "top":
                TabWidget.splitter.setOrientation(Qt.Vertical)
                TabWidget.splitter.addWidget(newTabWidget)
                TabWidget.splitter.addWidget(self)
            elif flag == "right":
                TabWidget.splitter.setOrientation(Qt.Horizontal)
                TabWidget.splitter.addWidget(self)
                TabWidget.splitter.addWidget(newTabWidget)
            elif flag == "bottom":
                TabWidget.splitter.setOrientation(Qt.Vertical)
                TabWidget.splitter.addWidget(self)
                TabWidget.splitter.addWidget(newTabWidget)
            elif flag == "left":
                TabWidget.splitter.setOrientation(Qt.Horizontal)
                TabWidget.splitter.addWidget(newTabWidget)
                TabWidget.splitter.addWidget(self)

            splitter.insertWidget(index, TabWidget.splitter)
            splitter.setSizes([60000, 60000])
            TabWidget.splitter.setSizes([60000, 60000])


class TabDockWidget(QWidget):
    """ 自定义占位用的 widget
    """
    instances = []

    def __init__(self):
        super(TabDockWidget, self).__init__()
        self.tabWidget = TabWidget(self)
        # self.vLayout = QVBoxLayout()
        self.hLayout = QHBoxLayout()
        self.splitter = Splitter()

        self.initUI()

    def initUI(self):
        self.hLayout.setContentsMargins(0, 0, 0, 0)
        # self.vLayout.setContentsMargins(0, 0, 0, 0)
        # self.splitter.setOrientation(Qt.Horizontal)
        self.splitter.addWidget(self.tabWidget)
        # self.splitter.setOrientation(Qt.Vertical)
        # self.splitter2.addWidget(self.splitter1)

        self.hLayout.addWidget(self.splitter)
        self.setLayout(self.hLayout)
        TabDockWidget.instances.insert(0, self)  # 添加当前实例到列表最开头

    def event(self, a0: QEvent) -> bool:
        if a0.type() == QEvent.DeferredDelete:
            # print("{} tabDockWidget delete".format(self))
            TabDockWidget.instances.remove(self)  # 删除当前实例
        return super(TabDockWidget, self).event(a0)

    def addTab(self, widget: QWidget, *__args):  # real signature unknown; restored from __doc__ with multiple overloads
        """
        addTab(self, QWidget, str) -> int
        addTab(self, QWidget, QIcon, str) -> int
        """
        return self.tabWidget.addTab(widget, *__args)

    def setTabIcon(self, index: int, icon: QIcon):  # real signature unknown; restored from __doc__
        """ setTabIcon(self, int, QIcon) """
        self.tabWidget.setTabIcon(index, icon)

    def setTabToolTip(self, index: int, tip: str):  # real signature unknown; restored from __doc__
        """ setTabToolTip(self, int, str) """
        self.tabWidget.setTabToolTip(index, tip)

    def setTabWhatsThis(self, index: int, text: str):  # real signature unknown; restored from __doc__
        """ setTabWhatsThis(self, int, str) """
        self.tabWidget.setTabWhatsThis(index, text)

    def region(self):
        rect = self.contentsRect()
        rect.translate(self.mapToGlobal(QPoint(0, 0)))
        return QRegion(rect)
