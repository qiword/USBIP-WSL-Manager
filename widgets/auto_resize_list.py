"""自适应宽度 + 手动高亮的 QListWidget"""

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QListWidget


class AutoResizeListWidget(QListWidget):
    """自适应 item widget 宽度 + 手动高亮的 QListWidget"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._last_selected = -1
        self.itemSelectionChanged.connect(self._on_selection)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._update_item_widths()

    def rowsInserted(self, parent, start, end):
        super().rowsInserted(parent, start, end)
        QTimer.singleShot(50, self._update_item_widths)

    def _on_selection(self):
        if self._last_selected >= 0:
            w = self.itemWidget(self.item(self._last_selected))
            if w:
                w.setStyleSheet("background: transparent;")
        items = self.selectedItems()
        if items:
            row = self.row(items[0])
            self._last_selected = row
            w = self.itemWidget(self.item(row))
            if w:
                w.setStyleSheet("background-color: #e8e8e8; border-radius: 6px;")
        else:
            self._last_selected = -1

    def _update_item_widths(self):
        w = self.viewport().width() - 4
        if w < 100:
            return
        for i in range(self.count()):
            widget = self.itemWidget(self.item(i))
            if widget:
                widget.setFixedWidth(w)
