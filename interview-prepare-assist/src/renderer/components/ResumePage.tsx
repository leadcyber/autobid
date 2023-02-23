import * as React from 'react';
import { AppContext } from '../context/AppContext'
import DocViewer, { MSDocRenderer } from "react-doc-viewer";
import axios from 'axios'

import './resumepage.css'

const PY_SERVICE_URL = "http://localhost:7001"

export default function ResumePage() {
  const { job, pageData } = React.useContext(AppContext)
  const [ metadata, setMetadata ] = React.useState<any>(null)
  const [ skillMatrix, setSkillMatrix ] = React.useState<any[]>([])
  const [ sentences, setSentences ] = React.useState<any[]>([])
  React.useEffect(() => {
    const position = job.position;
    const jd = pageData?.description || "";
    console.log(job?.position);
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
        console.log(response.data)
      } catch(err) {
        console.log("PyService not reachable.")
        setSkillMatrix([])
      }
    })();

    (async () => {
      try {
        const response = await axios.post(`${PY_SERVICE_URL}/resume/generate/sentences`, { position, jd })
        setSentences(response.data)
      } catch(err) {
        console.log("PyService not reachable.")
        setSentences([])
      }
    })();
  }, [ job, pageData ])

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
        <div className="resume-sentences">
          {sentences.map(sentence => (
            <p key={sentence}>{sentence}</p>
          ))}
        </div>
      </div>
    </div>
  );
}
