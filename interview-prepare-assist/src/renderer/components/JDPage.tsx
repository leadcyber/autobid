import * as React from 'react';
import { AppContext } from '../context/AppContext'
import Button from '@mui/material/Button';
import _ from 'lodash';

import DownloadIcon from '@mui/icons-material/Download';
import LaunchIcon from '@mui/icons-material/Launch';
import FolderOpenIcon from '@mui/icons-material/FolderOpen';
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
  const [ qaContent, setQAContent ] = React.useState<string>("")

  React.useEffect(() => {
    const removeGetQAListener = window.electron.ipcRenderer.on('qa', (qa: any) => {
      setQAContent(qa)
    });
    return () => {
      removeGetQAListener!()
    }
  }, [])

  React.useEffect(() => {
    (async() => {
      let text: string = pageData?.description || ""
      try {
        let response: any = await axios.post(`${serviceURL}/jd/mark`, { jd: text })
        text = response.data
      } catch(err) {
        text = "------------------ [ RAW ] ------------------<br/><br/>" + text
      }
      setPageContent(text)
    })();
  }, [pageData])

  React.useEffect(() => {
    window.electron.ipcRenderer.sendMessage('getQA', job.id);
  }, [job])

  const onDownloadJD = React.useCallback(() => {
    if(!job || !pageData) return
    window.electron.ipcRenderer.sendMessage('downloadJD', { jd: pageData.description });
  }, [job, pageData])


  return (
    <div className="panel-description">
      <div className="job-description-wrapper">
        <div className="job-description" dangerouslySetInnerHTML={{__html: pageContent}}></div>
        <br/>
        <br/>
        <hr/>
        <div className="job-qa">
          {Object.entries(qaContent).map(([ question, answer ]) => (
            <>
              <hr/>
              <div key={question} className="qa-row">
                <div className="question">{question}</div>
                <div className="answer">{answer}</div>
              </div>
            </>
          ))
          }
        </div>
      </div>
      <hr/>
      <div className="jd-control-board">
        <Button
          size="small"
          color="primary"
          variant="contained"
          endIcon={<DownloadIcon/>}
          onClick={onDownloadJD}
        >
          JD Html
        </Button>
      </div>
    </div>
  );
}
