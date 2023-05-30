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
import { app, BrowserWindow, globalShortcut, ipcMain, Tray, nativeImage, Menu, clipboard } from "electron";
import { resolveHtmlPath } from './util';

import {
  createLinkedInListener,
  getPageData,
  isAutofillSupported,
  setFetchMode,
  getFetchMode,
  getFamilarity,
  getRequiredSkills,
  getBlockerKeywords,
  resetFetchTimeout
} from './api'
import {
  deleteAll,
  deleteCopied,
  deleteFromDB,
  setCopied,
  getAllAvailableJobs,
  getPageDataFromDB,
  setPageDataToDB,
  getIdFromIdentifier,
  setAlreadyApplied,
  isAlreadyApplied,
  getRelatedJobCount,
  setAnnotation,
  connect as connectToDB
} from "./db";
import { Job, PageData, BidState, FetchMode } from '../job.types'
import { myConsole } from './util/myconsole';
import {
  applyExternal,
  pushToAutoBidQueue,
  setAutoBidMode,
  skipTask,
  registerAutoBidEvents,
  getQueueState,
  getBidState,
  getAutoBidMode,
  getRequestConnectMode,
  setRequestConnectMode,
  getExceptionSkipMode,
  setExceptionSkipMode
} from './api/autobidder'
import {
  generateResume
} from './api/pyengine'


let mainWindow: BrowserWindow | null = null;
let tray: any;


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
  // const extensions = ['REACT_DEVELOPER_TOOLS'];
  const extensions: string[] = [];

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

let lazyTimeout: any = null
const awakeFetchMode = () => {
  const currentFetchMode = getFetchMode()
  if(currentFetchMode == FetchMode.LAZY) {
    setFetchMode(FetchMode.NORMAL)
    mainWindow?.webContents.send('fetchMode', FetchMode.NORMAL)
  }
  clearTimeout(lazyTimeout)
  if(getFetchMode() !== FetchMode.ETERNAL) {
    lazyTimeout = setTimeout(() => {
      setFetchMode(FetchMode.LAZY)
      mainWindow?.webContents.send('fetchMode', FetchMode.LAZY)
    }, 1000 * 60 * 15)
  }
}
awakeFetchMode()

