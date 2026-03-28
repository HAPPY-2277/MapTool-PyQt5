from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QLabel,
    QScrollBar
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QTextCursor, QColor, QTextCharFormat
from typing import Optional, List

from data import MapData


class TextViewer(QWidget):
    line_clicked = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.map_data: Optional[MapData] = None
        self.lines: List[str] = []
        self.highlighted_line: int = -1
        
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        header = QLabel("文本内容")
        header.setStyleSheet("font-weight: bold; padding: 5px; background-color: #f0f0f0;")
        layout.addWidget(header)
        
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setFont(QFont("Consolas", 10))
        self.text_edit.setLineWrapMode(QTextEdit.NoWrap)
        self.text_edit.mousePressEvent = self._on_mouse_press
        layout.addWidget(self.text_edit)
        
        self.line_number_bar = QLabel("行号: -")
        self.line_number_bar.setStyleSheet("padding: 3px; background-color: #e0e0e0;")
        layout.addWidget(self.line_number_bar)

    def load_text(self, map_data: MapData):
        self.map_data = map_data
        self.lines = map_data.text_lines or []
        
        content_with_lines = ""
        for i, line in enumerate(self.lines):
            content_with_lines += f"{i+1:5d} | {line}\n"
        
        self.text_edit.setPlainText(content_with_lines)

    def highlight_line(self, line_number: int):
        cursor = self.text_edit.textCursor()
        
        cursor.movePosition(QTextCursor.Start)
        for _ in range(line_number):
            cursor.movePosition(QTextCursor.Down)
        
        cursor.select(QTextCursor.LineUnderCursor)
        
        extra_selections = []
        selection = QTextEdit.ExtraSelection()
        selection.format.setBackground(QColor(255, 255, 0, 100))
        selection.format.setProperty(QTextCharFormat.FullWidthSelection, True)
        selection.cursor = cursor
        extra_selections.append(selection)
        
        self.text_edit.setExtraSelections(extra_selections)
        
        self.text_edit.setTextCursor(cursor)
        self.text_edit.ensureCursorVisible()
        
        self.line_number_bar.setText(f"行号: {line_number + 1}")
        self.highlighted_line = line_number

    def _on_mouse_press(self, event):
        if event.button() == Qt.LeftButton:
            cursor = self.text_edit.cursorForPosition(event.pos())
            
            cursor.movePosition(QTextCursor.StartOfLine)
            line_text = cursor.block().text()
            
            if line_text.strip():
                parts = line_text.split('|')
                if parts:
                    try:
                        line_num = int(parts[0].strip()) - 1
                        self.line_clicked.emit(line_num)
                    except ValueError:
                        pass
        
        from PyQt5.QtGui import QMouseEvent
        QTextEdit.mousePressEvent(self.text_edit, event)

    def clear_highlight(self):
        self.text_edit.setExtraSelections([])
        self.highlighted_line = -1
        self.line_number_bar.setText("行号: -")
