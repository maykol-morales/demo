import json
from typing import Any
from models.item import Item
from utils.item_repository import ItemRepository
from utils.s3_helper import S3Helper
from utils.response_helper import (
    success_response,
    created_response,
    bad_request_response,
    not_found_response,
    server_error_response
)

repository = ItemRepository()
s3_helper = S3Helper()


def create_item(event: dict, context: Any) -> dict:
    """Crear un nuevo item"""
    try:
        body = json.loads(event.get('body', '{}'))

        item = Item(
            board_id=body.get('board_id'),
            x=float(body.get('x', 0)),
            y=float(body.get('y', 0)),
            document=body.get('document')
        )

        is_valid, error_message = item.validate()
        if not is_valid:
            return bad_request_response(error_message)

        created_item = repository.create(item)

        return created_response(
            created_item.to_dict(),
            "Item created successfully"
        )

    except json.JSONDecodeError:
        return bad_request_response("Invalid JSON in request body")
    except ValueError as e:
        return bad_request_response(str(e))
    except Exception as e:
        print(f"Error creating item: {e}")
        return server_error_response(f"Error creating item: {str(e)}")


def get_item(event: dict, context: Any) -> dict:
    """Obtener un item por ID"""
    try:
        item_id = event['pathParameters']['id']

        item = repository.get_by_id(item_id)

        if not item:
            return not_found_response("Item not found")

        return success_response(item.to_dict())

    except KeyError:
        return bad_request_response("Item ID is required")
    except Exception as e:
        print(f"Error getting item: {e}")
        return server_error_response(f"Error getting item: {str(e)}")


def list_items(event: dict, context: Any) -> dict:
    """Listar todos los items"""
    try:
        query_params = event.get('queryStringParameters') or {}
        limit = int(query_params.get('limit', 50))

        items = repository.list_all(limit=limit)

        return success_response({
            'items': [item.to_dict() for item in items],
            'count': len(items)
        })

    except Exception as e:
        print(f"Error listing items: {e}")
        return server_error_response(f"Error listing items: {str(e)}")


def get_items_by_board(event: dict, context: Any) -> dict:
    """Obtener items por board"""
    try:
        board_id = event['pathParameters']['board_id']

        items = repository.get_by_board(board_id)

        return success_response({
            'items': [item.to_dict() for item in items],
            'count': len(items)
        })

    except KeyError:
        return bad_request_response("Board ID is required")
    except Exception as e:
        print(f"Error getting items by board: {e}")
        return server_error_response(f"Error getting items by board: {str(e)}")


def update_item(event: dict, context: Any) -> dict:
    """Actualizar un item"""
    try:
        item_id = event['pathParameters']['id']
        body = json.loads(event.get('body', '{}'))

        existing_item = repository.get_by_id(item_id)
        if not existing_item:
            return not_found_response("Item not found")

        updates = {}

        if 'board_id' in body:
            updates['board_id'] = body['board_id']

        if 'x' in body:
            updates['x'] = float(body['x'])

        if 'y' in body:
            updates['y'] = float(body['y'])

        if 'document' in body:
            updates['document'] = body['document']

        if not updates:
            return bad_request_response("No fields to update")

        updated_item = repository.update(item_id, updates)

        if not updated_item:
            return server_error_response("Failed to update item")

        return success_response(
            updated_item.to_dict(),
            "Item updated successfully"
        )

    except json.JSONDecodeError:
        return bad_request_response("Invalid JSON in request body")
    except KeyError:
        return bad_request_response("Item ID is required")
    except ValueError as e:
        return bad_request_response(str(e))
    except Exception as e:
        print(f"Error updating item: {e}")
        return server_error_response(f"Error updating item: {str(e)}")


def delete_item(event: dict, context: Any) -> dict:
    """Eliminar un item y su documento de S3"""
    try:
        item_id = event['pathParameters']['id']

        # Obtener el item para eliminar el documento de S3
        item = repository.get_by_id(item_id)
        if item:
            # Intentar eliminar el documento de S3
            key = s3_helper.get_object_key_from_url(item.document)
            if key:
                s3_helper.delete_object(key)

        success = repository.delete(item_id)

        if not success:
            return not_found_response("Item not found")

        return success_response(
            message="Item deleted successfully"
        )

    except KeyError:
        return bad_request_response("Item ID is required")
    except Exception as e:
        print(f"Error deleting item: {e}")
        return server_error_response(f"Error deleting item: {str(e)}")


def get_upload_url(event: dict, context: Any) -> dict:
    """Obtener URL pre-firmada para subir un documento a S3"""
    try:
        body = json.loads(event.get('body', '{}'))

        file_name = body.get('file_name')
        content_type = body.get('content_type', 'application/octet-stream')

        if not file_name:
            return bad_request_response("file_name is required")

        result = s3_helper.generate_presigned_upload_url(
            file_name=file_name,
            content_type=content_type
        )

        if not result:
            return server_error_response("Failed to generate upload URL")

        return success_response({
            'upload_url': result['upload_url'],
            'document_url': result['document_url'],
            'key': result['key']
        }, "Upload URL generated successfully")

    except json.JSONDecodeError:
        return bad_request_response("Invalid JSON in request body")
    except Exception as e:
        print(f"Error generating upload URL: {e}")
        return server_error_response(f"Error generating upload URL: {str(e)}")
