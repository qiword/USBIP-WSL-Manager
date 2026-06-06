"""自启动管理（启动文件夹快捷方式）"""

import os
import pathlib
import sys

APP_NAME = "USBIP-WSL-Manager"


def _startup_dir() -> pathlib.Path:
    """获取启动文件夹路径"""
    return (
        pathlib.Path(os.environ["APPDATA"])
        / "Microsoft"
        / "Windows"
        / "Start Menu"
        / "Programs"
        / "Startup"
    )


def _get_exe_path() -> str:
    """获取当前 exe 或 pythonw 路径"""
    if getattr(sys, "frozen", False):
        return sys.executable
    return ""


def _shortcut_path() -> pathlib.Path:
    return _startup_dir() / f"{APP_NAME}.lnk"


def is_autostart_enabled() -> bool:
    return _shortcut_path().exists()


def enable_autostart():
    exe = _get_exe_path()
    if not exe:
        return False

    try:
        import pythoncom
        from win32com.client import Dispatch

        _startup_dir().mkdir(parents=True, exist_ok=True)

        shell = Dispatch("WScript.Shell")
        shortcut = shell.CreateShortcut(str(_shortcut_path()))
        shortcut.TargetPath = exe
        shortcut.WorkingDirectory = str(pathlib.Path(exe).parent)
        shortcut.Description = "USBIP-WSL-Manager"
        shortcut.IconLocation = exe
        shortcut.Save()
        return True
    except ImportError:
        # 降级：直接创建 .bat 快捷方式
        bat = _shortcut_path().with_suffix(".bat")
        bat.write_text(f'@echo off\nstart "" "{exe}"\nexit\n')
        return True
    except Exception:
        return False


def disable_autostart():
    sp = _shortcut_path()
    if sp.exists():
        sp.unlink()
        return True
    return False
