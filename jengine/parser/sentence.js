const fs = require('fs')
const yaml = require('js-yaml')
const additionalSentencePath = "/Volumes/Data/local_db/resume/addition_data.yaml"

exports.getAdditionalSentences = () => {
    let buffer = fs.readFileSync(additionalSentencePath, 'utf8')
    const doc = yaml.load(buffer)
    if(doc) return doc
    return {}
}