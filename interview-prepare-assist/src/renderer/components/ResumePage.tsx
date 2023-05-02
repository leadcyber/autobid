import * as React from 'react';
import { AppContext } from '../context/AppContext'
import DocViewer, { MSDocRenderer } from "react-doc-viewer";
import axios from 'axios'

import DownloadIcon from '@mui/icons-material/Download';
import LaunchIcon from '@mui/icons-material/Launch';
import FolderOpenIcon from '@mui/icons-material/FolderOpen';
import Button from '@mui/material/Button';

import './resumepage.css'

const PY_SERVICE_URL = "http://localhost:7001"
const sentenceCountPerCompany = [5, 4, 4, 4]

export default function ResumePage() {
  const { job, pageData } = React.useContext(AppContext)
  const [ metadata, setMetadata ] = React.useState<any>(null)
  const [ skillMatrix, setSkillMatrix ] = React.useState<any[]>([])
  const [ sentences, setSentences ] = React.useState<any[]>([])
  React.useEffect(() => {
    const position = job.position;
    const jd = pageData?.description || "";
    (async () => {
      try {
        const response = await axios.post(`${PY_SERVICE_URL}/resume/generate/metadata`, { position, jd })
        setMetadata(response.data)
      } catch(err) {
        console.log("PyService not reachable.")
        setMetadata(null)
      }
    })();

    (async () => {
      try {
        const response = await axios.post(`${PY_SERVICE_URL}/resume/generate/skillmatrix/detail`, { position, jd })
        setSkillMatrix(response.data)
      } catch(err) {
        console.log("PyService not reachable.")
        setSkillMatrix([])
      }
    })();

    (async () => {
      try {
        const response = await axios.post(`${PY_SERVICE_URL}/resume/generate/sentences/detail`, { position, jd })
        setSentences(response.data)
      } catch(err) {
        console.log("PyService not reachable.")
        setSentences([])
      }
    })();
  }, [ pageData ])

  const dividerPos = sentenceCountPerCompany.reduce((total: number[], current: number, index: number) => {
    if(index == 0) total.push(current)
    else total.push(current + total[total.length - 1])
    return total
  }, [])

  const onOpenResume = React.useCallback(() => {
    window.electron.ipcRenderer.sendMessage('openResume', job.id);
  }, [job])
  const onOpenResumeFolder = React.useCallback(() => {
    window.electron.ipcRenderer.sendMessage('openResumeFolder', job.id);
  }, [job])
  const onGeneratePdfResume = React.useCallback(() => {
    if(!job || !pageData) return
    window.electron.ipcRenderer.sendMessage('generatePdfResume', { jobId: job.id, position: job.position, jd: pageData.description });
  }, [job, pageData])
  const onGenerateDocResume = React.useCallback(() => {
    if(!job || !pageData) return
    window.electron.ipcRenderer.sendMessage('generateDocResume', { jobId: job.id, position: job.position, jd: pageData.description });
  }, [job, pageData])

  return (
    <div className="panel-resume">
      <div className="resume-wrapper">
        <div className="resume-metadata">
          {metadata &&
            <>
              <h3>{metadata.headline}</h3>
              <p className="resume-summary">{metadata.summary}</p>
            </>
          }
        </div>
        <hr/>
        <div className="skill-section-wrapper">
          {skillMatrix.map(section => (
            <div className="skill-section" key={ section.header.label }>
              <div className="skill-section-header">{ section.header.label } - { section.header.score }</div>
              <div className="skill-section-content">{ section.content.skills.join(" • ") }</div>
            </div>
          ))
          }
        </div>
        <hr/>
        <div className="resume-sentence-wrapper">
          {sentences.map((sentence, index) => (
            <>
              { dividerPos.includes(index) && <hr/> }
              <div key={sentence.content} className="resume-sentence">
                <p className="resume-sentence-content">{sentence.content}</p>
                {sentence.metadata &&
                  <div className="resume-sentence-metadata">
                    <p className="resume-sentence-score">
                      {`${sentence.metadata.similarity.toFixed(3)} = ${sentence.metadata.vector_similarity.toFixed(3)} * ${sentence.metadata.sentence_quality}`}
                    </p>
                    <p className="resume-sentence-relation">
                      {`${sentence.metadata.among.join(" ")}  <=>  ${sentence.metadata.relations.join(" ")}`}
                    </p>
                  </div>
                }
              </div>
            </>
          ))}
        </div>
      </div>
      <div className="resume-board">
        <Button
          size="small"
          color="info"
          variant="contained"
          endIcon={<LaunchIcon/>}
          onClick={onOpenResume}
        >
          Open
        </Button>
        &nbsp;
        <Button
          size="small"
          color="info"
          variant="contained"
          endIcon={<FolderOpenIcon/>}
          onClick={onOpenResumeFolder}
        >
          Open Folder
        </Button>
        &nbsp;
        <Button
          size="small"
          color="primary"
          variant="contained"
          endIcon={<DownloadIcon/>}
          onClick={onGeneratePdfResume}
        >
          Gen. PDF
        </Button>
        &nbsp;
        <Button
          size="small"
          color="primary"
          variant="contained"
          endIcon={<DownloadIcon/>}
          onClick={onGenerateDocResume}
        >
          Gen. DOC
        </Button>
      </div>
    </div>
  );
}
