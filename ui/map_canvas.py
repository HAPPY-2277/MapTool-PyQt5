from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, pyqtSignal, QPointF, QRectF
from PyQt5.QtGui import (
    QPainter, QPixmap, QImage, QPen, QColor, 
    QBrush, QFont, QWheelEvent, QMouseEvent
)
import numpy as np
from typing import Optional, Dict, List, Tuple

from data import MapData, DataType, ErrorRecord


class MapCanvas(QWidget):
    position_changed = pyqtSignal(float, float)
    point_clicked = pyqtSignal(float, float)
    error_marker_clicked = pyqtSignal(str)

    MARKER_SIZE = 12

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.map_data: Optional[MapData] = None
        self.pixmap: Optional[QPixmap] = None
        self.error_markers: Dict[str, ErrorRecord] = {}
        self.highlighted_error_id: Optional[str] = None
        
        self.zoom_factor = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 10.0
        
        self.offset_x = 0
        self.offset_y = 0
        self.is_panning = False
        self.last_mouse_pos = None
        
        self.is_marking_mode = False
        
        self.setMinimumSize(400, 300)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)

    def load_data(self, map_data: MapData):
        self.map_data = map_data
        
        if map_data.data_type == DataType.RASTER:
            self._load_raster_data(map_data)
        elif map_data.data_type == DataType.VECTOR:
            self._load_vector_data(map_data)
        
        self.zoom_factor = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.fit_to_window()
        self.update()

    def _load_raster_data(self, map_data: MapData):
        if map_data.raster_data is None:
            return
        
        data = map_data.raster_data
        
        if data.dtype != np.uint8:
            data = ((data - data.min()) / (data.max() - data.min()) * 255).astype(np.uint8)
        
        if len(data.shape) == 2:
            height, width = data.shape
            q_image = QImage(data.data, width, height, width, QImage.Format_Grayscale8)
        elif len(data.shape) == 3:
            height, width, channels = data.shape
            if channels == 3:
                bytes_per_line = 3 * width
                q_image = QImage(data.data, width, height, bytes_per_line, QImage.Format_RGB888)
            elif channels == 4:
                bytes_per_line = 4 * width
                q_image = QImage(data.data, width, height, bytes_per_line, QImage.Format_RGBA8888)
            else:
                q_image = QImage(data[:, :, 0].data, width, height, width, QImage.Format_Grayscale8)
        else:
            return
        
        self.pixmap = QPixmap.fromImage(q_image.copy())

    def _load_vector_data(self, map_data: MapData):
        if not map_data.vector_features:
            return
        
        from PyQt5.QtGui import QPainterPath
        
        width = 800
        height = 600
        self.pixmap = QPixmap(width, height)
        self.pixmap.fill(Qt.white)
        
        painter = QPainter(self.pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        extent = map_data.extent or (0, 0, width, height)
        x_min, y_min, x_max, y_max = extent
        x_range = x_max - x_min if x_max != x_min else 1
        y_range = y_max - y_min if y_max != y_min else 1
        
        scale_x = (width - 40) / x_range
        scale_y = (height - 40) / y_range
        scale = min(scale_x, scale_y)
        
        offset_x = 20 - x_min * scale
        offset_y = height - 20 + y_min * scale
        
        pen = QPen(QColor(0, 100, 200), 2)
        painter.setPen(pen)
        brush = QBrush(QColor(100, 150, 220, 100))
        painter.setBrush(brush)
        
        for feature in map_data.vector_features:
            geom = feature.get('geometry', {})
            geom_type = geom.get('type', '')
            coords = geom.get('coordinates', [])
            
            if geom_type == 'Point' and coords:
                x = coords[0] * scale + offset_x
                y = -coords[1] * scale + offset_y
                painter.drawEllipse(QPointF(x, y), 5, 5)
                
            elif geom_type == 'LineString' and coords:
                path = QPainterPath()
                for i, coord in enumerate(coords):
                    x = coord[0] * scale + offset_x
                    y = -coord[1] * scale + offset_y
                    if i == 0:
                        path.moveTo(x, y)
                    else:
                        path.lineTo(x, y)
                painter.drawPath(path)
                
            elif geom_type == 'Polygon' and coords:
                for ring in coords:
                    path = QPainterPath()
                    for i, coord in enumerate(ring):
                        x = coord[0] * scale + offset_x
                        y = -coord[1] * scale + offset_y
                        if i == 0:
                            path.moveTo(x, y)
                        else:
                            path.lineTo(x, y)
                    path.closeSubpath()
                    painter.drawPath(path)
        
        painter.end()

    def set_marking_mode(self, enabled: bool):
        self.is_marking_mode = enabled
        if enabled:
            self.setCursor(Qt.CrossCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

    def add_error_marker(self, error: ErrorRecord):
        self.error_markers[error.error_id] = error
        self.update()

    def remove_error_marker(self, error_id: str):
        if error_id in self.error_markers:
            del self.error_markers[error_id]
            self.update()

    def clear_error_markers(self):
        self.error_markers.clear()
        self.highlighted_error_id = None
        self.update()

    def highlight_error(self, error: ErrorRecord):
        self.highlighted_error_id = error.error_id
        self.update()

    def zoom_in(self):
        self._set_zoom(self.zoom_factor * 1.2)

    def zoom_out(self):
        self._set_zoom(self.zoom_factor / 1.2)

    def _set_zoom(self, factor: float):
        factor = max(self.min_zoom, min(self.max_zoom, factor))
        if self.pixmap:
            center_x = self.width() / 2
            center_y = self.height() / 2
            
            old_offset_x = (center_x - self.offset_x) / self.zoom_factor
            old_offset_y = (center_y - self.offset_y) / self.zoom_factor
            
            self.zoom_factor = factor
            
            self.offset_x = center_x - old_offset_x * self.zoom_factor
            self.offset_y = center_y - old_offset_y * self.zoom_factor
            
        self.update()

    def fit_to_window(self):
        if not self.pixmap:
            return
        
        widget_ratio = self.width() / self.height()
        pixmap_ratio = self.pixmap.width() / self.pixmap.height()
        
        if widget_ratio > pixmap_ratio:
            self.zoom_factor = self.height() / self.pixmap.height() * 0.9
        else:
            self.zoom_factor = self.width() / self.pixmap.width() * 0.9
        
        self.offset_x = (self.width() - self.pixmap.width() * self.zoom_factor) / 2
        self.offset_y = (self.height() - self.pixmap.height() * self.zoom_factor) / 2
        
        self.update()

    def screen_to_map(self, screen_x: int, screen_y: int) -> Tuple[float, float]:
        if not self.pixmap:
            return screen_x, screen_y
        
        map_x = (screen_x - self.offset_x) / self.zoom_factor
        map_y = (screen_y - self.offset_y) / self.zoom_factor
        
        return map_x, map_y

    def map_to_screen(self, map_x: float, map_y: float) -> Tuple[int, int]:
        screen_x = map_x * self.zoom_factor + self.offset_x
        screen_y = map_y * self.zoom_factor + self.offset_y
        return int(screen_x), int(screen_y)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        painter.fillRect(self.rect(), QColor(240, 240, 240))
        
        if self.pixmap:
            painter.save()
            painter.translate(self.offset_x, self.offset_y)
            painter.scale(self.zoom_factor, self.zoom_factor)
            painter.drawPixmap(0, 0, self.pixmap)
            painter.restore()
            
            self._draw_error_markers(painter)
        else:
            painter.setPen(QColor(150, 150, 150))
            painter.setFont(QFont("Arial", 14))
            painter.drawText(
                self.rect(), 
                Qt.AlignCenter, 
                "请打开地图数据文件\n\n支持的格式:\n栅格: TIF, BMP, PNG, JPG\n矢量: SHP, GeoJSON\n文本: TXT, CSV"
            )

    def _draw_error_markers(self, painter: QPainter):
        for error_id, error in self.error_markers.items():
            screen_x, screen_y = self.map_to_screen(error.position[0], error.position[1])
            
            screen_x = int(screen_x)
            screen_y = int(screen_y)
            
            is_highlighted = error_id == self.highlighted_error_id
            
            size = self.MARKER_SIZE
            if is_highlighted:
                size = int(self.MARKER_SIZE * 1.5)
            else:
                size = int(size)
            
            color = QColor(255, 0, 0)
            if error.error_type.name == "ATTRIBUTE":
                color = QColor(0, 200, 0)
            elif error.error_type.name == "TOPOLOGY":
                color = QColor(0, 0, 255)
            elif error.error_type.name == "COORDINATE":
                color = QColor(255, 200, 0)
            
            if is_highlighted:
                pen = QPen(QColor(255, 255, 0), 3)
            else:
                pen = QPen(Qt.black, 1)
            
            painter.setPen(pen)
            painter.setBrush(QBrush(color))
            
            painter.drawEllipse(
                screen_x - size // 2, 
                screen_y - size // 2, 
                size, 
                size
            )
            
            painter.setPen(QPen(Qt.white))
            painter.setFont(QFont("Arial", 8, QFont.Bold))
            painter.drawText(
                screen_x - 4, 
                screen_y + 4, 
                "!"
            )

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            if self.is_marking_mode and self.pixmap:
                map_x, map_y = self.screen_to_map(event.x(), event.y())
                self.point_clicked.emit(map_x, map_y)
            else:
                self.is_panning = True
                self.last_mouse_pos = event.pos()
                self.setCursor(Qt.ClosedHandCursor)
                
        elif event.button() == Qt.RightButton:
            screen_x, screen_y = event.x(), event.y()
            for error_id, error in self.error_markers.items():
                ex, ey = self.map_to_screen(error.position[0], error.position[1])
                if abs(screen_x - ex) < self.MARKER_SIZE and abs(screen_y - ey) < self.MARKER_SIZE:
                    self.error_marker_clicked.emit(error_id)
                    return

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.pixmap:
            map_x, map_y = self.screen_to_map(event.x(), event.y())
            self.position_changed.emit(map_x, map_y)
        
        if self.is_panning and self.last_mouse_pos:
            delta = event.pos() - self.last_mouse_pos
            self.offset_x += delta.x()
            self.offset_y += delta.y()
            self.last_mouse_pos = event.pos()
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.is_panning = False
            self.last_mouse_pos = None
            if self.is_marking_mode:
                self.setCursor(Qt.CrossCursor)
            else:
                self.setCursor(Qt.ArrowCursor)

    def wheelEvent(self, event: QWheelEvent):
        if not self.pixmap:
            return
        
        delta = event.angleDelta().y()
        
        mouse_x = event.x()
        mouse_y = event.y()
        
        map_x, map_y = self.screen_to_map(mouse_x, mouse_y)
        
        if delta > 0:
            self.zoom_factor *= 1.1
        else:
            self.zoom_factor /= 1.1
        
        self.zoom_factor = max(self.min_zoom, min(self.max_zoom, self.zoom_factor))
        
        self.offset_x = mouse_x - map_x * self.zoom_factor
        self.offset_y = mouse_y - map_y * self.zoom_factor
        
        self.update()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.pixmap and self.zoom_factor == 1.0:
            self.fit_to_window()
