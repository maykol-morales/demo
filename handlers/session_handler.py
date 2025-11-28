import json
from typing import Any
from models.session import Session
from repositories.session_repository import SessionRepository
from utils.response_helper import (
    success_response,
    created_response,
    bad_request_response,
    not_found_response,
    server_error_response
)

repository = SessionRepository()


def create_session(event: dict, context: Any) -> dict:
    """Crear una nueva sesión"""
    try:
        body = json.loads(event.get('body', '{}'))

        session = Session(
            course_id=body.get('course_id'),
            board_id=body.get('board_id'),
            name=body.get('name'),
            active=body.get('active', True)
        )

        is_valid, error_message = session.validate()
        if not is_valid:
            return bad_request_response(error_message)

        created_session = repository.create(session)

        return created_response(
            created_session.to_dict(),
            "Session created successfully"
        )

    except json.JSONDecodeError:
        return bad_request_response("Invalid JSON in request body")
    except ValueError as e:
        return bad_request_response(str(e))
    except Exception as e:
        print(f"Error creating session: {e}")
        return server_error_response(f"Error creating session: {str(e)}")


def get_session(event: dict, context: Any) -> dict:
    """Obtener una sesión por ID"""
    try:
        session_id = event['pathParameters']['id']

        session = repository.get_by_id(session_id)

        if not session:
            return not_found_response("Session not found")

        return success_response(session.to_dict())

    except KeyError:
        return bad_request_response("Session ID is required")
    except Exception as e:
        print(f"Error getting session: {e}")
        return server_error_response(f"Error getting session: {str(e)}")


def list_sessions(event: dict, context: Any) -> dict:
    """Listar todas las sesiones"""
    try:
        query_params = event.get('queryStringParameters') or {}
        limit = int(query_params.get('limit', 50))

        sessions = repository.list_all(limit=limit)

        return success_response({
            'sessions': [session.to_dict() for session in sessions],
            'count': len(sessions)
        })

    except Exception as e:
        print(f"Error listing sessions: {e}")
        return server_error_response(f"Error listing sessions: {str(e)}")


def get_sessions_by_course(event: dict, context: Any) -> dict:
    """Obtener sesiones por curso"""
    try:
        course_id = event['pathParameters']['course_id']

        sessions = repository.get_by_course(course_id)

        return success_response({
            'sessions': [session.to_dict() for session in sessions],
            'count': len(sessions)
        })

    except KeyError:
        return bad_request_response("Course ID is required")
    except Exception as e:
        print(f"Error getting sessions by course: {e}")
        return server_error_response(f"Error getting sessions by course: {str(e)}")


def get_sessions_by_board(event: dict, context: Any) -> dict:
    """Obtener sesiones por board"""
    try:
        board_id = event['pathParameters']['board_id']

        sessions = repository.get_by_board(board_id)

        return success_response({
            'sessions': [session.to_dict() for session in sessions],
            'count': len(sessions)
        })

    except KeyError:
        return bad_request_response("Board ID is required")
    except Exception as e:
        print(f"Error getting sessions by board: {e}")
        return server_error_response(f"Error getting sessions by board: {str(e)}")


def update_session(event: dict, context: Any) -> dict:
    """Actualizar una sesión"""
    try:
        session_id = event['pathParameters']['id']
        body = json.loads(event.get('body', '{}'))

        existing_session = repository.get_by_id(session_id)
        if not existing_session:
            return not_found_response("Session not found")

        updates = {}

        if 'name' in body:
            updates['name'] = body['name']

        if 'course_id' in body:
            updates['course_id'] = body['course_id']

        if 'board_id' in body:
            updates['board_id'] = body['board_id']

        if 'active' in body:
            updates['active'] = body['active']

        if not updates:
            return bad_request_response("No fields to update")

        updated_session = repository.update(session_id, updates)

        if not updated_session:
            return server_error_response("Failed to update session")

        return success_response(
            updated_session.to_dict(),
            "Session updated successfully"
        )

    except json.JSONDecodeError:
        return bad_request_response("Invalid JSON in request body")
    except KeyError:
        return bad_request_response("Session ID is required")
    except ValueError as e:
        return bad_request_response(str(e))
    except Exception as e:
        print(f"Error updating session: {e}")
        return server_error_response(f"Error updating session: {str(e)}")


def delete_session(event: dict, context: Any) -> dict:
    """Eliminar una sesión"""
    try:
        session_id = event['pathParameters']['id']

        success = repository.delete(session_id)

        if not success:
            return not_found_response("Session not found")

        return success_response(
            message="Session deleted successfully"
        )

    except KeyError:
        return bad_request_response("Session ID is required")
    except Exception as e:
        print(f"Error deleting session: {e}")
        return server_error_response(f"Error deleting session: {str(e)}")
