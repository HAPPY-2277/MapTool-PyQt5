from typing import Optional, List, Tuple
from datetime import datetime

from data import ErrorRecord, ErrorType, ErrorStatus, MapData, DataType
from data import FileReader, ErrorStore


class DataLoaderService:
    def __init__(self):
        self._current_data: Optional[MapData] = None
        self._file_reader = FileReader()

    def load_map_data(self, file_path: str) -> Optional[MapData]:
        try:
            self._current_data = self._file_reader.load_file(file_path)
            return self._current_data
        except Exception as e:
            raise RuntimeError(f"加载数据失败: {e}")

    def get_current_data(self) -> Optional[MapData]:
        return self._current_data

    def is_data_loaded(self) -> bool:
        return self._current_data is not None and self._current_data.is_loaded

    def get_data_info(self) -> Optional[dict]:
        if self._current_data:
            return self._current_data.to_display_info()
        return None

    def clear_current_data(self) -> None:
        self._current_data = None

    def get_supported_formats(self) -> dict:
        return {
            'raster': list(FileReader.SUPPORTED_RASTER),
            'vector': list(FileReader.SUPPORTED_VECTOR),
            'text': list(FileReader.SUPPORTED_TEXT)
        }
