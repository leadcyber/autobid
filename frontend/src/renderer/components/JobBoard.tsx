import * as React from 'react';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Snackbar from '@mui/material/Snackbar';
import Alert from '@mui/material/Alert';
import { DataGrid, GridRowsProp, GridSelectionModel, GridCellParams } from '@mui/x-data-grid';
import { Job, JobState, JobRow, PageData, RequiredSkill, LocationKeyword } from '../../job.types';
import _ from 'lodash';

import DeleteIcon from '@mui/icons-material/Delete';
import ClearIcon from '@mui/icons-material/Clear';
import CheckIcon from '@mui/icons-material/Check';
import LaunchIcon from '@mui/icons-material/Launch';
import CopyAllIcon from '@mui/icons-material/CopyAll';
import PlaylistAddCheckIcon from '@mui/icons-material/PlaylistAddCheck';
import LinearProgress from '@mui/material/LinearProgress';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import DragHandleIcon from '@mui/icons-material/DragHandle';
import RefreshIcon from '@mui/icons-material/Refresh';
import DownloadIcon from '@mui/icons-material/Download';
import Drawer from '@mui/material/Drawer';

import Chip from '@mui/material/Chip';
import Fab from '@mui/material/Fab';

import moment from 'moment'
import axios from 'axios'

import "./JobBoard.css"
import { CurrencyYenTwoTone } from '@mui/icons-material';
import { CircularProgress } from '@mui/material';

export const serviceURL = "http://localhost:7000"
export const pyServiceURL = "http://localhost:7001"

const columns = [
  { field: 'id', headerName: 'ID', hide: true },
  { field: 'category', headerName: 'Category', width: 140 },
  { field: 'position', headerName: 'Position', width: 320 },
  { field: 'company', headerName: 'Company', width: 150 },
  { field: 'salary', headerName: 'Salary', width: 140 },
  { field: 'postedAgo', headerName: 'Posted', width: 100, },
  { field: 'postedDate', headerName: 'Post Date', width: 90 },
  { field: 'scannedDate', headerName: 'Scan Date', width: 90 },
  { field: 'postCount', headerName: 'Posting Acitivity', width: 90 },
  { field: 'jobUrl', headerName: 'URL', width: 100, hide: true },
  { field: 'state', headerName: 'state', width: 100, hide: true },
];

