// background.js — Manifest V3 Background Service Worker

// 1. Listen for tab updates (navigation)
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === "complete" && tab.url) {
    if (tab.url.startsWith("chrome://") || tab.url.startsWith("chrome-extension://")) return;

    // Persist for the popup to read on open
    chrome.storage.local.set({ currentUrl: tab.url, tabId });

    // Broadcast to the UI if it's currently open
    chrome.runtime.sendMessage({
      type: "TAB_UPDATED",
      url: tab.url,
      tabId
    }).catch(() => {
      // Ignore error: This just means the dashboard UI isn't open right now
    });
  }
});

// 2. Listen for tab activation (switching tabs)
chrome.tabs.onActivated.addListener(async (activeInfo) => {
  try {
    const tab = await chrome.tabs.get(activeInfo.tabId);
    if (tab.url && !tab.url.startsWith("chrome://")) {
      chrome.storage.local.set({ currentUrl: tab.url, tabId: activeInfo.tabId });

      chrome.runtime.sendMessage({
        type: "TAB_UPDATED",
        url: tab.url,
        tabId: activeInfo.tabId
      }).catch(() => { });
    }
  } catch (e) {
    // Tab might have closed
  }
});

// 3. Handle explicit requests for the current state
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "GET_CURRENT_TAB") {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      const tab = tabs[0];
      sendResponse({ url: tab?.url || null, tabId: tab?.id || null });
    });
    return true;
  }
});