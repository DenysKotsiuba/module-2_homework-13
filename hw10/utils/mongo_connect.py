from configparser import ConfigParser

from pymongo import MongoClient
from pymongo.server_api import ServerApi


config = ConfigParser()
config.read('hw10/utils/mongo_config.ini')

mongo_user = config.get('DB', 'user')
mongodb_pass = config.get('DB', 'pass')
domain = config.get('DB', 'domain')

uri = f"mongodb+srv://{mongo_user}:{mongodb_pass}@{domain}/?retryWrites=true&w=majority"

client = MongoClient(uri, server_api=ServerApi('1'))