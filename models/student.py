import uuid
from datetime import datetime
from typing import Optional


class Student:
    def __init__(
        self,
        name: str,
        email: str,
        password: str,
        active: bool = True,
        score: int = 0,
        id: Optional[str] = None,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None
    ):
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.email = email
        self.password = password
        self.active = active
        self.score = score
        self.created_at = created_at or datetime.utcnow().isoformat()
        self.updated_at = updated_at or datetime.utcnow().isoformat()

    def to_dict(self, include_password: bool = False) -> dict:
        """Convertir el estudiante a diccionario"""
        data = {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'active': self.active,
            'score': self.score,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        if include_password:
            data['password'] = self.password
        return data

    @staticmethod
    def from_dict(data: dict) -> 'Student':
        """Crear un objeto Student desde un diccionario"""
        return Student(
            id=data.get('id'),
            name=data.get('name'),
            email=data.get('email'),
            password=data.get('password'),
            active=data.get('active', True),
            score=int(data.get('score', 0)),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

    def validate(self) -> tuple[bool, Optional[str]]:
        """Validar los datos del estudiante"""
        if not self.name or len(self.name.strip()) == 0:
            return False, "Name is required"

        if not self.email or len(self.email.strip()) == 0:
            return False, "Email is required"

        if '@' not in self.email:
            return False, "Invalid email format"

        if not self.password or len(self.password) < 6:
            return False, "Password must be at least 6 characters"

        if self.score < 0 or self.score > 100:
            return False, "Score must be between 0 and 100"

        return True, None
