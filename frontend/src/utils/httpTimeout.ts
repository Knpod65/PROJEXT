export function withTimeout<T>(promise: Promise<T>, ms: number = 15000): Promise<T> {
  return new Promise((resolve, reject) => {
    const timeoutId = setTimeout(() => reject(new Error("Request timeout")), ms);
    promise
      .then((value) => {
        clearTimeout(timeoutId);
        resolve(value);
      })
      .catch((err) => {
        clearTimeout(timeoutId);
        reject(err);
      });
  });
}

export const DEFAULT_TIMEOUT_MS = 15000;