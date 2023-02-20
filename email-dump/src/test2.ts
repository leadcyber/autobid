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


(async() => {
  await connectEmailDB()
  const email: EmailRecord = await getEmailById("63a617d10117286d827a2303") as EmailRecord
  await disconnectEmailDB()
  await connectJobDB()
  decodeContent(email)
  let data = null
  if(isLinkedinEasyApplied(email))
    data = getLinkedinEasyAppliedData(email)
  else if(isLinkedinApplyFailed(email))
    data = getLinkedinApplyFailedData(email)
  else if(isLinkedinApplyViewed(email))
    data = getLinkedinApplyViewedData(email)

  else if(isLeverFailed(email))
    data = await getLeverFailedData(email)
  else if(isLeverApplied(email))
    data = await getLeverAppliedData(email)

  else if(isGreenhouseFailed(email))
    data = await getGreenhouseFailedData(email)
  else if(isGreenhouseApplied(email))
    data = await getGreenhouseAppliedData(email)

  else if(isAshbyhqApplied(email))
    data = await getAshbyhqAppliedData(email)
  // const str = getPlainContent(email)
  // console.log(str)
  console.log(email._id, data)
  await disconnectJobDB()
})()
