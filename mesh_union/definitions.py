import os

def __get_int_env_var(var_name, default_value = None):
    var = os.getenv(var_name)
    if var != None and len(var) > 0:
        return int(var)
    return default_value


RABBITMQ_HOST                   = os.getenv('RABBITMQ_HOST')
RABBITMQ_PORT                   = os.getenv('RABBITMQ_PORT')
RABBITMQ_USER                   = os.getenv('RABBITMQ_USER')
RABBITMQ_PASSWORD               = os.getenv('RABBITMQ_PASSWORD')
RABBITMQ_CONNECTION_HEARBEAT    = __get_int_env_var('RABBITMQ_CONNECTION_HEARBEAT', None)
RABBITMQ_QUEUE_PREFETCH_COUNT   = __get_int_env_var('RABBITMQ_QUEUE_PREFETCH_COUNT', 1)

RABBITMQ_CUSTOMIZER_QUEUE       = os.getenv('RABBITMQ_CUSTOMIZER_QUEUE')
RABBITMQ_CUSTOMIZER_ROUTING_KEY = os.getenv('RABBITMQ_CUSTOMIZER_ROUTING_KEY')
MINIO_HOST                      = os.getenv('MINIO_HOST')
MINIO_ACCESS_KEY                = os.getenv('MINIO_ACCESS_KEY')
MINIO_SECRET_KEY                = os.getenv('MINIO_SECRET_KEY')
MINIO_CUSTOMIZER_BUCKET         = os.getenv('MINIO_CUSTOMIZER_BUCKET')
MINIO_USE_SECURE_CONNECTION     = os.getenv('MINIO_USE_SECURE_CONNECTION') != 'false'
MMF_SECRET                      = os.getenv('MMF_SECRET')
