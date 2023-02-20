import { getEmailById, getEmailList, connectEmailDB, disconnectEmailDB, connectJobDB, disconnectJobDB } from './db'
import { EmailRecord } from './email/email.types';
import { decodeContent, getPlainContent, getEmailSenderName } from './email/parser'
import {
  isLinkedinEasyApplied,
  isLinkedinApplyFailed,
  isLinkedinApplyViewed,
  isLeverApplied,
  isLeverFailed,
  isGreenhouseApplied,
  isGreenhouseFailed,
  isAshbyhqApplied,

  getLinkedinEasyAppliedData,
  getLinkedinApplyFailedData,
  getLinkedinApplyViewedData,
  getLeverAppliedData,
  getLeverFailedData,
  getGreenhouseAppliedData,
  getGreenhouseFailedData,
  getAshbyhqAppliedData,
} from './recognizer'
import fs from 'fs'


(async() => {
  await connectEmailDB()
  const emails: EmailRecord[] = [
    ... await getEmailList({ sender: "no-reply@hire.lever.co" }),
    ... await getEmailList({ sender: "no-reply@us.greenhouse-mail.io" }),
    ... await getEmailList({ sender: "no-reply@greenhouse.io" }),
    ... await getEmailList({ sender: "no-reply@ashbyhq.com" })
  ]
  // const emails: EmailRecord[] = await getEmailList({})
  await disconnectEmailDB()

  await connectJobDB()
  let failedCount = 0

  for(let email of emails) {
    decodeContent(email)
    console.log(email._id)
    // console.log(email.payload)
    let data = null
    // if(isLeverApplied(email))
    //   data = await getLeverAppliedData(email)
    // else if(isLeverFailed(email))
    //   data = await getLeverFailedData(email)

    // else if(isGreenhouseApplied(email))
      data = await getGreenhouseAppliedData(email)
    // else if(isGreenhouseFailed(email))
    //   data = await getGreenhouseFailedData(email)

    // else if(isAshbyhqApplied(email))
    //   data = await getAshbyhqAppliedData(email)
    if(data === null || data.length == 0)
      failedCount ++
    else {
    }
    console.log(data)
  }
  console.log( emails.length, failedCount)
  await disconnectJobDB()
  // const str = getPlainContent(email)
  // console.log(str)
})()
