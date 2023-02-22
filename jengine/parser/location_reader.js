const fs = require('fs')
const yaml = require('js-yaml')

const workLocationPath = "/Volumes/Data/local_db/work_location.yaml"

const getLocationData = () => {
    let fileBuffer = fs.readFileSync(workLocationPath, 'utf8')
    const doc = yaml.load(fileBuffer)
    if(doc) return doc
    return {}
}

exports.getLocationData = getLocationData