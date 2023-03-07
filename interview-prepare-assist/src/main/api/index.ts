import url from "url"
import path from "path"
import { workspaceSetting } from '../config/constant'
import fs from 'fs'
import { RequiredSkill } from '../../job.types'
import cheerio from 'cheerio'
import axios from 'axios'
import os from 'os'

const defaultQueryOptions = [{
  category: "React&Frontend",
  keyword: "react OR angular OR frontend OR fullstack",
  location: "United States",
  dateSincePosted: "24hr",
  remoteFilter: "remote",
  sortBy: "relevant",
  jobType: "F,C"
}, {
  category: "React&Frontend",
  keyword: "react OR angular OR frontend OR fullstack",
  location: "United States",
  dateSincePosted: "24hr",
  remoteFilter: "remote",
  sortBy: "recent",
  jobType: "F,C"
}];


const supportedPlatformPath = path.join(workspaceSetting.workspacePath, workspaceSetting.supportedPlatForms)
let supportPlatforms: any = []

const familarityPath = path.join(workspaceSetting.workspacePath, workspaceSetting.familarity)


export const isAutofillSupported = (jobUrl: string): boolean => {
  const hostname = url.parse(jobUrl).hostname
  if(!hostname) return false
  try {
    supportPlatforms = JSON.parse(fs.readFileSync(supportedPlatformPath).toString())
  } catch(err) {}
  return supportPlatforms.some((platform: string) => hostname.search(new RegExp(platform, "ig")) >= 0)
}

export const getFamilarity = (jobDescription: string | undefined): number => {
  if(jobDescription === undefined) return 0
  let familarityDict: any = { _: 100 }
  try {
    familarityDict = JSON.parse(fs.readFileSync(familarityPath).toString())
  } catch(err) {}

  let total = 0, occurrence = 0
  let normal = familarityDict['_'][0]
  for(let key in familarityDict) {
    const [ score, weight ] = familarityDict[key]
    const matches = jobDescription.match(new RegExp(key, "ig"))
    const count = matches == null ? 0 : matches.length
    occurrence += count * Number(weight)
    total += Number(score) * count * Number(weight)
  }
  return total / occurrence / normal * 100
}

export const getCompanyUrl = async (brief: string) => {
  const $ = cheerio.load(brief);
  const orgLink = $(".topcard__org-name-link")
  return orgLink.attr("href") || ""
}


export const getRequiredSkills = async (jobDescription: string | undefined) => {
  if(!jobDescription) return []
  try {
    const response = await axios.post(`${workspaceSetting.serviceURL}/skill/measure`, {jd:jobDescription})
    const requiredSkills: any[] = response.data
    return requiredSkills as RequiredSkill[]
  } catch(err) {
    return []
  }
}
export const generateResume = async (jobId: string, position: string, description: string) => {
  const downloadPath = path.join(os.homedir(), "downloads", `${jobId}.pdf`)
  console.log(downloadPath)
  try {
    await axios.post(`${workspaceSetting.pyServiceURL}/resume/generate/file`, {
      position,
      jd: description,
      path: downloadPath
    })
    console.log(`Resume generated at ${downloadPath}`)
  } catch(err: any) {
    console.log(`[bidder-interface-error]: ${err.response.status}`)
  }
}
