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

x_axis = [ "{:02d}:00".format(hour) for hour in range(0, 24) ]
companies = {}
for job in jobs:
    company = job["company"]
    if company in companies:
        companies[company] = companies[company] + 1
    else:
        companies[company] = 1


occurrence = []
for company in companies:
    occurrence.append({ "company": company, "count": companies[company] })
occurrence.sort(key=lambda a: a["count"], reverse=True)
offset = 0
display_count = 25
x_axis = [item["company"] for item in occurrence[offset:offset + display_count]]
y_axis = [item["count"] for item in occurrence[offset:offset + display_count]]

plt.figure(figsize=(18, 5))
plt.subplot(111)
plt.bar(x_axis, y_axis)
plt.suptitle('Top Job Posters')
plt.show()