export default function CheckboxSelectionGrid() {
  const [selectionModel, setSelectionModel] =
    React.useState<GridSelectionModel>([]);
  const previousSelection = React.useRef<string[]>([]);
  const [ rows, setRows ] = React.useState<JobRow[]>([]);
  const [ isSnackbarOpen, setSnackbarOpen ] = React.useState<boolean>(false);
  const [ drawOpen, setDrawOpen ] = React.useState<boolean>(false);
  const [ markedJD, setMarkedJD ] = React.useState<string>("");
  const [ selectedJob, setSelectedJob ] = React.useState<Job | null>(null);
  const [ pageData, setPageData ] = React.useState<PageData | null>(null)
  const [ pageDataLoading, setPageDataLoading ] = React.useState<boolean>(false)
  const [ autofillSupported, setAutofillSupport ] = React.useState<boolean>(false)
  const [ isAlreadyApplied, setAlreadyApplied ] = React.useState<boolean>(false)
  const [ relatedCount, setRelatedCount ] = React.useState<any>(null)
  const [ requiredSkills, setRequiredSkills ] = React.useState<any[]>([])
  const [ familarity, setFamilarity ] = React.useState<any[]>([])
  const [ locationKeywords, setLocationKeywords ] = React.useState<any[]>([])

  React.useEffect(() => {
    const removeUpdateListener = window.electron.ipcRenderer.on('update', (newJobs: Job[]) => {
      const jobs = newJobs.map(job => {
        let postedDate = new Date(job.scannedDate).getTime()
        if(job.postedAgo == "Just now") {}
        else if(job.postedAgo.includes("hour")) {
          postedDate -= parseInt(job.postedAgo) * 1000 * 60 * 60
        } else if(job.postedAgo.includes("min")) {
          postedDate -= parseInt(job.postedAgo) * 1000 * 60
        }
        const duration = moment.duration(Date.now() - postedDate)
        return { ...job, postedAgo: `${duration.humanize()} ago`, postedDate, scannedDate: new Date(job.scannedDate).getTime() }
      })
      setRows(jobs);
      const selection = jobs.filter(job => job.state == JobState.COPIED).map(job => job.id!)
      setSelectionModel(selection);
      previousSelection.current = selection
    });
    const removeCopiedListener = window.electron.ipcRenderer.on('copied', (job: Job) => {
      setSnackbarOpen(true);
    });

    const removePageDBDataListener = window.electron.ipcRenderer.on('pageDBData', (relatedCount: any) => {
      setRelatedCount(relatedCount)
    });
    const removePageOnlineDataListener =
      window.electron.ipcRenderer.on('pageOnlineData', (
        _pageData: PageData,
        isSupported: boolean,
        isApplied: boolean,
        _requiredSkills: Array<any>,
        _locationKeywords: Array<any>
      ) => {
      setPageDataLoading(false)
      setPageData(_pageData);
      setAlreadyApplied(isApplied)
      setAutofillSupport(isSupported)
      setRequiredSkills(_requiredSkills);
      setLocationKeywords(_locationKeywords);

      const jd = _pageData?.description || "";

      (async() => {
        let text: string = jd
        try {
          let response: any = await axios.post(`${serviceURL}/skill/highlights`, { jd: text })
          let intervals: any[] = response.data
          intervals.sort((a, b) => b[0] - a[0])
          for(let interval of intervals) {
            text = `${text.slice(0, interval[0])}<span class='highlight-skill'>${text.slice(interval[0], interval[1])}</span>${text.slice(interval[1])}`
          }

          response = await axios.post(`${serviceURL}/location/highlights/tagged`, { jd: text })
          intervals = response.data
          intervals.sort((a, b) => b[0] - a[0])
          for(let interval of intervals) {
            text = `${text.slice(0, interval[0])}<span class='position-${interval[2].toLowerCase()}'>${text.slice(interval[0], interval[1])}</span>${text.slice(interval[1])}`
          }

        } catch(err) {
          text = "------------------ [ RAW ] ------------------<br/><br/>" + text
        }
        setMarkedJD(text)
      })();

      (async() => {
        try {
          let response: any = await axios.post(`${pyServiceURL}/job/rate`, { jd })
          setFamilarity(response.data.rate)
        } catch(err) {

        }
      })();
    });
    return () => {
      removeUpdateListener!()
      removeCopiedListener!()
      removePageDBDataListener!()
      removePageOnlineDataListener!()
    }
  }, []);

  const handleSnackbarClose = React.useCallback((event: any, reason?: string) => {
    if (reason === 'clickaway') {
      return;
    }
    setSnackbarOpen(false);
  }, []);
  const handleSelectionModelChange = React.useCallback(
    (newSelectionModel: any) => {
      let difference = _.difference(
        newSelectionModel,
        previousSelection.current
      );
      if (difference.length > 0) {
        const selectedRow = rows.find((row: JobRow) => row.id == difference[0]);
        setSelectionModel(newSelectionModel);
        previousSelection.current = previousSelection.current.concat(difference)
      }
    },
    [rows]
  );
  const handleCellClick = React.useCallback((params: GridCellParams) => {
    window.electron.ipcRenderer.sendMessage('copy', params.row.jobUrl);
    window.electron.ipcRenderer.sendMessage('markCopy', params.row);
    window.electron.ipcRenderer.sendMessage('getPageData', params.row);
    setRelatedCount(null)
    setPageDataLoading(true)
    setSelectedJob(params.row);
  }, [rows])

  const deleteFromDB = React.useCallback(() => {
    window.electron.ipcRenderer.sendMessage('deleteFromDB', selectedJob?.id);
  }, [selectedJob])
  const removeSelected = React.useCallback(() => {
    window.electron.ipcRenderer.sendMessage('deleteCopied');
  }, []);
  const clearAll = React.useCallback(() => {
    window.electron.ipcRenderer.sendMessage('deleteAll');
  }, []);

  const onRefresh = React.useCallback(() => {
    if(selectedJob == null) return
    window.electron.ipcRenderer.sendMessage('fetchPageData', selectedJob);
    setPageDataLoading(true)
  }, [selectedJob])
  const onEasyApply = React.useCallback((requestConnect: boolean) => {
    window.electron.ipcRenderer.sendMessage('applyExternal', { jobId: selectedJob?.id, applyUrl: pageData?.applyUrl, requestConnect});
    window.electron.ipcRenderer.sendMessage('setAppliedFlag', selectedJob?.id);
    setAlreadyApplied(true)
  }, [pageData, selectedJob])
  const onApplyExternal = React.useCallback(() => {
    window.electron.ipcRenderer.sendMessage('applyExternal', { jobId: selectedJob?.id, applyUrl: pageData?.applyUrl, requestConnect: false});
    window.electron.ipcRenderer.sendMessage('setAppliedFlag', selectedJob?.id);
    setAlreadyApplied(true)
  }, [pageData, selectedJob])
  const onCopyExternal = React.useCallback(() => {
    window.electron.ipcRenderer.sendMessage('copy', pageData?.applyUrl);
    window.electron.ipcRenderer.sendMessage('setAppliedFlag', selectedJob?.id);
    setAlreadyApplied(true)
  }, [pageData, selectedJob])

  const onGenerateResume = React.useCallback(() => {
    window.electron.ipcRenderer.sendMessage('generateResume', {
      jobId: selectedJob?.id,
      position: selectedJob?.position,
      description: pageData?.description
    });
  }, [selectedJob, pageData])

  return (
    <>
      <div style={{ width: '100%' }}>
        <div style={{ height: `calc(100vh - ${!!selectedJob ? 250 : 100}px)` }} className="board-wrapper">
          <DataGrid
            columns={columns}
            rows={rows}
            initialState={{
              sorting: {
                sortModel: [{ field: 'postedDate', sort: 'desc' }],
              },
            }}
            checkboxSelection={true}
            onCellClick={handleCellClick}
            onSelectionModelChange={handleSelectionModelChange}
            selectionModel={selectionModel}
            sx={{ fontSize: '12px' }}
            getRowClassName={(params) =>
              params.row.postCount > 10 ? 'job-many' : 'job-few'
            }
          />
          <Box
            sx={{ '& button': { m: 1 }, textAlign: 'right', marginTop: '12px', marginBottom: "12px" }}
          >
            {relatedCount && (
              <>
                <Chip
                  label={`${relatedCount.exactMatch}/${relatedCount.companyJobs}`}
                  color={relatedCount.exactMatch <= 5 && relatedCount.companyJobs <= 10 ? "success" : "error"}
                  icon={<AccountBalanceIcon fontSize="small"/>} />
                  &nbsp;
                <Chip
                  label={`${relatedCount.recentExactMatch}/${relatedCount.recentCompanyJobs}`}
                  color={relatedCount.recentExactMatch <= 3 && relatedCount.recentCompanyJobs <= 4 ? "success" : "error"}
                  icon={<DragHandleIcon fontSize="small"/>}
                  />
                  &nbsp;
                  &nbsp;
              </>
            )}
            {pageDataLoading ? (
                <div style={{ display: "inline-block", width: "100px" }}>
                  <LinearProgress/>
                </div>
              ) : pageData ? (
                <>
                  <Button
                    color="info"
                    variant="contained"
                    endIcon={<DownloadIcon/>}
                    onClick={onGenerateResume}
                    size="small"
                  >
                    Resume
                  </Button>
                  {
                    pageData.applyMode == "EasyApply" ? (
                      <>
                        <Button
                          color={isAlreadyApplied ? "success" : "primary"}
                          variant="contained"
                          startIcon={isAlreadyApplied && <PlaylistAddCheckIcon/>}
                          endIcon={<LaunchIcon />}
                          onClick={() => onEasyApply(false)}
                          size="small"
                        >
                          Easy Apply
                        </Button>
                        <Button
                          color={pageData.recruiter ? (isAlreadyApplied ? "success" : "primary") : "inherit"}
                          variant="contained"
                          startIcon={isAlreadyApplied && <PlaylistAddCheckIcon/>}
                          endIcon={<LaunchIcon />}
                          onClick={() => onEasyApply(true)}
                          size="small"
                        >
                          Easy Apply & Connect
                        </Button>
                      </>
                    ) : pageData.applyMode == "Apply" ? (
                      <>
                        {
                          autofillSupported ? (
                            <Button
                              color={isAlreadyApplied ? "success" : "primary"}
                              variant="contained"
                              startIcon={isAlreadyApplied && <PlaylistAddCheckIcon/>}
                              endIcon={<LaunchIcon />}
                              onClick={onApplyExternal}
                              size="small"
                            >
                              Apply
                            </Button>
                          ) : (
                            <Button
                              color={isAlreadyApplied ? "success" : "primary"}
                              variant="contained"
                              startIcon={isAlreadyApplied && <PlaylistAddCheckIcon/>}
                              endIcon={<CopyAllIcon />}
                              onClick={onCopyExternal}
                              size="small"
                            >
                              Copy
                            </Button>
                          )
                        }
                      </>
                    ) : pageData.applyMode == "Closed" ? (
                      <span style={{ color: "red" }}>No longer accepting applications.</span>
                    ) : (
                      <span style={{ color: "grey" }}>Error occured during the JD load</span>
                    )
                  }
                </>
              ) : null
            }
            &nbsp;&nbsp;&nbsp;
            &nbsp;&nbsp;&nbsp;
            {selectedJob && (
              <Button
                variant="contained"
                endIcon={<DeleteIcon />}
                color="error"
                onClick={deleteFromDB}
                size="small"
              >
                Delete from DB
              </Button>
            )}
            <Button
              variant="contained"
              color="secondary"
              endIcon={<CheckIcon />}
              onClick={removeSelected}
              size="small"
            >
              Remove selected
            </Button>
            <Button
              variant="contained"
              endIcon={<ClearIcon />}
              color="warning"
              onClick={clearAll}
              size="small"
            >
              Clear all
            </Button>

            <Fab size="small" color="primary" onClick={onRefresh}>
              <RefreshIcon />
            </Fab>
          </Box>
          <Box
            sx={{ '& button': { m: 1 }, marginTop: '0px', display: "flex" }}
          >
            {pageDataLoading ? (
                <div className="circular-progress-wrapper">
                  <CircularProgress/>
                </div>
            ) : (pageData && !pageDataLoading &&
              <>
                <div className="job-info">
                  <span className="job-url">
                    <a href="#">{pageData.applyUrl.substring(0, 80) + " ..."}</a>
                    <p style={{ marginTop: 5, marginBottom: 5 }}>{selectedJob?.id}</p>
                  </span>
                  <div className="requirement-field">
                    <div className="requirement-chip">
                      {requiredSkills.map(({skill, familarity, importance}: RequiredSkill) =>
                        <Chip
                          key={skill}
                          label={`${skill} ${familarity}`}
                          size={ importance > 6 ? "medium" : "small" }
                          color={
                            familarity >= 8 ? "success":
                            familarity >= 6 ? "primary":
                            familarity >= 4 ? "info":
                            familarity >= 2 ? "warning": "error"
                          }
                          sx={{ marginRight: "3px" }}
                        />
                      )}
                    </div>
                    <div className="requirement-familarity">
                      <h2 className="familarity-good">{familarity[1] * 100 | 0}</h2>
                      <h2 className="familarity-bad">{familarity[0] * 100 | 0}</h2>
                      <p>%</p>
                      <Button
                        variant="contained"
                        size="medium"
                        sx={{ marginTop: "10px" }}
                        onClick={() => setDrawOpen(true)}
                      >J.D.</Button>
                    </div>
                  </div>
                </div>
                {pageData.recruiter &&
                  <div className="recruiter">
                    <div className="recruiter-image">
                      <img src={pageData.recruiter?.image} width="80px"/>
                    </div>
                    <div className="recruiter-info">
                      <span className="recruiter-name"><b>{pageData.recruiter?.name}</b></span><br/>
                      <span>{pageData.recruiter?.title}</span>
                    </div>
                  </div>
                }
                {pageData.criterias &&
                  <div className="criteria">
                    <p>
                      {locationKeywords.map(({keyword, count, familarity}: LocationKeyword) =>
                        <Chip
                          key={keyword}
                          label={`${keyword} ${count}`}
                          size="small"
                          color={
                            familarity >= 8 ? "success":
                            familarity < 5 ? "error": "warning"
                          }
                          sx={{ marginRight: "3px" }}
                        />
                      )}
                    </p>
                    {
                      Object.entries(pageData.criterias).map(([cType, cValue]) =>
                        <p key={cType}>
                          {cType}: <b>{cValue}</b>
                        </p>
                      )
                    }
                  </div>
                }
              </>
            )}
          </Box>
        </div>
      </div>
      <Drawer
        anchor="right"
        open={drawOpen}
        onClose={() => setDrawOpen(false)}
      >
        <div dangerouslySetInnerHTML={{ __html: markedJD }} style={{ width: "800px", padding: "60px" }}>
        </div>
      </Drawer>
      <Snackbar
        open={isSnackbarOpen}
        autoHideDuration={6000}
        onClose={handleSnackbarClose}
        key={selectedJob?.id}
        anchorOrigin={{ vertical: "top", horizontal: "center" }}
      >
        <Alert
          onClose={handleSnackbarClose}
          severity="info"
          sx={{ width: '100%' }}
        >
          "{selectedJob?.position}" URL copied!
        </Alert>
      </Snackbar>
    </>
  );
}
