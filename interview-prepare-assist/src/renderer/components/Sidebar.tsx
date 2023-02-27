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

import CheckIcon from '@mui/icons-material/Check';

import { Job, JobState, JobRow, PageData, RequiredSkill } from '../../job.types';
import "./sidebar.css"

export default ({ onSelectJob }: any) => {

  const [ jobs, setJobs ] = React.useState<Job[]>([])
  const [ rawQuery, setRawQuery ] = React.useState<string>("")
  React.useEffect(() => {
    const removeJobListListener = window.electron.ipcRenderer.on('jobList', (_jobs: Job[]) => {
      setJobs(_jobs);
    });
    window.electron.ipcRenderer.sendMessage('query', {});
    return () => {
      removeJobListListener!()
    }
  }, [])

  const handleSearch = React.useCallback((evt: any) => {
    evt.preventDefault()
    const formData = new FormData(evt.target)
    const query: any = {
      position: formData.get("position"),
      company: formData.get("company"),
      "pageData.description": formData.get("content"),
      "pageData.recruiter.name": formData.get("recruiter"),
    }
    for(let key in query) {
      if(query[key].length == 0)
        delete query[key]
    }
    window.electron.ipcRenderer.sendMessage('query', query);
    setRawQuery(JSON.stringify(query, null, 3))
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
            <Button
              color="info"
              variant="contained"
              endIcon={<CheckIcon/>}
              type="submit"
            >
              Search
            </Button>
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
