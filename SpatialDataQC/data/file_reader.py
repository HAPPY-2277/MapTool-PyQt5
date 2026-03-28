import os
from typing import Optional, List, Dict, Any
import numpy as np
from PIL import Image

from data.models import MapData, DataType


class FileReader:
    SUPPORTED_RASTER = {'.tif', '.tiff', '.bmp', '.png', '.jpg', '.jpeg'}
    SUPPORTED_VECTOR = {'.shp', '.geojson'}
    SUPPORTED_TEXT = {'.txt', '.csv'}

    @classmethod
    def get_data_type(cls, file_path: str) -> DataType:
        ext = os.path.splitext(file_path)[1].lower()
        if ext in cls.SUPPORTED_RASTER:
            return DataType.RASTER
        elif ext in cls.SUPPORTED_VECTOR:
            return DataType.VECTOR
        elif ext in cls.SUPPORTED_TEXT:
            return DataType.TEXT
        return DataType.UNKNOWN

    @classmethod
    def is_supported(cls, file_path: str) -> bool:
        return cls.get_data_type(file_path) != DataType.UNKNOWN

    @classmethod
    def load_file(cls, file_path: str) -> Optional[MapData]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        data_type = cls.get_data_type(file_path)
        file_name = os.path.basename(file_path)

        map_data = MapData(
            file_path=file_path,
            data_type=data_type,
            file_name=file_name
        )

        if data_type == DataType.RASTER:
            return cls._load_raster(map_data)
        elif data_type == DataType.VECTOR:
            return cls._load_vector(map_data)
        elif data_type == DataType.TEXT:
            return cls._load_text(map_data)
        
        return None

    @classmethod
    def _load_raster(cls, map_data: MapData) -> MapData:
        try:
            img = Image.open(map_data.file_path)
            raster_array = np.array(img)
            
            map_data.raster_data = raster_array
            map_data.width = img.width
            map_data.height = img.height
            map_data.extent = (0, 0, img.width, img.height)
            
            return map_data
        except Exception as e:
            raise RuntimeError(f"无法加载栅格文件: {e}")

    @classmethod
    def _load_vector(cls, map_data: MapData) -> MapData:
        try:
            features = []
            ext = os.path.splitext(map_data.file_path)[1].lower()
            
            if ext == '.geojson':
                import json
                with open(map_data.file_path, 'r', encoding='utf-8') as f:
                    geojson_data = json.load(f)
                    features = geojson_data.get('features', [])
                    
                    if features:
                        coords = []
                        for feature in features:
                            geom = feature.get('geometry', {})
                            if geom.get('type') == 'Point':
                                coords.append(geom.get('coordinates', []))
                            elif geom.get('type') in ['LineString', 'MultiPoint']:
                                coords.extend(geom.get('coordinates', []))
                            elif geom.get('type') in ['Polygon', 'MultiLineString']:
                                for ring in geom.get('coordinates', []):
                                    coords.extend(ring)
                        
                        if coords:
                            xs = [c[0] for c in coords if len(c) >= 2]
                            ys = [c[1] for c in coords if len(c) >= 2]
                            if xs and ys:
                                map_data.extent = (min(xs), min(ys), max(xs), max(ys))
            
            map_data.vector_features = features
            map_data.width = 800
            map_data.height = 600
            
            return map_data
        except Exception as e:
            raise RuntimeError(f"无法加载矢量文件: {e}")

    @classmethod
    def _load_text(cls, map_data: MapData) -> MapData:
        try:
            with open(map_data.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.splitlines()
            
            map_data.text_content = content
            map_data.text_lines = lines
            map_data.width = 80
            map_data.height = len(lines)
            
            return map_data
        except UnicodeDecodeError:
            try:
                with open(map_data.file_path, 'r', encoding='gbk') as f:
                    content = f.read()
                    lines = content.splitlines()
                
                map_data.text_content = content
                map_data.text_lines = lines
                map_data.width = 80
                map_data.height = len(lines)
                
                return map_data
            except Exception as e:
                raise RuntimeError(f"无法加载文本文件: {e}")
        except Exception as e:
            raise RuntimeError(f"无法加载文本文件: {e}")
