import os
import boto3
from typing import Optional, List
from botocore.exceptions import ClientError
from models.instructor import Instructor


class InstructorRepository:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.table_name = os.environ.get('INSTRUCTORS_TABLE')
        self.table = self.dynamodb.Table(self.table_name)

    def create(self, instructor: Instructor) -> Instructor:
        """Crear un nuevo instructor"""
        try:
            self.table.put_item(
                Item=instructor.to_dict(include_password=True),
                ConditionExpression='attribute_not_exists(id)'
            )
            return instructor
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise ValueError("Instructor with this ID already exists")
            raise e

    def get_by_id(self, instructor_id: str) -> Optional[Instructor]:
        """Obtener instructor por ID"""
        try:
            response = self.table.get_item(Key={'id': instructor_id})
            if 'Item' in response:
                return Instructor.from_dict(response['Item'])
            return None
        except ClientError as e:
            print(f"Error getting instructor: {e}")
            return None

    def get_by_email(self, email: str) -> Optional[Instructor]:
        """Obtener instructor por email"""
        try:
            response = self.table.query(
                IndexName='EmailIndex',
                KeyConditionExpression='email = :email',
                ExpressionAttributeValues={':email': email}
            )
            if response['Items']:
                return Instructor.from_dict(response['Items'][0])
            return None
        except ClientError as e:
            print(f"Error getting instructor by email: {e}")
            return None

    def list_all(self, limit: int = 50) -> List[Instructor]:
        """Listar todos los instructores"""
        try:
            response = self.table.scan(Limit=limit)
            instructors = [Instructor.from_dict(item) for item in response.get('Items', [])]
            return instructors
        except ClientError as e:
            print(f"Error listing instructors: {e}")
            return []

    def update(self, instructor_id: str, updates: dict) -> Optional[Instructor]:
        """Actualizar un instructor"""
        try:
            # Construir la expresión de actualización
            update_expression = "SET "
            expression_attribute_values = {}
            expression_attribute_names = {}

            for key, value in updates.items():
                if key not in ['id', 'created_at']:  # No actualizar ID ni fecha de creación
                    update_expression += f"#{key} = :{key}, "
                    expression_attribute_values[f":{key}"] = value
                    expression_attribute_names[f"#{key}"] = key

            # Agregar updated_at
            from datetime import datetime
            update_expression += "#updated_at = :updated_at"
            expression_attribute_values[":updated_at"] = datetime.utcnow().isoformat()
            expression_attribute_names["#updated_at"] = "updated_at"

            response = self.table.update_item(
                Key={'id': instructor_id},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values,
                ExpressionAttributeNames=expression_attribute_names,
                ReturnValues='ALL_NEW'
            )

            return Instructor.from_dict(response['Attributes'])
        except ClientError as e:
            print(f"Error updating instructor: {e}")
            return None

    def delete(self, instructor_id: str) -> bool:
        """Eliminar un instructor"""
        try:
            self.table.delete_item(
                Key={'id': instructor_id},
                ConditionExpression='attribute_exists(id)'
            )
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                return False
            print(f"Error deleting instructor: {e}")
            return False
