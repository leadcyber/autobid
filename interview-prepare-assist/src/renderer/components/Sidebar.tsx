import * as React from 'react';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import Divider from '@mui/material/Divider';
import InboxIcon from '@mui/icons-material/Inbox';
import HistoryIcon from '@mui/icons-material/History';
import InfoIcon from '@mui/icons-material/Info';
import Input from '@mui/material/Input'

import CheckIcon from '@mui/icons-material/Check';

import { Job, JobState, JobRow, PageData, RequiredSkill } from '../../job.types';
import "./sidebar.css"

export default ({ onSelectJob }: any) => {
  const [ position, setPosition ] = React.useState<string>("")
  const [ company, setCompany ] = React.useState<string>("")
  const [ jobs, setJobs ] = React.useState<Job[]>([])
  React.useEffect(() => {
    const removeJobListListener = window.electron.ipcRenderer.on('jobList', (_jobs: Job[]) => {
      setJobs(_jobs);
    });
    window.electron.ipcRenderer.sendMessage('getJobList', { position, company });
    return () => {
      removeJobListListener!()
    }
  }, [])

  const handleSearch = React.useCallback((evt: any) => {
    evt.preventDefault()
    const formData = new FormData(evt.target)
    window.electron.ipcRenderer.sendMessage('getJobList', {
      position: formData.get("position"),
      company: formData.get("company")
    });
  }, [position, company])
  const handleJobSelect = React.useCallback((job: Job) => {
    onSelectJob(job)
  }, [])
  return (
    <Box sx={{ width: '100%', maxWidth: 250, bgcolor: 'background.paper' }}>
      <nav aria-label="main mailbox folders">
        <form onSubmit={handleSearch}>
          <List>
            <ListItem>
              <ListItemText primary="Pos." />
              <Input name="position"/>
            </ListItem>
            <br/>
            <ListItem>
              <ListItemText primary="Com." />
              <Input name="company"/>
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
