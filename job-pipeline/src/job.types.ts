export enum JobState {
    FOUND,
    COPIED,
    DELETED,
}
export type Job = {
  id?: string
  category: string,
  company: string,
  position: string,
  postedAgo: string,
  postedDate: string,
  scannedDate: Date,
  copiedDate: Date | null,
  location: string,
  salary: string,
  jobUrl: string,
  identifier: string,
  state: JobState,
  available?: boolean,
  alreadyApplied: boolean
}
export type JobRow = {
  id?: string
  category: string,
  company: string,
  position: string,
  postedAgo: string,
  postedDate: number,
  scannedDate: number,
  location: string,
  salary: string,
  jobUrl: string,
  identifier: string,
  state: JobState
}
export type FetchedJob = {
  company: string,
  position: string,
  postedAgo: string,
  postedDate: string,
  location: string,
  salary: string,
  jobUrl: string
}
export type PageData = {
  brief?: string,
  detail?: string,
  description?: string,
  applyMode: "EasyApply" | "Apply" | "Closed" | "Error",
  applyUrl: string,
  recruiter: {
    image: string,
    name: string,
    title: string
  } | null,
  criterias: Object,
}
export type RequiredSkill = {
  skill: string,
  familarity: number,
  release: number,
  parent: any,
  level: number,
  importance: number
}
export enum BidState {
  LAZY,
  PENDING
}

export enum FetchMode {
  LAZY,
  NORMAL,
  CRAZY
}
