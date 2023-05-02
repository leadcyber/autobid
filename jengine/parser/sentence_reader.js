import fs from 'fs'
import yaml from 'js-yaml'
import { WORKSPACE_PATH } from '../config'


const additionalSentencePath = `${WORKSPACE_PATH}/resume/addition_data.yaml`

export const getAdditionalSentences = () => {
    let buffer = fs.readFileSync(additionalSentencePath, 'utf8')
    const doc = yaml.load(buffer)
    if(doc) return doc
    return {}
}