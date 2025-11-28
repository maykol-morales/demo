from typing import Optional
from datetime import datetime
import uuid


class Session:
    def __init__(
            self,
            course_id: str,
            board_id: str,
            name: str,
            active: bool = True,
            id: Optional[str] = None,
            created_at: Optional[str] = None,
            updated_at: Optional[str] = None
    ):
        self.id = id or str(uuid.uuid4())
        self.course_id = course_id
        self.board_id = board_id
        self.name = name
        self.active = active
        self.created_at = created_at or datetime.utcnow().isoformat()
        self.updated_at = updated_at or datetime.utcnow().isoformat()

    def to_dict(self) -> dict:
        """Convertir la sesión a diccionario"""
        return {
            'id': self.id,
            'course_id': self.course_id,
            'board_id': self.board_id,
            'name': self.name,
            'active': self.active,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @staticmethod
    def from_dict(data: dict) -> 'Session':
        """Crear un objeto Session desde un diccionario"""
        return Session(
            id=data.get('id'),
            course_id=data.get('course_id'),
            board_id=data.get('board_id'),
            name=data.get('name'),
            active=data.get('active', True),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

    def validate(self) -> tuple[bool, Optional[str]]:
        """Validar los datos de la sesión"""
        if not self.name or len(self.name.strip()) == 0:
            return False, "Name is required"

        if not self.course_id or len(self.course_id.strip()) == 0:
            return False, "Course ID is required"

        if not self.board_id or len(self.board_id.strip()) == 0:
            return False, "Board ID is required"

        return True, None
