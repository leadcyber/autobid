import { Channels } from 'main/preload';

declare global {
  interface Window {
    electron: {
      ipcRenderer: {
        sendMessage(channel: Channels, args?: any): void;
        on(
          channel: Channels,
          func: (...args: any) => void
        ): (() => void) | undefined;
        once(channel: Channels, func: (...args: any) => void): void;
      };
    };
  }
}

export {};
