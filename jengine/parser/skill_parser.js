const { getSkillData } = require('./skill_reader')
const cheerio = require('cheerio')


const getHighlightPositions = (jobDescription, skillData) => {
    let intervals = []
    for(let skillName in skillData) {
        const skill = skillData[skillName]
        if(!skill.pattern) continue
        skill.pattern.forEach((pattern) => {
            let patternStr = "", patternGroup = 0
            if(typeof pattern === "string") {
                patternStr = pattern
                patternGroup = 0
            } else {
                patternStr = pattern[0]
                patternGroup = pattern[1]
            }
            const regFlag = patternStr.endsWith("/ni") ? "g" : "ig"
            if(patternStr.endsWith("/ni")) {
                patternStr = patternStr.replace("/ni", "")
            }
            const re = new RegExp(patternStr, regFlag)

            let match = null
            while ((match = re.exec(jobDescription)) != null) {
                const currentIndex = jobDescription.indexOf(match[patternGroup], match.index)
                let outerStart = match.index, outerEnd = match.index + match[0].length
                let innerStart = currentIndex, innerEnd = currentIndex + match[patternGroup].length

                let included = false
                for(let interval of intervals) {
                    const [ is, ie, os, oe ] = interval
                    if((outerStart >= os && outerStart < oe) || (outerEnd > os && outerEnd <= oe)) {
                        interval[0] = innerStart
                        interval[1] = innerEnd
                        interval[2] = Math.min(outerStart, os)
                        interval[3] = Math.max(outerEnd, oe)
                        included = true
                    }
                }
                if(!included) intervals.push([ innerStart, innerEnd, outerStart, outerEnd ])
            }
        })
    }
    return intervals
}
const getHighlightPositionsWithTags = (jobDescription, skillData) => {
    const intervals = getHighlightPositions(jobDescription, skillData)
    const taggedIntervals = []
    for(let interval of intervals) {
        const substr = jobDescription.substring(interval[2], interval[3])
        let maxMatchLength = 0, maxMatchSkillName = ""
        for(let skillName in skillData) {
            const skill = skillData[skillName]
            if(!skill.pattern) continue
            const maxLengthStr = skill.pattern.reduce((res, pattern) => {
                let patternStr = "", patternGroup = 0
                if(typeof pattern === "string") {
                    patternStr = pattern
                    patternGroup = 0
                } else {
                    patternStr = pattern[0]
                    patternGroup = pattern[1]
                }
                const regFlag = patternStr.endsWith("/ni") ? "g" : "ig"
                if(patternStr.endsWith("/ni")) {
                    patternStr = patternStr.replace("/ni", "")
                }
                const re = new RegExp(patternStr, regFlag)
                const match = re.exec(substr)
                if(!match) return res
                const currentIndex = substr.indexOf(match[patternGroup], match.index)
                return res.length > match[patternGroup].length ? res : match[patternGroup]
            }, "")
            if(maxLengthStr.length > maxMatchLength) {
                maxMatchLength = maxLengthStr.length
                maxMatchSkillName = skillName
            }
        }
        taggedIntervals.push([ interval[0], interval[1], maxMatchSkillName ])
    }
    return taggedIntervals
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