import re
import subprocess
import webbrowser

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)
from qfluentwidgets import (
    BodyLabel,
    CardWidget,
    InfoBar,
    PushButton,
    SubtitleLabel,
)

from utils.i18n import get_language, set_language, tr

try:
    from urllib.request import Request, urlopen
except ImportError:
    from urllib2 import Request, urlopen

USBIPD_RELEASE_URL = "https://github.com/dorssel/usbipd-win/releases"
GITHUB_API_URL = "https://api.github.com/repos/dorssel/usbipd-win/releases/latest"


class _VersionCheckThread(QThread):
    """后台检查 GitHub 最新版本"""

    result_signal = pyqtSignal(bool, str)  # ok, version_or_error

    def run(self):
        try:
            req = Request(GITHUB_API_URL)
            req.add_header("Accept", "application/vnd.github+json")
            req.add_header("User-Agent", "USBIP-WSL-Manager")
            with urlopen(req, timeout=10) as resp:
                import json

                data = json.loads(resp.read().decode("utf-8"))
                tag = data.get("tag_name", "")
                if tag:
                    self.result_signal.emit(True, tag.lstrip("v"))
                else:
                    self.result_signal.emit(False, "无法解析版本号")
        except Exception as e:
            self.result_signal.emit(False, str(e)[:80])


