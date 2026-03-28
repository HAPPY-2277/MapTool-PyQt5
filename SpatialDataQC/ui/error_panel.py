from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QPushButton, QComboBox,
    QGroupBox, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QFont
from typing import List, Optional

from data import ErrorRecord, ErrorType, ErrorStatus


class ErrorPanel(QWidget):
    error_selected = pyqtSignal(str)
    error_delete_requested = pyqtSignal(str)
    error_edit_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._errors: List[ErrorRecord] = []
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        header_layout = QHBoxLayout()
        header_label = QLabel("错误记录列表")
        header_label.setFont(QFont("Arial", 11, QFont.Bold))
        header_layout.addWidget(header_label)
        
        self.count_label = QLabel("(0)")
        header_layout.addWidget(self.count_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        filter_group = QGroupBox("筛选")
        filter_layout = QHBoxLayout(filter_group)
        
        filter_layout.addWidget(QLabel("类型:"))
        self.type_filter = QComboBox()
        self.type_filter.addItem("全部", None)
        for error_type in ErrorType:
            self.type_filter.addItem(error_type.value, error_type)
        self.type_filter.currentIndexChanged.connect(self._apply_filter)
        filter_layout.addWidget(self.type_filter)
        
        filter_layout.addWidget(QLabel("状态:"))
        self.status_filter = QComboBox()
        self.status_filter.addItem("全部", None)
        for status in ErrorStatus:
            self.status_filter.addItem(status.value, status)
        self.status_filter.currentIndexChanged.connect(self._apply_filter)
        filter_layout.addWidget(self.status_filter)
        
        layout.addWidget(filter_group)
        
        self.error_list = QListWidget()
        self.error_list.itemClicked.connect(self._on_item_clicked)
        self.error_list.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.error_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.error_list.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self.error_list)
        
        btn_layout = QHBoxLayout()
        
        self.edit_btn = QPushButton("编辑")
        self.edit_btn.clicked.connect(self._edit_selected)
        btn_layout.addWidget(self.edit_btn)
        
        self.delete_btn = QPushButton("删除")
        self.delete_btn.clicked.connect(self._delete_selected)
        btn_layout.addWidget(self.delete_btn)
        
        layout.addLayout(btn_layout)

    def update_errors(self, errors: List[ErrorRecord]):
        self._errors = errors
        self._refresh_list()

    def add_error(self, error: ErrorRecord):
        self._errors.append(error)
        self._add_list_item(error)
        self._update_count()

    def remove_error(self, error_id: str):
        self._errors = [e for e in self._errors if e.error_id != error_id]
        self._refresh_list()

    def refresh_errors(self, errors: List[ErrorRecord]):
        self._errors = errors
        self._refresh_list()

    def clear_errors(self):
        self._errors.clear()
        self.error_list.clear()
        self._update_count()

    def select_error(self, error_id: str):
        for i in range(self.error_list.count()):
            item = self.error_list.item(i)
            if item.data(Qt.UserRole) == error_id:
                self.error_list.setCurrentItem(item)
                self.error_list.scrollToItem(item)
                break

    def _refresh_list(self):
        self.error_list.clear()
        
        type_filter = self.type_filter.currentData()
        status_filter = self.status_filter.currentData()
        
        filtered_errors = []
        for error in self._errors:
            if type_filter and error.error_type != type_filter:
                continue
            if status_filter and error.status != status_filter:
                continue
            filtered_errors.append(error)
        
        for error in filtered_errors:
            self._add_list_item(error)
        
        self._update_count()

    def _add_list_item(self, error: ErrorRecord):
        item = QListWidgetItem()
        item.setData(Qt.UserRole, error.error_id)
        
        text = f"{error.error_id}\n"
        text += f"类型: {error.error_type.value}\n"
        text += f"描述: {error.description[:30]}..." if len(error.description) > 30 else f"描述: {error.description}\n"
        text += f"位置: ({error.position[0]:.1f}, {error.position[1]:.1f})\n"
        text += f"状态: {error.status.value}"
        
        item.setText(text)
        
        color_map = {
            ErrorType.GEOMETRY: QColor(255, 100, 100),
            ErrorType.ATTRIBUTE: QColor(100, 200, 100),
            ErrorType.TOPOLOGY: QColor(100, 100, 255),
            ErrorType.COORDINATE: QColor(255, 200, 100),
            ErrorType.OTHER: QColor(150, 150, 150)
        }
        item.setForeground(color_map.get(error.error_type, QColor(0, 0, 0)))
        
        self.error_list.addItem(item)

    def _update_count(self):
        self.count_label.setText(f"({len(self._errors)})")

    def _apply_filter(self):
        self._refresh_list()

    def _on_item_clicked(self, item: QListWidgetItem):
        error_id = item.data(Qt.UserRole)
        self.error_selected.emit(error_id)

    def _on_item_double_clicked(self, item: QListWidgetItem):
        error_id = item.data(Qt.UserRole)
        self.error_edit_requested.emit(error_id)

    def _show_context_menu(self, pos):
        item = self.error_list.itemAt(pos)
        if item:
            from PyQt5.QtWidgets import QMenu
            menu = QMenu(self)
            
            edit_action = menu.addAction("编辑")
            delete_action = menu.addAction("删除")
            
            from PyQt5.QtWidgets import QAction
            action = menu.exec_(self.error_list.mapToGlobal(pos))
            
            error_id = item.data(Qt.UserRole)
            if action == edit_action:
                self.error_edit_requested.emit(error_id)
            elif action == delete_action:
                self.error_delete_requested.emit(error_id)

    def _edit_selected(self):
        current_item = self.error_list.currentItem()
        if current_item:
            error_id = current_item.data(Qt.UserRole)
            self.error_edit_requested.emit(error_id)

    def _delete_selected(self):
        current_item = self.error_list.currentItem()
        if current_item:
            error_id = current_item.data(Qt.UserRole)
            self.error_delete_requested.emit(error_id)
