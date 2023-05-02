import * as React from 'react';
import Range from './Range'
import JobFlow from './JobFlow'
import VerticalSizer from './VerticalSizer'
import "./content.css"


export default function Content() {
  return (
    <div className="panel-container">
      <div className="flow-container">
        <JobFlow/>
        <VerticalSizer/>
      </div>
      <Range/>
    </div>
  );
}
