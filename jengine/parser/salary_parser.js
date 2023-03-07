exports.getSalaryData = (jd) => {
    const re = /\$[0-9,.]*/ig
    let match = null
    while ((match = re.exec(jd)) != null) {
        const start = match.index, end = match.index + match[0].length
        if(end < jd.length && jd[end].toLowerCase() === "k") {
            
        }
        console.log(match[0])
    }
    return {
        type: "yr",
        min: 150000,
        max: 180000
    }
}