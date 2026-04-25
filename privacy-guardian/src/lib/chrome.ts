/* eslint-disable @typescript-eslint/no-explicit-any */
declare const chrome: any;

/**
 * Chrome Extension API helpers.
 * Gracefully falls back when running in a normal browser (dev mode).
 */

const isChromeExtension =
  typeof chrome !== "undefined" && !!chrome.runtime?.id;

/** Get the active tab's URL from the extension background */
export async function getCurrentTabUrl(): Promise<string | null> {
  if (!isChromeExtension) {
    // Dev fallback — return a mock URL
    return "https://example.com/privacy-policy";
  }

  return new Promise((resolve) => {
    chrome.runtime.sendMessage({ type: "GET_CURRENT_TAB" }, (response) => {
      resolve(response?.url ?? null);
    });
  });
}

/** Persist user config in chrome.storage (or localStorage in dev) */
export async function saveConfig(config: unknown): Promise<void> {
  if (isChromeExtension) {
    await chrome.storage.local.set({ userConfig: config });
  } else {
    localStorage.setItem("userConfig", JSON.stringify(config));
  }
}

/** Load persisted user config */
export async function loadConfig<T>(): Promise<T | null> {
  if (isChromeExtension) {
    const result = await chrome.storage.local.get("userConfig");
    return (result.userConfig as T) ?? null;
  }
  const raw = localStorage.getItem("userConfig");
  return raw ? JSON.parse(raw) : null;
}

export { isChromeExtension };
