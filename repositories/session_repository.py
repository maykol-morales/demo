import os
import boto3
from typing import Optional, List
from botocore.exceptions import ClientError
from models.session import Session


class SessionRepository:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.table_name = os.environ.get('SESSIONS_TABLE')
        self.table = self.dynamodb.Table(self.table_name)

    def create(self, session: Session) -> Session:
        """Crear una nueva sesión"""
        try:
            self.table.put_item(
                Item=session.to_dict(),
                ConditionExpression='attribute_not_exists(id)'
            )
            return session
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise ValueError("Session with this ID already exists")
            raise e

    def get_by_id(self, session_id: str) -> Optional[Session]:
        """Obtener sesión por ID"""
        try:
            response = self.table.get_item(Key={'id': session_id})
            if 'Item' in response:
                return Session.from_dict(response['Item'])
            return None
        except ClientError as e:
            print(f"Error getting session: {e}")
            return None

    def get_by_course(self, course_id: str) -> List[Session]:
        """Obtener sesiones por curso"""
        try:
            response = self.table.query(
                IndexName='CourseIndex',
                KeyConditionExpression='course_id = :course_id',
                ExpressionAttributeValues={':course_id': course_id}
            )
            return [Session.from_dict(item) for item in response.get('Items', [])]
        except ClientError as e:
            print(f"Error getting sessions by course: {e}")
            return []

    def get_by_board(self, board_id: str) -> List[Session]:
        """Obtener sesiones por board"""
        try:
            response = self.table.query(
                IndexName='BoardIndex',
                KeyConditionExpression='board_id = :board_id',
                ExpressionAttributeValues={':board_id': board_id}
            )
            return [Session.from_dict(item) for item in response.get('Items', [])]
        except ClientError as e:
            print(f"Error getting sessions by board: {e}")
            return []

    def list_all(self, limit: int = 50) -> List[Session]:
        """Listar todas las sesiones"""
        try:
            response = self.table.scan(Limit=limit)
            sessions = [Session.from_dict(item) for item in response.get('Items', [])]
            return sessions
        except ClientError as e:
            print(f"Error listing sessions: {e}")
            return []

    def update(self, session_id: str, updates: dict) -> Optional[Session]:
        """Actualizar una sesión"""
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
                Key={'id': session_id},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values,
                ExpressionAttributeNames=expression_attribute_names,
                ReturnValues='ALL_NEW'
            )

            return Session.from_dict(response['Attributes'])
        except ClientError as e:
            print(f"Error updating session: {e}")
            return None

    def delete(self, session_id: str) -> bool:
        """Eliminar una sesión"""
        try:
            self.table.delete_item(
                Key={'id': session_id},
                ConditionExpression='attribute_exists(id)'
            )
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                return False
            print(f"Error deleting session: {e}")
            return False
