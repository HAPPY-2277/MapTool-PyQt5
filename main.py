import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from ui import MainWindow
from utils import logger


def main():
    logger.info("启动空间数据质量检查工具...")
    
    app = QApplication(sys.argv)
    
    app.setApplicationName("空间数据质量检查工具")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("SpatialDataQC")
    
    app.setStyle('Fusion')
    
    font = QFont("Microsoft YaHei", 9)
    app.setFont(font)
    
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f5f5f5;
        }
        QToolBar {
            background-color: #e8e8e8;
            border-bottom: 1px solid #c0c0c0;
            spacing: 5px;
            padding: 3px;
        }
        QToolBar QToolButton {
            background-color: transparent;
            border: 1px solid transparent;
            border-radius: 3px;
            padding: 5px;
            min-width: 60px;
        }
        QToolBar QToolButton:hover {
            background-color: #d0d0d0;
            border: 1px solid #a0a0a0;
        }
        QToolBar QToolButton:pressed {
            background-color: #c0c0c0;
        }
        QToolBar QToolButton:checked {
            background-color: #b0d0f0;
            border: 1px solid #4080c0;
        }
        QStatusBar {
            background-color: #e0e0e0;
            border-top: 1px solid #c0c0c0;
        }
        QListWidget {
            border: 1px solid #c0c0c0;
            background-color: white;
        }
        QListWidget::item {
            padding: 5px;
            border-bottom: 1px solid #e0e0e0;
        }
        QListWidget::item:selected {
            background-color: #b0d0f0;
            color: black;
        }
        QListWidget::item:hover {
            background-color: #e8f0f8;
        }
        QGroupBox {
            font-weight: bold;
            border: 1px solid #c0c0c0;
            border-radius: 3px;
            margin-top: 10px;
            padding-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }
        QTextEdit {
            border: 1px solid #c0c0c0;
            background-color: white;
        }
        QComboBox {
            border: 1px solid #c0c0c0;
            border-radius: 3px;
            padding: 2px 5px;
            background-color: white;
        }
        QComboBox::drop-down {
            border: none;
            width: 20px;
        }
        QPushButton {
            background-color: #f0f0f0;
            border: 1px solid #c0c0c0;
            border-radius: 3px;
            padding: 5px 15px;
            min-width: 60px;
        }
        QPushButton:hover {
            background-color: #e0e0e0;
            border: 1px solid #a0a0a0;
        }
        QPushButton:pressed {
            background-color: #d0d0d0;
        }
        QTableWidget {
            border: 1px solid #c0c0c0;
            background-color: white;
            gridline-color: #e0e0e0;
        }
        QTableWidget::item {
            padding: 5px;
        }
        QTableWidget::item:selected {
            background-color: #b0d0f0;
            color: black;
        }
        QHeaderView::section {
            background-color: #e8e8e8;
            padding: 5px;
            border: 1px solid #c0c0c0;
            font-weight: bold;
        }
    """)
    
    window = MainWindow()
    window.show()
    
    logger.info("应用程序窗口已显示")
    
    exit_code = app.exec_()
    
    logger.info(f"应用程序退出，退出码: {exit_code}")
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
