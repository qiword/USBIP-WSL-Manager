"""USB/IP 错误信息翻译"""


def translate_usbip_error(msg: str) -> str:
    """将 usbipd 英文错误翻译为用户友好的中文提示"""
    ml = msg.lower()
    if "access denied" in ml or "administrator" in ml:
        return "需要管理员权限，请以管理员身份运行程序"
    if "device busy" in ml or "exported" in ml:
        return "设备正忙，请先断开该设备的所有连接后重试"
    if "used by windows" in ml:
        return "设备正被 Windows 占用，请先弹出/停用该设备"
    if "not shared" in ml or "not bind" in ml:
        return "设备尚未共享，请先点击「共享」绑定设备"
    if "not found" in ml:
        return "未找到该设备，请刷新后重试"
    if "timeout" in ml or "timed out" in ml:
        return "操作超时，请检查 WSL 是否正常运行"
    if "wsl" in ml and ("distro" in ml or "not running" in ml or "stopped" in ml):
        return "WSL 发行版未运行，请先启动 WSL (wsl -d <发行版>)"
    if "wsl" in ml and "not found" in ml:
        return "未找到 WSL 发行版，请确认 WSL 已安装"
    if "network" in ml or "127.0.0.1" in ml:
        return "WSL 网络不可达，请检查 WSL 网络配置"
    for line in msg.splitlines():
        line = line.strip()
        if "error:" in line.lower() or "warning:" in line.lower():
            return line
    return msg[:120] if len(msg) > 120 else msg
