const express = require("express")
const cors = require('cors')
const bodyParser = require('body-parser')
const {
    getSkillData,
    getSkillOccurenceMatrix
} = require('./parser/skill')
const {
    getRequiredSkills,
    getRequiredSkillGroups,
    getHighlightPositions,
    getHighlightPositionsWithTags
} = require('./parser/jd')
const { getAdditionalSentences } = require("./parser/sentence")

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

app.get("/sentences/additional", (req, res) => {
    try {
        const sentences = getAdditionalSentences()
        res.json(sentences)
    } catch(err) {
        res.status(500).send()
    }
})
app.listen(7000, () => {
    console.log("Server is listening...")
})