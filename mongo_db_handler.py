import json

import pymongo

file_name = "auto_record/want_2024_06_02.json"

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["mydatabase"]
mycol = mydb["pokemon"]

mydict = { "name": "John", "address": "Highway 37" }

with open(file_name, 'r') as json_file:
    json_file_data = json.loads(json_file.read())

result = mycol.bulk_write(json_file_data)
print(result.inserted_count)
print(result.bulk_api_result)

myclient.close()