const createWindow = async () => {
  if (isDebug) {
    await installExtensions();
  }

  mainWindow = new BrowserWindow({
    width: 1680,
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
  mainWindow.excludedFromShownWindowsMenu = true

  mainWindow.loadURL(resolveHtmlPath('index.html'));

  mainWindow.on('ready-to-show', () => {
    if (!mainWindow) {
      throw new Error('"mainWindow" is not defined');
    }
    if (process.env.START_MINIMIZED) {
      mainWindow.minimize();
    } else {
      mainWindow.show();
      app.dock.show()
    }
    updateRenderer()
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
};

const toggleWindowVisibility = async () => {
  if(!mainWindow) {
    await createWindow()
  }
  else if(mainWindow.isVisible()) {
    mainWindow.hide()
    await app.dock.hide()
  }
  else {
    mainWindow.show()
    mainWindow.focus()
    await app.dock.show()
  }
}
const registerGlobalShortcut = () => {
  globalShortcut.register('Alt+CommandOrControl+A', () => {
    toggleWindowVisibility()
  })
}
const createTray = () => {
  const icon = nativeImage.createFromPath(getAssetPath('tray.png')).resize({ width: 16, height: 16 })
  tray = new Tray(icon)
  const contextMenu = Menu.buildFromTemplate([
    { label: 'Show/Hide', type: 'normal', click: () => toggleWindowVisibility()},
    { label: 'Quit', type: 'normal', role: "quit"}
  ])

  tray.setContextMenu(contextMenu)

  tray.setToolTip('LinkedIn Job Bot')
}

const handleIPC = () => {
  ipcMain.on('deleteCopied', async (event) => {
    await deleteCopied()
    await updateRenderer()
  })
  ipcMain.on('deleteFromDB', async (event, jobId) => {
    await deleteFromDB(jobId)
    await updateRenderer()
  })
  ipcMain.on('deleteAll', async (event) => {
    await deleteAll()
    await updateRenderer()
  })
  ipcMain.on('copy', async (event, jobUrl) => {
    clipboard.writeText(jobUrl)
  })
  ipcMain.on('markCopy', async (event, job) => {
    const { id, jobUrl } = job
    await setCopied(id)
    event.reply("copied", job)
    awakeFetchMode()
  })
  ipcMain.on('notificationClicked', async (event, newJobs: Job[]) => {
    if(newJobs.length > 1) {
      if(!mainWindow || !mainWindow.isVisible())
        toggleWindowVisibility()
      mainWindow?.focus()
    } else if(newJobs.length == 1) {
      const job = newJobs[0]
      const jobId = await getIdFromIdentifier(job.identifier)
      myConsole.log(`[notification-click]: ${jobId} - ${job.position}@${job.company}`, )
      clipboard.writeText(job.jobUrl)
      await setCopied(jobId)
      updateRenderer()
    }
  })
  ipcMain.on('getPageData', async (event, job) => {
    event.reply("pageDBData",
      await getRelatedJobCount(job)
    )

    let pageData: PageData | null = await getPageDataFromDB(job.id)
    if(!pageData || pageData.applyMode == "Error") {
      pageData = await getPageData(job)
      await setPageDataToDB(job.id, pageData)
    }
    event.reply("pageOnlineData",
      pageData,
      isAutofillSupported(pageData.applyUrl),
      await isAlreadyApplied(pageData.applyUrl),
      await getRequiredSkills(pageData.description),
      await getBlockerKeywords(pageData.description)
    )
  })
  ipcMain.on('fetchPageData', async (event, job) => {
    event.reply("pageDBData",
      await getRelatedJobCount(job)
    )

    const pageData = await getPageData(job)
    await setPageDataToDB(job.id, pageData)
    event.reply("pageOnlineData",
      pageData,
      isAutofillSupported(pageData.applyUrl),
      await isAlreadyApplied(pageData.applyUrl),
      await getRequiredSkills(pageData.description),
      await getBlockerKeywords(pageData.description)
    )
  })
  ipcMain.on('applyExternal', async (event, { jobId, applyUrl, requestConnect }) => {
    applyExternal(jobId, applyUrl, requestConnect)
  })
  ipcMain.on('generateResume', async (event, { jobId, position, description }) => {
    generateResume(jobId, position, description)
  })
  ipcMain.on('setAppliedFlag', async (event, jobId: string) => {
    setAlreadyApplied(jobId)
  })
  ipcMain.on('setFetchMode', async (event, mode: FetchMode) => {
    setFetchMode(mode)
    if(mode === FetchMode.ETERNAL) {
      clearTimeout(lazyTimeout)
    }
    resetFetchTimeout()
    event.reply('fetchMode', mode)
  })

  ipcMain.on('getAutoBidMode', async (event) => {
    event.reply("autobidMode", getAutoBidMode())
  })
  ipcMain.on('setAutoBidMode', async (event, mode: boolean) => {
    setAutoBidMode(mode)
    event.reply('autobidMode', mode)
  })

  ipcMain.on('getExceptionSkipMode', async (event) => {
    event.reply("exceptionSkipMode", getExceptionSkipMode())
  })
  ipcMain.on('setExceptionSkipMode', async (event, mode: boolean) => {
    setExceptionSkipMode(mode)
    event.reply('exceptionSkipMode', mode)
  })

  ipcMain.on('skipTask', async (event, jobId: string) => {
    skipTask(jobId)
  })
  ipcMain.on('getQueueState', async (event) => getQueueState())
  ipcMain.on('getBidState', async (event) => getBidState())

  ipcMain.on('getRequestConnectMode', async (event) => {
    event.reply("requestConnectMode", getRequestConnectMode())
  })
  ipcMain.on('setRequestConnectMode', async (event, mode: boolean) => {
    setRequestConnectMode(mode)
    event.reply("requestConnectMode", getRequestConnectMode())
  })
  ipcMain.on('annotate', async (event, { jobId, value }) => {
    setAnnotation(jobId, value)
  })
}
const updateRenderer = async () => {
  if(mainWindow) {
    const jobs = await getAllAvailableJobs()
    mainWindow.webContents.send('update', jobs)
  }
}

const onAutobidableJobsFound = async (autobidables: Job[]) => {
  pushToAutoBidQueue(autobidables)
}
const showNotification = (newJobs: Job[]) => {
  mainWindow?.webContents.send('jobNotification', newJobs)
}
const setFetchStep = (status: string, data: any) => {
  mainWindow?.webContents.send('fetchStatus', status, data)
}
/**
 * Add event listeners...
 */
registerAutoBidEvents(
  updateRenderer,
  (queueLength: number) => mainWindow?.webContents.send('queueState', queueLength),
  (bidState: BidState) => mainWindow?.webContents.send('bidState', bidState),
)

app.on("ready", async () => {
  createTray()
  handleIPC()
  createLinkedInListener(updateRenderer, onAutobidableJobsFound, showNotification, setFetchStep)
  registerGlobalShortcut()

  await toggleWindowVisibility()
});

// Quit when all windows are closed.
app.on("window-all-closed", () => {
  // On OS X it is common for applications and their menu bar
  // to stay active until the user quits explicitly with Cmd + Q
  console.log("windows all closed")
  if (process.platform !== "darwin") {
    app.quit();
  }
});

app.on("activate", () => {
  // On OS X it"s common to re-create a window in the app when the
  // dock icon is clicked and there are no other windows open.
  if(!mainWindow || !mainWindow.isVisible())
    toggleWindowVisibility()
});
