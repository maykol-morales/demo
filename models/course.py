from typing import Optional
from datetime import datetime
import uuid


class Course:
    def __init__(
            self,
            name: str,
            instructor_id: str,
            active: bool = True,
            id: Optional[str] = None,
            created_at: Optional[str] = None,
            updated_at: Optional[str] = None
    ):
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.instructor_id = instructor_id
        self.active = active
        self.created_at = created_at or datetime.utcnow().isoformat()
        self.updated_at = updated_at or datetime.utcnow().isoformat()

    def to_dict(self) -> dict:
        """Convertir el curso a diccionario"""
        return {
            'id': self.id,
            'name': self.name,
            'instructor_id': self.instructor_id,
            'active': self.active,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @staticmethod
    def from_dict(data: dict) -> 'Course':
        """Crear un objeto Course desde un diccionario"""
        return Course(
            id=data.get('id'),
            name=data.get('name'),
            instructor_id=data.get('instructor_id'),
            active=data.get('active', True),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

    def validate(self) -> tuple[bool, Optional[str]]:
        """Validar los datos del curso"""
        if not self.name or len(self.name.strip()) == 0:
            return False, "Name is required"

        if not self.instructor_id or len(self.instructor_id.strip()) == 0:
            return False, "Instructor ID is required"

        return True, None
