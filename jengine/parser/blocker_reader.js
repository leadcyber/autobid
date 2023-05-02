import fs from 'fs'
import yaml from 'js-yaml'

const blockerPath = "/Volumes/Data/local_db/blocker.yaml"

export const getBlockerData = () => {
    let fileBuffer = fs.readFileSync(blockerPath, 'utf8')
    const doc = yaml.load(fileBuffer)
    if(doc) return doc
    return {}
}