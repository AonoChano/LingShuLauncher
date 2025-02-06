import sys, math, os, json
import win32com.client  # 用于处理 .lnk 快捷方式
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QGridLayout, QFileDialog,
                             QFrame, QVBoxLayout, QFileIconProvider, QCheckBox)
from PyQt5.QtCore import Qt, QPoint, QSize, QFileInfo
from PyQt5.QtGui import QPainter, QPen, QColor, QIcon

CONFIG_FILE = "launcher_config.json"

class ProgramButton(QPushButton):
    def __init__(self, path, icon, icon_size, parentLauncher):
        super().__init__()
        self.path = path
        self.parentLauncher = parentLauncher
        self.setFixedSize(icon_size, icon_size)
        if not icon.isNull():
            self.setIcon(icon)
            # 将图标大小设置为比按钮略小，防止被截断
            self.setIconSize(QSize(icon_size - 50, icon_size - 50))
        else:
            self.setText("App")
        self.setStyleSheet("QPushButton { border: none; background-color: transparent; }")
        # 用于拖拽排序
        self.dragStartPos = None


    def getShortcutInfo(lnk_path):
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(lnk_path)
        target = shortcut.Targetpath
        icon_location = shortcut.IconLocation  # 格式可能为 "C:\Path\to\App.exe,0"
        return target, icon_location

    def mousePressEvent(self, event):
        # 在布局模式下，允许中键删除程序
        if event.button() == Qt.MiddleButton and self.parentLauncher.layoutMode.isChecked():
            self.parentLauncher.deleteProgram(self.path)
            return
        # 右键按下，在布局模式下启动拖动排序（这里仅打印信息，实际实现需增加拖放逻辑）
        if event.button() == Qt.RightButton and self.parentLauncher.layoutMode.isChecked():
            self.dragStartPos = event.pos()
            self.parentLauncher.startReorderDrag(self)
            return
        # 左键：启动程序
        super().mousePressEvent(event)

