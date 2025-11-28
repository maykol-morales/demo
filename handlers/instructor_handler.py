import json
import hashlib
from typing import Any
from models.instructor import Instructor
from repositories.instructor_repository import InstructorRepository
from utils.response_helper import (
    success_response,
    created_response,
    bad_request_response,
    not_found_response,
    server_error_response
)

repository = InstructorRepository()


def hash_password(password: str) -> str:
    """Hash de la contraseña usando SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


def create_instructor(event: dict, context: Any) -> dict:
    """Crear un nuevo instructor"""
    try:
        body = json.loads(event.get('body', '{}'))

        # Crear objeto Instructor
        instructor = Instructor(
            name=body.get('name'),
            email=body.get('email'),
            password=hash_password(body.get('password', '')),
            active=body.get('active', True)
        )

        # Validar datos
        is_valid, error_message = instructor.validate()
        if not is_valid:
            return bad_request_response(error_message)

        # Verificar si el email ya existe
        existing_instructor = repository.get_by_email(instructor.email)
        if existing_instructor:
            return bad_request_response("Email already registered")

        # Crear instructor
        created_instructor = repository.create(instructor)

        return created_response(
            created_instructor.to_dict(),
            "Instructor created successfully"
        )

    except json.JSONDecodeError:
        return bad_request_response("Invalid JSON in request body")
    except ValueError as e:
        return bad_request_response(str(e))
    except Exception as e:
        print(f"Error creating instructor: {e}")
        return server_error_response(f"Error creating instructor: {str(e)}")


def get_instructor(event: dict, context: Any) -> dict:
    """Obtener un instructor por ID"""
    try:
        instructor_id = event['pathParameters']['id']

        instructor = repository.get_by_id(instructor_id)

        if not instructor:
            return not_found_response("Instructor not found")

        return success_response(instructor.to_dict())

    except KeyError:
        return bad_request_response("Instructor ID is required")
    except Exception as e:
        print(f"Error getting instructor: {e}")
        return server_error_response(f"Error getting instructor: {str(e)}")


def list_instructors(event: dict, context: Any) -> dict:
    """Listar todos los instructores"""
    try:
        query_params = event.get('queryStringParameters') or {}
        limit = int(query_params.get('limit', 50))

        instructors = repository.list_all(limit=limit)

        return success_response({
            'instructors': [instructor.to_dict() for instructor in instructors],
            'count': len(instructors)
        })

    except Exception as e:
        print(f"Error listing instructors: {e}")
        return server_error_response(f"Error listing instructors: {str(e)}")


def update_instructor(event: dict, context: Any) -> dict:
    """Actualizar un instructor"""
    try:
        instructor_id = event['pathParameters']['id']
        body = json.loads(event.get('body', '{}'))

        # Verificar que el instructor existe
        existing_instructor = repository.get_by_id(instructor_id)
        if not existing_instructor:
            return not_found_response("Instructor not found")

        # Preparar actualizaciones
        updates = {}

        if 'name' in body:
            updates['name'] = body['name']

        if 'email' in body:
            # Verificar que el nuevo email no esté en uso
            email_instructor = repository.get_by_email(body['email'])
            if email_instructor and email_instructor.id != instructor_id:
                return bad_request_response("Email already in use")
            updates['email'] = body['email']

        if 'password' in body:
            updates['password'] = hash_password(body['password'])

        if 'active' in body:
            updates['active'] = body['active']

        if not updates:
            return bad_request_response("No fields to update")

        # Actualizar instructor
        updated_instructor = repository.update(instructor_id, updates)

        if not updated_instructor:
            return server_error_response("Failed to update instructor")

        return success_response(
            updated_instructor.to_dict(),
            "Instructor updated successfully"
        )

    except json.JSONDecodeError:
        return bad_request_response("Invalid JSON in request body")
    except KeyError:
        return bad_request_response("Instructor ID is required")
    except ValueError as e:
        return bad_request_response(str(e))
    except Exception as e:
        print(f"Error updating instructor: {e}")
        return server_error_response(f"Error updating instructor: {str(e)}")


def delete_instructor(event: dict, context: Any) -> dict:
    """Eliminar un instructor"""
    try:
        instructor_id = event['pathParameters']['id']

        success = repository.delete(instructor_id)

        if not success:
            return not_found_response("Instructor not found")

        return success_response(
            message="Instructor deleted successfully"
        )

    except KeyError:
        return bad_request_response("Instructor ID is required")
    except Exception as e:
        print(f"Error deleting instructor: {e}")
        return server_error_response(f"Error deleting instructor: {str(e)}")


def get_instructor_by_email(event: dict, context: Any) -> dict:
    """Obtener un instructor por email"""
    try:
        email = event['pathParameters']['email']

        instructor = repository.get_by_email(email)

        if not instructor:
            return not_found_response("Instructor not found")

        return success_response(instructor.to_dict())

    except KeyError:
        return bad_request_response("Email is required")
    except Exception as e:
        print(f"Error getting instructor by email: {e}")
        return server_error_response(f"Error getting instructor by email: {str(e)}")