from typing import Optional, List, Tuple
from datetime import datetime
import os

from data import ErrorRecord, ErrorType, ErrorStatus, ErrorStore


class ErrorManagerService:
    def __init__(self):
        self._error_store = ErrorStore()
        self._counter = 0
        self._current_map_file: Optional[str] = None

    def set_current_map_file(self, file_path: str) -> None:
        self._current_map_file = file_path

    def create_error(
        self,
        error_type: ErrorType,
        description: str,
        position: Tuple[float, float],
        layer_name: str = "默认图层"
    ) -> ErrorRecord:
        self._counter += 1
        date_str = datetime.now().strftime('%Y%m%d')
        error_id = f"ERR-{date_str}-{self._counter:04d}"
        
        error = ErrorRecord(
            error_id=error_id,
            error_type=error_type,
            description=description,
            position=position,
            layer_name=layer_name,
            created_time=datetime.now(),
            file_path=self._current_map_file or ""
        )
        
        self._error_store.add_error(error)
        return error

    def update_error(self, error_id: str, **kwargs) -> bool:
        return self._error_store.update_error(error_id, **kwargs)

    def delete_error(self, error_id: str) -> bool:
        return self._error_store.delete_error(error_id)

    def get_error(self, error_id: str) -> Optional[ErrorRecord]:
        return self._error_store.get_error(error_id)

    def get_all_errors(self) -> List[ErrorRecord]:
        return self._error_store.get_all_errors()

    def get_errors_by_type(self, error_type: ErrorType) -> List[ErrorRecord]:
        return self._error_store.get_errors_by_type(error_type)

    def get_errors_by_status(self, status: ErrorStatus) -> List[ErrorRecord]:
        return self._error_store.get_errors_by_status(status)

    def save_errors(self, file_path: Optional[str] = None) -> bool:
        if file_path is None and self._current_map_file:
            file_path = self._error_store.get_error_file_path(self._current_map_file)
        return self._error_store.save_errors(file_path)

    def load_errors(self, file_path: str) -> List[ErrorRecord]:
        errors = self._error_store.load_errors(file_path)
        if errors:
            max_num = 0
            for error in errors:
                parts = error.error_id.split('-')
                if len(parts) >= 3:
                    try:
                        num = int(parts[-1])
                        max_num = max(max_num, num)
                    except ValueError:
                        pass
            self._counter = max_num
        return errors

    def get_error_count(self) -> int:
        return self._error_store.get_error_count()

    def get_statistics(self) -> dict:
        return self._error_store.get_statistics()

    def clear_errors(self) -> None:
        self._error_store.clear_errors()
        self._counter = 0

    def get_error_store(self) -> ErrorStore:
        return self._error_store
