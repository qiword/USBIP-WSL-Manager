"""单实例检测 + 激活已有窗口（使用 QSharedMemory）"""

from PyQt6.QtCore import QSharedMemory, QSystemSemaphore, QTimer
from PyQt6.QtNetwork import QLocalServer, QLocalSocket

SERVER_NAME = "USBIP-WSL-Manager"
ACTIVATE_MSG = b"ACTIVATE"
SEMAPHORE_KEY = "USBIP-WSL-Manager-Sem"
SHARED_MEM_KEY = "USBIP-WSL-Manager-Mem"


class SingleInstance:
    """单实例管理器"""

    def __init__(self, on_activate=None):
        self._sem = QSystemSemaphore(SEMAPHORE_KEY, 1)
        self._shared_mem = QSharedMemory(SHARED_MEM_KEY)
        self._server = QLocalServer()
        self._on_activate = on_activate

    def try_acquire(self) -> bool:
        """返回 True = 首个实例；False = 已有实例"""
        self._sem.acquire()

        # 检查共享内存是否已存在
        already_running = self._shared_mem.attach()
        if already_running:
            self._shared_mem.detach()
            self._sem.release()
            self._notify_existing()
            return False

        # 创建共享内存
        if not self._shared_mem.create(1):
            self._sem.release()
            return False

        # 启动本地服务器监听激活请求
        self._server.listen(SERVER_NAME)
        self._server.newConnection.connect(self._on_new_connection)

        self._sem.release()
        return True

    def _notify_existing(self):
        sock = QLocalSocket()
        sock.connectToServer(SERVER_NAME)
        if sock.waitForConnected(1000):
            sock.write(ACTIVATE_MSG)
            sock.flush()
            sock.waitForBytesWritten(500)
        sock.close()

    def _on_new_connection(self):
        sock = self._server.nextPendingConnection()
        if sock:
            sock.waitForReadyRead(500)
            if sock.bytesAvailable():
                msg = sock.readAll().data()
                if msg == ACTIVATE_MSG and self._on_activate:
                    self._on_activate()
            sock.disconnectFromServer()
            sock.close()

    def release(self):
        self._server.close()
        if self._shared_mem.isAttached():
            self._shared_mem.detach()
