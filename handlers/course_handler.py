import json
from typing import Any
from models.course import Course
from repositories.course_repository import CourseRepository
from utils.response_helper import (
    success_response,
    created_response,
    bad_request_response,
    not_found_response,
    server_error_response
)

repository = CourseRepository()


def create_course(event: dict, context: Any) -> dict:
    """Crear un nuevo curso"""
    try:
        body = json.loads(event.get('body', '{}'))

        course = Course(
            name=body.get('name'),
            instructor_id=body.get('instructor_id'),
            active=body.get('active', True)
        )

        is_valid, error_message = course.validate()
        if not is_valid:
            return bad_request_response(error_message)

        created_course = repository.create(course)

        return created_response(
            created_course.to_dict(),
            "Course created successfully"
        )

    except json.JSONDecodeError:
        return bad_request_response("Invalid JSON in request body")
    except ValueError as e:
        return bad_request_response(str(e))
    except Exception as e:
        print(f"Error creating course: {e}")
        return server_error_response(f"Error creating course: {str(e)}")


def get_course(event: dict, context: Any) -> dict:
    """Obtener un curso por ID"""
    try:
        course_id = event['pathParameters']['id']

        course = repository.get_by_id(course_id)

        if not course:
            return not_found_response("Course not found")

        return success_response(course.to_dict())

    except KeyError:
        return bad_request_response("Course ID is required")
    except Exception as e:
        print(f"Error getting course: {e}")
        return server_error_response(f"Error getting course: {str(e)}")


def list_courses(event: dict, context: Any) -> dict:
    """Listar todos los cursos"""
    try:
        query_params = event.get('queryStringParameters') or {}
        limit = int(query_params.get('limit', 50))

        courses = repository.list_all(limit=limit)

        return success_response({
            'courses': [course.to_dict() for course in courses],
            'count': len(courses)
        })

    except Exception as e:
        print(f"Error listing courses: {e}")
        return server_error_response(f"Error listing courses: {str(e)}")


def get_courses_by_instructor(event: dict, context: Any) -> dict:
    """Obtener cursos por instructor"""
    try:
        instructor_id = event['pathParameters']['instructor_id']

        courses = repository.get_by_instructor(instructor_id)

        return success_response({
            'courses': [course.to_dict() for course in courses],
            'count': len(courses)
        })

    except KeyError:
        return bad_request_response("Instructor ID is required")
    except Exception as e:
        print(f"Error getting courses by instructor: {e}")
        return server_error_response(f"Error getting courses by instructor: {str(e)}")


def update_course(event: dict, context: Any) -> dict:
    """Actualizar un curso"""
    try:
        course_id = event['pathParameters']['id']
        body = json.loads(event.get('body', '{}'))

        existing_course = repository.get_by_id(course_id)
        if not existing_course:
            return not_found_response("Course not found")

        updates = {}

        if 'name' in body:
            updates['name'] = body['name']

        if 'instructor_id' in body:
            updates['instructor_id'] = body['instructor_id']

        if 'active' in body:
            updates['active'] = body['active']

        if not updates:
            return bad_request_response("No fields to update")

        updated_course = repository.update(course_id, updates)

        if not updated_course:
            return server_error_response("Failed to update course")

        return success_response(
            updated_course.to_dict(),
            "Course updated successfully"
        )

    except json.JSONDecodeError:
        return bad_request_response("Invalid JSON in request body")
    except KeyError:
        return bad_request_response("Course ID is required")
    except ValueError as e:
        return bad_request_response(str(e))
    except Exception as e:
        print(f"Error updating course: {e}")
        return server_error_response(f"Error updating course: {str(e)}")


def delete_course(event: dict, context: Any) -> dict:
    """Eliminar un curso"""
    try:
        course_id = event['pathParameters']['id']

        success = repository.delete(course_id)

        if not success:
            return not_found_response("Course not found")

        return success_response(
            message="Course deleted successfully"
        )

    except KeyError:
        return bad_request_response("Course ID is required")
    except Exception as e:
        print(f"Error deleting course: {e}")
        return server_error_response(f"Error deleting course: {str(e)}")
