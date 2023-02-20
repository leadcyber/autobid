import mongoose from 'mongoose'
import { PageData, Job, JobState } from '../../job.types'


let ORIGINAL_START_DATE = new Date(2022, 7, 29)

const companySchema = new mongoose.Schema({
  companyName: {
    type: String,
  },
  postCount: {
    type: Number,
    default: 0
  }
})

// mongoose.Types.ObjectId
const jobSchema = new mongoose.Schema({
  category: {
      type: String
  },
  company: {
    type: mongoose.Schema.Types.ObjectId,
    ref: "Company"
  },
  position: {
      type: String
  },
  postedAgo: {
    type: String
  },
  postedDate: {
      type: String
  },
  scannedDate: {
      type: Date
  },
  copiedDate: {
    type: Date
  },
  location: {
      type: String
  },
  salary: {
      type: String
  },
  jobUrl: {
      type: String
  },
  identifier: {
      type: String
  },
  pageData: {
      type: Object,
      default: null
  },
  alreadyApplied: {
    type: Boolean,
    default: false
  },
  state: {
      type: String,
  },
  available: {
    type: Boolean,
    default: false
  }
})

export const Jobs = mongoose.model('Job', jobSchema)
export const Companies = mongoose.model('Company', companySchema)


export const connect = async () => {
    await mongoose.connect('mongodb://localhost:27017/linkedinbot');
    console.log("MongoDB successfully connected!")
}
export const disconnect = async() => {
    await mongoose.disconnect()
}

export const getJobList = async (positionFilter: string, companyFilter: string, limit: number, _alreadyApplied: boolean) => {
  const companyRegExp = new RegExp(companyFilter, "ig")
  const jobDocs = await Jobs.find({ $and: [
    {available: true},
    {position: new RegExp(positionFilter, "ig")},
    {alreadyApplied: _alreadyApplied},
    {$not: {pageData: null} }
  ] }).sort({
    scannedDate: -1,
  }).populate("company")
  let jobs = []
  for(let doc of jobDocs) {
    const company = (doc.company as any)
    const companyName = company?.companyName
    if(!companyRegExp.test(companyName)) continue
    jobs.push({
      id: doc._id.toString(),
      category: doc.category,
      company: companyName,
      alreadyApplied: doc.alreadyApplied,
      position: doc.position,
      postedAgo: doc.postedAgo,
      postedDate: doc.postedDate,
      scannedDate: doc.scannedDate,
      copiedDate: doc.copiedDate,
      location: doc.location,
      salary: doc.salary,
      jobUrl: doc.jobUrl,
      identifier: doc.identifier,
      state: doc.state,
      available: true,
      postCount: company?.postCount
    })
    if(jobs.length > limit) break
  }
  return jobs
}

export const getNewlyFoundJobs = async (jobs: Job[]) => {
  if(jobs.length == 0) return []
  try {
    const dateStr = new Date(Date.now() - 1000 * 60 * 60 * 48).toISOString().substring(0, 10)
    const dayJobs = await Jobs.find({ $gte: { postedDate: dateStr } }, { identifier: 1 }) /* 2fix */
    const identifiers = dayJobs.map(d => d.identifier)
    return jobs.filter(job => !identifiers.includes(job.identifier))
  } catch(err) {
    console.log(err)
    return []
  }
}

export const addNewJobs = async (jobs: Job[]) => {
  const companies = [ ...new Set(jobs.map(({ company }) => company)) ]
  const companyRecords: {[key: string]: any} = {}
  const companyRecordIdMap: {[key: string]: any} = {}
  // Get company records ( id, companyName, postCount ) while ensuring all the companies are registered to DB.
  for(let companyName of companies) {
    let companyRecord = await Companies.findOne({companyName})
    // Create new company record if it's new to DB
    if(companyRecord === null) {
      const newCompany = new Companies({
        companyName,
        postCount: 0
      })
      companyRecord = await newCompany.save()
    }

    companyRecords[companyName] = {
      id: companyRecord._id,
      postCount: companyRecord.postCount
    }
    companyRecordIdMap[companyRecord._id!.toString()] = companyName
  }
  // Insert all newly found jobs with found company ids.
  const res = await Jobs.insertMany(jobs.map(job => ({
    ...job,
    company: companyRecords[job.company].id
  })))
  // Update job posting count per company in-memory
  jobs.forEach(({company}) => {
    companyRecords[company].postCount ++
  })
  // Update job posting count in DB
  await Companies.updateMany({ $or: jobs.map(({ company }) => ({ companyName: company })) }, {$inc: { postCount: 1 }} )
  // return new Job array
  return res.map(doc => {
    const companyId = doc.company!.toString()
    const companyName = companyRecordIdMap[companyId]
    return {
      id: doc._id.toString(),
      category: doc.category,
      company: companyName,
      position: doc.position,
      postedAgo: doc.postedAgo,
      postedDate: doc.postedDate,
      scannedDate: doc.scannedDate,
      copiedDate: doc.copiedDate,
      location: doc.location,
      salary: doc.salary,
      jobUrl: doc.jobUrl,
      identifier: doc.identifier,
      state: doc.state,
      available: doc.available,
      postCount: companyRecords[companyName].postCount
    }
  })
}

export const getPageDataFromDB = async (jobId: string): Promise<PageData|null> => {
  const res = await Jobs.findOne({ _id: jobId }, { pageData: 1 })
  return res?.pageData
}
export const setPageDataToDB = async (id: string, pageData: PageData) => {
  await Jobs.updateOne({ _id: id }, { pageData: pageData })
}

export const deleteFromDB = async(jobId: string) => {
  await Jobs.deleteOne({ _id: jobId })
}
export const deleteCopied = async() => {
  await Jobs.updateMany({ state: JobState.COPIED }, { state: JobState.DELETED })
}
export const deleteAll = async() => {
  await Jobs.updateMany({ available: true }, { state: JobState.DELETED })
}
export const setCopied = async(jobId: string) => {
  await Jobs.updateOne({ _id: jobId }, { state: JobState.COPIED, copiedDate: new Date() })
}
export const setCompleted = async(jobIds: string[]) => {
  await Jobs.updateMany({ $or: jobIds.map(jobId => ({ _id: jobId })) }, { state: JobState.DELETED })
}

export const getIdFromIdentifier = async (identifier: string): Promise<string> => {
  const doc = await Jobs.findOne({ identifier }, { _id: 1 })
  return doc?._id.toString()!
}

export const setAlreadyApplied = async (jobId: string) => {
  await Jobs.updateOne({ _id: jobId }, { alreadyApplied: true })
}
export const isAlreadyApplied = async (externalUrl: string) => {
  try {
    const doc = await Jobs.findOne({ "pageData.applyUrl": externalUrl, alreadyApplied: true })
    if(doc == null) return false
    return true
  } catch(err) {
    return false
  }
}

export const getRelatedJobCount = async (job: Job) => {
  const limitDate = new Date(new Date().getTime() - 1000 * 60 * 60 * 24 * 7).toISOString()
  const companyRecord = await Companies.findOne({companyName: job.company})
  const companyId = companyRecord!._id
  return {
    companyJobs: await Jobs.count({ company: companyId }),
    recentCompanyJobs: await Jobs.count({ company: companyId, postedDate: { $gte: limitDate.substring(0, 10) } }),
    exactMatch: await Jobs.count({ company: companyId, position: job.position }),
    recentExactMatch: await Jobs.count({ company: companyId, position: job.position, postedDate: { $gte: limitDate.substring(0, 10) } })
  }
}
