from PyQt6.QtGui import QColor

# ── 柔和配色方案 ───────────────────────────────────────────────
COLORS = {
    "SUCCESS": QColor(76, 175, 80),
    "ERROR": QColor(229, 57, 53),
    "WARNING": QColor(255, 152, 0),
    "INFO": QColor(33, 150, 243),
    "DISABLED": QColor(158, 158, 158),
    "BORDER": QColor(224, 224, 224),
    "BACKGROUND_LIGHT": QColor(245, 245, 245),
    "SELECTION": QColor(227, 242, 253),
}

# 状态文本
STATUS = {
    "DISCONNECTED": "断开",
    "CONNECTED": "连接",
    "SHARED": "共享",
    "BOUND": "已绑定",
}

# 表格列宽
TABLE_COLUMNS = {
    "VID_PID": 120,
    "ACTION": 85,
}

# 按钮大小
BUTTON_SIZE = {
    "SMALL": (60, 28),
    "MEDIUM": (72, 28),
    "LARGE": (120, 30),
    "STATUS_BAR": 32,
}

# 容器最小高度
CONTAINER_HEIGHT = {
    "TABLE": 160,
    "WSL_LIST": 130,
}

# 主题色
THEME_COLOR = "#1976D2"
