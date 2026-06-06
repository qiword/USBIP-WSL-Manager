"""
USB/IP 设备管理器
通过调用 Windows usbipd 命令管理 USB 设备的共享、绑定、连接等操作。
"""

import json
import shutil
import subprocess
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class UsbDevice:
    """USB 设备数据结构"""

    busid: str
    vid: str
    pid: str
    name: str
    instance_id: str = ""
    # 绑定状态: None=未共享, "bound"=已绑定(强制共享), "shared"=共享(未强制)
    bind_state: Optional[str] = None
    # 连接状态: None=未连接, (client_ip, wsl_distro)
    attached_client: Optional[str] = None
    attached_wsl: Optional[str] = None
    is_forced: bool = False
    persisted_guid: Optional[str] = None

    @property
    def vid_pid(self) -> str:
        return f"{self.vid}:{self.pid}"

    @property
    def status_text(self) -> str:
        """返回中文状态文本"""
        if self.attached_wsl:
            return f"已连接({self.attached_wsl})"
        if self.bind_state == "bound":
            return "已绑定"
        if self.bind_state == "shared":
            return "已共享"
        return "未共享"

    @property
    def is_shared(self) -> bool:
        return self.bind_state is not None

    @property
    def is_attached(self) -> bool:
        return self.attached_client is not None

    def to_dict(self) -> dict:
        """转为表格数据字典"""
        return {
            "busid": self.busid,
            "vid": self.vid,
            "pid": self.pid,
            "name": self.name,
            "status": self.status_text,
            "is_bound": self.bind_state == "bound",
            "is_shared": self.is_shared,
            "is_attached": self.is_attached,
            "attached_wsl": self.attached_wsl,
            "_obj": self,
        }

    def to_wsl_dict(self) -> dict:
        """转为 WSL 列表数据字典"""
        return {
            "busid": self.busid,
            "vid": self.vid,
            "pid": self.pid,
            "name": self.name,
            "status": "\u5df2\u8fde\u63a5",
            "wsl_distro": self.attached_wsl or "WSL",
            "_obj": self,
        }


def _find_usbipd() -> str:
    """查找 usbipd.exe 路径"""
    path = shutil.which("usbipd")
    if path:
        return path
    # 常见安装路径
    candidates = [
        r"C:\Program Files\usbipd-win\usbipd.exe",
        r"C:\Program Files (x86)\usbipd-win\usbipd.exe",
    ]
    for c in candidates:
        if shutil.which(c):
            return c
    return "usbipd"  # fallback


def _find_wsl() -> str:
    """查找 wsl.exe 路径"""
    path = shutil.which("wsl")
    if path:
        return path
    candidates = [
        r"C:\Windows\System32\wsl.exe",
        r"C:\Windows\Sysnative\wsl.exe",
    ]
    for c in candidates:
        if shutil.which(c):
            return c
    return "wsl"


