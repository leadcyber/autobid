/* eslint global-require: off, no-console: off, promise/always-return: off */

/**
 * This module executes inside of electron's main process. You can start
 * electron renderer process from here and communicate with the other processes
 * through IPC.
 *
 * When running `npm run build` or `npm run build:main`, this file is compiled to
 * `./src/main.js` using webpack. This gives us some performance wins.
 */
import path from 'path';
import { app, BrowserWindow, ipcMain, shell } from "electron";
import { resolveHtmlPath } from './util';
import fs from 'fs'

import {
  getRequiredSkills,
  getCompanyUrl,
  generateResume,
  downloadJD
} from './api'
import {
  getJobList,
  getPageDataFromDB,
  getQAContentFromDB,
  connect as connectToDB
} from "./db";

const RESUME_DB_PATH = '/Volumes/Work/_own/autobid/bidengine/log/resume'


let mainWindow: BrowserWindow | null = null;

connectToDB()

if (process.env.NODE_ENV === 'production') {
  const sourceMapSupport = require('source-map-support');
  sourceMapSupport.install();
}
const isDebug = process.env.NODE_ENV === 'development' || process.env.DEBUG_PROD === 'true';
if (isDebug) require('electron-debug')();

const installExtensions = async () => {
  const installer = require('electron-devtools-installer');
  const forceDownload = !!process.env.UPGRADE_EXTENSIONS;
  const extensions = ['REACT_DEVELOPER_TOOLS'];

  return installer
    .default(
      extensions.map((name) => installer[name]),
      forceDownload
    )
    .catch(console.log);
};

const RESOURCES_PATH = app.isPackaged
    ? path.join(process.resourcesPath, 'assets')
    : path.join(__dirname, '../../assets');

const getAssetPath = (...paths: string[]): string => {
  return path.join(RESOURCES_PATH, ...paths);
};


const createWindow = async () => {
  if (isDebug) {
    await installExtensions();
  }

  mainWindow = new BrowserWindow({
    width: 1800,
    height: 920,
    show: true,
    frame: true,
    icon: getAssetPath('icon.png'),
    webPreferences: {
      preload: app.isPackaged
        ? path.join(__dirname, 'preload.js')
        : path.join(__dirname, '../../.erb/dll/preload.js'),
    },
  });
  mainWindow.loadURL(resolveHtmlPath('index.html'));

  mainWindow.on('ready-to-show', () => {
    if (!mainWindow) {
      throw new Error('"mainWindow" is not defined');
    }
    if (process.env.START_MINIMIZED) {
      mainWindow.minimize();
    } else {
      mainWindow.show();
    }
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
};


const handleIPC = () => {
  ipcMain.on('query', async (event, query) => {
    const limit = 10
    const jobList = await getJobList(query, limit, true)
    if(jobList.length < limit) {
      jobList.push(...(await getJobList(query, limit - jobList.length, false)))
    }
    event.reply("jobList", jobList)
  })
  ipcMain.on('getPageData', async (event, job) => {
    const pageData = await getPageDataFromDB(job.id)
    const companyUrl = await getCompanyUrl(pageData?.brief!)
    const requiredSkills = await getRequiredSkills(pageData?.description!)
    event.reply("pageData", pageData, companyUrl, requiredSkills)
  })
  ipcMain.on('getQA', async (event, jobId) => {
    const qaContent = await getQAContentFromDB(jobId)
    event.reply("qa", qaContent)
  })
  ipcMain.on('getResume', async (event, jobId) => {
    if(!jobId || jobId == "") event.reply("resume", "")
    else {
      const resumePath = `${RESUME_DB_PATH}/${jobId}/Michael.C Resume.pdf`
      console.log(resumePath)
      if(fs.existsSync(resumePath)) {
        event.reply("resume", resumePath)
      } else {
        event.reply("resume", "")
      }
    }
  })
  ipcMain.on('openResume', async (event, jobId) => {
    const resumePath = `${RESUME_DB_PATH}/${jobId}/Michael.C Resume.pdf`
    shell.openPath(resumePath);
  })
  ipcMain.on('openResumeFolder', async (event, jobId) => {
    const resumeFolderPath = `${RESUME_DB_PATH}/${jobId}`
    shell.openPath(resumeFolderPath);
  })
  ipcMain.on('generatePdfResume', async (event, { jobId, position, jd }) => {
    generateResume(jobId, position, jd, 'pdf')
  })
  ipcMain.on('generateDocResume', async (event, { jobId, position, jd }) => {
    generateResume(jobId, position, jd, 'doc')
  })
  ipcMain.on('downloadJD', async (event, { jd }) => {
    downloadJD(jd)
  })
  ipcMain.on('openExternalUrl', async (event, url) => {
    shell.openExternal(url);
  })
}


app.on("ready", async () => {
  handleIPC()

  createWindow()
});

// Quit when all windows are closed.
app.on("window-all-closed", () => {
  // On OS X it is common for applications and their menu bar
  // to stay active until the user quits explicitly with Cmd + Q
  console.log("windows all closed")
  app.quit();
});

app.on("activate", () => {
  // On OS X it"s common to re-create a window in the app when the
  // dock icon is clicked and there are no other windows open.
  if(!mainWindow || !mainWindow.isVisible())
    createWindow()
});
