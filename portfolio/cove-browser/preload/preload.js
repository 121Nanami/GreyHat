'use strict';

const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('cove', {
  getSettings: () => ipcRenderer.invoke('settings:get'),
  setSettings: (partial) => ipcRenderer.invoke('settings:set', partial),
  partitionFor: (url) => ipcRenderer.invoke('privacy:partition', url),
  paths: () => ipcRenderer.invoke('app:paths'),
  onBlocked: (cb) => {
    const handler = (_e, payload) => cb(payload);
    ipcRenderer.on('privacy:blocked', handler);
    return () => ipcRenderer.removeListener('privacy:blocked', handler);
  },
});
