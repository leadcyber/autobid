import { EmailRecord } from "../email/email.types";
import { getPlainContent, getEmailSenderName, getEmailSubject, normalizeContent } from '../email/parser'
import { filterCompany } from '../db'

import winkNLP from 'wink-nlp';
import model from 'wink-eng-lite-model'
import axios from 'axios'
import fs from 'fs'

const nlp = winkNLP( model );
let companyFilterCache: any = {}
let id = 1

const getSentences = (plainText: string) => {
  const lines = plainText.split("\r\n")
  let sentences = []
  for(let line of lines) {
    const doc = nlp.readDoc(line)
    sentences.push(...doc.sentences().out())
  }
  return sentences.filter(s => s !== "")
}
export const isJobRelatedContent = (email: EmailRecord) => {
  const plainText: string = normalizeContent(getPlainContent(email))
  const sentences = getSentences(plainText)
  for(let sentence of sentences) {
    if(/Thank you (for|to)/ig.exec(sentence)) return true
  }
  return false
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
const detectInSentence = async (sentence: string) => {
  // console.log(sentence)
  const doc = nlp.readDoc( sentence );
  const tokenTypes = doc.tokens().out(nlp.its.pos)
  const tokens = doc.tokens().out()
  const candidateTokens = []
  for(let index = 1; index < tokens.length; index ++) {
    const firstLetter = tokens[index].length > 0 ? tokens[index][0] : null
    if(firstLetter === null) continue
    if(tokenTypes[index - 1] !== "ADP") continue
    if(/[A-Z]/.test(firstLetter) || tokenTypes[index] === "PROPN")
      candidateTokens.push(index)
  }
  const matches = []
  for(let index = 0; index < tokens.length; index ++) {
    const token = tokens[index]
    if(candidateTokens.includes(index)) {
      const startIndex = sentence.indexOf(token)
      const companyNames = companyFilterCache[token] || await filterCompany({ companyName: new RegExp(`^${token}`) })
      companyFilterCache[token] = companyNames
      const possibleCompanyNames = new Set([
        ...companyNames,
        ...companyNames.map((name: string) => name.replace(/ studios/i, ""))
      ])
      // console.log(possibleCompanyNames)
      for(let companyName of possibleCompanyNames) {
        if(sentence.substr(startIndex, companyName?.length) === companyName) {
          const endIndex = startIndex + companyName.length
          if(endIndex >= sentence.length || /[\s.,!]/.test(sentence[endIndex])) {
            matches.push(companyName)
          }
        }
      }
    }
    sentence = sentence.replace(token, "")
  }
  return matches
}
export const parseEmailSubject = async (email: EmailRecord) => {
  const subject = getEmailSubject(email)
  return await detectInSentence(subject)
}
export const getCompanyContent = async (email: EmailRecord) => {
  let plainText: string = normalizeContent(getPlainContent(email))
  plainText = plainText.replace(/(?![*#0-9]+)[\p{Emoji}\p{Emoji_Modifier}\p{Emoji_Component}\p{Emoji_Modifier_Base}\p{Emoji_Presentation}]/gu, '')
  let sentences = getSentences(plainText)
  let candidates = []
  for(let sentence of sentences) {
    const newCandidates = await detectInSentence(sentence)
    candidates.push(...newCandidates)
  }
  if(candidates.length === 0) {
    candidates.push(...await parseEmailSubject(email))
  }
  if(candidates.length === 0) {
    try {
      sentences = sentences.slice(0, 5).concat(sentences.slice(sentences.length - 5))
      sentences.push(getEmailSubject(email))
      const senderName = getEmailSenderName(email)
      if(senderName) {
        sentences.push(senderName)
      }

      for(let sentence of sentences) {
        const response: any = await axios.post("http://localhost:7001/email/parse/company", {
          sentence: sentence
        })
        const newCandidates = response.data.company
        if(newCandidates) {
          console.log("AI: ", sentence, newCandidates)
          candidates.push(...newCandidates)
        }
      }
    } catch(err) {
    }
  }
  // if(candidates.length > 0) {
  //   sentences.push(getEmailSubject(email))
  //   const senderName = getEmailSenderName(email)
  //   if(senderName) {
  //     sentences.push(senderName)
  //     // console.log(senderName)
  //   }
  //   for(let sentence of sentences) {
  //     let annotations: any = []
  //     let startIndex = sentence.indexOf(candidates[0])
  //     if(startIndex >= 0) {
  //       annotations = [{
  //         label: 1,
  //         start_offset: startIndex,
  //         end_offset: startIndex + candidates[0].length,
  //         user: 1
  //       }]
  //     }
  //     fs.appendFileSync('training_data.json', JSON.stringify({
  //       id: id ++,
  //       text: sentence,
  //       annotations: annotations,
  //       meta: {},
  //       annotation_approver: null
  //     }) + "\r\n");
  //   }
  // }
  console.log(candidates)
  const tc = candidates.reduce((total, current) => {
    total[current] = (total[current] || 0) + 1
    return total
  }, {})
  const entries = Object.entries(tc)
  const maxCount = entries.reduce((max, current: any) => {
    if(max > current[1]) return max
    return current[1]
  }, 0)
  const maxEntry = entries.find(([_, count]) => count === maxCount )
  if(!maxEntry) return null
  return maxEntry[0]
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
    companyUrl: companyUrl ? companyUrl[1] : undefined,
    careerSiteUrl: careerSiteUrl ? careerSiteUrl[1] : undefined
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
export const getLeverAppliedData = async (email: EmailRecord) => {
  const company = await getCompanyContent(email)
  if(company) return { company }
  return null
}







export const isLeverFailed = (email: EmailRecord) => {
  if(email.sender === "no-reply@hire.lever.co") {
    return isFailedContent(email)
  }
  return false
}
export const getLeverFailedData = async (email: EmailRecord) => {
  const company = await getCompanyContent(email)
  if(company) return { company }
  return null
}






export const isGreenhouseApplied = (email: EmailRecord) => {
  if(email.sender === "no-reply@greenhouse.io" || email.sender === "no-reply@us.greenhouse-mail.io") {
    return isAppliedContent(email)
  }
  return false
}
export const getGreenhouseAppliedData = async (email: EmailRecord) => {
  const company = await getCompanyContent(email)
  if(company) return { company }
  return null
}







export const isGreenhouseFailed = (email: EmailRecord) => {
  if(email.sender === "no-reply@greenhouse.io") {
    return isFailedContent(email)
  }
  return false
}
export const getGreenhouseFailedData = async (email: EmailRecord) => {
  const company = await getCompanyContent(email)
  if(company) return { company }
  return null
}






export const isAshbyhqApplied = (email: EmailRecord) => {
  if(email.sender === "no-reply@ashbyhq.com") {
    return isAppliedContent(email)
  }
  return false
}
export const getAshbyhqAppliedData = async (email: EmailRecord) => {
  const company = await getCompanyContent(email)
  if(company) return { company }
  return null
}






export const isAshbyhqFailed = (email: EmailRecord) => {
  if(email.sender === "no-reply@ashbyhq.com") {
    return isFailedContent(email)
  }
  return false
}
export const getAshbyhqFailedData = async (email: EmailRecord) => {
  const company = await getCompanyContent(email)
  if(company) return { company }
  return null
}
