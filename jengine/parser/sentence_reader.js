import fs from 'fs'
import yaml from 'js-yaml'


const additionalSentencePath = "/Volumes/Data/local_db/resume/addition_data.yaml"

export const getAdditionalSentences = () => {
    let buffer = fs.readFileSync(additionalSentencePath, 'utf8')
    const doc = yaml.load(buffer)
    if(doc) return doc
    return {}
}