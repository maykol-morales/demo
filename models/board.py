from typing import Optional
from datetime import datetime
import uuid


class Board:
    def __init__(
            self,
            title: str,
            active: bool = True,
            id: Optional[str] = None,
            created_at: Optional[str] = None,
            updated_at: Optional[str] = None
    ):
        self.id = id or str(uuid.uuid4())
        self.title = title
        self.active = active
        self.created_at = created_at or datetime.utcnow().isoformat()
        self.updated_at = updated_at or datetime.utcnow().isoformat()

    def to_dict(self) -> dict:
        """Convertir el board a diccionario"""
        return {
            'id': self.id,
            'title': self.title,
            'active': self.active,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @staticmethod
    def from_dict(data: dict) -> 'Board':
        """Crear un objeto Board desde un diccionario"""
        return Board(
            id=data.get('id'),
            title=data.get('title'),
            active=data.get('active', True),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

    def validate(self) -> tuple[bool, Optional[str]]:
        """Validar los datos del board"""
        if not self.title or len(self.title.strip()) == 0:
            return False, "Title is required"

        return True, None
