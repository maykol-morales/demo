import os
from typing import List, Optional

import boto3
from botocore.exceptions import ClientError

from models.student import Student


class StudentRepository:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.table_name = os.environ.get('STUDENTS_TABLE')
        self.table = self.dynamodb.Table(self.table_name)

    def create(self, student: Student) -> Student:
        """Crear un nuevo estudiante"""
        try:
            self.table.put_item(
                Item=student.to_dict(include_password=True),
                ConditionExpression='attribute_not_exists(id)'
            )
            return student
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise ValueError("Student with this ID already exists")
            raise e

    def get_by_id(self, student_id: str) -> Optional[Student]:
        """Obtener estudiante por ID"""
        try:
            response = self.table.get_item(Key={'id': student_id})
            if 'Item' in response:
                return Student.from_dict(response['Item'])
            return None
        except ClientError as e:
            print(f"Error getting student: {e}")
            return None

    def get_by_email(self, email: str) -> Optional[Student]:
        """Obtener estudiante por email"""
        try:
            response = self.table.query(
                IndexName='EmailIndex',
                KeyConditionExpression='email = :email',
                ExpressionAttributeValues={':email': email}
            )
            if response['Items']:
                return Student.from_dict(response['Items'][0])
            return None
        except ClientError as e:
            print(f"Error getting student by email: {e}")
            return None

    def list_all(self, limit: int = 50) -> List[Student]:
        """Listar todos los estudiantes"""
        try:
            response = self.table.scan(Limit=limit)
            students = [Student.from_dict(item) for item in response.get('Items', [])]
            return students
        except ClientError as e:
            print(f"Error listing students: {e}")
            return []

    def update(self, student_id: str, updates: dict) -> Optional[Student]:
        """Actualizar un estudiante"""
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
                Key={'id': student_id},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values,
                ExpressionAttributeNames=expression_attribute_names,
                ReturnValues='ALL_NEW'
            )

            return Student.from_dict(response['Attributes'])
        except ClientError as e:
            print(f"Error updating student: {e}")
            return None

    def delete(self, student_id: str) -> bool:
        """Eliminar un estudiante"""
        try:
            self.table.delete_item(
                Key={'id': student_id},
                ConditionExpression='attribute_exists(id)'
            )
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                return False
            print(f"Error deleting student: {e}")
            return False
