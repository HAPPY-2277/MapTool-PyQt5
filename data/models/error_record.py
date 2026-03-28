from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, Tuple, Dict, Any
from enum import Enum
import json


class ErrorType(Enum):
    GEOMETRY = "几何错误"
    ATTRIBUTE = "属性错误"
    TOPOLOGY = "拓扑错误"
    COORDINATE = "坐标错误"
    OTHER = "其他"

    @classmethod
    def from_code(cls, code: str) -> 'ErrorType':
        code_map = {
            "GEOMETRY": cls.GEOMETRY,
            "ATTRIBUTE": cls.ATTRIBUTE,
            "TOPOLOGY": cls.TOPOLOGY,
            "COORDINATE": cls.COORDINATE,
            "OTHER": cls.OTHER
        }
        return code_map.get(code.upper(), cls.OTHER)


class ErrorStatus(Enum):
    PENDING = "未处理"
    PROCESSING = "处理中"
    RESOLVED = "已解决"
    IGNORED = "已忽略"

    @classmethod
    def from_str(cls, status: str) -> 'ErrorStatus':
        status_map = {
            "未处理": cls.PENDING,
            "处理中": cls.PROCESSING,
            "已解决": cls.RESOLVED,
            "已忽略": cls.IGNORED
        }
        return status_map.get(status, cls.PENDING)


@dataclass
class ErrorRecord:
    error_id: str
    error_type: ErrorType
    description: str
    position: Tuple[float, float]
    layer_name: str
    created_time: datetime
    file_path: str
    status: ErrorStatus = ErrorStatus.PENDING
    remark: Optional[str] = None
    modified_time: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {
            'error_id': self.error_id,
            'error_type': self.error_type.name,
            'error_type_name': self.error_type.value,
            'description': self.description,
            'position': list(self.position),
            'layer_name': self.layer_name,
            'created_time': self.created_time.strftime('%Y-%m-%d %H:%M:%S'),
            'file_path': self.file_path,
            'status': self.status.value,
            'remark': self.remark
        }
        if self.modified_time:
            result['modified_time'] = self.modified_time.strftime('%Y-%m-%d %H:%M:%S')
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ErrorRecord':
        return cls(
            error_id=data['error_id'],
            error_type=ErrorType.from_code(data['error_type']),
            description=data['description'],
            position=tuple(data['position']),
            layer_name=data['layer_name'],
            created_time=datetime.strptime(data['created_time'], '%Y-%m-%d %H:%M:%S'),
            file_path=data['file_path'],
            status=ErrorStatus.from_str(data.get('status', '未处理')),
            remark=data.get('remark'),
            modified_time=datetime.strptime(data['modified_time'], '%Y-%m-%d %H:%M:%S') 
                         if data.get('modified_time') else None
        )

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
