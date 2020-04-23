from io import BytesIO
from minio import Minio
from minio.error import ResponseError
from mesh_union.definitions import (
    MINIO_HOST,
    MINIO_ACCESS_KEY,
    MINIO_SECRET_KEY,
    MINIO_CUSTOMIZER_BUCKET,
    MINIO_USE_SECURE_CONNECTION,
)



minioClient = Minio(MINIO_HOST,
                    access_key=MINIO_ACCESS_KEY,
                    secret_key=MINIO_SECRET_KEY,
                    secure=MINIO_USE_SECURE_CONNECTION)

def put_customizer_object(key: str, data: bytes):
    minioClient.put_object(MINIO_CUSTOMIZER_BUCKET, key, BytesIO(data), len(data))

def get_customizer_object(key: str):
    return minioClient.get_object(MINIO_CUSTOMIZER_BUCKET, key)