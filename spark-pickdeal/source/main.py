import findspark
findspark.init()
import numpy as np
import pyspark
from pyspark.sql import SparkSession
from pyspark.sql.types import *
from datetime import datetime
from pyspark.sql.functions import *
from urllib.request import urlopen
import json
import random
import requests
import base64
import os

HDFS_ITEMS = "hdfs://172.16.1.198:8020/user/fujinet/items/"
HDFS_IMAGE = "hdfs://172.16.1.198:8020/user/fujinet/images/"
HDFS_ARCHIVE = "hdfs://172.16.1.198:8020/user/fujinet/archive/device_data/"
CHECK_POINT = "hdfs://172.16.1.198:8020/user/fujinet/checkpoint"
SEAWEEDFS_IMAGE = 'http://172.16.1.198:9888/images/'
# SEAWEEDFS_IMAGE = 'http://192.168.137.57:9888/images/'
JAR_WORKING = "jars/*"
MONGODB_URI = "mongodb://pickdeal:Abc12345@172.16.1.198:27117"# ?authSource=admin&retryWrites=true&w=majority
DBNAME = "pickdeal"
# CHECK_POINT = "/home/fujinet/Desktop/huy-ndh/PickDeal/checkpoint"
KAFKA_SERVER = "172.16.1.198:9092"
KAFKA_TOPIC = "items"
SPARK_LOGS = "/home/fujinet/Documents/huy-ndh/PickDeal/spark.log"
AI_ENPOINTS = "http://172.16.1.198:6006/api/v1/pickdeal"
LOGO_CLASSIFICATION = f"{AI_ENPOINTS }/logo-classification"
INFO_NER = f"{AI_ENPOINTS }/ner-extraction"
SERVER_ENPOINTS = "http://172.16.1.198:4001/brands"

spark = SparkSession \
    .builder \
    .appName("Streaming Process Files") \
    .master("local[*]") \
    .config("spark.sql.adaptive.enabled", True)\
    .config("spark.streaming.stopGracefullyOnShutdown", True) \
    .config("spark.sql.streaming.schemaInference", True) \
    .config('spark.driver.extraClassPath', JAR_WORKING) \
    .getOrCreate()

print('hello')
spark.stop()
