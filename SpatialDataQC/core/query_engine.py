from typing import List, Optional
from data import ErrorRecord, ErrorType, ErrorStatus


class QueryService:
    def __init__(self, error_manager):
        self._error_manager = error_manager

    def search_by_keyword(self, keyword: str) -> List[ErrorRecord]:
        if not keyword or not keyword.strip():
            return self._error_manager.get_all_errors()
        
        return self._error_manager.get_error_store().search_errors(keyword.strip())

    def search_by_id(self, error_id: str) -> Optional[ErrorRecord]:
        return self._error_manager.get_error(error_id)

    def filter_by_type(self, error_type: ErrorType) -> List[ErrorRecord]:
        return self._error_manager.get_errors_by_type(error_type)

    def filter_by_status(self, status: ErrorStatus) -> List[ErrorRecord]:
        return self._error_manager.get_errors_by_status(status)

    def filter_by_position_range(
        self,
        x_min: float,
        y_min: float,
        x_max: float,
        y_max: float
    ) -> List[ErrorRecord]:
        results = []
        for error in self._error_manager.get_all_errors():
            x, y = error.position
            if x_min <= x <= x_max and y_min <= y <= y_max:
                results.append(error)
        return results

    def advanced_search(
        self,
        keyword: Optional[str] = None,
        error_type: Optional[ErrorType] = None,
        status: Optional[ErrorStatus] = None
    ) -> List[ErrorRecord]:
        results = self._error_manager.get_all_errors()
        
        if keyword and keyword.strip():
            keyword_lower = keyword.strip().lower()
            results = [
                e for e in results
                if (keyword_lower in e.error_id.lower() or
                    keyword_lower in e.description.lower() or
                    keyword_lower in e.layer_name.lower())
            ]
        
        if error_type:
            results = [e for e in results if e.error_type == error_type]
        
        if status:
            results = [e for e in results if e.status == status]
        
        return results

    def get_sorted_errors(
        self,
        by_field: str = 'created_time',
        ascending: bool = True
    ) -> List[ErrorRecord]:
        errors = self._error_manager.get_all_errors()
        
        reverse = not ascending
        
        if by_field == 'created_time':
            return sorted(errors, key=lambda e: e.created_time, reverse=reverse)
        elif by_field == 'error_id':
            return sorted(errors, key=lambda e: e.error_id, reverse=reverse)
        elif by_field == 'error_type':
            return sorted(errors, key=lambda e: e.error_type.value, reverse=reverse)
        elif by_field == 'status':
            return sorted(errors, key=lambda e: e.status.value, reverse=reverse)
        
        return errors