class SettingsPage(QWidget):
    """设置页面"""

    def __init__(self):
        super().__init__()
        self.setObjectName("settingsPage")
        self.setup_ui()
        self.load_settings()

    # ------------------------------------------------------------------
    # UI 构建
    # ------------------------------------------------------------------

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        layout.addWidget(SubtitleLabel("\u2699\ufe0f \u8bbe\u7f6e"))

        # ── 环境检查 ──
        card = CardWidget()
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(10)

        title = BodyLabel("\U0001f50d \u73af\u5883\u68c0\u67e5")
        card_layout.addWidget(title)

        # usbipd 状态行
        row1 = QHBoxLayout()
        self._usbipd_status = BodyLabel("\u68c0\u67e5\u4e2d...")
        row1.addWidget(self._usbipd_status)
        row1.addStretch()
        self._check_btn = PushButton("\u68c0\u67e5\u66f4\u65b0")
        self._check_btn.clicked.connect(self._run_check)
        row1.addWidget(self._check_btn)
        card_layout.addLayout(row1)

        # WSL 状态行
        row2 = QHBoxLayout()
        self._wsl_status = BodyLabel("")
        row2.addWidget(self._wsl_status)
        row2.addStretch()
        card_layout.addLayout(row2)

        # 下载按钮（仅在未安装时显示）
        row3 = QHBoxLayout()
        self._download_btn = PushButton("\U0001f4e5 \u4e0b\u8f7d usbipd-win")
        self._download_btn.clicked.connect(self._open_download)
        self._download_btn.setVisible(False)
        row3.addWidget(self._download_btn)
        row3.addStretch()
        card_layout.addLayout(row3)

        layout.addWidget(card)

        # ── 语言切换 ──
        lang_card = CardWidget()
        lang_layout = QHBoxLayout(lang_card)
        lang_layout.addWidget(BodyLabel("\U0001f310 \u8bed\u8a00 / Language"))
        lang_layout.addStretch()
        self._lang_combo = QComboBox()
        self._lang_combo.setMinimumHeight(28)
        self._lang_combo.setMaximumWidth(120)
        self._lang_combo.addItem("\u4e2d\u6587", "zh")
        self._lang_combo.addItem(tr("settings_lang_en"), "en")
        self._lang_combo.currentIndexChanged.connect(self._on_lang_changed)
        # 默认选项根据当前语言
        current_lang = get_language()
        idx = self._lang_combo.findData(current_lang)
        self._lang_combo.setCurrentIndex(idx if idx >= 0 else 0)
        lang_layout.addWidget(self._lang_combo)
        layout.addWidget(lang_card)

        # ── 自启动 ──
        from utils.autostart import (
            disable_autostart,
            enable_autostart,
            is_autostart_enabled,
        )

        auto_card = CardWidget()
        auto_layout = QHBoxLayout(auto_card)
        auto_layout.addWidget(BodyLabel("\U0001f504 \u5f00\u673a\u81ea\u542f\u52a8"))
        auto_layout.addStretch()
        self._autostart_btn = PushButton("")
        self._autostart_btn.clicked.connect(self._toggle_autostart)
        self._update_autostart_btn(is_autostart_enabled())
        auto_layout.addWidget(self._autostart_btn)
        layout.addWidget(auto_card)

        # ── 关于 ──
        self._about_card = CardWidget()
        about_layout = QVBoxLayout(self._about_card)
        about_layout.setSpacing(8)
        about_layout.addWidget(BodyLabel("\U0001f4c4 \u5173\u4e8e"))

        self._about_info = QLabel(
            "USBIP-WSL \u7ba1\u7406\u5de5\u5177 v1.0\n"
            "\u57fa\u4e8e PyQt6 + QFluentWidgets \u6784\u5efa\n"
            "\u5c06 Windows USB \u8bbe\u5907\u5171\u4eab\u5230 WSL2 \u865a\u62df\u673a\n"
            "\u4f9d\u8d56 usbipd-win \u63d0\u4f9b USB/IP \u534f\u8bae\u652f\u6301"
        )
        self._about_info.setStyleSheet(
            "color: #757575; font-size: 11px; line-height: 1.6;"
        )
        about_layout.addWidget(self._about_info)
        layout.addWidget(self._about_card)

        layout.addStretch()

    # ------------------------------------------------------------------
    # 数据加载
    # ------------------------------------------------------------------

    def load_settings(self):
        self._run_check()

    def _run_check(self):
        """检查 usbipd 和 WSL 是否安装"""
        self._check_btn.setEnabled(False)
        self._check_btn.setText("\u68c0\u67e5\u4e2d...")

        # 检查 usbipd
        usbipd_ok, version = self._check_usbipd()
        if usbipd_ok:
            self._usbipd_status.setText(
                f"\u2705 usbipd-win \u5df2\u5b89\u88c5 ({version})"
            )
            self._download_btn.setVisible(False)
            self._installed_version = version
        else:
            self._usbipd_status.setText("\u274c usbipd-win \u672a\u5b89\u88c5")
            self._download_btn.setVisible(True)
            self._installed_version = ""

        # 检查 WSL
        wsl_ok, wsl_info = self._check_wsl()
        if wsl_ok:
            self._wsl_status.setText(f"\u2705 WSL \u5df2\u5b89\u88c5 ({wsl_info})")
        else:
            self._wsl_status.setText(f"\u274c WSL \u672a\u68c0\u6d4b\u5230")

        self._check_btn.setEnabled(True)
        self._check_btn.setText("\u68c0\u67e5\u66f4\u65b0")

        # 自动检查更新
        self._check_update()

    @staticmethod
    def _check_usbipd():
        try:
            result = subprocess.run(
                ["usbipd", "--version"],
                capture_output=True,
                encoding="utf-8",
                errors="replace",
                timeout=5,
                creationflags=0x08000000,
            )
            output = result.stdout.strip() or result.stderr.strip()
            if output:
                # 取第一行作为版本
                version = output.splitlines()[0] if output.splitlines() else output
                return True, version
            return False, ""
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False, ""

    @staticmethod
    def _check_wsl():
        try:
            result = subprocess.run(
                ["wsl", "--status"],
                capture_output=True,
                encoding="utf-16-le",
                errors="replace",
                timeout=10,
                creationflags=0x08000000,
            )
            output = result.stdout.strip()
            if output:
                # 提取默认发行版和内核版本
                lines = output.splitlines()
                return True, lines[0] if lines else "已安装"
            return False, ""
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False, ""

    def _check_update(self):
        """后台检查 GitHub 最新版本"""
        if not getattr(self, "_installed_version", ""):
            return
        self._usbipd_status.setText("\u6b63\u5728\u68c0\u67e5\u66f4\u65b0...")
        self._thread = _VersionCheckThread()
        self._thread.result_signal.connect(self._on_update_result)
        self._thread.start()

    def _on_update_result(self, ok: bool, latest: str):
        if not ok:
            return
        current = getattr(self, "_installed_version", "0")
        try:
            from packaging.version import parse as vparse
        except ImportError:

            def vparse(x):
                return tuple(int(n) for n in re.findall(r"\d+", x))

        if vparse(latest) > vparse(current):
            self._usbipd_status.setText(
                f"\U0001f4e5 \u53d1\u73b0\u65b0\u7248\u672c: v{latest} (\u5f53\u524d: v{current})"
            )
        else:
            self._usbipd_status.setText(
                f"\u2705 \u5df2\u662f\u6700\u65b0\u7248\u672c (v{current})"
            )

    def _open_download(self):
        webbrowser.open(USBIPD_RELEASE_URL)
        InfoBar.success(
            title="已打开浏览器",
            content="请在 GitHub 页面下载最新的 usbipd-win 安装包",
            parent=self,
            duration=4000,
        )

    def _on_lang_changed(self, index: int):
        lang = self._lang_combo.itemData(index)
        if lang:
            set_language(lang)
            InfoBar.success(
                title=tr("info_lang_switched"),
                content=tr("info_restart_hint"),
                parent=self,
                duration=3000,
            )

    def _toggle_autostart(self):
        from utils.autostart import (
            disable_autostart,
            enable_autostart,
            is_autostart_enabled,
        )

        if is_autostart_enabled():
            disable_autostart()
        else:
            enable_autostart()
        self._update_autostart_btn(is_autostart_enabled())

    def _update_autostart_btn(self, enabled: bool):
        if enabled:
            self._autostart_btn.setText("\u5df2\u5f00\u542f")
            self._autostart_btn.setStyleSheet(
                "PushButton { color: #2e7d32; font-weight: bold; }"
            )
        else:
            self._autostart_btn.setText("\u5df2\u5173\u95ed")
            self._autostart_btn.setStyleSheet("PushButton { color: #757575; }")
