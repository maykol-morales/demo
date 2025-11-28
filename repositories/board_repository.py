import os
import boto3
from typing import Optional, List
from botocore.exceptions import ClientError
from models.board import Board


class BoardRepository:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.table_name = os.environ.get('BOARDS_TABLE')
        self.table = self.dynamodb.Table(self.table_name)

    def create(self, board: Board) -> Board:
        """Crear un nuevo board"""
        try:
            self.table.put_item(
                Item=board.to_dict(),
                ConditionExpression='attribute_not_exists(id)'
            )
            return board
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise ValueError("Board with this ID already exists")
            raise e

    def get_by_id(self, board_id: str) -> Optional[Board]:
        """Obtener board por ID"""
        try:
            response = self.table.get_item(Key={'id': board_id})
            if 'Item' in response:
                return Board.from_dict(response['Item'])
            return None
        except ClientError as e:
            print(f"Error getting board: {e}")
            return None

    def list_all(self, limit: int = 50) -> List[Board]:
        """Listar todos los boards"""
        try:
            response = self.table.scan(Limit=limit)
            boards = [Board.from_dict(item) for item in response.get('Items', [])]
            return boards
        except ClientError as e:
            print(f"Error listing boards: {e}")
            return []

    def update(self, board_id: str, updates: dict) -> Optional[Board]:
        """Actualizar un board"""
        try:
            update_expression = "SET "
            expression_attribute_values = {}
            expression_attribute_names = {}

            for key, value in updates.items():
                if key not in ['id', 'created_at']:
                    update_expression += f"#{key} = :{key}, "
                    expression_attribute_values[f":{key}"] = value
                    expression_attribute_names[f"#{key}"] = key

            from datetime import datetime
            update_expression += "#updated_at = :updated_at"
            expression_attribute_values[":updated_at"] = datetime.utcnow().isoformat()
            expression_attribute_names["#updated_at"] = "updated_at"

            response = self.table.update_item(
                Key={'id': board_id},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values,
                ExpressionAttributeNames=expression_attribute_names,
                ReturnValues='ALL_NEW'
            )

            return Board.from_dict(response['Attributes'])
        except ClientError as e:
            print(f"Error updating board: {e}")
            return None

    def delete(self, board_id: str) -> bool:
        """Eliminar un board"""
        try:
            self.table.delete_item(
                Key={'id': board_id},
                ConditionExpression='attribute_exists(id)'
            )
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                return False
            print(f"Error deleting board: {e}")
            return False
