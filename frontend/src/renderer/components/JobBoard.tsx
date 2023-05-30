import React, { useState, useCallback, useRef, useContext, useEffect } from 'react';
import { AppContext } from '../context/AppContext'

import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Snackbar from '@mui/material/Snackbar';
import Alert from '@mui/material/Alert';
import { DataGrid, GridRowsProp, GridSelectionModel, GridCellParams } from '@mui/x-data-grid';
import { Job, JobState, JobRow, PageData, RequiredSkill, BlockerKeyword } from '../../job.types';
import _ from 'lodash';

import AddIcon from '@mui/icons-material/Add';
import ThumbUpIcon from '@mui/icons-material/ThumbUp';
import ThumbDownIcon from '@mui/icons-material/ThumbDown';
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
import ViewSidebarIcon from '@mui/icons-material/ViewSidebar';
import Drawer from '@mui/material/Drawer';

import Chip from '@mui/material/Chip';
import Fab from '@mui/material/Fab';

import moment from 'moment'
import axios from 'axios'

import "./JobBoard.css"
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
    useState<GridSelectionModel>([]);
  const previousSelection = useRef<string[]>([]);
  const [ rows, setRows ] = useState<JobRow[]>([]);
  const [ isSnackbarOpen, setSnackbarOpen ] = useState<boolean>(false);
  const [ drawOpen, setDrawOpen ] = useState<boolean>(false);
  const [ markedJD, setMarkedJD ] = useState<string>("");
  const [ selectedJob, setSelectedJob ] = useState<Job | null>(null);
  const [ pageData, setPageData ] = useState<PageData | null>(null)
  const [ pageDataLoading, setPageDataLoading ] = useState<boolean>(false)
  const [ autofillSupported, setAutofillSupport ] = useState<boolean>(false)
  const [ isAlreadyApplied, setAlreadyApplied ] = useState<boolean>(false)
  const [ relatedCount, setRelatedCount ] = useState<any>(null)
  const [ requiredSkills, setRequiredSkills ] = useState<any[]>([])
  const [ familarity, setFamilarity ] = useState<any[]>([])
  const [ blockerKeywords, setBlockerKeywords ] = useState<any[]>([])

  const { showJD } = useContext(AppContext)

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
        _blockerKeywords: Array<any>
      ) => {
      setPageDataLoading(false)
      setPageData(_pageData);
      setAlreadyApplied(isApplied)
      setAutofillSupport(isSupported)
      setRequiredSkills(_requiredSkills);
      setBlockerKeywords(_blockerKeywords);

      let jd = _pageData?.description || "";

      (async() => {
        try {
          let response: any = await axios.post(`${serviceURL}/jd/mark`, { jd })
          jd = response.data
        } catch(err) {
          jd = "------------------ [ RAW ] ------------------<br/><br/>" + jd
        }
        setMarkedJD(jd)
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

  useEffect(() => {
    if(showJD) {
      if(markedJD.length > 0)
        setDrawOpen(true)
    }
  }, [ markedJD, showJD ])

  const handleSnackbarClose = useCallback((event: any, reason?: string) => {
    if (reason === 'clickaway') {
      return;
    }
    setSnackbarOpen(false);
  }, []);
  const handleSelectionModelChange = useCallback(
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
  const handleCellClick = useCallback((params: GridCellParams) => {
    window.electron.ipcRenderer.sendMessage('copy', params.row.jobUrl);
    window.electron.ipcRenderer.sendMessage('markCopy', params.row);
    window.electron.ipcRenderer.sendMessage('getPageData', params.row);
    setRelatedCount(null)
    setPageDataLoading(true)
    setSelectedJob(params.row);
  }, [rows])

  const deleteFromDB = useCallback(() => {
    window.electron.ipcRenderer.sendMessage('deleteFromDB', selectedJob?.id);
  }, [selectedJob])
  const removeSelected = useCallback(() => {
    window.electron.ipcRenderer.sendMessage('deleteCopied');
  }, []);
  const clearAll = useCallback(() => {
    window.electron.ipcRenderer.sendMessage('deleteAll');
  }, []);

  const onRefresh = useCallback(() => {
    if(selectedJob == null) return
    window.electron.ipcRenderer.sendMessage('fetchPageData', selectedJob);
    setPageDataLoading(true)
  }, [selectedJob])
  const onEasyApply = useCallback((requestConnect: boolean) => {
    window.electron.ipcRenderer.sendMessage('applyExternal', { jobId: selectedJob?.id, applyUrl: pageData?.applyUrl, requestConnect});
    window.electron.ipcRenderer.sendMessage('setAppliedFlag', selectedJob?.id);
    setAlreadyApplied(true)
  }, [pageData, selectedJob])
  const onApplyExternal = useCallback(() => {
    window.electron.ipcRenderer.sendMessage('applyExternal', { jobId: selectedJob?.id, applyUrl: pageData?.applyUrl, requestConnect: false});
    window.electron.ipcRenderer.sendMessage('setAppliedFlag', selectedJob?.id);
    setAlreadyApplied(true)
  }, [pageData, selectedJob])
  const onCopyExternal = useCallback(() => {
    window.electron.ipcRenderer.sendMessage('copy', pageData?.applyUrl);
    window.electron.ipcRenderer.sendMessage('setAppliedFlag', selectedJob?.id);
    setAlreadyApplied(true)
  }, [pageData, selectedJob])

  const onGenerateResume = useCallback(() => {
    window.electron.ipcRenderer.sendMessage('generateResume', {
      jobId: selectedJob?.id,
      position: selectedJob?.position,
      description: pageData?.description
    });
  }, [selectedJob, pageData])


  const onUpVote = useCallback(() => {
    window.electron.ipcRenderer.sendMessage('annotate', {
      jobId: selectedJob?.id,
      value: true
    });
    setDrawOpen(false)
  }, [ selectedJob ])
  const onDownVote = useCallback(() => {
    window.electron.ipcRenderer.sendMessage('annotate', {
      jobId: selectedJob?.id,
      value: false
    });
    setDrawOpen(false)
  }, [ selectedJob ])
  const onUpVoteAndApply = useCallback((requestConnect: boolean) => {
    window.electron.ipcRenderer.sendMessage('annotate', {
      jobId: selectedJob?.id,
      value: true
    });
    window.electron.ipcRenderer.sendMessage('applyExternal', { jobId: selectedJob?.id, applyUrl: pageData?.applyUrl, requestConnect});
    window.electron.ipcRenderer.sendMessage('setAppliedFlag', selectedJob?.id);
    setAlreadyApplied(true)
    setDrawOpen(false)
  }, [ selectedJob, pageData ])

  const minBlocker = blockerKeywords.reduce((min, current) => min > current.familarity ? current.familarity : min, 15)
  const minBlockerClass = minBlocker == 15 ? "blank" : minBlocker >= 8 ? "success" : minBlocker < 5 ? "error" : "warning"

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
                  <Button
                    color="info"
                    variant="contained"
                    endIcon={<ViewSidebarIcon/>}
                    size="small"
                    onClick={() => setDrawOpen(true)}
                  >J.D.</Button>
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
            sx={{ '& button': { m: 1 }, marginTop: '0px', paddingBottom: '15px', display: "flex" }}
          >
            {pageDataLoading ? (
                <div className="circular-progress-wrapper">
                  <CircularProgress/>
                </div>
            ) : (pageData && !pageDataLoading &&
              <>
                <div className="job-info">
                  <div className="job-measure-panel">
                    <div className="requirement-familarity">
                      <span className="familarity-good">{familarity[1] * 100 | 0}</span>&nbsp;:&nbsp;
                      <span className="familarity-bad">{familarity[0] * 100 | 0}</span>
                    </div>
                    {blockerKeywords.map(({keyword, count, familarity}: BlockerKeyword) =>
                        <Chip
                          key={keyword}
                          label={`${keyword} ${count}`}
                          size="medium"
                          color={ familarity >= 8 ? "success" : familarity < 5 ? "error" : "warning" }
                          sx={{
                            marginTop: "12px",
                            transform: "scale(1.3)",
                            width: "100px",
                            border: "4px solid #dfdfdf"
                          }}
                        />
                      )}
                  </div>
                  <div className="job-info-panel">
                    <p>
                      <a href="#" className="job-link">{pageData.applyUrl.substring(0, 50) + " ..."}&nbsp;&nbsp;<CopyAllIcon fontSize='small' sx={{ top: "4px", position: "relative" }}/></a>
                      <a style={{ marginTop: 5, marginBottom: 5 }}>{selectedJob?.id}</a>
                    </p>
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
      <div className={`color-flag ${minBlockerClass}`}></div>
      <Drawer
        anchor="right"
        open={drawOpen}
        onClose={() => setDrawOpen(false)}
      >
        <div className="drawer-wrapper">
          <div className="annotation-pad" style={{ visibility: selectedJob ? "visible" : "hidden" }}>
            <Fab color="success" aria-label="up-vote" onClick={ () => onUpVoteAndApply(false) }>
              <ThumbUpIcon />
              <AddIcon sx={{ fontSize: "14px" }}/>
            </Fab>
            <br/>
            {pageData?.applyMode == "EasyApply" ? (
              <>
                <Fab color="success" aria-label="up-vote" onClick={ () => onUpVoteAndApply(true) }>
                  <ThumbUpIcon />
                  <AddIcon sx={{ fontSize: "14px" }}/>
                  <AddIcon sx={{ fontSize: "14px", marginLeft: "-7px" }}/>
                </Fab>
                <br/>
              </>
            ): null}
            <Fab color="success" aria-label="up-vote" onClick={ onUpVote }>
              <ThumbUpIcon />
            </Fab>
            <br/>
            <Fab color="error" aria-label="down-vote" onClick={ onDownVote }>
              <ThumbDownIcon />
            </Fab>
          </div>
          <div dangerouslySetInnerHTML={{ __html: markedJD }} className="jd-pad">
          </div>
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
