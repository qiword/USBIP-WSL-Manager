from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QAbstractScrollArea,
    QHBoxLayout,
    QHeaderView,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from qfluentwidgets import (
    BodyLabel,
    CardWidget,
)

from utils.constants import CONTAINER_HEIGHT, TABLE_COLUMNS
from utils.i18n import tr


class _NoContextMenuTable(QTableWidget):
    """禁用原生右键菜单的 QTableWidget"""

    def contextMenuEvent(self, a0):
        pass


class DeviceTable(CardWidget):
    """设备表格组件"""

    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.title = title
        self.devices = []
        self.table: _NoContextMenuTable | None = None

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(5)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        list_title = BodyLabel(self.title)
        list_title.setFont(QFont("Microsoft YaHei", 11, QFont.Weight.Bold))
        header_layout.addWidget(list_title)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        table_container = QWidget()
        table_container.setMinimumHeight(CONTAINER_HEIGHT["TABLE"])
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(0, 0, 0, 0)

        self.table = _NoContextMenuTable()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels([tr("detail_name"), tr("detail_action")])
        self.setup_table_style()
        self.setup_table_behavior()

        table_layout.addWidget(self.table)
        layout.addWidget(table_container)

    def setup_table_style(self):
        self.table.setStyleSheet("""
            QTableWidget {
                border: none;
                background-color: transparent;
                outline: none;
            }
            QTableWidget:focus {
                outline: none;
                border: none;
            }
            QTableWidget::item {
                padding: 2px 6px;
                min-height: 24px;
                outline: none;
                border: none;
            }
            QTableWidget::item:focus {
                outline: none;
                border: none;
                background-color: transparent;
            }
            QTableWidget::item:selected {
                background-color: #eeeeee;
                outline: none;
            }
            QTableWidget::item:selected:focus {
                background-color: #eeeeee;
                outline: none;
                border: none;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 4px 6px;
                border: none;
                border-bottom: 2px solid #e0e0e0;
                font-weight: bold;
                color: #616161;
                min-height: 28px;
            }
            QTableWidget QTableCornerButton::section {
                background-color: #f5f5f5;
                border: none;
                border-bottom: 2px solid #e0e0e0;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 10px;
                border-radius: 5px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                min-height: 30px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a0a0a0;
            }
            QScrollBar:horizontal {
                border: none;
                background: #f0f0f0;
                height: 10px;
                border-radius: 5px;
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background: #c0c0c0;
                min-width: 30px;
                border-radius: 5px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #a0a0a0;
            }
        """)

    def setup_table_behavior(self):
        assert self.table is not None
        self.table.verticalHeader().setDefaultSectionSize(32)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Fixed
        )
        self.table.setColumnWidth(1, TABLE_COLUMNS["ACTION"])

        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.table.setSizeAdjustPolicy(
            QAbstractScrollArea.SizeAdjustPolicy.AdjustToContentsOnFirstShow
        )
        self.table.setMinimumHeight(120)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

    def populate_table(self, devices, create_action_callback=None):
        assert self.table is not None
        self.devices = devices
        self.table.setRowCount(len(devices))

        for row, device in enumerate(devices):
            tooltip = (
                f"BUSID: {device.get('busid') or '-'}\n"
                f"VID:PID: {device.get('vid', '')}:{device.get('pid', '')}\n"
                f"\u72b6\u6001: {device.get('status', '')}"
            )
            name_item = QTableWidgetItem(device["name"])
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            name_item.setToolTip(tooltip)
            name_item.setData(Qt.ItemDataRole.UserRole, device.get("busid", ""))
            self.table.setItem(row, 0, name_item)

            if create_action_callback:
                create_action_callback(self.table, row, device)

    def get_table(self):
        return self.table

    def get_devices(self):
        return self.devices
