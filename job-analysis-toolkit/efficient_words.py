import pymongo
import datetime
import matplotlib.pyplot as plt
from utils import parseInt
import re

client = pymongo.MongoClient("localhost", 27017)
db = client.linkedinbot
job_collection = db.jobs

end_date = datetime.datetime.now()
start_date = end_date - datetime.timedelta(days=7)
start_date_str = "{:04d}-{:02d}-{:02d}".format(start_date.year, start_date.month, start_date.day)
end_date_str = "{:04d}-{:02d}-{:02d}".format(end_date.year, end_date.month, end_date.day)

print(start_date_str, end_date_str)

jobs = list(job_collection.find({"postedDate": {"$gte": start_date_str, "$lte": end_date_str}}))

words = {}

for job in jobs:
    position = job["position"].lower().strip()
    copied_data = None
    if "copiedDate" in job:
        copied_data = job["copiedDate"]
    splits = re.split("[\s!?@#$%^&*()_+=,;:|\\/\[\]\-–]", position)
    flag = 1 if copied_data is not None else 0
    for word in splits:
        if len(word) == 0:
            continue
        if word in words:
            words[word] = words[word] + flag
        else:
            words[word] = flag
        print(words[word])
occurrence = []
for word in words:
    occurrence.append({ "word": word, "count": words[word] })
occurrence.sort(key=lambda a: a["count"], reverse=True)
display_count = 100
x_axis = [item["word"] for item in occurrence[0:display_count]]
y_axis = [item["count"] for item in occurrence[0:display_count]]
print(y_axis)

plt.figure(figsize=(18, 5))
plt.subplot()
plt.bar(x_axis, y_axis)
plt.suptitle('Weekly Job Posting Rate')
plt.show()