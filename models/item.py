from typing import Optional
from datetime import datetime
import uuid


class Item:
    def __init__(
            self,
            board_id: str,
            x: float,
            y: float,
            document: str,
            id: Optional[str] = None,
            created_at: Optional[str] = None,
            updated_at: Optional[str] = None
    ):
        self.id = id or str(uuid.uuid4())
        self.board_id = board_id
        self.x = x
        self.y = y
        self.document = document  # URL de S3
        self.created_at = created_at or datetime.utcnow().isoformat()
        self.updated_at = updated_at or datetime.utcnow().isoformat()

    def to_dict(self) -> dict:
        """Convertir el item a diccionario"""
        return {
            'id': self.id,
            'board_id': self.board_id,
            'x': self.x,
            'y': self.y,
            'document': self.document,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @staticmethod
    def from_dict(data: dict) -> 'Item':
        """Crear un objeto Item desde un diccionario"""
        return Item(
            id=data.get('id'),
            board_id=data.get('board_id'),
            x=float(data.get('x', 0)),
            y=float(data.get('y', 0)),
            document=data.get('document'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

    def validate(self) -> tuple[bool, Optional[str]]:
        """Validar los datos del item"""
        if not self.board_id or len(self.board_id.strip()) == 0:
            return False, "Board ID is required"

        if self.x is None:
            return False, "X coordinate is required"

        if self.y is None:
            return False, "Y coordinate is required"

        if not self.document or len(self.document.strip()) == 0:
            return False, "Document URL is required"

        return True, None
