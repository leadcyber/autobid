import express from "express"
import cors from 'cors'
import bodyParser from 'body-parser'
import {
    getSkillData,
    getSkillOccurenceMatrix
} from './parser/skill_reader.js'
import { getBlockerData } from "./parser/blocker_reader.js"
import { getAdditionalSentences } from "./parser/sentence_reader.js"
import {
    getRequiredSkills,
    getRequiredSkillGroups,
    getHighlightPositions,
    getHighlightPositionsWithTags,
} from './parser/skill_parser.js'
import {
    getHighlightBlockerPositions,
    getHighlightBlockerPositionsWithTags,
    getBlockerProperties
} from './parser/blocker_parser.js'
import {
    getSalaryData
} from "./parser/salary_parser.js"
import {
    getClipboard
} from "./parser/util.js"




const app = express()
app.use(cors())
app.use(bodyParser())






app.get("/skill/list", (req, res) => {
    try {
        const skillData = getSkillData()
        res.json(skillData)
    } catch(err) {
        res.status(500).send()
    }
})
app.get("/skill/occurence/matrix", (req, res) => {
    try {
        const occurenceMatrix = getSkillOccurenceMatrix()
        res.json(occurenceMatrix)
    } catch(err) {
        res.status(500).send()
    }
})
app.post("/skill/highlights", (req, res) => {
    try {
        const skillData = getSkillData()
        const skillPositions = getHighlightPositions(req.body.jd, skillData)
        res.json(skillPositions)
    } catch(err) {
        res.status(500).send()
    }
})
app.post("/skill/highlights/tagged", (req, res) => {
    try {
        const skillData = getSkillData()
        const skillPositions = getHighlightPositionsWithTags(req.body.jd, skillData)
        res.json(skillPositions)
    } catch(err) {
        res.status(500).send()
    }
})
app.post("/skill/measure/groups", (req, res) => {
    try {
        const skillData = getSkillData()
        const groups = getRequiredSkillGroups(req.body.jd, skillData)
        res.json(groups)
    } catch(err) {
        res.status(500).send()
    }
})
app.post("/skill/measure", (req, res) => {
    try {
        const skillData = getSkillData()
        const requiredSkills = getRequiredSkills(req.body.jd, skillData)
        res.json(requiredSkills)
    } catch(err) {
        res.status(500).send()
    }
})







app.post("/blocker/highlights", (req, res) => {
    try {
        const blockerData = getBlockerData()
        const blockerPositions = getHighlightBlockerPositions(req.body.jd, blockerData)
        res.json(blockerPositions)
    } catch(err) {
        res.status(500).send()
    }
})
app.post("/blocker/highlights/tagged", (req, res) => {
    try {
        const blockerData = getBlockerData()
        const blockerPositions = getHighlightBlockerPositionsWithTags(req.body.jd, blockerData)
        res.json(blockerPositions)
    } catch(err) {
        res.status(500).send()
    }
})
app.post("/blocker/measure", (req, res) => {
    try {
        const blockerData = getBlockerData()
        const blockerProperties = getBlockerProperties(req.body.jd, blockerData)
        res.json(blockerProperties)
    } catch(err) {
        res.status(500).send()
    }
})





app.post("/jd/mark", (req, res) => {
    try {
        const jd = req.body.jd
        const skillData = getSkillData()
        const skillPositions = getHighlightPositions(jd, skillData)

        let text = jd

        let intervals = skillPositions.sort((a, b) => b[0] - a[0])
        for(let interval of intervals) {
            text = `${text.slice(0, interval[0])}<span class='highlight-skill'>${text.slice(interval[0], interval[1])}</span>${text.slice(interval[1])}`
        }

        const blockerData = getBlockerData()
        const blockerPositions = getHighlightBlockerPositionsWithTags(text, blockerData)
        intervals = blockerPositions.sort((a, b) => b[0] - a[0])
        for(let interval of intervals) {
            text = `${text.slice(0, interval[0])}<span class='position-${interval[2].toLowerCase()}'>${text.slice(interval[0], interval[1])}</span>${text.slice(interval[1])}`
        }
        res.send(text)
    } catch(err) {
        res.status(500).send()
    }
})
app.post("/jd/salary", (req, res) => {
    try {
        const salary = getSalaryData(req.body.jd)
        res.json(salary)
    } catch(err) {
        res.status(500).send()
    }
})

app.get("/sentences/additional", (req, res) => {
    try {
        const sentences = getAdditionalSentences()
        res.json(sentences)
    } catch(err) {
        res.status(500).send()
    }
})





app.get("/tool/clipboard", async (req, res) => {
    try {
        const rtf = await getClipboard()
        res.json(rtf)
    } catch(err) {
        res.status(500).send(err.toString())
    }
})






app.listen(7000, () => {
    console.log("Server is listening...")
})