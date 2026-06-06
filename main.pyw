import ctypes
import sys

from PyQt6.QtWidgets import QApplication
from qfluentwidgets import Theme, setTheme

from windows.main_window import Window


def is_admin() -> bool:
    """检测当前进程是否以管理员权限运行"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def run_as_admin():
    """通过 ShellExecute runas 触发 Windows UAC"""
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable,
        f'"{sys.argv[0]}"', None, 1)


if __name__ == "__main__":
    if not is_admin():
        if getattr(sys, "frozen", False):
            ctypes.windll.user32.MessageBoxW(
                0,
                "程序需要管理员权限运行。\n\n请右键程序→属性→兼容性→勾选「以管理员身份运行此程序」。",
                "USBIP-WSL-Manager", 0x00000010)
            sys.exit(1)
        else:
            run_as_admin()
            sys.exit(0)

    app = QApplication(sys.argv)
    setTheme(Theme.AUTO)

    # 设置应用图标
    import pathlib
    icon_path = str(pathlib.Path(__file__).resolve().parent / "icon.svg")
    from PyQt6.QtGui import QIcon
    app.setWindowIcon(QIcon(icon_path))

    # 单实例检测（在窗口创建之前）
    from utils.single_instance import SingleInstance
    single = SingleInstance()
    if not single.try_acquire():
        sys.exit(0)

    window = Window()

    # 第二个实例激活时恢复窗口
    single._on_activate = window._show_from_tray

    window.show()
    sys.exit(app.exec())
