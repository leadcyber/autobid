import path from 'path'
import fs from 'fs'

export const dirPath = process.env.NODE_ENV === "production" ? path.join(process.resourcesPath, "../../../") : "../"

export const workspacePath = path.join(dirPath, 'workspace.json')
export const workspaceSetting = JSON.parse(fs.readFileSync(workspacePath).toString())

export const CONCURRENCY_AUTOBID_SESSION = 5
