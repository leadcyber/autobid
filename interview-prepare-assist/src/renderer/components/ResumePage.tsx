import * as React from 'react';
import { AppContext } from '../context/AppContext'
import DocViewer, { MSDocRenderer } from "react-doc-viewer";

export default function ResumePage() {
  const { job, pageData } = React.useContext(AppContext)
  const [ docs, setDocs ] = React.useState<any>([])
  React.useEffect(() => {
    setTimeout(() => window.electron.ipcRenderer.sendMessage('getResume', job.id), 1000)
    setDocs([])
  }, [job?.id])
  React.useEffect(() => {
    const removeGetResumeListener = window.electron.ipcRenderer.on('resume', (resumePath: string) => {
      console.log(resumePath)
      if(resumePath == "") {
        console.log(resumePath)
        setDocs([
          { uri: resumePath }, // Local File
        ]);
      } else {
        setDocs([])
      }
    });
    return () => {
      removeGetResumeListener!()
    }
  }, [])

  return (
    <div className="panel-resume">
    </div>
  );
}
