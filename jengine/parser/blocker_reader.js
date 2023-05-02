import fs from 'fs'
import yaml from 'js-yaml'
import { WORKSPACE_PATH } from '../config'

const blockerPath = `${WORKSPACE_PATH}/blocker.yaml`

export const getBlockerData = () => {
    let fileBuffer = fs.readFileSync(blockerPath, 'utf8')
    const doc = yaml.load(fileBuffer)
    if(doc) return doc
    return {}
}