import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import { useState, useCallback, useEffect } from 'react';
import { styled } from '@mui/material/styles';
import Switch, { SwitchProps } from '@mui/material/Switch';

import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';

import { Job, FetchMode } from '../../job.types';
import NotificationIcon from '../assets/notification_icon.png';

const IOSSwitch = styled((props: SwitchProps) => (
  <Switch focusVisibleClassName=".Mui-focusVisible" disableRipple {...props} />
))(({ theme }) => ({
  width: 42,
  height: 26,
  padding: 0,
  '& .MuiSwitch-switchBase': {
    padding: 0,
    margin: 2,
    transitionDuration: '300ms',
    '&.Mui-checked': {
      transform: 'translateX(16px)',
      color: '#fff',
      '& + .MuiSwitch-track': {
        backgroundColor: theme.palette.mode === 'dark' ? '#2ECA45' : '#65C466',
        opacity: 1,
        border: 0,
      },
      '&.Mui-disabled + .MuiSwitch-track': {
        opacity: 0.5,
      },
    },
    '&.Mui-focusVisible .MuiSwitch-thumb': {
      color: '#33cf4d',
      border: '6px solid #fff',
    },
    '&.Mui-disabled .MuiSwitch-thumb': {
      color:
        theme.palette.mode === 'light'
          ? theme.palette.grey[100]
          : theme.palette.grey[600],
    },
    '&.Mui-disabled + .MuiSwitch-track': {
      opacity: theme.palette.mode === 'light' ? 0.7 : 0.3,
    },
  },
  '& .MuiSwitch-thumb': {
    boxSizing: 'border-box',
    width: 22,
    height: 22,
  },
  '& .MuiSwitch-track': {
    borderRadius: 26 / 2,
    backgroundColor: theme.palette.mode === 'light' ? '#E9E9EA' : '#39393D',
    opacity: 1,
    transition: theme.transitions.create(['background-color'], {
      duration: 500,
    }),
  },
}));
const FETCH_STATES = [ FetchMode.LAZY, FetchMode.NORMAL, FetchMode.CRAZY ]

export default () => {
  const [fetchMode, setFetchMode] = useState(1);
  const handleChange = useCallback(
    (event: React.SyntheticEvent, newValue: number) => {
      // console.log(newValue)
      window.electron.ipcRenderer.sendMessage('setFetchMode', FETCH_STATES[newValue]);
    },
    []
  );

  useEffect(() => {
    // calling IPC exposed from preload script
    window.electron.ipcRenderer.on('fetchMode', (mode: FetchMode) => {
      setFetchMode(FETCH_STATES.indexOf(mode))
    });
  }, []);

  return (
    <>
      <Tabs value={fetchMode} onChange={handleChange}>
          <Tab label="lazy" sx={{ minWidth: "40px",   padding: "10px 11px" }}/>
          <Tab label="normal" sx={{ minWidth: "40px", padding: "10px 11px" }}/>
          <Tab label="crazy" sx={{ minWidth: "40px",  padding: "10px 11px" }}/>
        </Tabs>
    </>
  );
};
