import hashlib
import json
from typing import Any

from models.student import Student
from utils.response_helper import (bad_request_response, created_response, not_found_response, server_error_response, success_response)
from utils.student_repository import StudentRepository

repository = StudentRepository()


def hash_password(password: str) -> str:
    """Hash de la contraseña usando SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


def create_student(event: dict, context: Any) -> dict:
    """Crear un nuevo estudiante"""
    try:
        body = json.loads(event.get('body', '{}'))

        # Crear objeto Student
        student = Student(
            name=body.get('name'),
            email=body.get('email'),
            password=hash_password(body.get('password', '')),
            active=body.get('active', True),
            score=int(body.get('score', 0))
        )

        # Validar datos
        is_valid, error_message = student.validate()
        if not is_valid:
            return bad_request_response(error_message)

        # Verificar si el email ya existe
        existing_student = repository.get_by_email(student.email)
        if existing_student:
            return bad_request_response("Email already registered")

        # Crear estudiante
        created_student = repository.create(student)

        return created_response(
            created_student.to_dict(),
            "Student created successfully"
        )

    except json.JSONDecodeError:
        return bad_request_response("Invalid JSON in request body")
    except ValueError as e:
        return bad_request_response(str(e))
    except Exception as e:
        print(f"Error creating student: {e}")
        return server_error_response(f"Error creating student: {str(e)}")


def get_student(event: dict, context: Any) -> dict:
    """Obtener un estudiante por ID"""
    try:
        student_id = event['pathParameters']['id']

        student = repository.get_by_id(student_id)

        if not student:
            return not_found_response("Student not found")

        return success_response(student.to_dict())

    except KeyError:
        return bad_request_response("Student ID is required")
    except Exception as e:
        print(f"Error getting student: {e}")
        return server_error_response(f"Error getting student: {str(e)}")


def list_students(event: dict, context: Any) -> dict:
    """Listar todos los estudiantes"""
    try:
        query_params = event.get('queryStringParameters') or {}
        limit = int(query_params.get('limit', 50))

        students = repository.list_all(limit=limit)

        return success_response({
            'students': [student.to_dict() for student in students],
            'count': len(students)
        })

    except Exception as e:
        print(f"Error listing students: {e}")
        return server_error_response(f"Error listing students: {str(e)}")


def update_student(event: dict, context: Any) -> dict:
    """Actualizar un estudiante"""
    try:
        student_id = event['pathParameters']['id']
        body = json.loads(event.get('body', '{}'))

        # Verificar que el estudiante existe
        existing_student = repository.get_by_id(student_id)
        if not existing_student:
            return not_found_response("Student not found")

        # Preparar actualizaciones
        updates = {}

        if 'name' in body:
            updates['name'] = body['name']

        if 'email' in body:
            # Verificar que el nuevo email no esté en uso
            email_student = repository.get_by_email(body['email'])
            if email_student and email_student.id != student_id:
                return bad_request_response("Email already in use")
            updates['email'] = body['email']

        if 'password' in body:
            updates['password'] = hash_password(body['password'])

        if 'active' in body:
            updates['active'] = body['active']

        if 'score' in body:
            score = int(body['score'])
            if score < 0 or score > 100:
                return bad_request_response("Score must be between 0 and 100")
            updates['score'] = score

        if not updates:
            return bad_request_response("No fields to update")

        # Actualizar estudiante
        updated_student = repository.update(student_id, updates)

        if not updated_student:
            return server_error_response("Failed to update student")

        return success_response(
            updated_student.to_dict(),
            "Student updated successfully"
        )

    except json.JSONDecodeError:
        return bad_request_response("Invalid JSON in request body")
    except KeyError:
        return bad_request_response("Student ID is required")
    except ValueError as e:
        return bad_request_response(str(e))
    except Exception as e:
        print(f"Error updating student: {e}")
        return server_error_response(f"Error updating student: {str(e)}")


def delete_student(event: dict, context: Any) -> dict:
    """Eliminar un estudiante"""
    try:
        student_id = event['pathParameters']['id']

        success = repository.delete(student_id)

        if not success:
            return not_found_response("Student not found")

        return success_response(
            message="Student deleted successfully"
        )

    except KeyError:
        return bad_request_response("Student ID is required")
    except Exception as e:
        print(f"Error deleting student: {e}")
        return server_error_response(f"Error deleting student: {str(e)}")


def get_student_by_email(event: dict, context: Any) -> dict:
    """Obtener un estudiante por email"""
    try:
        email = event['pathParameters']['email']

        student = repository.get_by_email(email)

        if not student:
            return not_found_response("Student not found")

        return success_response(student.to_dict())

    except KeyError:
        return bad_request_response("Email is required")
    except Exception as e:
        print(f"Error getting student by email: {e}")
        return server_error_response(f"Error getting student by email: {str(e)}")
