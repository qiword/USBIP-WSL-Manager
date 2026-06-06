"""现代圆角右键菜单"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMenu
from qfluentwidgets import FluentIcon
from qfluentwidgets import FluentIcon as FIF

from utils.i18n import tr

# ── QSS ──────────────────────────────────────────────────────
MENU_QSS = """
    QMenu {
        background-color: #fafafa;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 6px 4px;
        min-width: 140px;
    }
    QMenu::item {
        padding: 7px 32px 7px 14px;
        border-radius: 5px;
        margin: 1px 2px;
        color: #424242;
        font-size: 12px;
    }
    QMenu::item:selected {
        background-color: #e3f2fd;
        color: #1565c0;
    }
    QMenu::item:disabled {
        color: #bdbdbd;
    }
    QMenu::separator {
        height: 1px;
        background-color: #eeeeee;
        margin: 4px 10px;
    }
    QMenu::indicator {
        width: 16px;
        height: 16px;
        margin-left: 4px;
    }
"""


def menu_action(
    menu: QMenu,
    text: str,
    icon: FluentIcon,
    slot,
    tooltip: str = "",
    enabled: bool = True,
) -> QAction:
    """添加带图标和提示的菜单项"""
    action = QAction(text, menu)
    action.setIcon(icon.icon())
    action.setEnabled(enabled)
    if tooltip:
        action.setToolTip(tooltip)
    action.triggered.connect(slot)
    menu.addAction(action)
    return action


def build_windows_context_menu(
    parent,
    is_bound_table: bool,
    busids: list[str],
    on_attach,
    on_bind,
    on_bind_only,
    on_detach,
    on_unbind,
) -> QMenu:
    """构建 Windows 设备表格的右键菜单"""
    menu = QMenu(parent)
    menu.setStyleSheet(MENU_QSS)

    if is_bound_table:
        menu_action(
            menu,
            tr("menu_attach"),
            FIF.PLAY,
            lambda: on_attach(busids),
            tooltip=tr("menu_tt_attach"),
        )
        menu.addSeparator()
        menu_action(
            menu,
            tr("menu_unbind"),
            FIF.CLOSE,
            lambda: on_unbind(busids),
            tooltip=tr("menu_tt_unbind"),
        )
    else:
        menu_action(
            menu,
            tr("menu_share_to_wsl"),
            FIF.LINK,
            lambda: on_bind(busids),
            tooltip=tr("menu_tt_share"),
        )
        menu_action(
            menu,
            tr("menu_bind_only"),
            FIF.LINK,
            lambda: on_bind_only(busids),
            tooltip=tr("menu_tt_bind_only"),
        )
    return menu


def build_wsl_context_menu(
    parent, selected_items: list, on_detach_only, on_detach, on_detail
) -> QMenu:
    """构建 WSL 列表的右键菜单"""
    menu = QMenu(parent)
    menu.setStyleSheet(MENU_QSS)

    if len(selected_items) == 1:
        menu_action(
            menu, tr("menu_wsl_detail"), FIF.INFO, lambda: on_detail(selected_items[0])
        )
        menu.addSeparator()

    busids = []
    for item in selected_items:
        d = item.data(Qt.ItemDataRole.UserRole)
        if d:
            busids.append(d.get("busid", ""))

    menu_action(
        menu,
        tr("menu_wsl_detach_only"),
        FIF.PAUSE,
        lambda: on_detach_only(busids),
        tooltip=tr("menu_tt_detach_only"),
    )
    menu_action(
        menu,
        tr("menu_wsl_detach_unbind"),
        FIF.CLOSE,
        lambda: on_detach(busids),
        tooltip=tr("menu_tt_detach_unbind"),
    )
    return menu
