import os
import boto3
from typing import Optional, List
from botocore.exceptions import ClientError
from models.item import Item


class ItemRepository:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.table_name = os.environ.get('ITEMS_TABLE')
        self.table = self.dynamodb.Table(self.table_name)

    def create(self, item: Item) -> Item:
        """Crear un nuevo item"""
        try:
            self.table.put_item(
                Item=item.to_dict(),
                ConditionExpression='attribute_not_exists(id)'
            )
            return item
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise ValueError("Item with this ID already exists")
            raise e

    def get_by_id(self, item_id: str) -> Optional[Item]:
        """Obtener item por ID"""
        try:
            response = self.table.get_item(Key={'id': item_id})
            if 'Item' in response:
                return Item.from_dict(response['Item'])
            return None
        except ClientError as e:
            print(f"Error getting item: {e}")
            return None

    def get_by_board(self, board_id: str) -> List[Item]:
        """Obtener items por board"""
        try:
            response = self.table.query(
                IndexName='BoardIndex',
                KeyConditionExpression='board_id = :board_id',
                ExpressionAttributeValues={':board_id': board_id}
            )
            return [Item.from_dict(item) for item in response.get('Items', [])]
        except ClientError as e:
            print(f"Error getting items by board: {e}")
            return []

    def list_all(self, limit: int = 50) -> List[Item]:
        """Listar todos los items"""
        try:
            response = self.table.scan(Limit=limit)
            items = [Item.from_dict(item) for item in response.get('Items', [])]
            return items
        except ClientError as e:
            print(f"Error listing items: {e}")
            return []

    def update(self, item_id: str, updates: dict) -> Optional[Item]:
        """Actualizar un item"""
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
                Key={'id': item_id},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values,
                ExpressionAttributeNames=expression_attribute_names,
                ReturnValues='ALL_NEW'
            )

            return Item.from_dict(response['Attributes'])
        except ClientError as e:
            print(f"Error updating item: {e}")
            return None

    def delete(self, item_id: str) -> bool:
        """Eliminar un item"""
        try:
            self.table.delete_item(
                Key={'id': item_id},
                ConditionExpression='attribute_exists(id)'
            )
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                return False
            print(f"Error deleting item: {e}")
            return False
