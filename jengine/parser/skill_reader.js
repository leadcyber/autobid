import fs from 'fs'
import yaml from 'js-yaml'

const skillPath = "/Volumes/Data/local_db/skills.yaml"
const skillOccurencePath = "/Volumes/Data/local_db/skill_occurence.yaml"

export const getSkillData = () => {
    let skillBuffer = fs.readFileSync(skillPath, 'utf8')
    const doc = yaml.load(skillBuffer)
    if(doc && doc.skills) return doc.skills
    return {}
}
export const getSkillOccurenceMatrix = () => {
    let skillBuffer = fs.readFileSync(skillOccurencePath, 'utf8')
    const doc = yaml.load(skillBuffer)
    if(doc) return doc
    return {}
}
