import pymongo
from bson.objectid import ObjectId

client = pymongo.MongoClient("localhost", 27017)
db = client.linkedinbot
job_collection = db.jobs
bid_question_collection = db.bid_questions