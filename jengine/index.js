const express = require("express")
const cors = require('cors')
const bodyParser = require('body-parser')
const {
    getSkillData,
    getSkillOccurenceMatrix
} = require('./parser/skill_reader')
const { getLocationData } = require("./parser/location_reader")
const { getAdditionalSentences } = require("./parser/sentence_reader")
const {
    getRequiredSkills,
    getRequiredSkillGroups,
    getHighlightPositions,
    getHighlightPositionsWithTags,
} = require('./parser/skill_parser')
const {
    getHighlightLocationPositions,
    getHighlightLocationPositionsWithTags,
    getLocationProperties
} = require('./parser/location_parser')

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



app.post("/location/highlights", (req, res) => {
    try {
        const locationData = getLocationData()
        const locationPositions = getHighlightLocationPositions(req.body.jd, locationData)
        res.json(locationPositions)
    } catch(err) {
        res.status(500).send()
    }
})
app.post("/location/highlights/tagged", (req, res) => {
    try {
        const locationData = getLocationData()
        const locationPositions = getHighlightLocationPositionsWithTags(req.body.jd, locationData)
        res.json(locationPositions)
    } catch(err) {
        res.status(500).send()
    }
})
app.post("/location/measure", (req, res) => {
    try {
        const locationData = getLocationData()
        const locationProperties = getLocationProperties(req.body.jd, locationData)
        res.json(locationProperties)
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

        const locationData = getLocationData()
        const locationPositions = getHighlightLocationPositionsWithTags(text, locationData)
        intervals = locationPositions.sort((a, b) => b[0] - a[0])
        for(let interval of intervals) {
            text = `${text.slice(0, interval[0])}<span class='position-${interval[2].toLowerCase()}'>${text.slice(interval[0], interval[1])}</span>${text.slice(interval[1])}`
        }
        res.send(text)
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