import fs from 'fs'
import yaml from 'js-yaml'

const workLocationPath = "/Volumes/Data/local_db/work_location.yaml"

export const getLocationData = () => {
    let fileBuffer = fs.readFileSync(workLocationPath, 'utf8')
    const doc = yaml.load(fileBuffer)
    if(doc) return doc
    return {}
}