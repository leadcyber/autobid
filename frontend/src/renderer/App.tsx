import { Box, CssBaseline } from "@mui/material";
import React from "react";
import Sidebar from './components/Sidebar'
import JobBoard from './components/JobBoard'
import "./App.css"

export default function App(): JSX.Element {
  return (
    // Setup theme and css baseline for the Material-UI app
    // https://mui.com/customization/theming/
    <div style={{display: "flex"}}>
      <Sidebar/>
      <JobBoard/>
    </div>
  );
}
