import * as React from 'react';
import { AppContext } from '../context/AppContext'
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import { DataGrid, GridRowsProp, GridSelectionModel, GridCellParams } from '@mui/x-data-grid';
import { Job, JobState, JobRow, PageData, RequiredSkill } from '../../job.types';
import _ from 'lodash';
import axios from 'axios'

import moment from 'moment'
import "./jobmeta.css"

const SERVICE_URL = "http://localhost:7000"

const getUrlSnippet = (url: string) => {
  const maxLength = 30
  if(url.length < maxLength) return url
  return url.slice(0, maxLength - 3) + "..."
}

export default function JobMeta() {
  const { job, pageData, requiredSkills } = React.useContext(AppContext)
  const [ parsedSalary, setParsedSalary ] = React.useState("N/A")

  let postedDate = new Date(job.scannedDate).getTime()
  if(job.postedAgo == "Just now") {}
  else if(job.postedAgo.includes("hour")) {
    postedDate -= parseInt(job.postedAgo) * 1000 * 60 * 60
  } else if(job.postedAgo.includes("min")) {
    postedDate -= parseInt(job.postedAgo) * 1000 * 60
  }
  // const duration = moment.duration(Date.now() - postedDate)
  const criterias = pageData?.criterias || {}
  const applyUrl = pageData?.applyUrl
  const companyUrl = pageData?.companyUrl || ""
  const recruiter = pageData?.recruiter

  const openExternalLink = React.useCallback((url: string) => {
    window.electron.ipcRenderer.sendMessage('openExternalUrl', url);
  }, [])

  React.useEffect(() => {
    let jd: string = pageData?.description || "";
    (async () => {
      try {
        const response = await axios.post(`${SERVICE_URL}/jd/salary`, { jd })
        let { type, min, max } = response.data
        if(type) {
          if(type === "yr") {
            min = `${Number(min) / 1000}K`
            max = `${Number(max) / 1000}K`
          }
          setParsedSalary(`$${min}/${type} ~ $${max}/${type}`)
        } else {
          setParsedSalary("N/A")
        }
      } catch(err) {
        console.log("JsService not reachable.")
        setParsedSalary("N/A")
      }
    })();
  }, [pageData])

  return (
    <div className="panel-meta">
      <h3 className="meta-position">{job.position}</h3>
      <p className="meta-company">{job.company}</p>
      <p className="meta-company">{job.id}</p>
      <hr/>
      <div className="meta-table">
        <div className="meta-table-label">
          <p>Scan Date:</p>
          <p>Posted Ago:</p>
          <p>Posted Time:</p>
          <p>Apply Time:</p>
          <p>Salary:</p>
          {Object.keys(criterias).map((crt, index) => <p key={index}>{crt}</p> )}
        </div>
        <div className="meta-table-data">
          <p>{moment(job.scannedDate).format("YYYY-MM-DD  hh:mm")}</p>
          <p>{job.postedAgo}</p>
          <p>{moment(postedDate).format("YYYY-MM-DD  hh:mm")}</p>
          <p>{moment(job.copiedDate).format("YYYY-MM-DD  hh:mm")}+5</p>
          <p>{job.salary === "" ? parsedSalary : job.salary}</p>
          {Object.values(criterias).map((crt: any, index: number) => <p key={index}>{crt}</p> )}
        </div>
      </div>
      <hr/>
      <div className="meta-table">
        <div className="meta-table-label">
          <p>Linkedin URL:</p>
          <p>External URL:</p>
          <p>Company Site:</p>
        </div>
        <div className="meta-table-data">
          <p><a onClick={() => openExternalLink(job.jobUrl)} href="#">{getUrlSnippet(job.jobUrl)}</a></p>
          <p><a onClick={() => openExternalLink(applyUrl)} href="#">{applyUrl ? getUrlSnippet(applyUrl) : "N/A"}</a></p>
          <p><a onClick={() => openExternalLink(companyUrl)} href="#">{getUrlSnippet(companyUrl)}</a></p>
        </div>
      </div>
      <hr/>
      {recruiter &&
        <>
          <div className="recruiter">
            <div className="recruiter-image">
              <img src={recruiter?.image} width="80px"/>
            </div>
            <div className="recruiter-info">
              <span className="recruiter-name"><b>{recruiter?.name}</b></span><br/>
              <span>{recruiter?.title}</span>
            </div>
          </div>
          <hr/>
        </>
      }
      <div className="requirement-chip">
        {requiredSkills.map(({skill, familarity, importance}: RequiredSkill) =>
          <div key={skill} className="skill-item">
            <span className="skill-name">{skill}</span>
            <div className="skill-bar">
              <div className="skill-bar-handle" style={{ width: `${importance * 10}%` }}></div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