class Launcher(QWidget):
    def __init__(self):
        super().__init__()
        # 加载保存的程序配置（列表，每项为 {"path": 路径}）
        self.programs = []
        self.loadConfig()
        self._startPos = None  # 用于拖动窗口
        self.icon_size = self.iconSize()
        self.grid_columns = 3
        self.spacing = 10
        self.padding = 20  # 边距
        self.initUI()

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(500, 300)
        self.center()

        # 背景框
        self.bgFrame = QFrame(self)
        self.bgFrame.setStyleSheet("""
            QFrame {
                background-color: rgba(50, 50, 50, 200);
                border: 1px solid rgb(180, 180, 180);
                border-radius: 5px;
            }
        """)
        self.mainLayout = QVBoxLayout(self.bgFrame)
        self.mainLayout.setContentsMargins(self.padding, 30, self.padding, self.padding)
        self.gridLayout = QGridLayout()
        self.gridLayout.setSpacing(self.spacing)
        self.mainLayout.addLayout(self.gridLayout)

        # 关闭按钮
        self.closeButton = QPushButton("×", self.bgFrame)
        self.closeButton.setFixedSize(20, 20)
        self.closeButton.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                font-size: 16px;
            }
            QPushButton:hover {
                color: red;
            }
        """)
        self.closeButton.clicked.connect(self.close)

        # “布局模式”复选框（左上角），勾选时显示➕按钮，允许删除与拖动排序
        self.layoutMode = QCheckBox("布局模式", self.bgFrame)
        self.layoutMode.setStyleSheet("QCheckBox { color: white; }")
        self.layoutMode.setChecked(False)
        self.layoutMode.stateChanged.connect(lambda state: (self.updateGrid(), self.saveConfig()))


        # “➕”按钮，用于添加程序
        self.addButton = QPushButton("➕")
        self.addButton.setFixedSize(self.iconSize(), self.iconSize())
        self.addButton.setStyleSheet("""
            QPushButton {
                border: 2px dashed gray;
                background-color: transparent;
                color: white;
                font-size: 24px;
            }
            QPushButton:hover {
                border-color: white;
            }
        """)
        self.addButton.clicked.connect(self.addProgram)

        self.updateGrid()

    def center(self):
        screen = QApplication.desktop().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())//2, (screen.height()-size.height())//2)

    def iconSize(self):
        screen = QApplication.desktop().screenGeometry()
        return max(50, screen.width() // 20)

    def addProgram(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择程序", "", "Executable Files (*.exe);;All Files (*)")
        if path:
            self.programs.append({"path": path})
            self.saveConfig()
            self.updateGrid()

    def deleteProgram(self, path):
        self.programs = [p for p in self.programs if p["path"] != path]
        self.saveConfig()
        self.updateGrid()

    def updateGrid(self):
        # 清空布局
        while self.gridLayout.count():
            item = self.gridLayout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
        # 总项目数：程序图标 + 如果布局模式开启则添加➕按钮
        total = len(self.programs) + (1 if self.layoutMode.isChecked() else 0)
        cols = math.ceil(math.sqrt(total)) if total > 0 else 1
        rows = math.ceil(total / cols)

        icon_size = self.iconSize()
        index = 0
        icon_provider = QFileIconProvider()
        for prog in self.programs:
            path = prog["path"]
            file_info = QFileInfo(path)
            # 检查是否为 .lnk 快捷方式
            if path.lower().endswith(".lnk"):
                target, icon_location = getShortcutInfo(path)
                if icon_location:
                    # icon_location 可能形如 "C:\Program Files\xxx\xxx.exe,0"，分割取文件部分
                    icon_path = icon_location.split(",")[0]
                    file_info = QFileInfo(icon_path)
                else:
                    # 如果没有指定 icon_location，则退回到目标程序路径
                    file_info = QFileInfo(target)
            icon = icon_provider.icon(file_info)
            btn = ProgramButton(path, icon, icon_size, self)
            # 正常点击启动程序（已经在 ProgramButton 内处理了中键删除与右键拖动）
            btn.clicked.connect(lambda checked, p=path: self.startProgram(p))
            row = index // cols
            col = index % cols
            self.gridLayout.addWidget(btn, row, col)
            index += 1

        # 如果布局模式开启，则显示➕按钮
        if self.layoutMode.isChecked():
            row = index // cols
            col = index % cols
            self.addButton.setFixedSize(icon_size, icon_size)
            self.gridLayout.addWidget(self.addButton, row, col)

        # 调整窗口大小
        new_width = cols * (icon_size + self.spacing) + self.padding * 2 - self.spacing
        new_height = rows * (icon_size + self.spacing) + 30 + self.padding * 2 - self.spacing
        self.bgFrame.resize(new_width, new_height)
        self.resize(self.bgFrame.size())
        # 关闭按钮放右上角
        self.closeButton.move(self.bgFrame.width() - self.closeButton.width() - 5, 5)
        # 布局模式复选框放左上角
        self.layoutMode.move(5, 5)

    def startProgram(self, path):
        print(f"启动程序: {path}")
        try:
            os.startfile(path)
        except Exception as e:
            print(f"启动失败: {e}")

    def startReorderDrag(self, btn):
        # 这里只打印提示，具体拖拽排序实现比较复杂，需要处理拖放事件和交换self.programs中的顺序
        print(f"开始拖拽排序: {btn.path}")
        # 可考虑记录拖拽开始位置和目标位置，完成后交换列表中的项目，再调用 updateGrid()

    def loadConfig(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    self.programs = config.get("programs", [])
                    # 若配置文件中没有设置，则默认使用 False
                    layout_mode = config.get("layoutMode", False)
                    self.layoutModeDefault = layout_mode
            except Exception as e:
                print("加载配置失败:", e)
                self.programs = []
                self.layoutModeDefault = False
        else:
            self.programs = []
            self.layoutModeDefault = False


    import sys, math, os, json
import win32com.client  # 用于处理 .lnk 快捷方式
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QGridLayout, QFileDialog,
                             QFrame, QVBoxLayout, QFileIconProvider, QCheckBox)
from PyQt5.QtCore import Qt, QPoint, QSize, QFileInfo
from PyQt5.QtGui import QPainter, QPen, QColor, QIcon

CONFIG_FILE = "launcher_config.json"

class ProgramButton(QPushButton):
    def __init__(self, path, icon, icon_size, parentLauncher):
        super().__init__()
        self.path = path
        self.parentLauncher = parentLauncher
        self.setFixedSize(icon_size, icon_size)
        if not icon.isNull():
            self.setIcon(icon)
            # 将图标大小设置为比按钮略小，防止被截断
            self.setIconSize(QSize(icon_size - 50, icon_size - 50))
        else:
            self.setText("App")
        self.setStyleSheet("QPushButton { border: none; background-color: transparent; }")
        # 用于拖拽排序
        self.dragStartPos = None


    def getShortcutInfo(lnk_path):
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(lnk_path)
        target = shortcut.Targetpath
        icon_location = shortcut.IconLocation  # 格式可能为 "C:\Path\to\App.exe,0"
        return target, icon_location

    def mousePressEvent(self, event):
        # 在布局模式下，允许中键删除程序
        if event.button() == Qt.MiddleButton and self.parentLauncher.layoutMode.isChecked():
            self.parentLauncher.deleteProgram(self.path)
            return
        # 右键按下，在布局模式下启动拖动排序（这里仅打印信息，实际实现需增加拖放逻辑）
        if event.button() == Qt.RightButton and self.parentLauncher.layoutMode.isChecked():
            self.dragStartPos = event.pos()
            self.parentLauncher.startReorderDrag(self)
            return
        # 左键：启动程序
        super().mousePressEvent(event)

class Launcher(QWidget):
    def __init__(self):
        super().__init__()
        # 加载保存的程序配置（列表，每项为 {"path": 路径}）
        self.programs = []
        self.loadConfig()
        self._startPos = None  # 用于拖动窗口
        self.icon_size = self.iconSize()
        self.grid_columns = 3
        self.spacing = 10
        self.padding = 20  # 边距
        self.initUI()

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(500, 300)
        self.center()

        # 背景框
        self.bgFrame = QFrame(self)
        self.bgFrame.setStyleSheet("""
            QFrame {
                background-color: rgba(50, 50, 50, 200);
                border: 1px solid rgb(180, 180, 180);
                border-radius: 5px;
            }
        """)
        self.mainLayout = QVBoxLayout(self.bgFrame)
        self.mainLayout.setContentsMargins(self.padding, 30, self.padding, self.padding)
        self.gridLayout = QGridLayout()
        self.gridLayout.setSpacing(self.spacing)
        self.mainLayout.addLayout(self.gridLayout)

        # 关闭按钮
        self.closeButton = QPushButton("×", self.bgFrame)
        self.closeButton.setFixedSize(20, 20)
        self.closeButton.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                font-size: 16px;
            }
            QPushButton:hover {
                color: red;
            }
        """)
        self.closeButton.clicked.connect(self.close)

        # “布局模式”复选框（左上角），勾选时显示➕按钮，允许删除与拖动排序
        self.layoutMode = QCheckBox("布局模式", self.bgFrame)
        self.layoutMode.setStyleSheet("QCheckBox { color: white; }")
        self.layoutMode.setChecked(False)
        self.layoutMode.stateChanged.connect(self.updateGrid)

        # “➕”按钮，用于添加程序
        self.addButton = QPushButton("➕")
        self.addButton.setFixedSize(self.iconSize(), self.iconSize())
        self.addButton.setStyleSheet("""
            QPushButton {
                border: 2px dashed gray;
                background-color: transparent;
                color: white;
                font-size: 24px;
            }
            QPushButton:hover {
                border-color: white;
            }
        """)
        self.addButton.clicked.connect(self.addProgram)

        self.updateGrid()

    def center(self):
        screen = QApplication.desktop().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())//2, (screen.height()-size.height())//2)

    def iconSize(self):
        screen = QApplication.desktop().screenGeometry()
        return max(50, screen.width() // 20)

    def addProgram(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择程序", "", "Executable Files (*.exe);;All Files (*)")
        if path:
            self.programs.append({"path": path})
            self.saveConfig()
            self.updateGrid()

    def deleteProgram(self, path):
        self.programs = [p for p in self.programs if p["path"] != path]
        self.saveConfig()
        self.updateGrid()

    def updateGrid(self):
        # 清空布局
        while self.gridLayout.count():
            item = self.gridLayout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
        # 总项目数：程序图标 + 如果布局模式开启则添加➕按钮
        total = len(self.programs) + (1 if self.layoutMode.isChecked() else 0)
        cols = math.ceil(math.sqrt(total)) if total > 0 else 1
        rows = math.ceil(total / cols)

        icon_size = self.iconSize()
        index = 0
        icon_provider = QFileIconProvider()
        for prog in self.programs:
            path = prog["path"]
            file_info = QFileInfo(path)
            # 检查是否为 .lnk 快捷方式
            if path.lower().endswith(".lnk"):
                target, icon_location = getShortcutInfo(path)
                if icon_location:
                    # icon_location 可能形如 "C:\Program Files\xxx\xxx.exe,0"，分割取文件部分
                    icon_path = icon_location.split(",")[0]
                    file_info = QFileInfo(icon_path)
                else:
                    # 如果没有指定 icon_location，则退回到目标程序路径
                    file_info = QFileInfo(target)
            icon = icon_provider.icon(file_info)
            btn = ProgramButton(path, icon, icon_size, self)
            # 正常点击启动程序（已经在 ProgramButton 内处理了中键删除与右键拖动）
            btn.clicked.connect(lambda checked, p=path: self.startProgram(p))
            row = index // cols
            col = index % cols
            self.gridLayout.addWidget(btn, row, col)
            index += 1

        # 如果布局模式开启，则显示➕按钮
        if self.layoutMode.isChecked():
            row = index // cols
            col = index % cols
            self.addButton.setFixedSize(icon_size, icon_size)
            self.gridLayout.addWidget(self.addButton, row, col)

        # 调整窗口大小
        new_width = cols * (icon_size + self.spacing) + self.padding * 2 - self.spacing
        new_height = rows * (icon_size + self.spacing) + 30 + self.padding * 2 - self.spacing
        self.bgFrame.resize(new_width, new_height)
        self.resize(self.bgFrame.size())
        # 关闭按钮放右上角
        self.closeButton.move(self.bgFrame.width() - self.closeButton.width() - 5, 5)
        # 布局模式复选框放左上角
        self.layoutMode.move(5, 5)

    def startProgram(self, path):
        print(f"启动程序: {path}")
        try:
            os.startfile(path)
        except Exception as e:
            print(f"启动失败: {e}")

    def startReorderDrag(self, btn):
        # 这里只打印提示，具体拖拽排序实现比较复杂，需要处理拖放事件和交换self.programs中的顺序
        print(f"开始拖拽排序: {btn.path}")
        # 可考虑记录拖拽开始位置和目标位置，完成后交换列表中的项目，再调用 updateGrid()

    def loadConfig(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    self.programs = json.load(f)
            except Exception as e:
                print("加载配置失败:", e)
                self.programs = []
        else:
            self.programs = []

    def saveConfig(self):
        try:
            config = {
                "programs": self.programs,
                "settings": {
                    "layoutModeChecked": self.layoutMode.isChecked()
                }
            }
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print("保存配置失败:", e)


    # 窗口拖动实现
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._startPos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._startPos is not None and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self._startPos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._startPos = None


if __name__ == '__main__':
    app = QApplication(sys.argv)
    launcher = Launcher()
    launcher.show()
    sys.exit(app.exec_())



    # 窗口拖动实现
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._startPos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._startPos is not None and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self._startPos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._startPos = None


if __name__ == '__main__':
    app = QApplication(sys.argv)
    launcher = Launcher()
    launcher.show()
    sys.exit(app.exec_())

