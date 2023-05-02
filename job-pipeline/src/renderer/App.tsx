import { useCallback, useEffect, useState } from "react";
import Sidebar from './components/Sidebar'
import Content from './components/Content'
import { AppProvider } from './context/AppContext'

import "./App.css"
import { Job, JobState, JobRow, PageData, RequiredSkill } from '../job.types';

export default function App(): JSX.Element {
  const [ selectedJob, setSelectedJob ] = useState<Job | null>()
  const [ requiredSkills, setRequiredSkills ] = useState<any[] | null>([])
  const [ pageData, setPageData ] = useState<PageData | null>()
  const handleSelectJob = useCallback((job: Job) => {
    setSelectedJob(job)
    window.electron.ipcRenderer.sendMessage('getPageData', job);
  }, [])
  useEffect(() => {
    const removePageDataListener = window.electron.ipcRenderer.on('pageData', (_pageData: PageData, _companyUrl: string, _requiredSkills: any[]) => {
      setPageData({ ... _pageData, companyUrl: _companyUrl } as any)
      setRequiredSkills(_requiredSkills)
    });
    return () => {
      removePageDataListener!()
    }
  }, [])
  return (
    // Setup theme and css baseline for the Material-UI app
    // https://mui.com/customization/theming/
    <div style={{display: "flex"}}>
      <AppProvider value={{job: selectedJob, pageData, requiredSkills}}>
        <Sidebar onSelectJob={handleSelectJob} onQueryChange={handleQueryChange}/>
        <Content/>
      </AppProvider>
    </div>
  );
}
