import json
from typing import Any
from models.board import Board
from repositories.board_repository import BoardRepository
from utils.response_helper import (
    success_response,
    created_response,
    bad_request_response,
    not_found_response,
    server_error_response
)

repository = BoardRepository()


def create_board(event: dict, context: Any) -> dict:
    """Crear un nuevo board"""
    try:
        body = json.loads(event.get('body', '{}'))

        board = Board(
            title=body.get('title'),
            active=body.get('active', True)
        )

        is_valid, error_message = board.validate()
        if not is_valid:
            return bad_request_response(error_message)

        created_board = repository.create(board)

        return created_response(
            created_board.to_dict(),
            "Board created successfully"
        )

    except json.JSONDecodeError:
        return bad_request_response("Invalid JSON in request body")
    except ValueError as e:
        return bad_request_response(str(e))
    except Exception as e:
        print(f"Error creating board: {e}")
        return server_error_response(f"Error creating board: {str(e)}")


def get_board(event: dict, context: Any) -> dict:
    """Obtener un board por ID"""
    try:
        board_id = event['pathParameters']['id']

        board = repository.get_by_id(board_id)

        if not board:
            return not_found_response("Board not found")

        return success_response(board.to_dict())

    except KeyError:
        return bad_request_response("Board ID is required")
    except Exception as e:
        print(f"Error getting board: {e}")
        return server_error_response(f"Error getting board: {str(e)}")


def list_boards(event: dict, context: Any) -> dict:
    """Listar todos los boards"""
    try:
        query_params = event.get('queryStringParameters') or {}
        limit = int(query_params.get('limit', 50))

        boards = repository.list_all(limit=limit)

        return success_response({
            'boards': [board.to_dict() for board in boards],
            'count': len(boards)
        })

    except Exception as e:
        print(f"Error listing boards: {e}")
        return server_error_response(f"Error listing boards: {str(e)}")


def update_board(event: dict, context: Any) -> dict:
    """Actualizar un board"""
    try:
        board_id = event['pathParameters']['id']
        body = json.loads(event.get('body', '{}'))

        existing_board = repository.get_by_id(board_id)
        if not existing_board:
            return not_found_response("Board not found")

        updates = {}

        if 'title' in body:
            updates['title'] = body['title']

        if 'active' in body:
            updates['active'] = body['active']

        if not updates:
            return bad_request_response("No fields to update")

        updated_board = repository.update(board_id, updates)

        if not updated_board:
            return server_error_response("Failed to update board")

        return success_response(
            updated_board.to_dict(),
            "Board updated successfully"
        )

    except json.JSONDecodeError:
        return bad_request_response("Invalid JSON in request body")
    except KeyError:
        return bad_request_response("Board ID is required")
    except ValueError as e:
        return bad_request_response(str(e))
    except Exception as e:
        print(f"Error updating board: {e}")
        return server_error_response(f"Error updating board: {str(e)}")


def delete_board(event: dict, context: Any) -> dict:
    """Eliminar un board"""
    try:
        board_id = event['pathParameters']['id']

        success = repository.delete(board_id)

        if not success:
            return not_found_response("Board not found")

        return success_response(
            message="Board deleted successfully"
        )

    except KeyError:
        return bad_request_response("Board ID is required")
    except Exception as e:
        print(f"Error deleting board: {e}")
        return server_error_response(f"Error deleting board: {str(e)}")
