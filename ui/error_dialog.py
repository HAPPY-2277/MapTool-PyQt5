from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QComboBox, QTextEdit, QPushButton,
    QGroupBox
)
from PyQt5.QtCore import Qt
from typing import Optional, Tuple

from data import ErrorRecord, ErrorType


class ErrorDialog(QDialog):
    def __init__(self, parent=None, error: Optional[ErrorRecord] = None):
        super().__init__(parent)
        
        self.error = error
        self.is_edit_mode = error is not None
        
        title = "编辑错误" if self.is_edit_mode else "添加错误记录"
        self.setWindowTitle(title)
        self.setMinimumWidth(400)
        
        self._init_ui()
        
        if self.is_edit_mode and error:
            self._load_error_data()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        info_group = QGroupBox("错误信息")
        info_layout = QVBoxLayout(info_group)
        
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("错误类型:"))
        self.type_combo = QComboBox()
        for error_type in ErrorType:
            self.type_combo.addItem(error_type.value, error_type)
        type_layout.addWidget(self.type_combo)
        type_layout.addStretch()
        info_layout.addLayout(type_layout)
        
        info_layout.addWidget(QLabel("错误描述:"))
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("请输入错误描述信息...")
        self.description_edit.setMaximumHeight(100)
        info_layout.addWidget(self.description_edit)
        
        layout.addWidget(info_group)
        
        if self.is_edit_mode and self.error:
            position_group = QGroupBox("位置信息")
            position_layout = QHBoxLayout(position_group)
            position_layout.addWidget(QLabel(f"X: {self.error.position[0]:.2f}"))
            position_layout.addWidget(QLabel(f"Y: {self.error.position[1]:.2f}"))
            position_layout.addStretch()
            layout.addWidget(position_group)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)

    def _load_error_data(self):
        if not self.error:
            return
        
        index = self.type_combo.findData(self.error.error_type)
        if index >= 0:
            self.type_combo.setCurrentIndex(index)
        
        self.description_edit.setPlainText(self.error.description)

    def get_error_info(self) -> Tuple[ErrorType, str]:
        error_type = self.type_combo.currentData()
        description = self.description_edit.toPlainText().strip()
        return error_type, description
