import { getEmailById, getEmailList, connectEmailDB, disconnectEmailDB, connectJobDB, disconnectJobDB, getLastExtractedDate, addExtractions } from './db'
import { EmailRecord } from './email/email.types';
import { decodeContent, getPlainContent, getEmailSubject } from './email/parser'
import {
  isLinkedinEasyApplied,
  isLinkedinApplyFailed,
  isLinkedinApplyViewed,
  getLinkedinEasyAppliedData,
  getLinkedinApplyFailedData,
  getLinkedinApplyViewedData,

  isJobRelatedContent,

  isAppliedContent,
  isFailedContent,
  getCompanyContent
} from './recognizer'

const possibleSenders = [
  "jobs-noreply@linkedin.com",
  /lever\.co/i,
  /greenhouse/i,
  /jobvite/i,
  /breezy/i,
  /applytojob/i,
  /ashbyhq/i
];

(async() => {

  await connectEmailDB()
  const lastExtDate = await getLastExtractedDate()
  console.log(lastExtDate)
  let filter = {}
  if(lastExtDate) filter = { date: { $gt: lastExtDate } }

  let emails: EmailRecord[] = []
  for(let sender of possibleSenders) {
    console.log("Fetching for " + sender)
    emails = emails.concat(await getEmailList({ sender: sender, ...filter }))
  }
  await disconnectEmailDB()



  await connectJobDB()

  const extractions = []
  for(let email of emails) {
    decodeContent(email)

    let data = null
    let emailType = null
    if(isLinkedinEasyApplied(email)) {
      data = getLinkedinEasyAppliedData(email)
      emailType = "applied"
    }
    else if(isLinkedinApplyFailed(email)) {
      data = getLinkedinApplyFailedData(email)
      emailType = "failed"
    }
    else if(isLinkedinApplyViewed(email)) {
      data = getLinkedinApplyViewedData(email)
      emailType = "viewed"
    }

    else if(isJobRelatedContent(email)) {
      let companyName = null
      console.log(email._id, email.sender)
      if(isAppliedContent(email)) {
        companyName = await getCompanyContent(email)
        emailType = "applied"
      } else if(isFailedContent(email)) {
        companyName = await getCompanyContent(email)
        emailType = "failed"
      }

      if(companyName !== null) {
        data = { company: companyName }
      }
    }

    if(data !== null) {
      console.log(email._id, data.company)
      extractions.push({
        emailId: email._id,
        date: email.internalDate,
        type: emailType,
        data
      })
    }
  }
  await disconnectJobDB()

  console.log("Extraction count: " + extractions.length)

  await connectEmailDB()
  await addExtractions(extractions)
  await disconnectEmailDB()
})()
