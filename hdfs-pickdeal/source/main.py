from fastapi import FastAPI, UploadFile, File
from typing import List
from hdfs import InsecureClient
import datetime
import requests
import json
from kafka import KafkaProducer
import logging
import os
# from io import BytesIO
# import boto3
# import base64

app = FastAPI()

kafka_servers = os.environ.get('KAFKA_HOST', 'localhost')
kafka_port = os.environ.get('KAFKA_PORT', 9092)
bootstrap_servers= f'{kafka_servers}:{kafka_port}'

hdfs_host = os.environ.get('HDFS_HOST', 'namenode')
hdfs_port = os.environ.get('HDFS_PORT', 9870)
hdfs_user = os.environ.get('HDFS_USER', 'hadoop')
hdfs_client = InsecureClient(f'http://{hdfs_host}:{hdfs_port}', user=hdfs_user)

seaweedfs_host = os.environ.get('SEAWEEDFS_HOST', 'localhost')
seaweedfs_port = os.environ.get('SEAWEEDFS_PORT', 4001)
seaweedfs_bucket = os.environ.get('SEAWEEDFS_BUCKET', 'storages')
seaweedfs_url = f'http://{seaweedfs_host}:{seaweedfs_port}/{seaweedfs_bucket}'
seaweed_domain = 'https://pickdeal.fujinet.net/storages/pickdeal/'

aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID','Q3AM3UQ867SPQQA43P2F')
aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY','zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG')

server_logs = 'logs/hdfs-kafka.log'
logging.basicConfig(filename=server_logs,
                    filemode='a',
                    format='%(asctime)s %(message)s',
                    level=logging.INFO)
logging.info('Running server HDFS')
logger = logging.getLogger('urbanGUI')


# Messages will be serialized as JSON
def serializer(message):
    return json.dumps(message).encode('utf-8')

# Kafka Producer
# producer = KafkaProducer(
#     bootstrap_servers=[bootstrap_servers],
#     value_serializer=serializer
# )

@app.get('/')
async def root():
    return {'message': {bootstrap_servers,
                        hdfs_host,
                        hdfs_port,
                        seaweedfs_url,
                        aws_access_key_id,
                        aws_secret_access_key}}

@app.post('/upload')
async def upload_file(file: UploadFile=File(...), images: List[UploadFile]=File(...)):
    producer = KafkaProducer(
        bootstrap_servers=[bootstrap_servers],
        value_serializer=serializer
    )
    logging.info(f'Crawler calls API @app.post("/upload")')
    content = await file.read()
    time = str(int(round(datetime.datetime.now().timestamp())))
    lines = content.splitlines()
    logging.info(f'Sending {len(lines)} message(s) to spark')
    for line in lines:
        item = json.loads(line)
        item['img_seaweed'] = ''
        item['img_seaweed_path'] = ''

        if item['images'][0]:
            for img in images:
                if img.filename in item['images'][0]['path']:
                    data = {
                        'feature': 'promotion',
                    }
                    re_img = await img.read()
                    files = {
                        'file': (img.filename, re_img)
                    }
                    try:
                        res = requests.post(seaweedfs_url, data=data, files=files)
                        item['img_seaweed'] = seaweed_domain + json.loads(res.text)['filePath']
                        item['img_seaweed_path'] = json.loads(res.text)['filePath']
                    except:
                        pass
        producer.send('items', item)

    logging.info(f'Successfully sent {len(lines)} message(s) to spark')

    content = content.decode('utf-8')
    file = f'items/items_{time}.jsonl'

    file_exists = hdfs_client.status(file, strict=False) is not None
    logging.info(f'Saving 1 file and {len(images)} image(s) to HDFS')
    if file_exists:
        hdfs_client.write(file, data=content, append=True, encoding='utf-8')
    else:
        hdfs_client.write(file, data=content, encoding='utf-8')

    logging.info(f'Saved 1 file and {len(images)} image(s) to HDFS successfully')

    return {'message': 'Items and Images uploaded to HDFS successfully'}

@app.delete('/directory/{directory_path}')
def delete_directory(directory_path: str):
    hdfs_client.delete(directory_path, recursive=True)
    return {'message': f'Directory/File {directory_path} deleted successfully'}
