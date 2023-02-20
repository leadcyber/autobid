const { getSkillData } = require('./skill')
const cheerio = require('cheerio')




const getHighlightPositions = (jobDescription, skillData) => {
    let intervals = []
    for(let skillName in skillData) {
        const skill = skillData[skillName]
        if(!skill.pattern) continue
        skill.pattern.forEach((pattern) => {
            const regFlag = pattern.endsWith("/ni") ? "g" : "ig"
            if(pattern.endsWith("/ni")) {
                pattern = pattern.replace("/ni", "")
            }
            const re = new RegExp(pattern, regFlag)

            let match = null
            while ((match = re.exec(jobDescription)) != null) {
                let start = match.index, end = match.index + match[0].length
                let included = false
                for(let interval of intervals) {
                    if((start >= interval[0] && start < interval[1]) || (end > interval[0] && end <= interval[1])) {
                        interval[0] = Math.min(start, interval[0])
                        interval[1] = Math.max(end, interval[1])
                        included = true
                    }
                }
                if(!included) intervals.push([start, end])
            }
        })
    }
    return intervals
}
const getHighlightPositionsWithTags = (jobDescription, skillData) => {
    const intervals = getHighlightPositions(jobDescription, skillData)
    for(let interval of intervals) {
        const substr = jobDescription.substring(interval[0], interval[1])
        let maxMatchLength = 0, maxMatchSkillName = ""
        for(let skillName in skillData) {
            const skill = skillData[skillName]
            if(!skill.pattern) continue
            const maxLength = skill.pattern.reduce((res, pattern) => {
                const regFlag = pattern.endsWith("/ni") ? "g" : "ig"
                if(pattern.endsWith("/ni")) {
                    pattern = pattern.replace("/ni", "")
                }
                const re = new RegExp(pattern, regFlag)
                const match = re.exec(substr)
                if(!match) return res
                return res > match[0].length ? res : match[0].length
            }, 0)
            if(maxLength > maxMatchLength) {
                maxMatchLength = maxLength
                maxMatchSkillName = skillName
            }
        }
        interval.push(maxMatchSkillName)
    }
    return intervals
}
const getRequiredSkillGroupsPerSection = (section, skillData) => {
    const intervals = getHighlightPositionsWithTags(section, skillData)
    if(intervals.length == 0) return [[], []]

    const occurences = intervals.map(interval => ({
        skillName: interval[2],
        start: interval[0],
        end: interval[1]
    }))
    occurences.sort((a, b) => a.start - b.start)

    const groups = []
    let lastEnd = 0
    for(let occurence of occurences) {
        let between = section.slice(lastEnd, occurence.start)
        between = between.replace(/[\s,./]/ig, "").replace(/and|or/ig, "")
        if(between.length < 3 && groups.length > 0) {
            groups[groups.length - 1].push(occurence)
        } else {
            groups.push([ occurence ])
        }
        lastEnd = occurence.end - 1
    }
    return [ groups, occurences ]
}
const getRequiredSkillsPerSection = (section, skillData) => {
    const [ groups, occurences ] = getRequiredSkillGroupsPerSection(section, skillData)
    if(occurences.length == 0) return { impact: 0, importances: {} }

    let betweenItem = 1.0 / occurences.length / 3
    let betweenGroup = (1.0 - betweenItem * occurences.length) / groups.length
    let curScore = 1.0

    for(let i = 0; i < groups.length; i ++) {
        for(let item of groups[i]) {
            item.weight = curScore
            curScore -= betweenItem
        }
        curScore -= betweenGroup
    }

    let maxImportance = 0

    const importances = {}
    let impact = 0
    for(let oid in occurences) {
        const occurence = occurences[oid]
        const { skillName } = occurence
        
        const importance = importances[occurence.skillName] || 0 + occurence.weight
        impact += skillData[skillName].affect
        // console.log(skillData[skillName].affect)
        importances[occurence.skillName] = importance
        maxImportance = Math.max(maxImportance, importance)
    }

    for(let skillName in importances) {
        importances[skillName] /= maxImportance
    }

    impact /= occurences.length // impact average
    impact = impact * (1.0 - 0.6 ** occurences.length)

    return {
        impact,
        importances
    }
}
const getRequiredSkillGroups = (jdHtml, skillData) => {
    const $ = cheerio.load(`<div id="root">${jdHtml}</div>`)
    const sections = $("#root")
    const groups = []
    for(let element of sections.contents()) {
        const section = $(element)
        const [ subgroups ] = getRequiredSkillGroupsPerSection(section.text(), skillData)
        groups.push(...subgroups)
    }
    return groups
}
const getRequiredSkills = (jdHtml, skillData) => {
    const $ = cheerio.load(`<div id="root">${jdHtml}</div>`)
    const sections = $("#root")
    const requiredSkills = []
    let maxImportance = 0

    for(let element of sections.contents()) {
        const section = $(element)
        const { impact, importances } = getRequiredSkillsPerSection(section.text(), skillData)
        // console.log(impact, importances)
        for(let skillName in importances) {
            const requiredSkill = requiredSkills.find(({skill}) => skill === skillName)
            const skill = skillData[skillName]
            const importance = importances[skillName] * impact * skill.affect
            if(!requiredSkill) {
                requiredSkills.push({
                    skill: skillName,
                    familarity: skill.familarity,
                    release: skill.release,
                    parent: skill.parent,
                    level: skill.level,
                    pattern: skill.pattern,
                    affect: skill.affect,
                    importance: importance
                })
                maxImportance = Math.max(maxImportance, importance)
            } else {
                requiredSkill.importance += importance
                maxImportance = Math.max(maxImportance, requiredSkill.importance)
            }
        }
    }
    return requiredSkills.map(skill => ({ ...skill, importance: skill.importance / maxImportance * 10.0 })).sort((a, b) => b.importance - a.importance)
}
exports.getHighlightPositions = getHighlightPositions
exports.getHighlightPositionsWithTags = getHighlightPositionsWithTags
exports.getRequiredSkillGroups = getRequiredSkillGroups
exports.getRequiredSkills = getRequiredSkills