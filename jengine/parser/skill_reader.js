const fs = require('fs')
const yaml = require('js-yaml')

const skillPath = "/Volumes/Data/local_db/skills.yaml"
const skillOccurencePath = "/Volumes/Data/local_db/skill_occurence.yaml"

const getSkillData = () => {
    let skillBuffer = fs.readFileSync(skillPath, 'utf8')
    const doc = yaml.load(skillBuffer)
    if(doc && doc.skills) return doc.skills
    return {}
}
const getSkillOccurenceMatrix = () => {
    let skillBuffer = fs.readFileSync(skillOccurencePath, 'utf8')
    const doc = yaml.load(skillBuffer)
    if(doc) return doc
    return {}
}

exports.getSkillData = getSkillData
exports.getSkillOccurenceMatrix = getSkillOccurenceMatrix