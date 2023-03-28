export const getHighlightLocationPositions = (jobDescription, locationData) => {
    let intervals = []
    for(let keyword in locationData) {
        const { pattern, familarity } = locationData[keyword]
        pattern.forEach((reg) => {
            const regFlag = reg.endsWith("/ni") ? "g" : "ig"
            if(reg.endsWith("/ni")) {
                reg = reg.replace("/ni", "")
            }
            const re = new RegExp(reg, regFlag)

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
export const getHighlightLocationPositionsWithTags = (jobDescription, locationData) => {
    const intervals = getHighlightLocationPositions(jobDescription, locationData)
    for(let interval of intervals) {
        const substr = jobDescription.substring(interval[0], interval[1])
        let maxMatchLength = 0, maxMatchKeyword = ""
        for(let keyword in locationData) {
            const { pattern, familarity } = locationData[keyword]
            const maxLength = pattern.reduce((res, reg) => {
                const regFlag = reg.endsWith("/ni") ? "g" : "ig"
                if(reg.endsWith("/ni")) {
                    reg = reg.replace("/ni", "")
                }
                const re = new RegExp(reg, regFlag)
                const match = re.exec(substr)
                if(!match) return res
                return res > match[0].length ? res : match[0].length
            }, 0)
            if(maxLength > maxMatchLength) {
                maxMatchLength = maxLength
                maxMatchKeyword = keyword
            }
        }
        interval.push(maxMatchKeyword)
    }
    return intervals
}


export const getLocationProperties = (jdHtml, locationData) => {
    const intervals = getHighlightLocationPositionsWithTags(jdHtml, locationData)
    const props = {}
    for(let interval of intervals) {
        props[interval[2]] = (props[interval[2]] || 0) + 1
    }
    return Object.entries(props).sort((a, b) => b[1] - a[1]).map((entry) => ({ keyword: entry[0], count: entry[1], familarity: locationData[entry[0]].familarity }))
}
