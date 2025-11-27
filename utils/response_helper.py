import json
from typing import Any, Optional


def create_response(
    status_code: int,
    body: Any,
    message: Optional[str] = None
) -> dict:
    """Crear una respuesta HTTP estandarizada"""
    response_body = {}

    if message:
        response_body['message'] = message

    if body is not None:
        if isinstance(body, dict):
            response_body.update(body)
        else:
            response_body['data'] = body

    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
        'body': json.dumps(response_body)
    }


def success_response(data: Any = None, message: str = "Success") -> dict:
    """Respuesta de éxito (200)"""
    return create_response(200, data, message)


def created_response(data: Any = None, message: str = "Created successfully") -> dict:
    """Respuesta de creación exitosa (201)"""
    return create_response(201, data, message)


def bad_request_response(message: str = "Bad request") -> dict:
    """Respuesta de solicitud incorrecta (400)"""
    return create_response(400, None, message)


def not_found_response(message: str = "Resource not found") -> dict:
    """Respuesta de recurso no encontrado (404)"""
    return create_response(404, None, message)


def server_error_response(message: str = "Internal server error") -> dict:
    """Respuesta de error del servidor (500)"""
    return create_response(500, None, message)
