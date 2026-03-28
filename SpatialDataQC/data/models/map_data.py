from dataclasses import dataclass
from typing import Optional, List, Tuple, Any
from enum import Enum
import numpy as np


class DataType(Enum):
    RASTER = "栅格数据"
    VECTOR = "矢量数据"
    TEXT = "文本数据"
    UNKNOWN = "未知类型"


@dataclass
class MapData:
    file_path: str
    data_type: DataType
    file_name: str
    width: int = 0
    height: int = 0
    extent: Optional[Tuple[float, float, float, float]] = None
    crs: Optional[str] = None
    raster_data: Optional[np.ndarray] = None
    vector_features: Optional[List[dict]] = None
    text_content: Optional[str] = None
    text_lines: Optional[List[str]] = None

    @property
    def is_loaded(self) -> bool:
        if self.data_type == DataType.RASTER:
            return self.raster_data is not None
        elif self.data_type == DataType.VECTOR:
            return self.vector_features is not None and len(self.vector_features) > 0
        elif self.data_type == DataType.TEXT:
            return self.text_content is not None
        return False

    def get_pixel_at(self, x: int, y: int) -> Optional[Tuple]:
        if self.raster_data is not None and 0 <= x < self.width and 0 <= y < self.height:
            pixel = self.raster_data[y, x]
            if isinstance(pixel, np.ndarray):
                return tuple(pixel.tolist())
            return (pixel,)
        return None

    def get_line_at(self, line_number: int) -> Optional[str]:
        if self.text_lines and 0 <= line_number < len(self.text_lines):
            return self.text_lines[line_number]
        return None

    def to_display_info(self) -> dict:
        info = {
            '文件名': self.file_name,
            '数据类型': self.data_type.value,
            '文件路径': self.file_path
        }
        
        if self.data_type == DataType.RASTER:
            info['宽度'] = f"{self.width} 像素"
            info['高度'] = f"{self.height} 像素"
            if self.extent:
                info['范围'] = f"X: {self.extent[0]:.2f} - {self.extent[2]:.2f}"
                info[''] = f"Y: {self.extent[1]:.2f} - {self.extent[3]:.2f}"
        elif self.data_type == DataType.TEXT:
            info['行数'] = len(self.text_lines) if self.text_lines else 0
            
        return info
