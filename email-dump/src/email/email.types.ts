export type EmailRecord = {
  _id?: string,
  id: string,
  idDec: number,
  sender: string,
  recipients: string[]
  threadId: string,
  labelIds: string[],
  snippet: string,
  historyId: string,
  internalDate: Date,
  payload: any,
  sizeEstimate: number
}
export type ScanData = {
  scanDate: Date,
  latestEmailIdDec: number
}
