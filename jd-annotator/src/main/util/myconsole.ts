import fs from 'fs'
import { dirPath } from '../config/constant'
import path from 'path'

export const writeStream = fs.createWriteStream(path.join(dirPath, 'console.log'))
export const myConsole = new console.Console(writeStream);
