import fs from 'fs'
import path from 'path'
import { sleep } from '../utils'

import { authenticate } from '@google-cloud/local-auth'
import { gmail_v1 as GmailNamespace, google } from 'googleapis'
import { OAuth2Client } from 'google-auth-library'

import { getEmailRecordFromMessage, processEmailRecords } from './parser'
import { emailExist, removeUncompletedScan } from '../db'

import { EmailRecord, ScanData } from './email.types'

import { workspacePath } from '../config'

const SCOPES = ['https://mail.google.com/', 'email']
const LATEST_SCAN_PATH = `${workspacePath}/email/latest_scan.txt`

export const authenticateGmail = async (credentialFilePath: string, cachedCredentialPath: string): Promise<OAuth2Client> => {
    if(fs.existsSync(cachedCredentialPath)) {
        const cachedCredentialData = fs.readFileSync(cachedCredentialPath).toString()
        const client = google.auth.fromJSON(JSON.parse(cachedCredentialData)) as OAuth2Client
        return client
    } else {
        const client = await authenticate({
            scopes: SCOPES,
            keyfilePath: credentialFilePath,
        })

        const credentialData = fs.readFileSync(credentialFilePath).toString()
        const credential = JSON.parse(credentialData).web;

        const cachedData = JSON.stringify({
            type: 'authorized_user',
            client_id: credential.client_id,
            client_secret: credential.client_secret,
            refresh_token: client.credentials.refresh_token,
        });
        fs.writeFileSync(cachedCredentialPath, cachedData)
        return client
    }
}

export const scanEmail = async (gmail: GmailNamespace.Gmail, scanData: ScanData): Promise<Date> => {
  let response: any = null;
  const toSearchDate = (date: Date) => date.toISOString().slice(0, 10)
  const query = `in:inbox after:${toSearchDate(scanData.scanDate)}`
  console.log(query)

  let latestEmailDate = scanData.scanDate
  // let latestEmailDate = new Date(1970, 0, 1)
  let latestEmailIdDec = Number.POSITIVE_INFINITY
  let totalCount = 0
  do {
    try {
      response = await gmail.users.messages.list({
          userId: "me",
          q: query,
          pageToken: response?.nextPageToken,
          maxResults: 10
      })
    } catch(err) {
      console.log(err)
      console.log("Unable to get gmail list.")
      continue
    }

    response = response.data
    let messageMetadatas = response?.messages
    totalCount += messageMetadatas.length
    console.log(totalCount)
    if(!messageMetadatas) break
    const emailRecords: EmailRecord[] = []

    for(let msgInfo of messageMetadatas) {
      if(await emailExist(msgInfo.id)) continue
      let message = null
      try {
        message = await gmail.users.messages.get({
          id: msgInfo.id,
          userId: "me"
        })
      } catch(err) {
        console.log("Unable to get message data.")
        continue
      }

      const messageData: GmailNamespace.Schema$Message = message.data
      if(messageData.labelIds?.includes("UNREAD")) {
        try {
          await gmail.users.messages.modify({
            id: msgInfo.id,
            userId: "me",
            requestBody: {
              "addLabelIds": [ "UNREAD" ]
            }
          })
        } catch(err) {
          console.log("Unable to relabel UNREAD message.")
          continue
        }
      }
      if(new Date(Number(messageData.internalDate)) <= scanData.scanDate) continue
      const emailRecord = getEmailRecordFromMessage(messageData)
      console.log(emailRecord.id)
      emailRecords.push(emailRecord)

      if(latestEmailDate < emailRecord.internalDate) {
        latestEmailDate = emailRecord.internalDate
      }
      if(latestEmailIdDec > emailRecord.idDec) {
        latestEmailIdDec = emailRecord.idDec
      }
      console.log(latestEmailIdDec)
    }
    if(emailRecords.length == 0) break;
    processEmailRecords(emailRecords)
    setLatestScanData({
      scanDate: scanData.scanDate,
      latestEmailIdDec: latestEmailIdDec
    })
  } while(response?.nextPageToken);

  return latestEmailDate
}


const getLatestScanData = (): ScanData => {
  try {
    let buffer = fs.readFileSync(LATEST_SCAN_PATH, "utf8")
    let data = JSON.parse(buffer)
    return {
      scanDate: new Date(Number(data.scanDate)),
      latestEmailIdDec: data.latestEmailIdDec
    }
  } catch(err) {
    return {
      scanDate: new Date(1970, 0, 1),
      latestEmailIdDec: 0
    }
  }
}
const setLatestScanData = (scanDate: ScanData) => {
  fs.writeFileSync(LATEST_SCAN_PATH, JSON.stringify({
    scanDate: scanDate.scanDate.getTime().toString(),
    latestEmailIdDec: scanDate.latestEmailIdDec
  }))
}

export const sync = async (client: OAuth2Client) => {
    const gmail: GmailNamespace.Gmail = google.gmail({version: 'v1', auth: client});
    let scanData = getLatestScanData()
    if(scanData.latestEmailIdDec > 0)
      await removeUncompletedScan(scanData)
    while(true) {
      scanData.scanDate = await scanEmail(gmail, scanData)
      setLatestScanData({ scanDate: scanData.scanDate, latestEmailIdDec: 0 })
      await sleep(1000 * 60 * 5)
    }
}
