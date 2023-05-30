import { myConsole } from '../util/myconsole'
import axios from 'axios'
import { getPageDataFromDB } from '../db'
import { workspaceSetting } from '../config/constant'
import os from 'os'
import path from 'path'

export const generateResume = async (jobId: string, position: string, description: string) => {
  myConsole.log(`[generate-resume]: ${jobId}`)
  // const downloadPath = path.join(os.homedir(), "downloads", `${jobId}.pdf`)
  const downloadPath = path.join(os.homedir(), "downloads", `Michael.C Resume.pdf`)
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
