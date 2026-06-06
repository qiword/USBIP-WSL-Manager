# USBIP-WSL-Manager

A GUI tool for managing USB devices shared between Windows and WSL2 via USB/IP protocol, built with PyQt6 + QFluentWidgets.

## Features

- **Device Management** - List shareable USB devices, bind/attach/detach with one click
- **WSL Integration** - Auto-detect WSL distributions, attach devices to running WSL instances
- **Batch Operations** - Detach all devices or clear persisted bindings
- **System Tray** - Minimize to tray, double-click to restore
- **Multi-language** - Chinese/English with auto-detection and persistence
- **Auto-start** - Register to Windows startup via registry
- **Update Check** - Compare installed usbipd version against GitHub releases
- **Admin Elevation** - UAC manifest for administrator privileges

## Requirements

- Windows 10/11
- [usbipd-win](https://github.com/dorssel/usbipd-win) installed
- WSL2 with a Linux distribution

## Quick Start

### Run from source

```bash
pip install PyQt6 PyQt6-Fluent-Widgets
pythonw main.pyw
```

### Build executable

```bash
# Option 1: PyInstaller
python -m PyInstaller usbip_manager.spec --noconfirm

# Option 2: Build script (interactive)
build.bat
```

### Inno Setup installer

```bash
# Build exe first, then:
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" setup.iss
```

## Project Structure

```
USBIP-WSL/
|-- main.pyw                 # Entry point, admin check
|-- main.py                  # CLI entry (with console)
|-- build.bat                # Build script
|-- setup.iss                # Inno Setup installer config
|-- usbip_manager.spec       # PyInstaller spec
|-- admin.manifest           # UAC elevation manifest
|-- icon.svg / icon.ico      # App icons
|
|-- utils/
|   |-- constants.py         # Colors, sizes, theme
|   |-- i18n.py              # Multi-language support
|   |-- usbip_manager.py     # UsbDevice dataclass + UsbipManager
|   |-- usbip_error.py       # Error message translation
|   |-- autostart.py         # Windows registry autostart
|
|-- widgets/
|   |-- device_table.py      # QTableWidget for device lists
|   |-- device_menu.py       # Right-click context menus
|   |-- cmd_thread.py        # Background QThread for usbipd commands
|   |-- auto_resize_list.py  # Auto-resizing QListWidget
|
|-- windows/
|   |-- main_window.py       # FluentWindow with tray icon
|   |-- pages/
|       |-- home_page.py     # Main device management page
|       |-- settings_page.py # Settings page
```

## Usbipd Commands Reference

| GUI Action | usbipd Command |
|---|---|
| Share (bind + attach) | `usbipd bind --busid X --force` + `usbipd attach --busid X --wsl` |
| Bind only | `usbipd bind --busid X --force` |
| Attach to WSL | `usbipd attach --busid X --wsl` |
| Detach only | `usbipd detach --busid X` |
| Detach + Unbind | `usbipd detach --busid X` + `usbipd unbind --busid X` |
| Unbind | `usbipd unbind --busid X` |
| Clear persisted | `usbipd unbind --guid <GUID>` |

## License

MIT
