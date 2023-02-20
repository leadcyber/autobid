import { insertEmails } from '../db'
import { EmailRecord } from './email.types'
import { google, gmail_v1 as GmailNamespace } from 'googleapis'
import { Base64 } from 'js-base64'
import cheerio from 'cheerio'


const getSender = (message: GmailNamespace.Schema$Message) => {
  const item = message.payload?.headers?.filter(
    (header) => header.name == 'From'
  );
  if (!item || !item[0]) return null;
  const value = item[0].value;
  const email: any = value?.match(/<(.+)>/);
  if (email && email[1]) return email[1];
  return value;
};
export const getEmailSenderName = (email: EmailRecord) => {
  const item = email.payload.headers.find((item: any) => item.name === "From")
  if (!item) return null;
  const value = item.value;
  const senderName: any = value?.match(/(.*?)<(.+)>/);
  if (senderName && senderName[1]) return senderName[1];
  return value;
}
export const getEmailSubject = (email: EmailRecord) => {
  const item = email.payload.headers.find((item: any) => item.name === "Subject")
  if (!item) return null;
  return item.value
}

export const decodeContent = (message: any) => {
  const { payload, body, parts } = message;

  if (payload && payload.body && payload.body.size)
    payload.body.data = Base64.decode(
      payload.body.data.replace(/-/g, '+').replace(/_/g, '/')
    );
  if (body && body.data)
    message.body.data = Base64.decode(
      body.data.replace(/-/g, '+').replace(/_/g, '/')
    );

  if (payload && payload.parts)
    payload.parts.forEach((part: any) => decodeContent(part))
  if(parts)
    parts.forEach((part: any) => decodeContent(part))
};
const toPlainText = (type: string, message: string) => {
  const contentType = type.toLowerCase()
  if(contentType === "text/plain")
    return message
  if(contentType == "text/html") {
    const $ = cheerio.load(`<html>${message}</html>`)
    var txt = $('html *').contents().map(function() {
      return (this.type === 'text') ? $(this).text() : '';
    }).get().join(' ');
    return txt
  }
  return message.toString()
}
export const getPlainContent = (message: any) => {
  const { payload, body, parts } = message;

  let contentStr: string = ""
  if (payload && payload.body && payload.body.size)
    contentStr = toPlainText(payload.mimeType, payload.body.data)
  if (body && body.data)
    contentStr = toPlainText(message.mimeType, message.body.data)

  if (payload && payload.parts)
    contentStr += payload.parts.map((part: any) => getPlainContent(part)).join("\r\n")
  if(parts)
    contentStr += parts.map((part: any) => getPlainContent(part)).join("\r\n")
  return contentStr
}
export const normalizeContent = (text: string) => {
  return text.replace(/Vue\.js/ig, "VueJS").replace(/React\.js/ig, "ReactJS")
}

export const getEmailRecordFromMessage = (email: GmailNamespace.Schema$Message): EmailRecord => {
  const sender = getSender(email)
  // decodeContent(email.data)

  // const { payload: { body, parts } } = email.data
  // console.log(body, parts)

  // return {
  //   id: email.metadata.id,
  //   threadId: email.metadata.threadId,
  //   data: email.data
  // }
  return {
    id: email.id!,
    idDec: parseInt(email.id!, 16),
    sender: sender,
    recipients: [],
    threadId: email.threadId!,
    labelIds: email.labelIds!,
    snippet: email.snippet!,
    historyId: email.historyId!,
    internalDate: new Date(Number(email.internalDate)),
    payload: email.payload,
    sizeEstimate: Number(email.sizeEstimate),
  }
}
export const processEmailRecords = (records: EmailRecord[]) => {
  console.log(`${records.length} records found!`)
  insertEmails(records)
}
