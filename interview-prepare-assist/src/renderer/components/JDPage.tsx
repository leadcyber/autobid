import * as React from 'react';
import { AppContext } from '../context/AppContext'
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import _ from 'lodash';

import DownloadIcon from '@mui/icons-material/Download';
import './jdpage.css'
import axios from 'axios'

export const serviceURL = "http://localhost:7000"

const getUrlSnippet = (url: string) => {
  const maxLength = 30
  if(url.length < maxLength) return url
  return url.slice(0, maxLength - 3) + "..."
}

export default function JobPage() {
  const { job, pageData, requiredSkills } = React.useContext(AppContext)
  const [ pageContent, setPageContent ] = React.useState<string>("")
  const [ resumePath, setResumePath ] = React.useState<string>("")

  React.useEffect(() => {
    const removeGetResumeListener = window.electron.ipcRenderer.on('resume', (resumePath: string) => {
      setResumePath(resumePath)
    });
    return () => {
      removeGetResumeListener!()
    }
  }, [])

  React.useEffect(() => {
    (async() => {
      let text: string = pageData?.description || ""
      const response: any = await axios.post(`${serviceURL}/skill/highlights`, { jd: text })
      const intervals: any[] = response.data
      intervals.sort((a, b) => b[0] - a[0])
      for(let interval of intervals) {
        text = text.slice(0, interval[0]) + "<mark>" + text.slice(interval[0], interval[1]) + "</mark>" + text.slice(interval[1])
      }
      setPageContent(text)
    })()
  }, [pageData])

  const onOpenResume = React.useCallback(() => {
    window.electron.ipcRenderer.sendMessage('openResume', resumePath);
  }, [job, resumePath])
  const onGenerateResume = React.useCallback(() => {
    if(!job || !pageData) return
    window.electron.ipcRenderer.sendMessage('generateResume', { jobId: job.id, position: job.position, jd: pageData.description });
  }, [job, resumePath])

  return (
    <div className="panel-description">
      <div className="job-description" dangerouslySetInnerHTML={{__html: pageContent}}>
      </div>
      <hr/>
      <div className="resume-board">
        <Button
          color="info"
          variant="contained"
          endIcon={<DownloadIcon/>}
          onClick={onOpenResume}
        >
          Open Resume
        </Button>
        &nbsp;
        <Button
          color="primary"
          variant="contained"
          endIcon={<DownloadIcon/>}
          onClick={onGenerateResume}
        >
          Generate Resume
        </Button>
      </div>
    </div>
  );
}
