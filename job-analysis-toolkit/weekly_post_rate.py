import pymongo
import datetime
import matplotlib.pyplot as plt
from utils import parseInt

client = pymongo.MongoClient("localhost", 27017)
db = client.linkedinbot
job_collection = db.jobs

end_date = datetime.datetime.now()
start_date = end_date - datetime.timedelta(days=7)
start_date_str = "{:04d}-{:02d}-{:02d}".format(start_date.year, start_date.month, start_date.day)
end_date_str = "{:04d}-{:02d}-{:02d}".format(end_date.year, end_date.month, end_date.day)

print(start_date_str, end_date_str)

jobs = list(job_collection.find({"postedDate": {"$gte": start_date_str, "$lte": end_date_str}}))

x_axis = [ "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun" ]
y_axis = [0] * 7

for job in jobs:
    posted_date = datetime.datetime.fromisoformat(job["postedDate"])
    weekday = posted_date.weekday()
    y_axis[weekday] = y_axis[weekday] + 1


print(y_axis)

plt.figure(figsize=(18, 5))
plt.subplot()
plt.bar(x_axis, y_axis)
plt.suptitle('Weekly Job Posting Rate')
plt.show()