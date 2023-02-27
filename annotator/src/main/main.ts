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
} from './api'
import {
  getJobList,
  getPageDataFromDB,
  connect as connectToDB,
  setAnnotation
} from "./db";
import { workspaceSetting } from './config/constant'
import axios from 'axios'

const annotationPath = path.join(workspaceSetting.workspacePath, "annotation")
const annotationIndexPath = path.join(annotationPath, "current_index.txt")
if(!fs.existsSync(annotationPath))
  fs.mkdirSync(annotationPath)

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
    width: 700,
    height: 800,
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

const markJD = async (jd: string) => {
  try {
    let response: any = await axios.post(`${workspaceSetting.serviceURL}/jd/mark`, { jd })
    return response.data
  } catch(err) {
    jd = "------------------ [ RAW ] ------------------<br/><br/>" + jd
  }
  return jd
}

const handleIPC = () => {
  let currentIndex: any = null
  let jobList: any = []
  ipcMain.on('getInitialState', async (event) => {
    jobList = await getJobList()
    let indexBuffer = "0"
    try {
      indexBuffer = fs.readFileSync(annotationIndexPath).toString()
    } catch(err) {}
    currentIndex = Math.max(Number(indexBuffer), 0)

    event.reply("initialState", jobList, currentIndex)
  })
  ipcMain.on('getPageData', async (event, { jobId, current } ) => {
    const pageData = await getPageDataFromDB(jobId)
    const jd = pageData?.description!
    const requiredSkills = await getRequiredSkills(jd)
    const markedJD = await markJD(jd)
    currentIndex = current
    fs.writeFileSync(annotationIndexPath, current.toString())

    event.reply("pageData", markedJD, requiredSkills)
  })
  ipcMain.on('setAnnotation', async (event, value) => {
    console.log(`[${currentIndex}]: ${jobList[currentIndex]}\t${value}`)
    setAnnotation(jobList[currentIndex], value)
  })
}


app.on("ready", async () => {
  handleIPC()

  createWindow()
});

// Quit when all windows are closed.
app.on("window-all-closed", () => {
  app.quit();
});

app.on("activate", () => {
  // On OS X it"s common to re-create a window in the app when the
  // dock icon is clicked and there are no other windows open.
  if(!mainWindow || !mainWindow.isVisible())
    createWindow()
});