class UsbipManager:
    """USB/IP 设备管理器"""

    def __init__(self):
        self._usbipd = _find_usbipd()
        self._wsl = _find_wsl()

    # ------------------------------------------------------------------
    # 设备列表获取
    # ------------------------------------------------------------------

    def get_all_devices(self) -> list[UsbDevice]:
        """获取 Windows 端所有 USB 设备列表（含状态）"""
        raw = self._run_json(["state"])
        if raw is None:
            return self._fallback_list()

        devices = []
        for d in raw.get("Devices", []):
            busid = d.get("BusId", "")
            # 解析 VID:PID
            instance_id = d.get("InstanceId", "")
            vid, pid = self._parse_vid_pid(instance_id)
            description = d.get("Description", "Unknown Device").strip()

            device = UsbDevice(
                busid=busid,
                vid=vid,
                pid=pid,
                name=description,
                instance_id=instance_id,
                is_forced=d.get("IsForced", False),
                persisted_guid=d.get("PersistedGuid"),
                attached_client=d.get("ClientIPAddress"),
            )
            # 判断绑定状态：
            # StubInstanceId 不为空 = 在线绑定中
            # PersistedGuid 不为空 = 持久化绑定记录
            # 只靠 IsForced 不靠谱（可能是残留标记）
            if d.get("StubInstanceId"):
                device.bind_state = "bound" if d.get("IsForced") else "shared"
            elif d.get("PersistedGuid"):
                device.bind_state = "bound"
            # 判断 WSL 连接
            if device.attached_client:
                device.attached_wsl = self._resolve_wsl_distro(device.attached_client)

            devices.append(device)
        return devices

    def get_wsl_devices(self) -> list[UsbDevice]:
        """获取已连接到 WSL 的设备"""
        all_devices = self.get_all_devices()
        return [d for d in all_devices if d.attached_wsl is not None]

    def get_shareable_devices(self) -> list[UsbDevice]:
        """获取可共享的设备（未绑定、未连接）"""
        all_devices = self.get_all_devices()
        return [
            d for d in all_devices if d.bind_state is None and d.attached_client is None
        ]

    def get_bound_devices(self) -> list[UsbDevice]:
        """获取已绑定（强制共享）的设备"""
        all_devices = self.get_all_devices()
        return [d for d in all_devices if d.bind_state == "bound"]

    def get_persisted_devices(self) -> list[UsbDevice]:
        """获取持久化绑定记录（BusId 为空 = 设备不在线）"""
        all_devices = self.get_all_devices()
        return [d for d in all_devices if d.persisted_guid and not d.busid]

    def unbind_persisted(self, guid: str) -> tuple[bool, str]:
        """删除持久化绑定记录"""
        return self._run_cmd(["unbind", "--guid", guid])

    # ------------------------------------------------------------------
    # 操作命令
    # ------------------------------------------------------------------

    def bind(self, busid: str, force: bool = False) -> tuple[bool, str]:
        """绑定设备（注册为可共享）"""
        cmd = ["bind", "--busid", busid]
        if force:
            cmd.append("--force")
        return self._run_cmd(cmd)

    def unbind(self, busid: str) -> tuple[bool, str]:
        """解绑设备"""
        return self._run_cmd(["unbind", "--busid", busid])

    def unbind_all(self) -> tuple[bool, str]:
        """解绑所有设备"""
        return self._run_cmd(["unbind", "--all"])

    def attach(
        self, busid: str, wsl_distro: str = "", auto_attach: bool = False
    ) -> tuple[bool, str]:
        """将设备连接到 WSL"""
        cmd = ["attach", "--busid", busid]
        if auto_attach:
            cmd.append("--auto-attach")
        if wsl_distro:
            cmd.extend(["--wsl", wsl_distro])
        else:
            cmd.append("--wsl")
        return self._run_cmd(cmd)

    def detach(self, busid: str) -> tuple[bool, str]:
        """从客户端断开设备"""
        return self._run_cmd(["detach", "--busid", busid])

    def detach_all(self) -> tuple[bool, str]:
        """断开所有设备"""
        return self._run_cmd(["detach", "--all"])

    # ------------------------------------------------------------------
    # WSL 发行版
    # ------------------------------------------------------------------

    def get_wsl_distributions(self) -> list[dict]:
        """获取 WSL 发行版列表"""
        try:
            result = subprocess.run(
                [self._wsl, "--list", "--verbose"],
                capture_output=True,
                encoding="utf-16-le",
                errors="replace",
                timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            lines = result.stdout.strip().split("\n")
            distros = []
            for line in lines[1:]:  # 跳过标题行
                if not line.strip():
                    continue
                # 格式: "* Ubuntu-24.04    Running    2"
                # 或:   "  Debian          Stopped    2"
                parts = line.split()
                if len(parts) >= 2:
                    starred = parts[0] == "*"
                    name = parts[1] if starred else parts[0]
                    state = parts[2] if starred else parts[1]
                    distros.append(
                        {
                            "name": name,
                            "running": state == "Running",
                            "default": starred,
                        }
                    )
            return distros
        except Exception:
            return []

    def get_default_wsl_distro(self) -> str:
        """获取默认 WSL 发行版名称"""
        distros = self.get_wsl_distributions()
        for d in distros:
            if d["default"]:
                return d["name"]
        if distros:
            return distros[0]["name"]
        return ""

    # ------------------------------------------------------------------
    # 内部辅助
    # ------------------------------------------------------------------

    def _run_cmd(self, args: list[str]) -> tuple[bool, str]:
        """执行 usbipd 命令，返回 (成功, 消息)"""
        try:
            result = subprocess.run(
                [self._usbipd] + args,
                capture_output=True,
                encoding="utf-8",
                errors="replace",
                timeout=30,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            output = (result.stdout + result.stderr).strip()
            if result.returncode == 0:
                return True, output or "操作成功"
            return False, output or f"命令执行失败 (code={result.returncode})"
        except subprocess.TimeoutExpired:
            return False, "命令执行超时"
        except FileNotFoundError:
            return False, f"找不到 usbipd，请确认已安装 usbipd-win"
        except Exception as e:
            return False, str(e)

    def _run_json(self, args: list[str]) -> Optional[dict]:
        """执行 usbipd 命令并解析 JSON 输出"""
        try:
            result = subprocess.run(
                [self._usbipd] + args,
                capture_output=True,
                encoding="utf-8",
                errors="replace",
                timeout=15,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            if result.returncode != 0:
                return None
            return json.loads(result.stdout)
        except (json.JSONDecodeError, subprocess.TimeoutExpired, FileNotFoundError):
            return None

    def _fallback_list(self) -> list[UsbDevice]:
        """使用 usbipd list 文本输出作为降级解析"""
        try:
            result = subprocess.run(
                [self._usbipd, "list"],
                capture_output=True,
                encoding="utf-8",
                errors="replace",
                timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            lines = result.stdout.split("\n")
            devices = []
            in_body = False
            for line in lines:
                line = line.strip()
                if line.startswith("BUSID"):
                    in_body = True
                    continue
                if not in_body or not line:
                    continue
                parts = line.split()
                if len(parts) < 3:
                    continue
                busid = parts[0]
                vid_pid = parts[1]
                vid, _, pid = vid_pid.partition(":")
                name = " ".join(parts[2:]).rsplit("  ", 1)[0].strip()
                devices.append(UsbDevice(busid=busid, vid=vid, pid=pid, name=name))
            return devices
        except Exception:
            return []

    @staticmethod
    def _parse_vid_pid(instance_id: str) -> tuple[str, str]:
        """从 Windows 设备实例 ID 中提取 VID 和 PID"""
        vid, pid = "", ""
        import re

        m_vid = re.search(r"VID_([0-9A-Fa-f]+)", instance_id)
        m_pid = re.search(r"PID_([0-9A-Fa-f]+)", instance_id)
        if m_vid:
            vid = m_vid.group(1)
        if m_pid:
            pid = m_pid.group(1)
        return vid, pid

    def _resolve_wsl_distro(self, client_ip: str) -> Optional[str]:
        """通过 client IP 推测对应的 WSL 发行版"""
        distros = self.get_wsl_distributions()
        running = [d for d in distros if d["running"]]
        if running:
            return running[0]["name"]
        return None
