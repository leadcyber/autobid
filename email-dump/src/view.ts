import { getEmailById, getEmailList, connectEmailDB, disconnectEmailDB } from './db'
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

(async() => {
  await connectEmailDB()
  const emails: EmailRecord[] = await getEmailList({ _id: "63a617a30117286d827a22a9" })
  const email = emails[0]
  decodeContent(email)
  // console.log(emails[0].payload.headers)
  const str = getPlainContent(email)
  console.log(str)
  await disconnectEmailDB()
})()
