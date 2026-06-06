from datetime import datetime

from PyQt6.QtCore import QSize, Qt, QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QListView,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)
from qfluentwidgets import (
    BodyLabel,
    CardWidget,
    InfoBar,
    PushButton,
)
from qfluentwidgets import FluentIcon as FIF

from utils.constants import BUTTON_SIZE
from utils.i18n import tr
from utils.usbip_error import translate_usbip_error
from utils.usbip_manager import UsbDevice, UsbipManager
from widgets.auto_resize_list import AutoResizeListWidget
from widgets.cmd_thread import CmdThread
from widgets.device_menu import build_windows_context_menu, build_wsl_context_menu
from widgets.device_table import DeviceTable


class HomePage(QWidget):
    """方案 D 布局（对齐优化版）"""

    def __init__(self):
        super().__init__()
        self.setObjectName("homePage")

        self.usbip = UsbipManager()
        self.devices_all: list[UsbDevice] = []
        self.wsl_devices: list[UsbDevice] = []
        self.table1 = None
        self.table2 = None
        self.wsl_list = None
        self._log_lines: list[str] = []
        self.global_refresh_btn = None

        self.setup_ui()
        QTimer.singleShot(300, self.refresh_all_data)

    # ==================================================================
    # UI 构建
    # ==================================================================

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(10)

        # ── 顶部工具栏（精简版：发行版选择 + 刷新） ──
        top_row = QHBoxLayout()
        top_row.setSpacing(12)

        distro_label = BodyLabel(tr("top_wsl_distro"))
        distro_label.setFont(QFont("Microsoft YaHei", 11, QFont.Weight.Bold))
        top_row.addWidget(distro_label)

        self._distro_combo = QComboBox()
        self._distro_combo.setMinimumHeight(28)
        self._distro_combo.setMaximumWidth(280)
        self._distro_combo.setMinimumWidth(200)
        self._distro_combo.setFont(QFont("Microsoft YaHei", 10))
        self._distro_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #e0e0e0; border-radius: 4px;
                padding: 2px 8px; background: #fafafa; font-size: 12px; color: #424242;
            }
            QComboBox:hover { border-color: #1565c0; }
            QComboBox QAbstractItemView {
                border: 1px solid #d0d0d0; border-radius: 4px;
                padding: 4px; background: white;
                outline: none;
            }
            QComboBox QAbstractItemView::item {
                padding: 5px 8px;
                border-radius: 4px;
                color: #333;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #e3f2fd;
                color: #1565c0;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #f0f7ff;
            }
        """)
        # 解决高分屏下弹出列表模糊的问题
        view = QListView()
        view.setFont(QFont("Microsoft YaHei", 10))
        self._distro_combo.setView(view)
        top_row.addWidget(self._distro_combo)
        top_row.addStretch()

        # 全局操作按钮（全部断开 + 清除持久化 + 刷新）
        self.panel_detach_btn = PushButton(FIF.PAUSE, tr("top_detach_all"))
        self.panel_detach_btn.setFixedSize(*BUTTON_SIZE["LARGE"])
        self.panel_detach_btn.clicked.connect(self._detach_all)
        top_row.addWidget(self.panel_detach_btn)

        self.clear_persist_btn = PushButton(FIF.DELETE, tr("top_clear_persist"))
        self.clear_persist_btn.setFixedSize(*BUTTON_SIZE["LARGE"])
        self.clear_persist_btn.clicked.connect(self._clear_persisted)
        top_row.addWidget(self.clear_persist_btn)

        self.global_refresh_btn = PushButton(FIF.SYNC, "\u5237\u65b0")
        self.global_refresh_btn.setFixedSize(*BUTTON_SIZE["LARGE"])
        self.global_refresh_btn.clicked.connect(self.refresh_all_data)
        top_row.addWidget(self.global_refresh_btn)

        main_layout.addLayout(top_row)

        body = QHBoxLayout()
        body.setSpacing(10)

        # ── 左侧 CardWidget ──
        left_card = CardWidget()
        left_layout = QVBoxLayout(left_card)
        left_layout.setContentsMargins(12, 12, 12, 12)
        left_layout.setSpacing(8)

        self.device_table1 = DeviceTable(tr("table_shareable"))
        self.table1 = self.device_table1.get_table()
        self.table1.customContextMenuRequested.connect(
            lambda pos: self.show_context_menu(pos, self.table1)
        )
        left_layout.addWidget(self.device_table1, stretch=3)

        self.device_table2 = DeviceTable(tr("table_bound"))
        self.table2 = self.device_table2.get_table()
        self.table2.customContextMenuRequested.connect(
            lambda pos: self.show_context_menu(pos, self.table2)
        )
        left_layout.addWidget(self.device_table2, stretch=2)

        body.addWidget(left_card, stretch=6)

        # ── 右侧 CardWidget ──
        right_card = CardWidget()
        right_layout = QVBoxLayout(right_card)
        right_layout.setContentsMargins(12, 12, 12, 12)
        right_layout.setSpacing(8)

        # WSL 标题
        wsl_header = QHBoxLayout()
        wsl_header.setContentsMargins(0, 0, 0, 0)
        wsl_title = BodyLabel(tr("wsl_list_title"))
        wsl_title.setFont(QFont("Microsoft YaHei", 11, QFont.Weight.Bold))
        wsl_header.addWidget(wsl_title)
        wsl_header.addStretch()
        right_layout.addLayout(wsl_header)

        # WSL 列表
        self.wsl_list = AutoResizeListWidget()
        self.wsl_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.wsl_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.wsl_list.customContextMenuRequested.connect(self.show_wsl_context_menu)
        self.wsl_list.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.wsl_list.setWordWrap(True)
        self.wsl_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                background-color: #fafafa;
                outline: none;
                padding: 2px;
            }
            QListWidget::item {
                padding: 6px 8px;
                border-radius: 6px;
                margin: 1px 2px;
            }
            QListWidget::item:selected {
                background-color: #e8e8e8;
            }
            QListWidget::item:hover {
                background-color: #f5f5f5;
            }
            QListWidget:focus {
                outline: none;
                border: 1px solid #e0e0e0;
            }
            QScrollBar:vertical {
                border: none; background: #f0f0f0; width: 10px;
                border-radius: 5px; margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0; min-height: 30px; border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover { background: #a0a0a0; }
        """)
        right_layout.addWidget(self.wsl_list, stretch=1)

        # 操作日志
        log_title = BodyLabel(tr("log_title"))
        log_title.setFont(QFont("Microsoft YaHei", 11, QFont.Weight.Bold))
        right_layout.addWidget(log_title)

        log_scroll = self._log_scroll = QScrollArea()
        log_scroll.setWidgetResizable(True)
        log_scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        log_scroll.setFixedHeight(160)
        log_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        log_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._log_label = QLabel()
        self._log_label.setWordWrap(True)
        self._log_label.setStyleSheet("""
            QLabel {
                font-size: 9px; color: #757575;
                background-color: #fafafa;
                border: 1px solid #e8e8e8; border-radius: 6px; padding: 6px 8px;
            }
        """)
        self._log_label.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        )
        log_scroll.setWidget(self._log_label)
        right_layout.addWidget(log_scroll, stretch=2)

        body.addWidget(right_card, stretch=4)
        main_layout.addLayout(body, stretch=1)

    # ==================================================================
    # 日志
    # ==================================================================

    def _add_log(self, msg: str):
        ts = datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] {msg}"
        self._log_lines.append(line)
        if len(self._log_lines) > 50:
            self._log_lines = self._log_lines[-50:]
        if hasattr(self, "_log_label"):
            self._log_label.setText("\n".join(self._log_lines))
            if hasattr(self, "_log_scroll"):
                sb = self._log_scroll.verticalScrollBar()
                sb.setValue(sb.maximum())

    # ==================================================================
    # 一键操作
    # ==================================================================

    def _share_all(self):
        shareable = [
            d
            for d in self.devices_all
            if d.bind_state is None and d.attached_client is None
        ]
        if not shareable:
            InfoBar.info(
                title=tr("info_share_all_title"),
                content=tr("info_no_shareable"),
                parent=self,
                duration=3000,
            )
            self._add_log("全部共享: 无设备可共享")
            return
        busids = [d.busid for d in shareable]
        self._do_bind_batch(busids)
        self._add_log(f"全部共享: 共 {len(busids)} 个设备")

    def _detach_all(self):
        # 只断开已共享/已绑定的设备（排除未共享和持久化记录）
        targets = [d.busid for d in self.devices_all if d.busid and d.is_shared]
        if not targets:
            InfoBar.info(
                title=tr("top_detach_all"),
                content=tr("info_no_device"),
                parent=self,
                duration=3000,
            )
            self._add_log(tr("log_detach_all_none"))
            return
        self._do_detach_batch(targets)
        self._add_log(tr("log_detach_all_done", count=len(targets)))

    def _clear_persisted(self):
        persisted = self.usbip.get_persisted_devices()
        if not persisted:
            InfoBar.info(
                title=tr("top_clear_persist"),
                content=tr("info_no_persist"),
                parent=self,
                duration=3000,
            )
            return
        count = 0
        for d in persisted:
            if d.persisted_guid:
                self.usbip.unbind_persisted(d.persisted_guid)
                count += 1
        InfoBar.success(
            title=tr("top_clear_persist"),
            content=tr("info_persist_cleared", count=count),
            parent=self,
            duration=3000,
        )
        self._add_log(f"清除持久: {count} 条")
        self.refresh_all_data()

    # ==================================================================
    # 数据刷新
    # ==================================================================

    def refresh_all_data(self):
        self.global_refresh_btn.setEnabled(False)
        self.global_refresh_btn.setText(tr("top_refreshing"))
        self.devices_all = self.usbip.get_all_devices()
        self.wsl_devices = self.usbip.get_wsl_devices()
        self._load_distros()
        self._populate_shareable()
        self._populate_bound()
        self._populate_wsl()
        self.global_refresh_btn.setEnabled(True)
        self.global_refresh_btn.setText(tr("top_refresh"))
        self.update_status()
        self._add_log(tr("log_refresh"))

        # 每30秒自动刷新发行版状态
        if not hasattr(self, "_distro_timer"):
            self._distro_timer = QTimer(self)
            self._distro_timer.timeout.connect(self._load_distros)
            self._distro_timer.start(30000)

    def _load_distros(self):
        """加载 WSL 发行版到下拉框，每次刷新都更新状态"""
        if not hasattr(self, "_distro_combo"):
            return
        current_data = self._distro_combo.currentData()
        self._distro_combo.blockSignals(True)
        self._distro_combo.clear()
        distros = self.usbip.get_wsl_distributions()
        default_name = self.usbip.get_default_wsl_distro()
        for d in distros:
            status = tr("distro_running") if d["running"] else tr("distro_stopped")
            marker = " \u2605 " if d["name"] == default_name else "    "
            label = f"{marker}{d['name']}  ({status})"
            self._distro_combo.addItem(label, d["name"])
        if current_data:
            idx = self._distro_combo.findData(current_data)
            if idx >= 0:
                self._distro_combo.setCurrentIndex(idx)
        self._distro_combo.blockSignals(False)

    def _selected_distro(self) -> str:
        """获取当前选中的 WSL 发行版名称"""
        if hasattr(self, "_distro_combo"):
            data = self._distro_combo.currentData()
            if data:
                return data
        return ""

    def _populate_shareable(self):
        shareable = [
            d
            for d in self.devices_all
            if d.bind_state is None and d.attached_client is None
        ]
        data = [d.to_dict() for d in shareable]
        self.device_table1.populate_table(data, self.create_action_button)

    def _populate_bound(self):
        bound = [d for d in self.devices_all if d.bind_state == "bound"]
        data = [d.to_dict() for d in bound]
        self.device_table2.populate_table(data, self.create_action_button)

    def _populate_wsl(self):
        data = [d.to_wsl_dict() for d in self.wsl_devices]
        self.wsl_list.clear()
        for device in data:
            item = QListWidgetItem()
            widget = self._create_wsl_item(device)
            widget.setFixedHeight(52)
            # 直接指定 item 高度为 50（两行内容），高亮条覆盖全部
            item.setSizeHint(QSize(0, 50))
            item.setData(Qt.ItemDataRole.UserRole, device)
            self.wsl_list.addItem(item)
            self.wsl_list.setItemWidget(item, widget)

    def _create_wsl_item(self, device):
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        lo = QHBoxLayout(w)
        lo.setContentsMargins(6, 4, 8, 4)
        lo.setSpacing(8)

        # 左侧状态指示圆点
        dot = QLabel()
        dot.setFixedSize(8, 8)
        dot.setStyleSheet(
            "background-color: #4CAF50; border-radius: 4px; border: none;"
        )
        lo.addWidget(dot)

        # 设备信息
        info = QVBoxLayout()
        info.setSpacing(1)

        # 第一行：设备名称
        name = QLabel(device["name"])
        name.setStyleSheet(
            "font-size: 11px; font-weight: bold; color: #424242; background: transparent;"
        )
        info.addWidget(name)

        # 第二行：VID:PID + BUSID + WSL发行版
        dl = QHBoxLayout()
        dl.setSpacing(6)
        vp = QLabel(f"{device['vid']}:{device['pid']}")
        vp.setStyleSheet("font-size: 9px; color: #999; background: transparent;")
        busid = QLabel(device["busid"])
        busid.setStyleSheet(
            "font-size: 9px; color: #999; background: #f0f0f0;"
            "padding: 1px 5px; border-radius: 4px;"
        )
        distro = QLabel(device.get("wsl_distro", "WSL"))
        distro.setStyleSheet(
            "font-size: 9px; color: #0078d4; background-color: #e8f4fd;"
            "padding: 1px 6px; border-radius: 6px;"
        )
        dl.addWidget(vp)
        dl.addWidget(busid)
        dl.addWidget(distro)
        dl.addStretch()
        info.addLayout(dl)

        lo.addLayout(info)

        # 右侧断开按钮（固定宽度，不被挤出）
        detach_btn = PushButton(FIF.PAUSE, "")
        detach_btn.setFixedSize(24, 24)
        detach_btn.setStyleSheet("""
            PushButton {
                background-color: transparent;
                border: none;
                border-radius: 4px;
                min-width: 24px; min-height: 24px;
            }
            PushButton:hover {
                background-color: #fee2e2;
            }
        """)
        busid_val = device.get("busid", "")
        detach_btn.clicked.connect(
            lambda checked, b=busid_val: self._do_wsl_detach_only([b])
        )
        lo.addWidget(detach_btn)

        return w

    # ==================================================================
    # 操作按钮
    # ==================================================================

    def create_action_button(self, table, row, device_dict):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(1, 0, 1, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(0)
        d = device_dict
        if d["is_attached"]:
            btn = PushButton(tr("btn_detach"))
            btn.setFixedSize(*BUTTON_SIZE["MEDIUM"])
            btn.setStyleSheet("""
                PushButton {
                    text-align: center; padding: 0px; margin: 0px;
                    background-color: #ef9a9a; color: #c62828;
                    border: none; border-radius: 4px; font-size: 11px;
                }
                PushButton:hover { background-color: #e57373; }
            """)
            btn.clicked.connect(lambda checked, t=table, r=row: self._do_detach(t, r))
        elif d["is_bound"]:
            btn = PushButton(tr("btn_bound"))
            btn.setFixedSize(*BUTTON_SIZE["MEDIUM"])
            btn.setEnabled(False)
            btn.setStyleSheet("""
                PushButton {
                    text-align: center; padding: 0px; margin: 0px;
                    background-color: #a5d6a7; color: #2e7d32;
                    border: none; border-radius: 4px; font-size: 11px;
                }
            """)
        else:
            btn = PushButton(tr("btn_share"))
            btn.setFixedSize(*BUTTON_SIZE["MEDIUM"])
            btn.setStyleSheet("""
                PushButton {
                    text-align: center; padding: 0px; margin: 0px;
                    background-color: #a5d6a7; color: #2e7d32;
                    border: none; border-radius: 4px; font-size: 11px;
                }
                PushButton:hover { background-color: #81c784; }
            """)
            btn.clicked.connect(lambda checked, t=table, r=row: self._do_bind(t, r))
        layout.addWidget(btn)
        old = table.cellWidget(row, 1)
        if old:
            old.deleteLater()
        table.setCellWidget(row, 1, container)

    # ==================================================================
    # 核心操作
    # ==================================================================

    def _do_bind(self, table, row):
        item = table.item(row, 0)
        if not item:
            return
        busid = item.data(Qt.ItemDataRole.UserRole) or ""
        name = item.text()

        self._current_thread = CmdThread(
            self.usbip, "bind", busid=busid, wsl_distro=self._selected_distro()
        )
        self._current_thread.finished_signal.connect(
            lambda ok, msg, tag: self._on_bind_done(ok, msg, busid, name)
        )
        self._current_thread.start()

    def _on_bind_done(self, ok: bool, msg: str, busid: str, name: str):
        if ok:
            InfoBar.success(
                title=tr("info_share_ok_title"),
                content=tr("info_share_ok", name=name),
                parent=self,
                duration=3000,
            )
            self._add_log(f"共享 {busid} ({name}) -> WSL")
        else:
            hint = translate_usbip_error(msg)
            InfoBar.error(
                title=tr("info_share_fail_title"),
                content=f"{name}: {hint}",
                parent=self,
                duration=5000,
            )
            self._add_log(f"共享 {busid} ({name}) -> 失败")
        self.refresh_all_data()

    def _on_detach_done(self, ok: bool, msg: str, busid: str, name: str):
        if ok:
            InfoBar.success(
                title=tr("info_detach_ok_title"),
                content=tr("info_detach_ok", name=name),
                parent=self,
                duration=3000,
            )
            self._add_log(f"断开 {busid} ({name})")
        else:
            InfoBar.error(
                title=tr("info_detach_fail_title"),
                content=msg,
                parent=self,
                duration=5000,
            )
        self.refresh_all_data()

    def _do_detach(self, table, row):
        item = table.item(row, 0)
        if not item:
            return
        busid = item.data(Qt.ItemDataRole.UserRole) or ""
        name = item.text()

        self._current_thread = CmdThread(self.usbip, "detach", busid=busid)
        self._current_thread.finished_signal.connect(
            lambda ok, msg, tag: self._on_detach_done(ok, msg, busid, name)
        )
        self._current_thread.start()

    def _do_bind_batch(self, busids: list[str]):
        ok = fail = 0
        last_error = ""
        distro = self._selected_distro() or self.usbip.get_default_wsl_distro()
        for bid in busids:
            s, msg = self.usbip.bind(bid, force=True)
            if s:
                s2, msg2 = self.usbip.attach(bid, wsl_distro=distro)
                if s2:
                    self.usbip.set_busid_distro(bid, distro)
                    ok += 1
                else:
                    fail += 1
                    last_error = msg2
            else:
                fail += 1
                last_error = msg
        if fail == 0:
            InfoBar.success(
                title=tr("info_bind_batch_title"),
                content=tr("info_bind_batch", count=ok),
                parent=self,
                duration=3000,
            )
            self._add_log(tr("log_bind_batch_ok", count=ok))
        else:
            hint = translate_usbip_error(last_error)
            InfoBar.warning(
                title=tr("info_bind_batch_title"),
                content=tr("info_bind_batch_partial", ok=ok, fail=fail) + ". " + hint,
                parent=self,
                duration=5000,
            )
            self._add_log(tr("log_bind_batch_partial", ok=ok, fail=fail))
        self.refresh_all_data()

    def _do_detach_batch(self, busids: list[str]):
        for bid in busids:
            self.usbip.detach(bid)
            self.usbip.unbind(bid)
        InfoBar.success(
            title=tr("info_detach_batch_title"),
            content=tr("info_detach_batch", count=len(busids)),
            parent=self,
            duration=3000,
        )
        self._add_log(tr("log_detach_batch", count=len(busids)))
        self.refresh_all_data()

    def _do_bind_only_batch(self, busids: list[str]):
        ok = fail = 0
        for bid in busids:
            s, _ = self.usbip.bind(bid, force=True)
            if s:
                ok += 1
            else:
                fail += 1
        msg = (
            tr("info_bind_done", count=ok)
            if fail == 0
            else tr("info_bind_batch_partial", ok=ok, fail=fail)
        )
        InfoBar.success(
            title=tr("info_bind_done_title"), content=msg, parent=self, duration=3000
        )
        self._add_log(tr("log_bind_only", count=ok))
        self.refresh_all_data()

    def _do_unbind_batch(self, busids: list[str]):
        valid = [b for b in busids if b]
        if not valid:
            InfoBar.error(
                title=tr("info_unbind_fail_title"),
                content=tr("info_invalid_id"),
                parent=self,
                duration=3000,
            )
            return
        for bid in valid:
            ok, msg = self.usbip.unbind(bid)
            if not ok:
                hint = translate_usbip_error(msg)
                InfoBar.error(
                    title=tr("info_unbind_fail_title"),
                    content=hint,
                    parent=self,
                    duration=5000,
                )
                return
        InfoBar.success(
            title=tr("info_unbind_done_title"),
            content=tr("info_unbind_done", count=len(valid)),
            parent=self,
            duration=3000,
        )
        self._add_log(tr("log_unbind", count=len(valid)))
        self.refresh_all_data()

    def _do_attach_batch(self, busids: list[str]):
        ok = fail = 0
        distro = self._selected_distro() or self.usbip.get_default_wsl_distro()
        for bid in busids:
            s, _ = self.usbip.attach(bid, wsl_distro=distro)
            if s:
                self.usbip.set_busid_distro(bid, distro)
                ok += 1
            else:
                fail += 1
        msg = (
            tr("info_attach_done", count=ok)
            if fail == 0
            else tr("info_bind_batch_partial", ok=ok, fail=fail)
        )
        InfoBar.success(
            title=tr("info_attach_done_title"), content=msg, parent=self, duration=3000
        )
        self._add_log(tr("log_attach", count=ok))
        self.refresh_all_data()

    def _do_wsl_detach(self, busids: list[str]):
        valid = [b for b in busids if b]
        if not valid:
            return
        for bid in valid:
            self.usbip.detach(bid)
            self.usbip.unbind(bid)
        InfoBar.success(
            title=tr("info_detach_ok_title"),
            content=tr("info_wsl_detach_unbind", count=len(valid)),
            parent=self,
            duration=3000,
        )
        self._add_log(tr("log_wsl_detach_unbind", count=len(valid)))
        self.refresh_all_data()

    def _do_wsl_detach_only(self, busids: list[str]):
        """仅从WSL断开设备，保留绑定"""
        valid = [b for b in busids if b]
        if not valid:
            return
        for bid in valid:
            self.usbip.detach(bid)
        InfoBar.success(
            title=tr("info_detach_ok_title"),
            content=tr("info_wsl_detach_only", count=len(valid)),
            parent=self,
            duration=3000,
        )
        self._add_log(tr("log_wsl_detach_only", count=len(valid)))
        self.refresh_all_data()

    # ==================================================================
    # 右键菜单
    # ==================================================================

    def show_context_menu(self, pos, table):
        selected_rows = set()
        for item in table.selectedItems():
            selected_rows.add(item.row())
        if not selected_rows:
            return

        busids = []
        for row in selected_rows:
            item = table.item(row, 0)
            if item:
                busids.append(item.data(Qt.ItemDataRole.UserRole) or item.text())

        menu = build_windows_context_menu(
            self,
            is_bound_table=(table is not self.table1),
            busids=busids,
            on_attach=self._do_attach_batch,
            on_bind=self._do_bind_batch,
            on_bind_only=self._do_bind_only_batch,
            on_detach=self._do_detach_batch,
            on_unbind=self._do_unbind_batch,
        )
        menu.exec(table.viewport().mapToGlobal(pos))

    def show_wsl_context_menu(self, pos):
        selected = self.wsl_list.selectedItems()
        if not selected:
            return
        menu = build_wsl_context_menu(
            self,
            selected_items=selected,
            on_detach_only=self._do_wsl_detach_only,
            on_detach=self._do_wsl_detach,
            on_detail=self._show_wsl_detail,
        )
        menu.exec(self.wsl_list.viewport().mapToGlobal(pos))

    def _show_wsl_detail(self, item):
        device = item.data(Qt.ItemDataRole.UserRole)
        if not device:
            return
        details = (
            f"<b>{tr('detail_name')}:</b> {device.get('name')}<br>"
            f"<b>BUSID:</b> {device.get('busid')}<br>"
            f"<b>VID:PID:</b> {device.get('vid')}:{device.get('pid')}<br>"
            f"<b>{tr('detail_distro')}:</b> {device.get('wsl_distro')}<br>"
            f"<b>{tr('detail_status')}:</b> {device.get('status')}"
        )
        QMessageBox.information(self, tr("detail_title"), details)

    def update_status(self):
        pass
