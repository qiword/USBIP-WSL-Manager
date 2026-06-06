"""多语言支持"""

import ctypes
import json
import locale
import os
import pathlib
import sys

# 持久化文件放在用户目录（打包后 MEIPASS 只读）
if getattr(sys, "frozen", False):
    LANG_FILE = (
        pathlib.Path(os.environ.get("APPDATA", os.path.expanduser("~")))
        / "USBIP-WSL-Manager"
        / "lang_config.json"
    )
else:
    LANG_FILE = pathlib.Path(__file__).resolve().parent / "lang_config.json"


def get_system_language() -> str:
    """检测系统语言，返回 'zh' 或 'en'"""
    try:
        windll = ctypes.windll.kernel32
        lang_id = windll.GetUserDefaultUILanguage()
        primary = lang_id & 0xFF
        if primary == 0x04:  # LANG_CHINESE
            return "zh"
    except Exception:
        pass
    # 兜底用 Python locale
    try:
        loc = locale.getdefaultlocale()
        if loc and loc[0] and loc[0].startswith("zh"):
            return "zh"
    except Exception:
        pass
    return "en"


# ── 翻译字典 ────────────────────────────────────────────────────
TEXTS = {
    "window_title": {"zh": "WSL USB管理器", "en": "WSL USB Manager"},
    "nav_devices": {"zh": "设备", "en": "Devices"},
    "nav_logs": {"zh": "日志", "en": "Logs"},
    "nav_settings": {"zh": "设置", "en": "Settings"},
    "top_wsl_distro": {"zh": "WSL发行版", "en": "WSL Distro"},
    "top_refresh": {"zh": "刷新", "en": "Refresh"},
    "top_refreshing": {"zh": "刷新中...", "en": "Refreshing..."},
    "top_detach_all": {"zh": "全部断开", "en": "Detach All"},
    "top_clear_persist": {"zh": "清除持久", "en": "Clear Persist"},
    "table_shareable": {"zh": "可共享设备", "en": "Shareable"},
    "table_bound": {"zh": "Windows已绑定设备", "en": "Windows Bound"},
    "table_wsl": {"zh": "WSL已连接设备", "en": "WSL Connected"},
    "quick_actions": {"zh": "快捷操作", "en": "Quick Actions"},
    "log_title": {"zh": "最近操作日志", "en": "Recent Logs"},
    "btn_share": {"zh": "共享", "en": "Share"},
    "btn_detach": {"zh": "断开", "en": "Detach"},
    "btn_bound": {"zh": "已绑定", "en": "Bound"},
    "menu_attach": {"zh": "连接到 WSL", "en": "Attach to WSL"},
    "menu_share_to_wsl": {"zh": "共享到 WSL", "en": "Share to WSL"},
    "menu_bind_only": {"zh": "仅绑定", "en": "Bind Only"},
    "menu_detach_unbind": {"zh": "断开并解绑", "en": "Detach & Unbind"},
    "menu_unbind": {"zh": "解绑", "en": "Unbind"},
    "menu_wsl_detach_only": {"zh": "仅断开连接", "en": "Detach Only"},
    "menu_wsl_detach_unbind": {"zh": "断开并解绑", "en": "Detach & Unbind"},
    "menu_wsl_detail": {"zh": "查看详情", "en": "Details"},
    "menu_tt_attach": {
        "zh": "将已绑定的设备连接(attach)到 WSL",
        "en": "Attach bound device to WSL",
    },
    "menu_tt_share": {
        "zh": "强制绑定并连接到 WSL，一步完成",
        "en": "Force bind and attach to WSL",
    },
    "menu_tt_bind_only": {
        "zh": "仅注册为可共享，暂不连接 WSL",
        "en": "Only register as shareable",
    },
    "menu_tt_unbind": {
        "zh": "取消共享注册，设备回到可共享列表",
        "en": "Remove sharing, device goes back to shareable",
    },
    "menu_tt_detach_only": {
        "zh": "从WSL断开，保留绑定状态",
        "en": "Detach from WSL, keep binding",
    },
    "menu_tt_detach_unbind": {
        "zh": "从WSL断开并取消共享",
        "en": "Detach and remove sharing",
    },
    "info_share_ok": {
        "zh": "{} 已共享并连接到 WSL",
        "en": "{} shared and connected to WSL",
    },
    "info_detach_ok": {"zh": "{} 已断开连接", "en": "{} disconnected"},
    "info_bind_fail": {"zh": "共享失败", "en": "Share Failed"},
    "info_detach_fail": {"zh": "断开失败", "en": "Detach Failed"},
    "info_no_device": {"zh": "没有需要断开的设备", "en": "No devices to detach"},
    "info_detach_all_done": {
        "zh": "已断开 {count} 个设备",
        "en": "Detached {count} devices",
    },
    "info_no_persist": {"zh": "没有持久化绑定记录", "en": "No persisted records"},
    "info_persist_cleared": {
        "zh": "已清除 {} 条持久化绑定记录",
        "en": "Cleared {} persisted records",
    },
    "info_wsl_detach_only": {
        "zh": "已从 WSL 断开 {} 个设备，绑定已保留",
        "en": "Detached {} from WSL, binding kept",
    },
    "info_wsl_detach_unbind": {
        "zh": "已从 WSL 断开并解绑 {} 个设备",
        "en": "Detached & unbound {count} from WSL",
    },
    "info_bind_batch": {"zh": "已共享 {count} 个设备", "en": "Shared {count} devices"},
    "info_bind_batch_partial": {
        "zh": "成功 {ok} 个，失败 {fail} 个",
        "en": "{ok} succeeded, {fail} failed",
    },
    "info_detach_batch": {
        "zh": "已断开 {count} 个设备",
        "en": "Detached {count} devices",
    },
    "info_bind_done": {"zh": "已绑定 {count} 个设备", "en": "Bound {count} devices"},
    "info_unbind_done": {
        "zh": "已解绑 {count} 个设备",
        "en": "Unbound {count} devices",
    },
    "info_attach_done": {
        "zh": "已连接 {count} 个设备到 WSL",
        "en": "Attached {count} to WSL",
    },
    "info_unbind_fail": {"zh": "解绑失败", "en": "Unbind Failed"},
    "info_invalid_id": {"zh": "无效的设备ID", "en": "Invalid device ID"},
    "log_refresh": {"zh": "刷新设备列表", "en": "Refresh device list"},
    "log_share": {"zh": "共享 {busid} ({name}) -> WSL", "en": "Share {busid} ({name}) -> WSL"},
    "log_share_fail": {"zh": "共享 {} ({}) -> 失败", "en": "Share {} ({}) -> failed"},
    "log_detach": {"zh": "断开 {busid} ({name})", "en": "Detach {busid} ({name})"},
    "log_persist_clear": {"zh": "清除持久记录: {count} 条", "en": "Clear persist: {count}"},
    "log_wsl_detach_only": {
        "zh": "WSL仅断开: {count} 个设备",
        "en": "WSL detach only: {count}",
    },
    "log_wsl_detach_unbind": {
        "zh": "WSL断开+解绑: {count} 个设备",
        "en": "WSL detach+unbind: {count}",
    },
    "log_bind_batch": {"zh": "批量共享: {count}", "en": "Batch share: {}"},
    "log_detach_batch": {"zh": "批量断开: {count} 个设备", "en": "Batch detach: {count}"},
    "log_bind_only": {"zh": "仅绑定: {count}", "en": "Bind only: {count}"},
    "log_unbind": {"zh": "解绑: {count} 个设备", "en": "Unbind: {count}"},
    "log_attach": {"zh": "连接: {count}", "en": "Attach: {count}"},
    "tooltip_busid": {"zh": "BUSID: {}", "en": "BUSID: {}"},
    "tooltip_vidpid": {"zh": "VID:PID: {}:{}", "en": "VID:PID: {}:{}"},
    "tooltip_status": {"zh": "状态: {}", "en": "Status: {}"},
    "detail_title": {"zh": "设备详情", "en": "Device Details"},
    "detail_name": {"zh": "设备名称", "en": "Name"},
    "detail_busid": {"zh": "BUSID", "en": "BUSID"},
    "detail_vidpid": {"zh": "VID:PID", "en": "VID:PID"},
    "detail_distro": {"zh": "WSL发行版", "en": "WSL Distro"},
    "detail_status": {"zh": "状态", "en": "Status"},
    "error_admin": {
        "zh": "需要管理员权限，请以管理员身份运行程序",
        "en": "Administrator privileges required",
    },
    "error_busy": {
        "zh": "设备正忙，请先断开该设备的所有连接后重试",
        "en": "Device busy, detach all connections first",
    },
    "error_used": {
        "zh": "设备正被 Windows 占用，请先弹出/停用该设备",
        "en": "Device used by Windows, eject it first",
    },
    "error_not_shared": {
        "zh": "设备尚未共享，请先点击「共享」绑定设备",
        "en": "Device not shared, bind it first",
    },
    "error_not_found": {
        "zh": "未找到该设备，请刷新后重试",
        "en": "Device not found, refresh and retry",
    },
    "error_timeout": {
        "zh": "操作超时，请检查 WSL 是否正常运行",
        "en": "Timeout, check if WSL is running",
    },
    "error_wsl_not_running": {
        "zh": "WSL 发行版未运行，请先启动 WSL",
        "en": "WSL distro not running, start it first",
    },
    "error_wsl_not_found": {
        "zh": "未找到 WSL 发行版，请确认 WSL 已安装",
        "en": "WSL distro not found",
    },
    "error_network": {
        "zh": "WSL 网络不可达，请检查 WSL 网络配置",
        "en": "WSL network unreachable",
    },
    "settings_title": {"zh": "⚙️ 设置", "en": "⚙️ Settings"},
    "settings_env": {"zh": "🔍 环境检查", "en": "🔍 Environment Check"},
    "settings_checking": {"zh": "检查中...", "en": "Checking..."},
    "settings_check_btn": {"zh": "检查更新", "en": "Check Update"},
    "settings_usbipd_ok": {
        "zh": "✅ usbipd-win 已安装 ({})",
        "en": "✅ usbipd-win installed ({})",
    },
    "settings_usbipd_no": {
        "zh": "❌ usbipd-win 未安装",
        "en": "❌ usbipd-win not installed",
    },
    "settings_wsl_ok": {"zh": "✅ WSL 已安装 ({})", "en": "✅ WSL installed ({})"},
    "settings_wsl_no": {"zh": "❌ WSL 未检测到", "en": "❌ WSL not detected"},
    "settings_download_btn": {
        "zh": "📥 下载 usbipd-win",
        "en": "📥 Download usbipd-win",
    },
    "settings_update_checking": {"zh": "正在检查更新...", "en": "Checking updates..."},
    "settings_latest": {"zh": "✅ 已是最新版本 (v{})", "en": "✅ Latest version (v{})"},
    "settings_new": {
        "zh": "📥 发现新版本: v{} (当前: v{})",
        "en": "📥 New version: v{} (current: v{})",
    },
    "settings_about": {"zh": "📄 关于", "en": "📄 About"},
    "settings_lang": {"zh": "🌐 语言 / Language", "en": "🌐 语言 / Language"},
    "settings_lang_zh": {"zh": "中文", "en": "中文"},
    "settings_lang_en": {"zh": "English", "en": "English"},
    "distro_running": {"zh": "\u25cf \u8fd0\u884c\u4e2d", "en": "\u25cf Running"},
    "distro_stopped": {"zh": "\u25cb \u5df2\u505c\u6b62", "en": "\u25cb Stopped"},
    # 补充缺失 key
    "wsl_list_title": {
        "zh": "WSL\u5df2\u8fde\u63a5\u8bbe\u5907",
        "en": "WSL Connected",
    },
    "btn_share_all": {"zh": "\u5171\u4eab\u5168\u90e8", "en": "Share All"},
    "info_share_ok_title": {"zh": "\u5171\u4eab\u6210\u529f", "en": "Share OK"},
    "info_detach_ok_title": {"zh": "\u5df2\u65ad\u5f00", "en": "Detached"},
    "info_share_fail_title": {"zh": "\u5171\u4eab\u5931\u8d25", "en": "Share Failed"},
    "info_detach_fail_title": {"zh": "\u65ad\u5f00\u5931\u8d25", "en": "Detach Failed"},
    "info_detach_all_title": {"zh": "\u5168\u90e8\u65ad\u5f00", "en": "Detach All"},
    "info_unbind_title": {"zh": "\u89e3\u7ed1", "en": "Unbind"},
    "log_detach_all_none": {
        "zh": "\u5168\u90e8\u65ad\u5f00: \u65e0\u8bbe\u5907",
        "en": "Detach all: none",
    },
    "detail_action": {"zh": "\u64cd\u4f5c", "en": "Action"},
    "info_browser_open": {
        "zh": "\u5df2\u6253\u5f00\u6d4f\u89c8\u5668",
        "en": "Browser opened",
    },
    "info_lang_switched": {
        "zh": "\u8bed\u8a00\u5df2\u5207\u6362",
        "en": "Language switched",
    },
    "info_restart_hint": {
        "zh": "\u8bf7\u91cd\u65b0\u6253\u5f00\u8bbe\u7f6e\u9875\u9762\u4ee5\u5237\u65b0\u5168\u90e8\u6587\u672c",
        "en": "Restart to apply language",
    },
    "tray_show": {"zh": "\u663e\u793a\u4e3b\u7a97\u53e3", "en": "Show Window"},
    "tray_quit": {"zh": "\u9000\u51fa", "en": "Quit"},
    "tray_minimized_hint": {
        "zh": "\u7a0b\u5e8f\u5df2\u6700\u5c0f\u5316\u5230\u7cfb\u7edf\u6258\u76d8\uff0c\u53cc\u51fb\u56fe\u6807\u6062\u590d\u7a97\u53e3",
        "en": "Minimized to tray. Double-click to restore.",
    },
    "info_no_device": {
        "zh": "\u6ca1\u6709\u9700\u8981\u65ad\u5f00\u7684\u8bbe\u5907",
        "en": "No devices to detach",
    },
    "info_no_persist": {
        "zh": "\u6ca1\u6709\u6301\u4e45\u5316\u7ed1\u5b9a\u8bb0\u5f55",
        "en": "No persisted records",
    },
    "info_no_shareable": {
        "zh": "\u6ca1\u6709\u53ef\u5171\u4eab\u7684\u8bbe\u5907",
        "en": "No shareable devices",
    },
    "info_share_all_title": {"zh": "\u5168\u90e8\u5171\u4eab", "en": "Share All"},
    "info_bind_batch_title": {"zh": "\u6279\u91cf\u5171\u4eab", "en": "Batch Share"},
    "info_detach_batch_title": {"zh": "\u6279\u91cf\u65ad\u5f00", "en": "Batch Detach"},
    "info_bind_done_title": {"zh": "\u7ed1\u5b9a\u5b8c\u6210", "en": "Bind Done"},
    "info_unbind_fail_title": {"zh": "\u89e3\u7ed1\u5931\u8d25", "en": "Unbind Failed"},
    "info_unbind_done_title": {"zh": "\u89e3\u7ed1\u5b8c\u6210", "en": "Unbind Done"},
    "info_attach_done_title": {"zh": "\u8fde\u63a5\u5b8c\u6210", "en": "Attach Done"},
    "info_bind_partial_title": {
        "zh": "\u5df2\u7ed1\u5b9a\uff0c\u8fde\u63a5\u5931\u8d25",
        "en": "Bound, attach failed",
    },
    "info_bind_fail_title": {"zh": "\u7ed1\u5b9a\u5931\u8d25", "en": "Bind Failed"},
    "info_bind_batch": {
        "zh": "\u5df2\u5171\u4eab {count} \u4e2a\u8bbe\u5907",
        "en": "Shared {count} devices",
    },
    "info_detach_batch": {
        "zh": "\u5df2\u65ad\u5f00 {count} \u4e2a\u8bbe\u5907",
        "en": "Detached {count} devices",
    },
    "info_bind_done": {
        "zh": "\u5df2\u7ed1\u5b9a {count} \u4e2a\u8bbe\u5907",
        "en": "Bound {count} devices",
    },
    "info_unbind_done": {
        "zh": "\u5df2\u89e3\u7ed1 {count} \u4e2a\u8bbe\u5907",
        "en": "Unbound {count} devices",
    },
    "info_attach_done": {
        "zh": "\u5df2\u8fde\u63a5 {count} \u4e2a\u8bbe\u5907\u5230 WSL",
        "en": "Attached {count} to WSL",
    },
    "info_share_ok": {
        "zh": "{name} \u5df2\u5171\u4eab\u5e76\u8fde\u63a5\u5230 WSL",
        "en": "{name} shared and attached to WSL",
    },
    "info_detach_ok": {
        "zh": "{name} \u5df2\u65ad\u5f00\u8fde\u63a5",
        "en": "{name} disconnected",
    },
    "info_invalid_id": {
        "zh": "\u65e0\u6548\u7684\u8bbe\u5907ID",
        "en": "Invalid device ID",
    },
    "info_wsl_detach_unbind": {
        "zh": "\u5df2\u4ece WSL \u65ad\u5f00\u5e76\u89e3\u7ed1 {count} \u4e2a\u8bbe\u5907",
        "en": "Detached & unbound {count} from WSL",
    },
    "info_wsl_detach_only": {
        "zh": "\u5df2\u4ece WSL \u65ad\u5f00 {count} \u4e2a\u8bbe\u5907\uff0c\u7ed1\u5b9a\u5df2\u4fdd\u7559",
        "en": "Detached {count} from WSL, binding kept",
    },
    "info_persist_cleared": {
        "zh": "\u5df2\u6e05\u9664 {count} \u6761\u6301\u4e45\u5316\u7ed1\u5b9a\u8bb0\u5f55",
        "en": "Cleared {count} persisted records",
    },
    "info_download_hint": {
        "zh": "\u8bf7\u5728 GitHub \u9875\u9762\u4e0b\u8f7d\u6700\u65b0\u7684 usbipd-win \u5b89\u88c5\u5305",
        "en": "Download the latest usbipd-win from GitHub",
    },
    "log_detach_all_done": {
        "zh": "\u5168\u90e8\u65ad\u5f00: \u5171 {count} \u4e2a\u8bbe\u5907",
        "en": "Detach all: {count} devices",
    },
    "log_detach_batch": {
        "zh": "\u6279\u91cf\u65ad\u5f00: {count} \u4e2a\u8bbe\u5907",
        "en": "Batch detach: {count} devices",
    },
    "log_bind_batch_ok": {
        "zh": "\u6279\u91cf\u5171\u4eab: \u5df2\u5171\u4eab {count} \u4e2a\u8bbe\u5907",
        "en": "Batch share: {count} shared",
    },
    "log_bind_batch_partial": {
        "zh": "\u6279\u91cf\u5171\u4eab: \u6210\u529f {ok} \u4e2a\uff0c\u5931\u8d25 {fail} \u4e2a",
        "en": "Batch share: {ok} ok, {fail} failed",
    },
}


def _load_lang() -> str:
    """加载语言配置：优先读持久化文件，否则检测系统语言"""
    try:
        if LANG_FILE.exists():
            data = json.loads(LANG_FILE.read_text(encoding="utf-8"))
            lang = data.get("lang", "")
            if lang in ("zh", "en"):
                return lang
    except Exception:
        pass
    return get_system_language()


def _save_lang(lang: str):
    """持久化语言配置"""
    try:
        LANG_FILE.parent.mkdir(parents=True, exist_ok=True)
        LANG_FILE.write_text(json.dumps({"lang": lang}), encoding="utf-8")
    except Exception:
        pass


_current_lang = _load_lang()


def tr(key: str, **kwargs) -> str:
    """获取翻译文本"""
    entry = TEXTS.get(key, {})
    text = entry.get(_current_lang) or entry.get("en", key)
    if kwargs:
        text = text.format(**kwargs)
    return text


def set_language(lang: str):
    """切换语言并持久化"""
    global _current_lang
    if lang in ("zh", "en"):
        _current_lang = lang
        _save_lang(lang)


def get_language() -> str:
    """获取当前语言"""
    return _current_lang
