import mongoose, { Mongoose } from 'mongoose'

const emailDB = new Mongoose()
const jobDB = new Mongoose()
const emailSchema = new mongoose.Schema({
  id: {
    type: String
  },
  idDec: {
    type: Number
  },
  sender: {
    type: String
  },
  recipients: {
    type: Array,
    default: []
  },
  threadId: {
    type: String
  },
  labelIds: {
    type: Array,
    default: []
  },
  snippet: {
    type: String
  },
  historyId: {
    type: String
  },
  internalDate: {
    type: Date
  },
  payload: {
    type: Object
  },
  sizeEstimate: {
    type: Number
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
      default: 0
  },
  available: {
    type: Boolean,
    default: false
  }
})

export {
  emailDB,
  jobDB
}
export const EmailModel = emailDB.model('Email', emailSchema)
export const JobModel = jobDB.model('Job', jobSchema)
export const CompanyModel = jobDB.model('Company', companySchema)
