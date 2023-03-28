
import axios from 'axios'
import mongoose from 'mongoose'
import { PageData, Job, JobState } from '../../job.types'


let ORIGINAL_START_DATE = new Date(2022, 7, 29)

const annotationSchema = new mongoose.Schema({
  job: {
    type: mongoose.Schema.Types.ObjectId,
    ref: "Job",
    index: true
  },
  annotation: {
    type: Number,
    default: 0
  }
})

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

export const Annotations = mongoose.model('Annotation', annotationSchema)
export const Jobs = mongoose.model('Job', jobSchema)
export const Companies = mongoose.model('Company', companySchema)


export const connect = async () => {
    await mongoose.connect('mongodb://localhost:27017/linkedinbot');
    console.log("MongoDB successfully connected!")
}
export const disconnect = async() => {
    await mongoose.disconnect()
}

export const getJobList = async () => {
  const jobDocs = await Jobs.find({ "pageData.description": {"$not": {"$eq": null} } }).sort({
    scannedDate: 1,
  })
  let jobs = []
  for(let doc of jobDocs) {
    jobs.push(doc._id.toString())
  }
  return jobs
}

export const getPageDataFromDB = async (jobId: string): Promise<PageData|null> => {
  const res = await Jobs.findOne({ _id: jobId }, { pageData: 1 })
  return res?.pageData
}
export const setPageDataToDB = async (id: string, pageData: PageData) => {
  await Jobs.updateOne({ _id: id }, { pageData: pageData })
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

export const setAnnotation = async(jobId: string, value: Number) => {
  const annotation = await Annotations.findOne({ job: jobId })
  if(!annotation) {
    const newAnnotation = new Annotations({
      job: jobId,
      annotation: value
    })
    await newAnnotation.save()
  } else {
    await Annotations.updateOne({ job: jobId }, { $set: { annotation: value } })
  }
}
