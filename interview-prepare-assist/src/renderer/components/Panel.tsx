import * as React from 'react';

import "./Panel.css"
import JobMeta from './JobMeta'
import JobPage from './JobPage'
import ResumePage from './ResumePage'


export default function Panel() {

  return (
    <div className="page-container">
      <JobMeta/>
      <JobPage/>
      <ResumePage/>
    </div>
  );
}
