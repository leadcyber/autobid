import fs from 'fs'
import path from 'path'
import { Job } from 'job.types';
import { BidState } from '../../job.types'
import { spawn } from 'child_process'
import { myConsole } from '../util/myconsole'
import { workspaceSetting, CONCURRENCY_AUTOBID_SESSION } from '../config/constant'
import axios from 'axios'
import express from 'express'
import cors from 'cors'
import bodyParser from 'body-parser'

import {
  setCopied,
  getPageDataFromDB,
  setPageDataToDB,
  setAlreadyApplied
} from "../db";
import { getPageData } from './index'

// --- Settings

let updateRenderer: Function, onQueueChange: Function, onBidStateChange: Function
let requestConnectMode = false
let exceptionSkipMode = false



// AutoBid Engine

class AutoBidTaskRunner {
  job: Job | null = null
  applyUrl: string = ""
  getState() {
    return this.job === null ? BidState.LAZY : BidState.PENDING
  }
  async retry() {
    await this.requestBid()
  }
  async bid(job: Job) {
    this.job = job
    let pageData = await getPageDataFromDB(this.job.id!)
    if(!pageData || pageData.applyMode == "Error") {
      for(let retry = 5; retry >= 0; retry --) {
        pageData = await getPageData(this.job)
        if(pageData?.applyMode != "Error") break
      }
      await setPageDataToDB(this.job.id!, pageData!)
    }
    if(pageData!.applyUrl != "") {
      this.applyUrl = pageData!.applyUrl
      await setCopied(this.job.id!)
      await this.requestBid()
    }
  }
  async requestBid() {
    console.log(`[auto-apply]: ${this.applyUrl}`)
    myConsole.log(`[auto-apply]: ${this.applyUrl}`)
    await _sendToBidder({
      type: "apply",
      payload: {
        id: this.job?.id,
        url: this.applyUrl,
        autoMode: true,
        exceptionMode: exceptionSkipMode,
        requestConnect: requestConnectMode
      }
    })
  }
  reset() {
    this.job = null
    this.applyUrl = ""
  }
}

class AutoBidTaskManager {
  sessions: AutoBidTaskRunner[] = Array(CONCURRENCY_AUTOBID_SESSION).fill(0).map(() => new AutoBidTaskRunner())
  mode: boolean = false
  pendingJobs: Job[] = []

  getSessionByJobID = (jobId: string) => {
    return this.sessions.find(session => session.job?.id === jobId)
  }
  nextTick = () => {
    if(this.pendingJobs.length > 0) {
      const lazySession = this.sessions.find(session => session.getState() === BidState.LAZY)
      if(lazySession) {
        lazySession.bid(this.pendingJobs.shift()!)
      }
    }
    onBidStateChange(this.sessions)
    onQueueChange(this.pendingJobs)
  }

  addJobToQueue = async (job: Job) => {
    console.log(job)
    const lazySession = this.sessions.find(session => session.getState() === BidState.LAZY)
    if(lazySession) {
      await lazySession.bid(job)
    } else {
      this.pendingJobs.push(job)
    }
  }
  skip = async (jobId: string) => {
    const index = this.pendingJobs.findIndex(job => job.id === jobId)
    if(index < 0) {
      const session = this.sessions.find(session => session.job?.id === jobId)
      if(session) {
        session.reset()
      }
    } else {
      this.pendingJobs.splice(index, 1)
    }
    this.nextTick()
  }
  resetTaskRunners = () => {
    this.sessions.forEach(session => {
      session.reset()
    })
    onBidStateChange(this.sessions)
  }
  setAutoBidMode = (mode: boolean) => {
    this.mode = mode
    if(mode == false) {
      this.pendingJobs = []
      onQueueChange(this.pendingJobs)
      this.resetTaskRunners()
    }
  }
}

const taskManager = new AutoBidTaskManager()



// --- API invocation

async function _sendToBidder(data: any) {
  try {
    await axios.post(`${workspaceSetting.bidderURL}/invoke`, data)
  } catch(err: any) {
    console.log(err)
    console.log(`[bidder-interface-error]: ${err.response.status}`)
  }
}

export const applyExternal = async (jobId: string, jobUrl: string, requestConnect: boolean) => {
  myConsole.log(`[manual-apply]: ${jobUrl}`)
  return await _sendToBidder({
    type: "apply",
    payload: {
      id: jobId,
      url: jobUrl,
      autoMode: false,
      exceptionMode: false,
      requestConnect
    }
  })
}

// --- Operation functions

export const pushToAutoBidQueue = async (jobs: Job[]) => {
  if(!taskManager.mode) return
  for(let job of jobs) {

    let pageData = await getPageDataFromDB(job.id!)
    if(!pageData || pageData.applyMode == "Error") {
      for(let retry = 5; retry >= 0; retry --) {
        pageData = await getPageData(job)
        if(pageData?.applyMode != "Error") break
      }
      await setPageDataToDB(job.id!, pageData!)
    }
    if(pageData!.applyUrl == "") continue
    try {
      const response = await axios.post(`${workspaceSetting.pyServiceURL}/job/autobiddable`, {
        position: job.position,
        jd: pageData?.description
      })
      if(response.data.available) {
        await taskManager.addJobToQueue(job)
      }
    } catch(err) {
      console.log("[py-engine]: Unable to determine the validity of this job.")
    }
  }
  updateRenderer()
  onBidStateChange(taskManager.sessions)
  onQueueChange(taskManager.pendingJobs)
}
export const skipTask = (jobId: string) => {
  taskManager.skip(jobId)
}



// --- Read functions

export const getBidState = () => onBidStateChange(taskManager.sessions)
export const getQueueState = () => onQueueChange(taskManager.pendingJobs)


// --- Setting functions

export const registerAutoBidEvents = (
  _updateRenderer: any,
  _onQueueChange: any,
  _onBidStateChange: any) =>
{
  updateRenderer = _updateRenderer
  onQueueChange = _onQueueChange
  onBidStateChange = _onBidStateChange
}
export const setAutoBidMode = taskManager.setAutoBidMode
export const getAutoBidMode = () => taskManager.mode
export const getRequestConnectMode = () => requestConnectMode
export const setRequestConnectMode = (mode: boolean) => {
  requestConnectMode = mode
  myConsole.log(`[set-request-connect-mode]: ${requestConnectMode}`)
}
export const getExceptionSkipMode = () => exceptionSkipMode
export const setExceptionSkipMode = (mode: boolean) => {
  exceptionSkipMode = mode
  myConsole.log(`[set-exception-skip-mode]: ${exceptionSkipMode}`)
}



// --- Web server

const app = express()
app.use(cors())
app.use(bodyParser())
app.post("/bidder", async (req: any, res: any) => {
  res.send()
  const response = req.body.data

  if(response.type == "success") {
    const jobId = response.payload.id
    await setAlreadyApplied(jobId)
    taskManager.getSessionByJobID(jobId)?.reset()
    await taskManager.nextTick()
  } else if(response.type == "failed") {
    const jobId = response.payload.id
    if(response.reason == "no-free-profile") {
      setTimeout(() => {
        taskManager.getSessionByJobID(jobId)?.retry()
      }, 10000)
    } else {
      taskManager.getSessionByJobID(jobId)?.reset()
      await taskManager.nextTick()
    }
  }
})
app.listen(workspaceSetting.dashboardPort, () => {
  console.log("Dashboard port is listening...")
})
