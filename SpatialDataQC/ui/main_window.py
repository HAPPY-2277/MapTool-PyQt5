import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QMenuBar, QMenu, QAction, QToolBar, QStatusBar,
    QFileDialog, QMessageBox, QSplitter, QLabel
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QKeySequence

from core import DataLoaderService, ErrorManagerService, QueryService
from data import ErrorType, ErrorStatus
from .map_canvas import MapCanvas
from .error_panel import ErrorPanel
from .text_viewer import TextViewer
from .query_dialog import QueryDialog
from .error_dialog import ErrorDialog


class MainWindow(QMainWindow):
    data_loaded = pyqtSignal(str)
    error_created = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        
        self.data_loader = DataLoaderService()
        self.error_manager = ErrorManagerService()
        self.query_service = QueryService(self.error_manager)
        
        self.current_file_path = None
        self.is_marking_mode = False
        
        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        self.setWindowTitle("空间数据质量检查工具 v1.0")
        self.setGeometry(100, 100, 1200, 800)
        
        self._create_menu_bar()
        self._create_tool_bar()
        self._create_central_widget()
        self._create_status_bar()

    def _create_menu_bar(self):
        menu_bar = self.menuBar()
        
        file_menu = menu_bar.addMenu("文件(&F)")
        
        open_action = QAction("打开地图数据(&O)", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        open_error_action = QAction("打开错误记录(&E)", self)
        open_error_action.setShortcut("Ctrl+Shift+O")
        open_error_action.triggered.connect(self.open_error_file)
        file_menu.addAction(open_error_action)
        
        file_menu.addSeparator()
        
        save_action = QAction("保存错误记录(&S)", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.save_errors)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("另存为...", self)
        save_as_action.triggered.connect(self.save_errors_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("退出(&X)", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        edit_menu = menu_bar.addMenu("编辑(&E)")
        
        mark_error_action = QAction("标记错误(&M)", self)
        mark_error_action.setShortcut("M")
        mark_error_action.triggered.connect(self.toggle_marking_mode)
        edit_menu.addAction(mark_error_action)
        
        edit_menu.addSeparator()
        
        clear_errors_action = QAction("清除所有错误", self)
        clear_errors_action.triggered.connect(self.clear_all_errors)
        edit_menu.addAction(clear_errors_action)
        
        view_menu = menu_bar.addMenu("视图(&V)")
        
        zoom_in_action = QAction("放大(&I)", self)
        zoom_in_action.setShortcut(QKeySequence.ZoomIn)
        zoom_in_action.triggered.connect(self.zoom_in)
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction("缩小(&O)", self)
        zoom_out_action.setShortcut(QKeySequence.ZoomOut)
        zoom_out_action.triggered.connect(self.zoom_out)
        view_menu.addAction(zoom_out_action)
        
        fit_action = QAction("适应窗口(&F)", self)
        fit_action.setShortcut("F")
        fit_action.triggered.connect(self.fit_to_window)
        view_menu.addAction(fit_action)
        
        tool_menu = menu_bar.addMenu("工具(&T)")
        
        query_action = QAction("查询错误(&Q)", self)
        query_action.setShortcut("Ctrl+F")
        query_action.triggered.connect(self.show_query_dialog)
        tool_menu.addAction(query_action)
        
        stats_action = QAction("统计信息(&S)", self)
        stats_action.triggered.connect(self.show_statistics)
        tool_menu.addAction(stats_action)
        
        help_menu = menu_bar.addMenu("帮助(&H)")
        
        help_doc_action = QAction("帮助文档(&H)", self)
        help_doc_action.setShortcut("F1")
        help_doc_action.triggered.connect(self.show_help_document)
        help_menu.addAction(help_doc_action)
        
        help_menu.addSeparator()
        
        about_action = QAction("关于(&A)", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def _create_tool_bar(self):
        toolbar = QToolBar("主工具栏")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        open_btn = QAction("打开", self)
        open_btn.setToolTip("打开地图数据文件")
        open_btn.triggered.connect(self.open_file)
        toolbar.addAction(open_btn)
        
        save_btn = QAction("保存", self)
        save_btn.setToolTip("保存错误记录")
        save_btn.triggered.connect(self.save_errors)
        toolbar.addAction(save_btn)
        
        toolbar.addSeparator()
        
        self.mark_btn = QAction("标记错误", self)
        self.mark_btn.setToolTip("点击进入标记模式")
        self.mark_btn.setCheckable(True)
        self.mark_btn.triggered.connect(self.toggle_marking_mode)
        toolbar.addAction(self.mark_btn)
        
        query_btn = QAction("查询", self)
        query_btn.setToolTip("查询错误记录")
        query_btn.triggered.connect(self.show_query_dialog)
        toolbar.addAction(query_btn)
        
        toolbar.addSeparator()
        
        zoom_in_btn = QAction("放大", self)
        zoom_in_btn.triggered.connect(self.zoom_in)
        toolbar.addAction(zoom_in_btn)
        
        zoom_out_btn = QAction("缩小", self)
        zoom_out_btn.triggered.connect(self.zoom_out)
        toolbar.addAction(zoom_out_btn)
        
        fit_btn = QAction("适应", self)
        fit_btn.triggered.connect(self.fit_to_window)
        toolbar.addAction(fit_btn)

    def _create_central_widget(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        splitter = QSplitter(Qt.Horizontal)
        
        self.map_canvas = MapCanvas()
        self.text_viewer = TextViewer()
        self.text_viewer.hide()
        
        self.display_stack = QWidget()
        stack_layout = QVBoxLayout(self.display_stack)
        stack_layout.setContentsMargins(0, 0, 0, 0)
        stack_layout.addWidget(self.map_canvas)
        stack_layout.addWidget(self.text_viewer)
        
        splitter.addWidget(self.display_stack)
        
        self.error_panel = ErrorPanel()
        splitter.addWidget(self.error_panel)
        
        splitter.setSizes([800, 400])
        
        layout.addWidget(splitter)

    def _create_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.status_file = QLabel("未加载文件")
        self.status_bar.addWidget(self.status_file, 1)
        
        self.status_position = QLabel("坐标: -")
        self.status_bar.addPermanentWidget(self.status_position)
        
        self.status_errors = QLabel("错误: 0")
        self.status_bar.addPermanentWidget(self.status_errors)

    def _connect_signals(self):
        self.map_canvas.position_changed.connect(self.update_position_status)
        self.map_canvas.point_clicked.connect(self.on_map_clicked)
        self.map_canvas.error_marker_clicked.connect(self.on_error_marker_clicked)
        
        self.text_viewer.line_clicked.connect(self.on_text_line_clicked)
        
        self.error_panel.error_selected.connect(self.on_error_selected)
        self.error_panel.error_delete_requested.connect(self.delete_error)
        self.error_panel.error_edit_requested.connect(self.edit_error)

    def open_file(self):
        file_filter = (
            "支持的文件 (*.tif *.tiff *.bmp *.png *.jpg *.jpeg *.shp *.geojson *.txt *.csv);;"
            "栅格文件 (*.tif *.tiff *.bmp *.png *.jpg *.jpeg);;"
            "矢量文件 (*.shp *.geojson);;"
            "文本文件 (*.txt *.csv);;"
            "所有文件 (*.*)"
        )
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开地图数据文件", "", file_filter
        )
        
        if file_path:
            self.load_file(file_path)

    def load_file(self, file_path: str):
        try:
            map_data = self.data_loader.load_map_data(file_path)
            
            if map_data is None:
                QMessageBox.warning(self, "警告", "无法加载该文件类型")
                return
            
            self.current_file_path = file_path
            self.error_manager.set_current_map_file(file_path)
            
            from data import DataType
            if map_data.data_type == DataType.TEXT:
                self.map_canvas.hide()
                self.text_viewer.show()
                self.text_viewer.load_text(map_data)
            else:
                self.text_viewer.hide()
                self.map_canvas.show()
                self.map_canvas.load_data(map_data)
            
            self.status_file.setText(f"文件: {map_data.file_name}")
            self.data_loaded.emit(file_path)
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载文件失败:\n{str(e)}")

    def open_error_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开错误记录文件", "", "错误记录文件 (*.err.json);;JSON文件 (*.json);;所有文件 (*.*)"
        )
        
        if file_path:
            try:
                errors = self.error_manager.load_errors(file_path)
                self.error_panel.update_errors(errors)
                self.update_error_count()
                
                for error in errors:
                    self.map_canvas.add_error_marker(error)
                
                QMessageBox.information(
                    self, "成功", f"已加载 {len(errors)} 条错误记录"
                )
            except Exception as e:
                QMessageBox.critical(self, "错误", f"加载错误记录失败:\n{str(e)}")

    def save_errors(self):
        if self.error_manager.get_error_count() == 0:
            QMessageBox.information(self, "提示", "没有错误记录需要保存")
            return
        
        if self.error_manager.save_errors():
            QMessageBox.information(self, "成功", "错误记录已保存")
        else:
            QMessageBox.warning(self, "警告", "保存失败，请尝试另存为")

    def save_errors_as(self):
        if self.error_manager.get_error_count() == 0:
            QMessageBox.information(self, "提示", "没有错误记录需要保存")
            return
        
        default_name = "errors.err.json"
        if self.current_file_path:
            base_name = os.path.splitext(self.current_file_path)[0]
            default_name = f"{os.path.basename(base_name)}.err.json"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存错误记录", default_name, "错误记录文件 (*.err.json);;JSON文件 (*.json)"
        )
        
        if file_path:
            if self.error_manager.save_errors(file_path):
                QMessageBox.information(self, "成功", "错误记录已保存")

    def toggle_marking_mode(self):
        self.is_marking_mode = not self.is_marking_mode
        self.mark_btn.setChecked(self.is_marking_mode)
        
        if self.is_marking_mode:
            self.status_bar.showMessage("标记模式已开启 - 点击地图位置标记错误", 3000)
            self.map_canvas.set_marking_mode(True)
        else:
            self.status_bar.showMessage("标记模式已关闭", 3000)
            self.map_canvas.set_marking_mode(False)

    def on_map_clicked(self, x: float, y: float):
        if not self.is_marking_mode:
            return
        
        dialog = ErrorDialog(self)
        if dialog.exec_():
            error_type, description = dialog.get_error_info()
            
            error = self.error_manager.create_error(
                error_type=error_type,
                description=description,
                position=(x, y)
            )
            
            self.map_canvas.add_error_marker(error)
            self.error_panel.add_error(error)
            self.update_error_count()
            
            self.error_created.emit(error.error_id)

    def on_text_line_clicked(self, line_number: int):
        if not self.is_marking_mode:
            return
        
        dialog = ErrorDialog(self)
        if dialog.exec_():
            error_type, description = dialog.get_error_info()
            
            error = self.error_manager.create_error(
                error_type=error_type,
                description=description,
                position=(0, line_number),
                layer_name=f"第{line_number + 1}行"
            )
            
            self.error_panel.add_error(error)
            self.update_error_count()

    def on_error_selected(self, error_id: str):
        error = self.error_manager.get_error(error_id)
        if error:
            from data import DataType
            map_data = self.data_loader.get_current_data()
            
            if map_data and map_data.data_type == DataType.TEXT:
                line_num = int(error.position[1])
                self.text_viewer.highlight_line(line_num)
            else:
                self.map_canvas.highlight_error(error)

    def on_error_marker_clicked(self, error_id: str):
        self.error_panel.select_error(error_id)

    def delete_error(self, error_id: str):
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除错误记录 {error_id} 吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.error_manager.delete_error(error_id)
            self.map_canvas.remove_error_marker(error_id)
            self.error_panel.remove_error(error_id)
            self.update_error_count()

    def edit_error(self, error_id: str):
        error = self.error_manager.get_error(error_id)
        if not error:
            return
        
        dialog = ErrorDialog(self, error)
        if dialog.exec_():
            error_type, description = dialog.get_error_info()
            self.error_manager.update_error(
                error_id,
                error_type=error_type,
                description=description
            )
            self.error_panel.refresh_errors(self.error_manager.get_all_errors())

    def clear_all_errors(self):
        if self.error_manager.get_error_count() == 0:
            QMessageBox.information(self, "提示", "没有错误记录")
            return
        
        reply = QMessageBox.question(
            self, "确认清除",
            "确定要清除所有错误记录吗？此操作不可撤销。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.error_manager.clear_errors()
            self.map_canvas.clear_error_markers()
            self.error_panel.clear_errors()
            self.update_error_count()

    def show_query_dialog(self):
        dialog = QueryDialog(self, self.query_service)
        dialog.error_selected.connect(self.on_error_selected)
        dialog.exec_()

    def show_statistics(self):
        stats = self.error_manager.get_statistics()
        
        msg = f"错误统计信息\n\n"
        msg += f"总计: {stats['total']} 条错误\n\n"
        msg += "按类型统计:\n"
        for type_name, count in stats['by_type'].items():
            msg += f"  {type_name}: {count} 条\n"
        msg += "\n按状态统计:\n"
        for status_name, count in stats['by_status'].items():
            msg += f"  {status_name}: {count} 条\n"
        
        QMessageBox.information(self, "统计信息", msg)

    def zoom_in(self):
        self.map_canvas.zoom_in()

    def zoom_out(self):
        self.map_canvas.zoom_out()

    def fit_to_window(self):
        self.map_canvas.fit_to_window()

    def update_position_status(self, x: float, y: float):
        self.status_position.setText(f"坐标: ({x:.2f}, {y:.2f})")

    def update_error_count(self):
        count = self.error_manager.get_error_count()
        self.status_errors.setText(f"错误: {count}")

    def show_help_document(self):
        import os
        import subprocess
        import sys
        
        readme_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "README.md"
        )
        
        if not os.path.exists(readme_path):
            QMessageBox.warning(
                self, "提示",
                f"帮助文档不存在:\n{readme_path}"
            )
            return
        
        try:
            if sys.platform == 'win32':
                os.startfile(readme_path)
            elif sys.platform == 'darwin':
                subprocess.run(['open', readme_path])
            else:
                subprocess.run(['xdg-open', readme_path])
        except Exception as e:
            QMessageBox.warning(
                self, "错误",
                f"无法打开帮助文档:\n{str(e)}"
            )

    def show_about(self):
        QMessageBox.about(
            self,
            "关于",
            "空间数据质量检查工具 v1.0\n\n"
            "功能说明:\n"
            "- 支持栅格、矢量、文本数据加载\n"
            "- 可视化显示地图数据\n"
            "- 错误位置标记与记录\n"
            "- 错误信息查询与统计\n\n"
            "运行环境: 单机桌面应用"
        )

    def closeEvent(self, event):
        if self.error_manager.get_error_count() > 0:
            reply = QMessageBox.question(
                self, "确认退出",
                "存在未保存的错误记录，是否保存？",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save
            )
            
            if reply == QMessageBox.Save:
                self.save_errors()
                event.accept()
            elif reply == QMessageBox.Discard:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
