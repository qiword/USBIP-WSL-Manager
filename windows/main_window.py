from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QApplication, QMenu, QSystemTrayIcon
from qfluentwidgets import (
    FluentIcon,
    FluentWindow,
    NavigationItemPosition,
    setThemeColor,
)
from qfluentwidgets import FluentIcon as FIF

from utils.constants import THEME_COLOR
from utils.i18n import tr
from windows.pages.home_page import HomePage
from windows.pages.settings_page import SettingsPage


class Window(FluentWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(tr("window_title"))
        # 固定内部标题用于单实例检测
        self.setWindowIconText("USBIP-WSL-Manager")
        self.resize(1000, 800)
        self.setMinimumSize(900, 600)

        self.home_page = HomePage()
        self.settings_page = SettingsPage()

        self.initNavigation()
        setThemeColor(THEME_COLOR)

        # 系统托盘
        self._setup_tray()

    def _setup_tray(self):
        self._tray = QSystemTrayIcon(self)
        self._tray.setIcon(self.windowIcon() or QIcon("icon.svg"))
        self._tray.setToolTip(tr("window_title"))

        tray_menu = QMenu()
        show_action = QAction(tr("tray_show"), tray_menu)
        show_action.triggered.connect(self._show_from_tray)
        tray_menu.addAction(show_action)
        tray_menu.addSeparator()
        quit_action = QAction(tr("tray_quit"), tray_menu)
        quit_action.triggered.connect(QApplication.quit)
        tray_menu.addAction(quit_action)

        self._tray.setContextMenu(tray_menu)
        self._tray.activated.connect(self._on_tray_activated)
        self._tray.show()

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._show_from_tray()

    def _show_from_tray(self):
        self.showNormal()
        self.activateWindow()
        self.raise_()

    def closeEvent(self, a0):
        a0.ignore()
        self.hide()

    def initNavigation(self):
        self.addSubInterface(self.home_page, FluentIcon.HOME, tr("nav_devices"))
        self.addSubInterface(
            self.settings_page,
            FluentIcon.SETTING,
            tr("nav_settings"),
            NavigationItemPosition.BOTTOM,
        )

        nav = self.navigationInterface
        nav.setExpandWidth(120)
        nav.setCollapsible(False)
        nav.expand(useAni=False)

        nav.setStyleSheet("""
            NavigationInterface {
                background-color: #f5f5f5;
                border-right: 1px solid #e0e0e0;
            }
            NavigationInterface QPushButton {
                font-size: 14px;
            }
        """)
