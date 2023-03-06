import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import { useState, useCallback, useEffect } from 'react';
import { styled } from '@mui/material/styles';
import Switch, { SwitchProps } from '@mui/material/Switch';

import { Job } from '../../job.types';
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

export default () => {
  const [showNotification, setShowNotification] = useState(true);
  const handleChange = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      setShowNotification(event.target.checked);
    },
    []
  );

  useEffect(() => {
    // calling IPC exposed from preload script
    window.electron.ipcRenderer.on('jobNotification', (newJobs: Job[]) => {
      let notificationParam: any = {};
      if (newJobs.length == 1) {
        const newJob = newJobs[0];
        notificationParam = {
          title: `${newJob.position} @ ${newJob.company}`,
          body: newJob.postedAgo,
        };
      } else {
        notificationParam = {
          title: 'New Jobs',
          body: `${newJobs.length} found!`,
        };
      }
      if (showNotification) {
        const notification = new Notification(notificationParam.title, {
          body: notificationParam.body,
          icon: NotificationIcon,
        });

        // close the notification after 10 seconds
        setTimeout(() => {
          notification.close();
        }, 10 * 1000);

        // navigate to a URL when clicked
        notification.addEventListener('click', () => {
          window.electron.ipcRenderer.sendMessage(
            'notificationClicked',
            newJobs
          );
        });
      }
    });
  }, []);

  return (
    <>
      <ListItemIcon>
        <IOSSwitch
          sx={{ m: 1 }}
          checked={showNotification}
          onChange={handleChange}
        />
      </ListItemIcon>
      &nbsp;&nbsp;
      <ListItemText primary="Notification" />
    </>
  );
};
