import { useCallback, useEffect, useState } from "react";
import { AppProvider } from './context/AppContext'
import path from 'path'

import "./App.css"
import { Job, JobState, JobRow, PageData, RequiredSkill } from '../job.types';
import Chip from '@mui/material/Chip';
import axios from "axios";

export default function App(): JSX.Element {
  const [ currentIndex, setCurrentIndex ] = useState<number>(-1)
  const [ jobIDs, setJobIDs ] = useState<any[]>([])
  const [ requiredSkills, setRequiredSkills ] = useState<any[]>([])
  const [ jd, setJD ] = useState<string>("")
  useEffect(() => {
    window.electron.ipcRenderer.on('initialState', (jobs, current) => {
      setJobIDs(jobs)
      setCurrentIndex(current)
    });
    window.electron.ipcRenderer.on('pageData', async (_jd: string, _requiredSkills: any[]) => {
      setJD(_jd)
      setRequiredSkills(_requiredSkills)
      const response = await axios.post("http://localhost:7001/job/score", { jd: _jd })
      const score = Number(response.data.score)
      console.log(score)
      if(score >= 7.5) {
        window.electron.ipcRenderer.sendMessage('setAnnotation', 1);
        setCurrentIndex(prev => prev + 1)
      } else if(score <= 4.8) {
        window.electron.ipcRenderer.sendMessage('setAnnotation', 0);
        setCurrentIndex(prev => prev + 1)
      } else {
      }
    });
    window.electron.ipcRenderer.sendMessage('getInitialState');
  }, [])
  useEffect(() => {
    const eventHandler = (event: any) => {
      if(event.key === 'y' || event.key === 'n') {
        console.log("next")
        window.electron.ipcRenderer.sendMessage('setAnnotation', event.key === 'y' ? 1 : 0);
        setCurrentIndex(prev => prev === jobIDs.length ? jobIDs.length : prev + 1)
      } else if(event.key === "ArrowLeft") {
        console.log("prev")
        setCurrentIndex(prev => prev > 0 ? prev - 1 : 0 )
      } else if(event.key === "ArrowRight") {
        console.log("blind next")
        setCurrentIndex(prev => prev === jobIDs.length ? jobIDs.length : prev + 1)
      }
    }
    window.addEventListener("keyup", eventHandler)
    return () => window.removeEventListener("keyup", eventHandler)
  }, [jobIDs])

  useEffect(() => {
    if(jobIDs.length === 0)
      return
    window.electron.ipcRenderer.sendMessage('getPageData', { jobId: jobIDs[currentIndex], current: currentIndex });
  }, [ currentIndex, jobIDs ])
  return (
    <div className="content">
      <div className="progress">{ `${currentIndex} / ${jobIDs.length}` }</div>
      <div className="job-description" dangerouslySetInnerHTML={{__html: jd}}></div>
      <hr/>
      <div className="skill-board">
        {requiredSkills.map(({skill, familarity, importance}: RequiredSkill) =>
          <Chip
            key={skill}
            label={`${skill} ${familarity}`}
            size={ importance > 6 ? "medium" : "small" }
            color={
              familarity >= 8 ? "success":
              familarity >= 6 ? "primary":
              familarity >= 4 ? "info":
              familarity >= 2 ? "warning": "error"
            }
            sx={{ marginRight: "3px" }}
          />
        )}
      </div>
    </div>
  );
}
