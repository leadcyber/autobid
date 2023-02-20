import { EmailRecord } from "../email/email.types";
import { getPlainContent, getEmailSubject, normalizeContent } from '../email/parser'
import { filterCompany } from '../db'

import winkNLP from 'wink-nlp';
import model from 'wink-eng-lite-model'
import { first } from "cheerio/lib/api/traversing";

const nlp = winkNLP( model );

const getSentences = (plainText: string) => {
  const lines = plainText.split("\r\n")
  let sentences = []
  for(let line of lines) {
    const doc = nlp.readDoc(line)
    sentences.push(...doc.sentences().out())
  }
  return sentences.filter(s => s !== "")
}

export const isAppliedContent = (email: EmailRecord) => {
  const plainText: string = normalizeContent(getPlainContent(email))
  const sentences = getSentences(plainText)
  for(let sentence of sentences) {
    if(/received your application/ig.exec(sentence)) return true
    if(/received your application/ig.exec(sentence)) return true
    if(/review your (resume|application|information)/ig.exec(sentence)) return true
    if(/is currently reviewing/ig.exec(sentence)) return true
    if(/reviewing (your application|resume)/ig.exec(sentence)) return true
    if(/Your application has been received/ig.exec(sentence)) return true
    if(/appreciate (.+) apply (to|for)/ig.exec(sentence)) return true
    if(/not able to advance (you )?(to )?(the )?next round/ig.exec(sentence)) return true
  }
  return false
}
export const isFailedContent = (email: EmailRecord) => {
  const plainText: string = normalizeContent(getPlainContent(email))
  const sentences = getSentences(plainText)
  for(let sentence of sentences) {
    if(/Unfortunately/ig.exec(sentence)) return true
    if(/have reviewed your/ig.exec(sentence)) return true
    if(/(pursue|move forward with|moving forward with) other candidate/ig.exec(sentence)) return true
    if(/move forward with other/ig.exec(sentence)) return true
    if(/not (to )?move (you )?forward/ig.exec(sentence)) return true
    if(/not (to )?proceed with you(r candi)?/ig.exec(sentence)) return true
    if(/regret to/ig.exec(sentence)) return true
    if(/reject/ig.exec(sentence)) return true
    if(/success in your job search/ig.exec(sentence)) return true
  }
  return false
}
const detectInSentence = (sentence: string) => {
  // console.log(sentence)
  const doc = nlp.readDoc( sentence );
  const tokenTypes = doc.tokens().out(nlp.its.pos)
  const tokens = doc.tokens().out()
  const candidateTokens = []
  for(let index = 1; index < tokens.length; index ++) {
    const firstLetter = tokens[index].length > 0 ? tokens[index][0] : null
    if(firstLetter === null) continue
    if(!/[A-Z]/.test(firstLetter)) continue
    if(tokenTypes[index - 1] !== "ADP") continue
    candidateTokens.push(index)
  }
  return candidateTokens.map(index => tokens[index])


  let company = null, position = null

  let match: any = (/(Thanks|Thank you) for applying to (join us at |work at |the )?(.+?)([.!]$| and|, Michael)/ig).exec(sentence)
  if(match) {
    company = company || match[2]
  }
  match = (/(Thanks|Thank you)(.*?) your interest in (joining |the |working at )?(position of )?(.+?)( (at|with) (.+?))?([.!]$| and|, Michael)/ig).exec(sentence)
  if(match) {
    if(match[4] === "position of ") {
      position = position || match[5]
      company = company || match[8]
    }
    if(match[7]) {
      if(match[8] && match[8].startsWith("such a"))
        company = company || match[5]
      else {
        position = position || match[5]
        company = company || match[8]
      }
    } else {
      company = company || match[5]
    }
  }
  match = (/(apply|applying|application) (to|for) (the |our open |our )?(.+?) (role|position|opening)(.*?)( (at|with) (.+?))?([.!]$| and|, Michael)/ig).exec(sentence)
  if(match) {
    if(match[4] !== "the" && match[4] !== "our") {
      position = position || match[4]
      company = company || match[9]
    }
  }
  match = (/(apply|applying|application) (to|for) (the |our open |our )?(role|position|opening) of (.+?)( (at|with) (.+?))?([.!]$| and|, Michael)/ig).exec(sentence)
  if(match) {
    position = position || match[5]
    company = company || match[8]
  }
  match = (/(apply|applying|application) (to|for) (the |our open |our )?(.+?)'s (.+?)( role| position| opening|([.!]$| and|, Michael))/ig).exec(sentence)
  if(match) {
    position = position || match[5]
    company = company || match[4]
  }
  match = (/(apply|applying|application) (to|for) (the |our open |our )?(.+?) (at|with) (.+?)([.!]$| and|, Michael)/ig).exec(sentence)
  if(match) {
    console.log(sentence)
    if(match[4] !== "the" && match[4] !== "our") {
      position = position || match[4]
      company = company || match[6]
    }
  }
  match = (/^the (.+?) (hiring |talent |people |culture |Recruiting )?team$/ig).exec(sentence)
  if(match) {
    company = company || match[1]
  }
  return {
    company,
    position
  }
}
export const parseEmailSubject = (email: EmailRecord) => {
  const subject = getEmailSubject(email)

  const res = detectInSentence(subject)

  return {
    company: res.company,
    position: res.position
  }
}
export const getCompanyPositionContent = (email: EmailRecord) => {
  const plainText: string = normalizeContent(getPlainContent(email))
  const sentences = getSentences(plainText)
  let company = null, position = null
  for(let sentence of sentences) {

    const res = detectInSentence(sentence)
    company = company || res.company
    position = position || res.position
    // let positionMatch: any = (/we received your application for (.*?), and we are delighted/ig).exec(plainText)
    // if(!positionMatch)
    //   positionMatch = (/is currently reviewing your application for (.*?), and should we find/ig).exec(plainText)
    // if(!positionMatch)
    //   positionMatch = (/We will review your information for the (.*?) role/ig).exec(plainText)
  }
  if(!company) {
    const subject = parseEmailSubject(email)
    company = subject?.company
    position = subject?.position
  }


  return {
    company,
    position
  }
}

export const isLinkedinEasyApplied = (email: EmailRecord) => {
  if(email.sender === "jobs-noreply@linkedin.com") {
    if(email.snippet.startsWith("Your application was sent to")) return true
  }
  return false
}
export const getLinkedinEasyAppliedData = (email: EmailRecord) => {
  const lines = email.payload.parts[0].body.data.split("\r\n")
  return {
    company: lines[4],
    position: lines[3],
    location: lines[5],
    appliedAgo: lines[6],
    jobUrl: lines[7].replace("View job: ", "")
  }
}




export const isLinkedinApplyFailed = (email: EmailRecord) => {
  if(email.sender === "jobs-noreply@linkedin.com") {
    if(email.snippet.startsWith("We have an update on")) {
      return true
    }
  }
  return false
}
export const getLinkedinApplyFailedData = (email: EmailRecord) => {
  const plainText = email.payload.parts[0].body.data
  const lines = plainText.split("\r\n")
  const companyUrl: any = (/feel free to connect with us on LinkedIn @  \" (.*?)\"/i).exec(plainText)
  const careerSiteUrl: any = (/openings on our career site \"(.*?)\"/i).exec(plainText)
  const companyMatch: any = (/Your update from (.*?)$/ig).exec(lines[0])
  const company = companyMatch[1]
  const position: any = lines[3].slice(company.length + 3)
  return {
    company: company,
    position: position,
    applied: lines[4],
    companyUrl: companyUrl[1],
    careerSiteUrl: careerSiteUrl[1]
  }
}




export const isLinkedinApplyViewed = (email: EmailRecord) => {
  if(email.sender === "jobs-noreply@linkedin.com") {
    if(email.snippet.includes("was viewed by")) {
      return true
    }
  }
  return false
}
export const getLinkedinApplyViewedData = (email: EmailRecord) => {
  const lines = email.payload.parts[0].body.data.split("\r\n")
  const jobUrl = email.payload.parts[1].body.data.match(/https:\/\/www\.linkedin\.com\/comm\/jobs\/view\/[\d]*/i)

  const wstart = lines.indexOf("People who work here")
  let workers = []
  if(wstart >= 0) {
    const wend = lines.indexOf("See more")
    for(let i = wstart + 2; i < wend; i += 5) {
      workers.push({
        name: lines[i],
        position: lines[i + 2],
        profileUrl: lines[i + 4]
      })
    }
  }
  return {
    company: lines[3],
    position: lines[4],
    location: lines[5],
    jobPosterName: lines[9],
    jobPosterTitle: lines[10],
    workers: workers,
    jobUrl: jobUrl[0]
  }
}





export const isLeverApplied = (email: EmailRecord) => {
  if(email.sender === "no-reply@hire.lever.co") {
    return isAppliedContent(email)
  }
  return false
}
export const getLeverAppliedData = (email: EmailRecord) => {
  return getCompanyPositionContent(email)
}







export const isLeverFailed = (email: EmailRecord) => {
  if(email.sender === "no-reply@hire.lever.co") {
    return isFailedContent(email)
  }
  return false
}
export const getLeverFailedData = (email: EmailRecord) => {
  return getCompanyPositionContent(email)
}






export const isGreenhouseApplied = (email: EmailRecord) => {
  if(email.sender === "no-reply@greenhouse.io") {
    return isAppliedContent(email)
  }
  return false
}
export const getGreenhouseAppliedData = (email: EmailRecord) => {
  return getCompanyPositionContent(email)
}







export const isGreenhouseFailed = (email: EmailRecord) => {
  if(email.sender === "no-reply@greenhouse.io") {
    return isFailedContent(email)
  }
  return false
}
export const getGreenhouseFailedData = (email: EmailRecord) => {
  return getCompanyPositionContent(email)
}






export const isAshbyhqApplied = (email: EmailRecord) => {
  if(email.sender === "no-reply@ashbyhq.com") {
    return isAppliedContent(email)
  }
  return false
}
export const getAshbyhqAppliedData = (email: EmailRecord) => {
  const plainText: string = normalizeContent(getPlainContent(email))
  const companyMatch: any = (/current opening at (.*?)\./ig).exec(plainText)
  return {
    company: companyMatch[1],
  }
}






export const isAshbyhqFailed = (email: EmailRecord) => {
  if(email.sender === "no-reply@ashbyhq.com") {
    return isFailedContent(email)
  }
  return false
}
export const getAshbyhqFailedData = (email: EmailRecord) => {
  const plainText: string = normalizeContent(getPlainContent(email))
  let match: any = (/Thank you for your interest in the (.*?) position with (.*?)\. Unfortunately/ig).exec(plainText)
  if(!match)
    match = (/Thank you for (.*?)apply(.*?) for the (.*?) at (.*?)\. /ig).exec(plainText)
  if(!match)
    match = (/Thank you for (.*?)apply(.*?) for the (.*?)( position)? at (.*?)\. /ig).exec(plainText)
  return {
    company: match[2],
    position: match[1]
  }
}


export const getContext = (email: EmailRecord, companyMap, positionMap) => {
  const plainText: string = normalizeContent(getPlainContent(email))
  const sentences = getSentences(plainText)
  let company = null, position = null
  for(let sentence of sentences) {
    const companyList = [], positionList = []
    for(let company in companyMap) {
      const index = sentence.indexOf(company)
      if(index >= 0) companyList.push()
    }
  }

  return {
    company,
    position
  }
}
