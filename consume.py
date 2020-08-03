import json
import os

import pika
import requests

import uuid
import sys
import pathlib
import shutil
import subprocess


from mesh_union.logger import logger
from mesh_union.tree import Node
from mesh_union.utils import union
from mesh_union.minio_client import put_customizer_object, get_customizer_object
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

    generated_successfully = False
    uploaded_successfully = False
    patched_successfully = False

    # save files locally before doing the union
    metadataFilePath = './tmp/metadata_%s.json' % uuid.uuid4()
    fileMappings = {}

    tmpFilesFolder = pathlib.Path('/tmp/customized-mesh').absolute()
    inputFilesFolderPath = tmpFilesFolder.joinpath('files')
    metadataFilePath = tmpFilesFolder.joinpath("metadata_%s.json" % uuid.uuid4())
    outputFilePath = tmpFilesFolder.joinpath('output_%s.stl' % uuid.uuid4())
    
    try:
        inputFilesFolderPath.mkdir(parents=True, exist_ok=True)
        
        for fileId, fileKey in metadata['file_mappings'].items():
            tmpFilePath = inputFilesFolderPath.joinpath(str(uuid.uuid4()))
            res = get_customizer_object(fileKey)
            with tmpFilePath.open('wb') as f:
                f.write(res.read())

            fileMappings[fileId] = str(tmpFilePath)
        
        metadataWithLocalFiles = {
            'tree': metadata['tree'],
            'file_mappings': fileMappings,
        }
        
        with metadataFilePath.open('w') as f:
            json.dump(metadataWithLocalFiles, f)

        p = subprocess.run(['python', 'unify.py', str(metadataFilePath), str(outputFilePath)])

        if p.returncode == 0:
            generated_successfully = True
            logger.info('Mesh generated successfully')
        else:
            logger.error('Mesh generation failed with status code %d' % p.returncode)
    except Exception as e:
        logger.error(e)

    if generated_successfully:
        try:
            with outputFilePath.open('rb') as f:
                put_customizer_object(output_object_key, f.read())
                logger.info('Mesh uploaded successfully. output path: %s' % output_object_key)
                uploaded_successfully = True
        except Exception as e:
            logger.error('There was a problem uploading the file')
            logger.error(e)

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

    try:
        shutil.rmtree(tmpFilesFolder)
    except Exception as e:
        logger.error('Failed to clean up')

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
