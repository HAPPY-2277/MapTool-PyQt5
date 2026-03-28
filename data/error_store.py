import json
import os
from datetime import datetime
from typing import List, Optional, Dict, Any

from data.models import ErrorRecord, ErrorType, ErrorStatus


class ErrorStore:
    ERROR_FILE_EXTENSION = '.err.json'

    def __init__(self, storage_dir: Optional[str] = None):
        self.storage_dir = storage_dir or os.getcwd()
        self._errors: Dict[str, ErrorRecord] = {}
        self._current_file: Optional[str] = None

    def set_storage_dir(self, directory: str) -> None:
        self.storage_dir = directory
        if not os.path.exists(directory):
            os.makedirs(directory)

    def get_error_file_path(self, map_file_path: str) -> str:
        base_name = os.path.splitext(map_file_path)[0]
        return f"{base_name}{self.ERROR_FILE_EXTENSION}"

    def save_errors(self, file_path: Optional[str] = None) -> bool:
        try:
            save_path = file_path or self._current_file
            if not save_path:
                return False

            errors_data = {
                'version': '1.0',
                'saved_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'errors': [error.to_dict() for error in self._errors.values()]
            }

            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(errors_data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"保存错误信息失败: {e}")
            return False

    def load_errors(self, file_path: str) -> List[ErrorRecord]:
        try:
            if not os.path.exists(file_path):
                return []

            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self._errors.clear()
            errors = []
            
            for error_data in data.get('errors', []):
                error = ErrorRecord.from_dict(error_data)
                self._errors[error.error_id] = error
                errors.append(error)

            self._current_file = file_path
            return errors
        except Exception as e:
            print(f"加载错误信息失败: {e}")
            return []

    def add_error(self, error: ErrorRecord) -> None:
        self._errors[error.error_id] = error

    def update_error(self, error_id: str, **kwargs) -> bool:
        if error_id not in self._errors:
            return False
        
        error = self._errors[error_id]
        
        if 'error_type' in kwargs:
            error.error_type = kwargs['error_type']
        if 'description' in kwargs:
            error.description = kwargs['description']
        if 'status' in kwargs:
            error.status = kwargs['status']
        if 'remark' in kwargs:
            error.remark = kwargs['remark']
        
        error.modified_time = datetime.now()
        return True

    def delete_error(self, error_id: str) -> bool:
        if error_id in self._errors:
            del self._errors[error_id]
            return True
        return False

    def get_error(self, error_id: str) -> Optional[ErrorRecord]:
        return self._errors.get(error_id)

    def get_all_errors(self) -> List[ErrorRecord]:
        return list(self._errors.values())

    def get_errors_by_type(self, error_type: ErrorType) -> List[ErrorRecord]:
        return [e for e in self._errors.values() if e.error_type == error_type]

    def get_errors_by_status(self, status: ErrorStatus) -> List[ErrorRecord]:
        return [e for e in self._errors.values() if e.status == status]

    def search_errors(self, keyword: str) -> List[ErrorRecord]:
        keyword_lower = keyword.lower()
        results = []
        
        for error in self._errors.values():
            if (keyword_lower in error.error_id.lower() or
                keyword_lower in error.description.lower() or
                keyword_lower in error.error_type.value.lower() or
                keyword_lower in error.layer_name.lower()):
                results.append(error)
        
        return results

    def clear_errors(self) -> None:
        self._errors.clear()

    def get_error_count(self) -> int:
        return len(self._errors)

    def get_statistics(self) -> Dict[str, int]:
        stats = {
            'total': len(self._errors),
            'by_type': {},
            'by_status': {}
        }
        
        for error_type in ErrorType:
            stats['by_type'][error_type.value] = len(
                [e for e in self._errors.values() if e.error_type == error_type]
            )
        
        for status in ErrorStatus:
            stats['by_status'][status.value] = len(
                [e for e in self._errors.values() if e.status == status]
            )
        
        return stats
