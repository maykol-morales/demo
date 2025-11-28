from typing import Optional
from datetime import datetime
import uuid


class Instructor:
    def __init__(
            self,
            name: str,
            email: str,
            password: str,
            active: bool = True,
            id: Optional[str] = None,
            created_at: Optional[str] = None,
            updated_at: Optional[str] = None
    ):
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.email = email
        self.password = password
        self.active = active
        self.created_at = created_at or datetime.utcnow().isoformat()
        self.updated_at = updated_at or datetime.utcnow().isoformat()

    def to_dict(self, include_password: bool = False) -> dict:
        """Convertir el instructor a diccionario"""
        data = {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'active': self.active,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        if include_password:
            data['password'] = self.password
        return data

    @staticmethod
    def from_dict(data: dict) -> 'Instructor':
        """Crear un objeto Instructor desde un diccionario"""
        return Instructor(
            id=data.get('id'),
            name=data.get('name'),
            email=data.get('email'),
            password=data.get('password'),
            active=data.get('active', True),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

    def validate(self) -> tuple[bool, Optional[str]]:
        """Validar los datos del instructor"""
        if not self.name or len(self.name.strip()) == 0:
            return False, "Name is required"

        if not self.email or len(self.email.strip()) == 0:
            return False, "Email is required"

        if '@' not in self.email:
            return False, "Invalid email format"

        if not self.password or len(self.password) < 6:
            return False, "Password must be at least 6 characters"

        return True, None
