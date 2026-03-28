from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QComboBox, QTextEdit, QPushButton,
    QGroupBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QWidget
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor
from typing import List, Optional

from data import ErrorRecord, ErrorType, ErrorStatus
from core import QueryService


class QueryDialog(QDialog):
    error_selected = pyqtSignal(str)

    def __init__(self, parent=None, query_service: Optional[QueryService] = None):
        super().__init__(parent)
        
        self.query_service = query_service
        self._results: List[ErrorRecord] = []
        
        self.setWindowTitle("错误查询")
        self.setMinimumSize(600, 500)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        search_group = QGroupBox("搜索条件")
        search_layout = QVBoxLayout(search_group)
        
        keyword_layout = QHBoxLayout()
        keyword_layout.addWidget(QLabel("关键字:"))
        self.keyword_input = QLineEdit()
        self.keyword_input.setPlaceholderText("输入错误编号、描述或图层名称...")
        self.keyword_input.returnPressed.connect(self.search)
        keyword_layout.addWidget(self.keyword_input)
        
        self.search_btn = QPushButton("搜索")
        self.search_btn.clicked.connect(self.search)
        keyword_layout.addWidget(self.search_btn)
        
        search_layout.addLayout(keyword_layout)
        
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("错误类型:"))
        self.type_combo = QComboBox()
        self.type_combo.addItem("全部", None)
        for error_type in ErrorType:
            self.type_combo.addItem(error_type.value, error_type)
        filter_layout.addWidget(self.type_combo)
        
        filter_layout.addWidget(QLabel("状态:"))
        self.status_combo = QComboBox()
        self.status_combo.addItem("全部", None)
        for status in ErrorStatus:
            self.status_combo.addItem(status.value, status)
        filter_layout.addWidget(self.status_combo)
        
        filter_layout.addStretch()
        
        search_layout.addLayout(filter_layout)
        layout.addWidget(search_group)
        
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(5)
        self.result_table.setHorizontalHeaderLabels([
            "错误编号", "类型", "描述", "位置", "状态"
        ])
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.result_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.result_table.setSelectionMode(QTableWidget.SingleSelection)
        self.result_table.doubleClicked.connect(self._on_result_double_clicked)
        layout.addWidget(self.result_table)
        
        self.result_label = QLabel("共 0 条结果")
        layout.addWidget(self.result_label)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        goto_btn = QPushButton("定位到错误")
        goto_btn.clicked.connect(self._goto_selected)
        btn_layout.addWidget(goto_btn)
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.close)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)

    def search(self):
        if not self.query_service:
            return
        
        keyword = self.keyword_input.text().strip()
        error_type = self.type_combo.currentData()
        status = self.status_combo.currentData()
        
        if keyword or error_type or status:
            self._results = self.query_service.advanced_search(
                keyword=keyword,
                error_type=error_type,
                status=status
            )
        else:
            self._results = self.query_service.search_by_keyword("")
        
        self._display_results()

    def _display_results(self):
        self.result_table.setRowCount(len(self._results))
        
        for row, error in enumerate(self._results):
            self.result_table.setItem(row, 0, QTableWidgetItem(error.error_id))
            self.result_table.setItem(row, 1, QTableWidgetItem(error.error_type.value))
            
            desc = error.description[:30] + "..." if len(error.description) > 30 else error.description
            self.result_table.setItem(row, 2, QTableWidgetItem(desc))
            
            pos_text = f"({error.position[0]:.1f}, {error.position[1]:.1f})"
            self.result_table.setItem(row, 3, QTableWidgetItem(pos_text))
            
            self.result_table.setItem(row, 4, QTableWidgetItem(error.status.value))
            
            color_map = {
                ErrorType.GEOMETRY: QColor(255, 200, 200),
                ErrorType.ATTRIBUTE: QColor(200, 255, 200),
                ErrorType.TOPOLOGY: QColor(200, 200, 255),
                ErrorType.COORDINATE: QColor(255, 255, 200),
                ErrorType.OTHER: QColor(220, 220, 220)
            }
            
            bg_color = color_map.get(error.error_type, QColor(255, 255, 255))
            for col in range(5):
                item = self.result_table.item(row, col)
                if item:
                    item.setBackground(bg_color)
        
        self.result_label.setText(f"共 {len(self._results)} 条结果")

    def _on_result_double_clicked(self):
        self._goto_selected()

    def _goto_selected(self):
        selected_rows = self.result_table.selectedItems()
        if selected_rows:
            row = selected_rows[0].row()
            if 0 <= row < len(self._results):
                error_id = self._results[row].error_id
                self.error_selected.emit(error_id)
                self.close()
