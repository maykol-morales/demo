import os
import boto3
from typing import Optional, List
from botocore.exceptions import ClientError
from models.course import Course


class CourseRepository:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.table_name = os.environ.get('COURSES_TABLE')
        self.table = self.dynamodb.Table(self.table_name)

    def create(self, course: Course) -> Course:
        """Crear un nuevo curso"""
        try:
            self.table.put_item(
                Item=course.to_dict(),
                ConditionExpression='attribute_not_exists(id)'
            )
            return course
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise ValueError("Course with this ID already exists")
            raise e

    def get_by_id(self, course_id: str) -> Optional[Course]:
        """Obtener curso por ID"""
        try:
            response = self.table.get_item(Key={'id': course_id})
            if 'Item' in response:
                return Course.from_dict(response['Item'])
            return None
        except ClientError as e:
            print(f"Error getting course: {e}")
            return None

    def get_by_instructor(self, instructor_id: str) -> List[Course]:
        """Obtener cursos por instructor"""
        try:
            response = self.table.query(
                IndexName='InstructorIndex',
                KeyConditionExpression='instructor_id = :instructor_id',
                ExpressionAttributeValues={':instructor_id': instructor_id}
            )
            return [Course.from_dict(item) for item in response.get('Items', [])]
        except ClientError as e:
            print(f"Error getting courses by instructor: {e}")
            return []

    def list_all(self, limit: int = 50) -> List[Course]:
        """Listar todos los cursos"""
        try:
            response = self.table.scan(Limit=limit)
            courses = [Course.from_dict(item) for item in response.get('Items', [])]
            return courses
        except ClientError as e:
            print(f"Error listing courses: {e}")
            return []

    def update(self, course_id: str, updates: dict) -> Optional[Course]:
        """Actualizar un curso"""
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
                Key={'id': course_id},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values,
                ExpressionAttributeNames=expression_attribute_names,
                ReturnValues='ALL_NEW'
            )

            return Course.from_dict(response['Attributes'])
        except ClientError as e:
            print(f"Error updating course: {e}")
            return None

    def delete(self, course_id: str) -> bool:
        """Eliminar un curso"""
        try:
            self.table.delete_item(
                Key={'id': course_id},
                ConditionExpression='attribute_exists(id)'
            )
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                return False
            print(f"Error deleting course: {e}")
            return False
