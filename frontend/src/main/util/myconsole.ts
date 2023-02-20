import fs from 'fs'
import { dirPath } from '../config/constant'
import path from 'path'

export const myConsole = new console.Console(fs.createWriteStream(path.join(dirPath, 'console.log')));
