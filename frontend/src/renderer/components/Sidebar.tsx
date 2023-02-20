import { useState, useEffect } from 'react';
import Box from '@mui/material/Box';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import Divider from '@mui/material/Divider';

import Notification from './Notification'
import AwakeButton from './AwakeButton'
import AutoBidPanel from './AutoBidPanel'
import { ListItemText } from '@mui/material';

export default () => {
  const [fetchStatus, setFetchStatus] = useState<any>({
    status: "lazy",
    data: null
  });

  useEffect(() => {
    // calling IPC exposed from preload script
    window.electron.ipcRenderer.on('fetchStatus', (status, data) => {
      setFetchStatus({
        status,
        data
      })
    });
  }, []);

  return (
    <Box sx={{ width: '100%', maxWidth: 220, bgcolor: 'background.paper' }}>
      <nav aria-label="secondary mailbox folders">
        <List>
          <ListItem disablePadding>
            <Notification/>
          </ListItem>
          <ListItem disablePadding>
            <AwakeButton/>
          </ListItem>
          <ListItem>
            <ListItemText primary={`[${fetchStatus.status}] ${fetchStatus.data?.skip ? fetchStatus.data?.skip : ""}`} sx={{ color: "#000" }}/>
          </ListItem>
        </List>
      </nav>
      <Divider />
      <nav aria-label="secondary mailbox folders">
        <AutoBidPanel/>
      </nav>
    </Box>
  );
}
