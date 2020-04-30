import json
import os

import pika
import requests

import time
import gc
# gc.enable()
# gc.set_debug(gc.DEBUG_LEAK)


from mesh_union.logger import logger
from mesh_union.tree import Node
from mesh_union.utils import union
from mesh_union.minio_client import put_customizer_object
from mesh_union.mmf_api import patch_customized_mesh
from mesh_union.definitions import (
    RABBITMQ_HOST,
    RABBITMQ_PORT,
    RABBITMQ_USER,
    RABBITMQ_PASSWORD,
    RABBITMQ_CUSTOMIZER_QUEUE,
    RABBITMQ_CONNECTION_HEARBEAT,
    RABBITMQ_QUEUE_PREFETCH_COUNT,
    MMF_SECRET,
)


def dump_garbage():
    """
    show us what's the garbage about
    """
        
    # force collection
    print("\nGARBAGE:")
    gc.collect()

    print("\nGARBAGE OBJECTS:")
    for x in gc.garbage:
        s = str(x)
        if len(s) > 80: s = s[:80]
        print(type(x),"\n  ", s)


def callback(
    ch: pika.adapters.blocking_connection.BlockingChannel,
    method: pika.spec.Basic.Deliver,
    properties: pika.spec.BasicProperties,
    body: bytes
):
    customizer_name   = None
    metadata          = None
    output_object_key = None
    callback_url      = None

    try:    
        body_dict = json.loads(body)
        customizer_name   = body_dict['customizer_name']
        metadata          = body_dict['metadata']
        output_object_key = body_dict['output_object_key']
        callback_url      = body_dict['callback_url']
    except Exception as e:
        logger.error('Invalid message body; %s' % e)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        return

    logger.info(" [x] Received task for: %s" % customizer_name)
    
    final_mesh = None
    generated_successfully = False
    uploaded_successfully = False
    patched_successfully = False
    try:
        tree = Node.from_json(metadata)
        meshes = tree.flatten()
        final_mesh = union(meshes)
        generated_successfully = True
        logger.info('Mesh generated successfully')

        for m in meshes:
            m._cache.clear()

    except Exception as e:
        logger.error(e)

    if generated_successfully:
        try:
            output_bytes = final_mesh.export(file_type='stl')
            put_customizer_object(output_object_key, output_bytes)
            logger.info('Mesh uploaded successfully. output path: %s' % output_object_key)
            uploaded_successfully = True
        except:
            logger.error('There was a problem uploading the file')

    if uploaded_successfully:
        try:
            r = patch_customized_mesh(callback_url, success=generated_successfully)
            if r.status_code == 200:
                patched_successfully = True
                logger.info('Mesh patched successfully as %s' % 'successful' if generated_successfully else 'failed')
        except Exception as e:
            logger.error(e)

    if generated_successfully and uploaded_successfully and patched_successfully:
        ch.basic_ack(delivery_tag=method.delivery_tag)
    else:
        requeue = generated_successfully and (not uploaded_successfully or not patched_successfully)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=requeue)
    
    gc.collect()
    


# TODO run callback in another thread
# example: https://github.com/pika/pika/blob/1.0.1/examples/basic_consumer_threaded.py

connection = pika.BlockingConnection(pika.ConnectionParameters(
    host=RABBITMQ_HOST,
    port=RABBITMQ_PORT,
    heartbeat=RABBITMQ_CONNECTION_HEARBEAT,
    credentials=pika.credentials.PlainCredentials(username=RABBITMQ_USER, password=RABBITMQ_PASSWORD)
))

channel = connection.channel()

channel.queue_declare(queue=RABBITMQ_CUSTOMIZER_QUEUE, durable=True)
channel.basic_qos(prefetch_count=RABBITMQ_QUEUE_PREFETCH_COUNT)
channel.basic_consume(
    queue=RABBITMQ_CUSTOMIZER_QUEUE,
    on_message_callback=callback
)

try:
    logger.info(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()
except KeyboardInterrupt:
    channel.stop_consuming()
except Exception as e:
    logger.error(e)

if connection.is_open:
    connection.close()
