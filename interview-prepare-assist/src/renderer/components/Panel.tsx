import * as React from 'react';
import SplitPane, { Pane } from 'react-split-pane'

import "./panel.css"
import JobMeta from './JobMeta'
import JDPage from './JDPage'
import ResumePage from './ResumePage'


export default function Panel() {

  return (
    <SplitPane split="vertical" defaultSize="350px" minSize={50}>
      <JobMeta/>
      <SplitPane split="vertical" defaultSize="50%">
        <JDPage/>
        <ResumePage/>
      </SplitPane>
    </SplitPane>
  );
}
