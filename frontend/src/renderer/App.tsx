import { Box, CssBaseline } from "@mui/material";
import React, { useState, useCallback } from "react";
import Sidebar from './components/Sidebar'
import JobBoard from './components/JobBoard'
import "./App.css"
import { AppProvider } from './context/AppContext'


export default function App(): JSX.Element {
  const [showJD, setShowJD] = useState<boolean>(true);

  const handleShowJDChange = useCallback((value: boolean) => {
    setShowJD(value)
  }, [])
  return (
    // Setup theme and css baseline for the Material-UI app
    // https://mui.com/customization/theming/
    <div style={{display: "flex"}}>
      <AppProvider value={{ showJD, onShowJDChange: handleShowJDChange }}>
        <Sidebar/>
        <JobBoard/>
      </AppProvider>
    </div>
  );
}
