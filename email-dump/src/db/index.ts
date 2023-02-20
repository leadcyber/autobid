import { CompanyModel, EmailModel, JobModel, emailDB, jobDB } from "./schema"
import { EmailRecord, ScanData } from "../email/email.types"
import mongoose from 'mongoose'

export const getLastCheckDateFromDB = async (): Promise<Date> => {
  const response = await EmailModel.find().sort({ internalDate: -1 }).limit(1)
  if(response.length == 0) return new Date(1970, 0, 1)
  return response[0].internalDate!
}
export const insertEmails = async (emails: EmailRecord[]) => {
    await EmailModel.insertMany(emails)
}
export const getEmailById = async (id: string): Promise<EmailRecord | null> => {
  const res = await EmailModel.findOne({ _id: new mongoose.Types.ObjectId(id) })
  if(res)
    return {
      _id: res._id.toString(),
      id: res.id,
      idDec: res.idDec!,
      sender: res.sender!,
      recipients: res.recipients!,
      threadId: res.threadId!,
      labelIds: res.labelIds!,
      snippet: res.snippet!,
      historyId: res.historyId!,
      internalDate: res.internalDate!,
      payload: res.payload!,
      sizeEstimate: res.sizeEstimate!
    }
  return null
}
export const getEmailList = async (filter: any) => {
  const res = await EmailModel.find(filter)
  if(res) {
    return res.map((email: any) => ({
      _id: email._id.toString(),
      id: email.id,
      idDec: email.idDec!,
      sender: email.sender!,
      recipients: email.recipients!,
      threadId: email.threadId!,
      labelIds: email.labelIds!,
      snippet: email.snippet!,
      historyId: email.historyId!,
      internalDate: email.internalDate!,
      payload: email.payload!,
      sizeEstimate: email.sizeEstimate!
    }))
  }
  return []
}
export const emailExist = async(emailId: string) => {
  try {
    const res = await EmailModel.findOne({id: emailId})
    return !!res
  } catch(err) {
    return false
  }
}
export const removeUncompletedScan = async (scanData: ScanData) => {
  await EmailModel.deleteMany({ internalDate: { $gte: scanData.scanDate }, idDec: {$gte: scanData.latestEmailIdDec} })
}

const connect = async (dbInstance: any, db: string) => {
  await dbInstance.connect(`mongodb://localhost:27017/${db}`);
  console.log("MongoDB successfully connected!")
}
const disconnect = async(dbInstance: any) => {
  await dbInstance.disconnect()
}

export const connectEmailDB = async () => {
  await connect(emailDB, "emaildump")
}
export const connectJobDB = async () => {
  await connect(jobDB, "linkedinbot")
}

export const disconnectEmailDB = async () => {
  await disconnect(emailDB)
}
export const disconnectJobDB = async () => {
  await disconnect(jobDB)
}


export const getAllPositions = async () => {
  const jobs = await JobModel.find({}, { position: 1 })
  return [ ...new Set(jobs.map(item => item.position)) ]
}
export const getAllCompanies = async () => {
  const companies = await CompanyModel.find({}, { companyName: 1 })
  return [ ...new Set(companies.map(item => item.companyName)) ]
}

export const filterCompany = async (filter: any) => {
  const companies = await CompanyModel.find(filter, { companyName: 1 })
  return companies.map(item => item.companyName)
}
