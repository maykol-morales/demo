import os
import boto3
from botocore.exceptions import ClientError
from typing import Optional
import uuid


class S3Helper:
    def __init__(self):
        self.s3_client = boto3.client('s3')
        self.bucket_name = os.environ.get('DOCUMENTS_BUCKET')

    def generate_presigned_upload_url(
            self,
            file_name: str,
            content_type: str = 'application/octet-stream',
            expiration: int = 3600
    ) -> Optional[dict]:
        """
        Generar URL pre-firmada para subir archivos a S3

        Args:
            file_name: Nombre del archivo
            content_type: Tipo de contenido
            expiration: Tiempo de expiración en segundos (default: 1 hora)

        Returns:
            Dict con url y key, o None si hay error
        """
        try:
            # Generar nombre único para el archivo
            file_extension = file_name.split('.')[-1] if '.' in file_name else ''
            unique_key = f"documents/{uuid.uuid4()}.{file_extension}" if file_extension else f"documents/{uuid.uuid4()}"

            # Generar URL pre-firmada
            presigned_url = self.s3_client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': unique_key,
                    'ContentType': content_type
                },
                ExpiresIn=expiration
            )

            # URL pública del archivo (sin firma)
            public_url = f"https://{self.bucket_name}.s3.amazonaws.com/{unique_key}"

            return {
                'upload_url': presigned_url,
                'document_url': public_url,
                'key': unique_key
            }

        except ClientError as e:
            print(f"Error generating presigned URL: {e}")
            return None

    def delete_object(self, key: str) -> bool:
        """
        Eliminar un objeto de S3

        Args:
            key: Clave del objeto en S3

        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=key
            )
            return True
        except ClientError as e:
            print(f"Error deleting object from S3: {e}")
            return False

    def get_object_key_from_url(self, url: str) -> Optional[str]:
        """
        Extraer la key de S3 desde una URL

        Args:
            url: URL del objeto en S3

        Returns:
            Key del objeto o None
        """
        try:
            # Formato: https://bucket-name.s3.amazonaws.com/key
            if self.bucket_name in url:
                parts = url.split(f"{self.bucket_name}.s3.amazonaws.com/")
                if len(parts) > 1:
                    return parts[1].split('?')[0]  # Remover query params si existen
            return None
        except Exception as e:
            print(f"Error extracting key from URL: {e}")
            return None
        


