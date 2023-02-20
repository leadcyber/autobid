const path = require('path')
const fs = require('fs')
const yaml = require('js-yaml')

const readSkillData = () => {
  let skillBuffer = fs.readFileSync('/Volumes/Data/bid_db/skills.yaml', 'utf8')
  const doc = yaml.load(skillBuffer)
  if(doc && doc.skills) return doc.skills
  return {}
}

const getRequiredSkills = (jobDescription) => {
  if(!jobDescription) return []
  try {
    const skillData = readSkillData()
    const occurences = []
    for(let skillName in skillData) {
      const skill = skillData[skillName]
      if(!skill.pattern) continue
      const regResult = skill.pattern.reduce((total, pattern) => {
        const reg = new RegExp(skill.pattern, "ig")
        const matches = jobDescription.match(reg)
        if(!matches) return total
        total.count += matches.length
        const currentPos = reg.exec(jobDescription).index
        total.pos = total.pos < currentPos ? total.pos : currentPos
        return total
      }, {count: 0, pos: Number.POSITIVE_INFINITY})
      if(regResult.pos === Number.POSITIVE_INFINITY) continue
      occurences.push({
        skillName,
        skill,
        ...regResult
      })
    }
    occurences.sort((a, b) => a.pos - b.pos)
    return occurences.map(({skillName, skill, count: skillCount}, index) => {
      const importance = 10 - (Number(index) / occurences.length) ** skillCount * 10
      return {
        skill: skillName,
        familarity: skill.familarity,
        release: skill.release,
        parent: skill.parent,
        level: skill.level,
        importance: importance * skill.affect
      }
    }).sort((a, b) => b.importance - a.importance)
  } catch(err) {
    return []
  }
}

const res = getRequiredSkills(fs.readFileSync("/Volumes/Work/_own/autobid/test/page_data.txt", "utf8"))
console.log(res)
// console.log(res.map(item => `${item.skill} ${item.importance}`))
