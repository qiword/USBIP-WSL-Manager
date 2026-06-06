"""后台命令执行线程 —— 在子线程中执行 usbipd 命令，避免阻塞 UI"""

from PyQt6.QtCore import QThread, pyqtSignal


class CmdThread(QThread):
    """在子线程中执行 usbipd 命令"""

    finished_signal = pyqtSignal(bool, str, str)  # ok, msg, action_tag

    def __init__(
        self,
        usbip_manager,
        action_tag: str,
        *,
        busid: str = "",
        busids: list[str] | None = None,
        wsl_distro: str = "",
        parent=None,
    ):
        super().__init__(parent)
        self._mgr = usbip_manager
        self._action = action_tag
        self._busid = busid
        self._busids = busids or []
        self._wsl_distro = wsl_distro

    def run(self):
        mgr = self._mgr
        tag = self._action
        if tag == "bind":
            ok, msg = mgr.bind(self._busid, force=True)
            if ok:
                ok2, msg2 = mgr.attach(self._busid, wsl_distro=self._wsl_distro)
                msg = msg2
                if not ok2:
                    ok = False
                else:
                    distro = self._wsl_distro or mgr.get_default_wsl_distro()
                    mgr.set_busid_distro(self._busid, distro)
            self.finished_signal.emit(ok, msg, tag)
        elif tag == "detach":
            ok, msg = mgr.detach(self._busid)
            mgr.unbind(self._busid)
            self.finished_signal.emit(ok, msg, tag)
        elif tag == "bind_batch":
            ok, fail = 0, 0
            for bid in self._busids:
                s, _ = mgr.bind(bid, force=True)
                if s:
                    s2, _ = mgr.attach(bid, wsl_distro=self._wsl_distro)
                    if s2:
                        ok += 1
                    else:
                        fail += 1
                else:
                    fail += 1
            msg = (
                f"已共享 {ok} 个设备" if fail == 0 else f"成功 {ok} 个，失败 {fail} 个"
            )
            self.finished_signal.emit(True, msg, tag)
        elif tag == "detach_batch":
            for bid in self._busids:
                mgr.detach(bid)
                mgr.unbind(bid)
            self.finished_signal.emit(True, f"已断开 {len(self._busids)} 个设备", tag)
        elif tag == "bind_only_batch":
            ok, fail = 0, 0
            for bid in self._busids:
                s, _ = mgr.bind(bid, force=True)
                if s:
                    ok += 1
                else:
                    fail += 1
            msg = (
                f"已绑定 {ok} 个设备" if fail == 0 else f"成功 {ok} 个，失败 {fail} 个"
            )
            self.finished_signal.emit(True, msg, tag)
        elif tag == "unbind_batch":
            for bid in self._busids:
                mgr.unbind(bid)
            self.finished_signal.emit(True, f"已解绑 {len(self._busids)} 个设备", tag)
        elif tag == "attach_batch":
            ok, fail = 0, 0
            for bid in self._busids:
                s, _ = mgr.attach(bid, wsl_distro=self._wsl_distro)
                if s:
                    ok += 1
                else:
                    fail += 1
            msg = (
                f"已连接 {ok} 个设备到 WSL"
                if fail == 0
                else f"成功 {ok} 个，失败 {fail} 个"
            )
            self.finished_signal.emit(True, msg, tag)
        elif tag == "wsl_detach":
            for bid in self._busids:
                mgr.detach(bid)
                mgr.unbind(bid)
            self.finished_signal.emit(
                True, f"已从 WSL 断开 {len(self._busids)} 个设备", tag
            )
