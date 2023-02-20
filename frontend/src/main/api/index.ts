import * as linkedIn from './linkedin'
import url from "url"
import path from "path"
import { workspaceSetting } from '../config/constant'
import fs from 'fs'
import { Job, JobState, PageData, FetchedJob, FetchMode, RequiredSkill } from '../../job.types'
import { addNewJobs, getNewlyFoundJobs } from '../db'
import { myConsole } from '../util/myconsole'
import yaml from 'js-yaml'
import axios from 'axios'

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


const fitLevelPath = path.join(workspaceSetting.workspacePath, workspaceSetting.fitLevel)
let fitLevel: any = null

const supportedPlatformPath = path.join(workspaceSetting.workspacePath, workspaceSetting.supportedPlatForms)
let supportPlatforms: any = []

const familarityPath = path.join(workspaceSetting.workspacePath, workspaceSetting.familarity)
const queryPath = path.join(workspaceSetting.workspacePath, workspaceSetting.searchQuery)

const blacklistPath = path.join(workspaceSetting.workspacePath, workspaceSetting.companyBlacklist)
let blacklistedCompanies = {
  query: [],
  original: []
}

const FETCH_INFO = {
  [ FetchMode.LAZY ]: { timeout: 1000 * 60 * 15, limit: [ 0.5, 0.2, 0.3 ] },
  [ FetchMode.NORMAL ]: { timeout: 1000 * 60 * 3, limit: [ 0, 0, 1 ] },
  [ FetchMode.CRAZY ]: { timeout: 1000, limit: [ 0.5, 0.1, 0.4 ] },
}
let currentFetchMode = FetchMode.NORMAL

const getJobScore = (position: string): number => {
  if(!fitLevel) return 0
  let sum = 0
  for(let reg in fitLevel.weight) {
    const match = position.match(new RegExp(reg, "ig"))
    if(!match) sum += fitLevel.unknown
    else sum += Number(fitLevel.weight[reg])
  }
  return sum
}
const isJobAvailable = ({ position }: Job) => {
  if(!fitLevel) return true
  return getJobScore(position) >= fitLevel.level
}
const isJobAutobidable = ({ position }: Job) => {
  if(!fitLevel) return true
  return getJobScore(position) >= fitLevel.autobidLevel
}
const getRandomFetchCount = () => {
  const randomness = Math.random()
  const fetchInfo = FETCH_INFO[currentFetchMode].limit
  if(randomness < fetchInfo[0]) return 200
  if(randomness < fetchInfo[0] + fetchInfo[1]) return 400
  return 600
}

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
  console.log({ total, occurrence, normal })
  return total / occurrence / normal * 100
}

export const setFetchMode = (mode: FetchMode) => {
  if(currentFetchMode != mode) {
    const modeStr = ["lazy", "normal", "crazy"][mode]
    myConsole.log(`[fetch-mode]: Switching to ${modeStr} mode`)
    console.log(`[fetch-mode]: Switching to ${modeStr} mode`)
  }
  currentFetchMode = mode
}
export const getFetchMode = () => currentFetchMode

export const createLinkedInListener = async (
  onNewJobsFound: any,
  onAutobidableJobsFound:any,
  showNotification: any,
  setFetchStep:any
) => {
  // Read querys from json file
  let queryOptions = defaultQueryOptions

  const fetch = async () => {
    try {
      fitLevel = JSON.parse(fs.readFileSync(fitLevelPath).toString())
    } catch(err) {}

    if(fs.existsSync(queryPath)) {
      const queryBuffer = fs.readFileSync(queryPath)
      try {
        queryOptions = JSON.parse(queryBuffer.toString())
      } catch(err) {}
    }

    try {
        blacklistedCompanies = JSON.parse(fs.readFileSync(blacklistPath).toString())
    } catch(err) {}

    await Promise.all(queryOptions.map((queryParam, index) =>
      linkedIn.query({
        ...queryParam,
        keyword: `(${queryParam.keyword}) NOT (${blacklistedCompanies.query.join(" OR ")})`,
        limit: `${getRandomFetchCount()}`
      }, async (response: FetchedJob[], skip: number) => {
        const scannedDate = new Date()
        let jobs: Job[] =
          response.map(job => {
            return {
              ...job,
              category: queryOptions[index].category,
              scannedDate,
              copiedDate: null,
              identifier: url.parse(job.jobUrl).pathname,
              state: JobState.FOUND
            } as Job
          })
          .filter(({ jobUrl }) => url.parse(jobUrl).hostname == "www.linkedin.com")
          .filter(({ company }) => blacklistedCompanies.original.every((item: string) => item.toLowerCase() !== company.toLowerCase()))

        let identifiers: any = {}
        const uniqueJobs = jobs.reduce((total: any, current: Job) => {
          if(!identifiers[current.identifier]) {
            total.push(current)
            identifiers[current.identifier] = true
          }
          return total
        }, [])

        const newJobs = await getNewlyFoundJobs(uniqueJobs)
        setFetchStep("data", { total: uniqueJobs.length, newCount: newJobs.length, skip })
        if(newJobs.length == 0) return

        newJobs.forEach(job => job.available = isJobAvailable(job))
        const availableJobs = newJobs.filter(({available}) => available)

        const addedJobs = await addNewJobs(newJobs)

        await onNewJobsFound()

        const autobidableJobs = addedJobs.filter(job => isJobAutobidable(job as Job))
        await onAutobidableJobsFound(autobidableJobs)

        console.log(`[jobs-found]:  ${autobidableJobs.length}/${availableJobs.length}/${newJobs.length}/${uniqueJobs.length}`)
        myConsole.log(`[jobs-found]: ${autobidableJobs.length}/${availableJobs.length}/${newJobs.length}/${uniqueJobs.length}`)

        if(availableJobs.length > 0)
          showNotification(availableJobs)
      })
    ))
  }

  async function repeatFetch() {
    try {
      setFetchStep("started")
      await fetch()
    } catch(err) {}
    setTimeout(repeatFetch, FETCH_INFO[currentFetchMode].timeout)
    setFetchStep("lazy")
  }
  repeatFetch()
}

export const getPageData = async (job: Job): Promise<PageData> => {
  try {
    return await linkedIn.getPageData(job.jobUrl)
  } catch(err) {
    return {
      applyMode: "Error",
      applyUrl: "",
      recruiter: null,
      criterias: {}
    }
  }
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
