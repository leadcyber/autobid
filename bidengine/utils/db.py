import pymongo
from bson.objectid import ObjectId

client = pymongo.MongoClient("localhost", 27017)
db = client.linkedinbot
job_collection = db.jobs
bid_question_collection = db.bid_questions

def register_bid_qa(job_id: str, platform: str, question: str, answer: str):
    if job_id == "":
        return
    job = bid_question_collection.find_one({ "job_id": ObjectId(job_id) }, { "qa": 1 })
    if job is not None:
        job["qa"][question] = answer
        bid_question_collection.update_one({ "job_id": ObjectId(job_id) }, { "$set": { "qa": job["qa"] } })
    else:
        bid_question_collection.insert_one({
            "job_id": ObjectId(job_id),
            "platform": platform,
            "qa": { question: answer }
        })