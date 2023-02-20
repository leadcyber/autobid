from utils.db import job_collection

job = job_collection.find_one({ "pageData.applyUrl": "https://boards.greenhouse.io/embed/job_app?for=truecar&t=fadd9ab35us&token=4132750005&b=https%3A%2F%2Fwww.truecar.com%2Fcareers%2F" })
print(job)