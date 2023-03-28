import pymongo
import datetime
from util import tmzone
import matplotlib.pyplot as plt
from utils import parseInt

client = pymongo.MongoClient("localhost", 27017)
email_db = client.emaildump
emails = email_db.emails
extracts = email_db.extracts

email_dict = {}
email_list = emails.find({})
for email in email_list:
    email_dict[email["_id"]] = email

extraction_dict = {}
extraction_list = list(extracts.find({}))
for extraction in extraction_list:
    extraction_dict[extraction["_id"]] = extraction

process = {}
for extraction in extraction_list:
    data = extraction["data"]
    company = data["company"]
    if company in process:
        process[company].append(extraction)
    else:
        process[company] = [ extraction ]



x_axis = []
y_axis = []
for company in process:
    if any([ extraction["type"] == "applied" for extraction in process[company] ]):
        pass

plt.figure(figsize=(18, 5))
plt.bar(x_axis, y_axis)
plt.suptitle('Apply -> View rate')
plt.show()