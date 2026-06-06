"""自启动管理（注册表）"""

import pathlib
import sys
import winreg

AUTORUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_NAME = "USBIP-WSL-Manager"


def _get_exe_path() -> str:
    """获取当前程序的启动路径"""
    if getattr(sys, "frozen", False):
        return sys.executable
    py_dir = pathlib.Path(sys.executable).parent
    pythonw = str(py_dir / "pythonw.exe")
    script = str(pathlib.Path(sys.argv[0]).resolve())
    if script.endswith(".py"):
        script = script[:-3] + ".pyw"
    return f'"{pythonw}" "{script}"'


def is_autostart_enabled() -> bool:
    """检查是否已设置自启动"""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, AUTORUN_KEY)
        try:
            winreg.QueryValueEx(key, APP_NAME)
            return True
        except FileNotFoundError:
            return False
        finally:
            winreg.CloseKey(key)
    except OSError:
        return False


def enable_autostart():
    """启用自启动"""
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, AUTORUN_KEY, 0, winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, _get_exe_path())
        winreg.CloseKey(key)
        return True
    except OSError:
        return False


def disable_autostart():
    """禁用自启动"""
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, AUTORUN_KEY, 0, winreg.KEY_SET_VALUE
        )
        winreg.DeleteValue(key, APP_NAME)
        winreg.CloseKey(key)
        return True
    except (OSError, FileNotFoundError):
        return False
