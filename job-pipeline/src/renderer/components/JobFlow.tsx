import Fab from '@mui/material/Fab';
import ZoomInIcon from '@mui/icons-material/ZoomIn';
import ZoomOutIcon from '@mui/icons-material/ZoomOut';

import FlowArea from './FlowArea'
import './JobFlow.css'

export default function JobFlow() {

  return (
    <div className="flow-container">
      <FlowArea/>
      <div className="zoom-pane">
        <Fab size="medium" color="primary">
          <ZoomInIcon fontSize="medium" />
        </Fab>
        <br/>
        <br/>
        <Fab size="medium" color="primary">
          <ZoomOutIcon fontSize="medium" />
        </Fab>
      </div>
    </div>
  );
}
