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
    """以管理员权限重新启动当前程序"""
    import pathlib

    if getattr(sys, "frozen", False):
        exe = sys.executable
        args = sys.argv[1:]
    else:
        # 用 pythonw.exe 启动，避免控制台窗口
        py_dir = pathlib.Path(sys.executable).parent
        pythonw = str(py_dir / "pythonw.exe")
        # 使用绝对路径
        script = str(pathlib.Path(sys.argv[0]).resolve())
        # 强制使用 .pyw 后缀
        if script.endswith(".py"):
            script = script[:-3] + ".pyw"
        exe = pythonw
        args = [script] + sys.argv[1:]

    params = " ".join(f'"{a}"' for a in args)

    ret = ctypes.windll.shell32.ShellExecuteW(
        None,  # hwnd
        "runas",  # operation
        exe,  # file
        params,  # parameters
        None,  # directory
        1,  # nShowCmd (SW_SHOWNORMAL)
    )
    # 返回值 > 32 表示成功
    if ret <= 32:
        raise OSError(f"ShellExecute failed with code {ret}")


if __name__ == "__main__":
    if not is_admin():
        try:
            run_as_admin()
        except OSError as e:
            ctypes.windll.user32.MessageBoxW(
                0,
                f"\u65e0\u6cd5\u83b7\u53d6\u7ba1\u7406\u5458\u6743\u9650:\n{e}",
                "错误",
                0x00000010,
            )
        sys.exit(0)

    # 防止重复运行
    import win32api
    import win32con
    import win32event
    import win32gui
    import winerror

    mutex_name = "Global\\USBIP-WSL-Manager-SingleInstance"
    mutex = win32event.CreateMutex(None, False, mutex_name)
    if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
        titles = ["USBIP-WSL-Manager", "WSL USB\u7ba1\u7406\u5668"]
        hwnd = 0
        for t in titles:
            hwnd = win32gui.FindWindow(None, t)
            if hwnd:
                break
        if hwnd:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
        sys.exit(0)

    app = QApplication(sys.argv)
    setTheme(Theme.AUTO)

    # 设置应用图标
    import pathlib

    icon_path = str(pathlib.Path(__file__).resolve().parent / "icon.svg")
    from PyQt6.QtGui import QIcon

    app.setWindowIcon(QIcon(icon_path))

    window = Window()
    window.show()
    sys.exit(app.exec())
