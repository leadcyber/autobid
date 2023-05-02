import * as React from 'react';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemText from '@mui/material/ListItemText';
import Divider from '@mui/material/Divider';
import TextareaAutosize from '@mui/base/TextareaAutosize';
import Input from '@mui/material/Input'
import LoadingButton from '@mui/lab/LoadingButton';

import CheckIcon from '@mui/icons-material/Check';

import { Job, JobState, JobRow, PageData, RequiredSkill } from '../../job.types';
import "./sidebar.css"

export default ({ onSelectJob }: any) => {

  const [ jobs, setJobs ] = React.useState<Job[]>([])
  const [ rawQuery, setRawQuery ] = React.useState<string>("")
  const [ loading, setLoading ] = React.useState<boolean>(false)
  React.useEffect(() => {
    const removeJobListListener = window.electron.ipcRenderer.on('jobList', (_jobs: Job[]) => {
      setLoading(false)
      setJobs(_jobs);
    });
    setLoading(true)
    window.electron.ipcRenderer.sendMessage('query', {});
    return () => {
      removeJobListListener!()
    }
  }, [])

  const handleSearch = React.useCallback((evt: any) => {
    evt.preventDefault()
    const formData = new FormData(evt.target)
    let _id: any = formData.get("id")?.toString()
    let position: any = formData.get("position")?.toString()
    let company: any = formData.get("company")?.toString()
    let content: any = formData.get("content")?.toString()
    let recruiter: any = formData.get("recruiter")?.toString()

    const rawQuery: any = {
      _id,
      position,
      company,
      content,
      recruiter
    }
    for(let key in rawQuery) {
      if(rawQuery[key] === null)
        delete rawQuery[key]
    }

    _id = _id.length > 0 ? _id : null
    position = position.length > 0 ? new RegExp(position, "ig") : null
    company = company.length > 0 ? new RegExp(company, "ig") : null
    content = content.length > 0 ? new RegExp(content, "ig") : null
    recruiter = recruiter.length > 0 ? new RegExp(recruiter, "ig") : null

    const query: any = {
      _id,
      position,
      company,
      "pageData.description": content,
      "pageData.recruiter.name": recruiter,
    }
    for(let key in query) {
      if(query[key] === null)
        delete query[key]
    }
    setLoading(true)
    window.electron.ipcRenderer.sendMessage('query', query);
    setRawQuery(JSON.stringify(rawQuery, null, 3))
  }, [])
  const handleJobSelect = React.useCallback((job: Job) => {
    onSelectJob(job)
  }, [])
  return (
    <Box className="search-wrapper" sx={{ bgcolor: 'background.paper' }}>
      <nav aria-label="main mailbox folders">
        <form onSubmit={handleSearch}>
          <List>
            <ListItem>
              <ListItemText primary="JobID" />
              <Input name="id"/>
            </ListItem>
            <ListItem>
              <ListItemText primary="Position" />
              <Input name="position"/>
            </ListItem>
            <ListItem>
              <ListItemText primary="Company" />
              <Input name="company"/>
            </ListItem>
            <ListItem>
              <ListItemText primary="Content" />
              <Input name="content"/>
            </ListItem>
            <ListItem>
              <ListItemText primary="Recruiter" />
              <Input name="recruiter"/>
            </ListItem>
            <ListItem>
              <ListItemText primary="Raw Query" />
              <br/>
              <TextareaAutosize
                aria-label="raw-query"
                minRows={3}
                placeholder="Raw Query"
                style={{ width: "100%" }}
                value={rawQuery}
              />
            </ListItem>
            <ListItem>
            <LoadingButton
              color="info"
              variant="contained"
              endIcon={<CheckIcon/>}
              loading={loading}
              loadingPosition="end"
              type="submit"
            >
              Search
            </LoadingButton>
            </ListItem>
          </List>
        </form>
      </nav>
      <Divider />
      <nav className="found-job-list">
        <List>
          {jobs.map((job) => (
            <ListItem disablePadding key={job.id}>
              <ListItemButton onClick={() => handleJobSelect(job)}>
                <ListItemText primary={job.position} secondary={job.company} sx={{ fontSize: "5px", color: job.alreadyApplied ? "#000" : "#aaa" }}/>
              </ListItemButton>
            </ListItem>
          ))}
        </List>
      </nav>
    </Box>
  );
}
