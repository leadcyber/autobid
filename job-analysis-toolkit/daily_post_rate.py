import pymongo
import datetime
from util import tmzone
import matplotlib.pyplot as plt
from utils import parseInt

client = pymongo.MongoClient("localhost", 27017)
db = client.linkedinbot
job_collection = db.jobs

day_count = 9
very_first_date = datetime.datetime.now() - datetime.timedelta(days=day_count - 1)
very_end_date = datetime.datetime.now() + datetime.timedelta(days=1)
interval = datetime.timedelta(days=1)
plt.figure(figsize=(18, 5))

plot_index = 1
for end_date_timestamp in range(int(very_first_date.timestamp()), int(very_end_date.timestamp()), int(interval.total_seconds())):
    end_date = datetime.datetime.fromtimestamp(end_date_timestamp)
    start_date = end_date - interval
    start_date_str = "{:04d}-{:02d}-{:02d}".format(start_date.year, start_date.month, start_date.day)
    end_date_str = "{:04d}-{:02d}-{:02d}".format(end_date.year, end_date.month, end_date.day)

    print(start_date_str, end_date_str)

    jobs = list(job_collection.find({"postedDate": {"$gte": start_date_str, "$lte": end_date_str}}))
    # jobs = list(job_collection.find({ "$and": [ {"postedDate": {"$gte": start_date_str, "$lte": end_date_str} }, { "available": True }] }))

    x_axis = [ "{:02d}:00".format(hour) for hour in range(0, 24) ]
    y_axis = [0] * 24
    y_axis2 = [0] * 24
    y_axis3 = [0] * 24
    bid_count = 0
    for job in jobs:
        # print(job["_id"])
        posted_date = tmzone.utc_to_est(job["scannedDate"])
        posted_ago = job["postedAgo"]
        available = job["available"]
        copied_date = job["copiedDate"]
        company = job["company"]
        position = job["position"]
        already_applied = job["alreadyApplied"]
        # print(posted_date)

        if posted_ago == "Just now": pass
        elif "hour" in posted_ago:
            posted_date -= datetime.timedelta(hours=parseInt(posted_ago))
        elif "min" in posted_ago:
            posted_date -= datetime.timedelta(minutes=parseInt(posted_ago))


        if already_applied:
            bid_count = bid_count + 1

        same = list(filter(lambda j: j["company"] == company, jobs))
        # same = [0]
        # if company != "Braintrust":
        #     continue
        # if company in ["Dice", "Mission Lane", "PwC", "Braintrust", "Actalent", "Autodesk", "Genesys", "Softrams", "Insight Global"]:
        #     continue
        # print(len(same))
        if len(same) > 10:
            continue
        y_axis[posted_date.hour] = y_axis[posted_date.hour] + 1.0 / len(same)
        if available:
            y_axis2[posted_date.hour] = y_axis2[posted_date.hour] + 1.0 / len(same)
        if already_applied:
            y_axis3[posted_date.hour] = y_axis3[posted_date.hour] + 1.0 / len(same)

    print("bid: ", bid_count)

    # plt.subplot(211)
    # plt.bar(x_axis, y_axis)
    plt.subplot(100 * day_count + 10 + plot_index)
    plt.bar(x_axis, y_axis)
    plt.bar(x_axis, y_axis2)
    plt.bar(x_axis, y_axis3)
    plt.suptitle('Hourly Job Posting Rate')
    plot_index = plot_index + 1

plt.show()