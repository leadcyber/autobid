import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import AutoBidButton from './AutoBidButton'
import SkipOnErrorButton from './SkipOnErrorButton'
import Button from '@mui/material/Button';
import RedoIcon from '@mui/icons-material/Redo';
import CancelIcon from '@mui/icons-material/Cancel';
import Divider from '@mui/material/Divider';
import Box from '@mui/material/Box';

import { useState, useEffect, useCallback } from 'react';
import { BidState } from '../../job.types';
import ConnectButton from './ConnectButton'

export default () => {
  const [queueState, setQueueState] = useState<any[]>([]);
  const [bidState, setBidState] = useState<any[]>([]);

  useEffect(() => {
    // calling IPC exposed from preload script
    window.electron.ipcRenderer.on('queueState', (state: any[]) => {
      setQueueState(state)
    });
    window.electron.ipcRenderer.on('bidState', (state: any[]) => {
      console.log(state)
      setBidState(state)
    });
    window.electron.ipcRenderer.sendMessage('getQueueState');
    window.electron.ipcRenderer.sendMessage('getBidState');
  }, []);

  const onSkip = useCallback((jobId: string) => {
    window.electron.ipcRenderer.sendMessage('skipTask', jobId);
  }, [])

  return (
    <>
      <List>
        <ListItem disablePadding>
          <AutoBidButton/>
        </ListItem>
        <ListItem disablePadding>
          <ConnectButton/>
        </ListItem>
        <ListItem disablePadding>
          <SkipOnErrorButton/>
        </ListItem>
      </List>
      <Divider />
      <List>
          {bidState.length > 0 ?
          bidState.map((session, index) =>
            session.job ?
                <ListItem disablePadding sx={{ paddingLeft: "15px" }} key={index}>
                  <ListItemText primary={`Task[${index}] ${session.job.company}`} sx={{ color: "#000" }}/>
                  <Button
                    color="error"
                    variant="text"
                    startIcon={<CancelIcon fontSize="small"/>}
                    size="small"
                    onClick={() => onSkip(session.job.id)}
                  ></Button>
                </ListItem>
              :
                <ListItem disablePadding sx={{ paddingLeft: "15px" }} key={index}>
                  <ListItemText primary={`Task[${index}] ---`} sx={{ color: "#666" }}/>
                </ListItem>
          ) :
          <ListItemText secondary="No task runner available" sx={{ paddingLeft: "15px" }}/>
          }
      </List>
      <Divider />
      <Box sx={{ height: "calc(100vh - 500px)", overflowY: "scroll" }}>
        <List>
            {queueState.length > 0 ?
            queueState.map((job, index) =>
              <ListItem disablePadding sx={{ paddingLeft: "15px" }} key={job.id}>
                <ListItemText primary={`Task[${index}] ${job.company}`} sx={{ color: "#000" }}/>
                <Button
                  color="error"
                  variant="text"
                  startIcon={<CancelIcon fontSize="small"/>}
                  size="small"
                  onClick={() => onSkip(job.id)}
                ></Button>
              </ListItem>
            ) :
            <ListItemText secondary="No task runner available" sx={{ paddingLeft: "15px" }}/>
            }
        </List>
      </Box>
    </>
  );
};
