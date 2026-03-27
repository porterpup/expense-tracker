self.addEventListener('install', (event) => self.skipWaiting());
self.addEventListener('activate', (event) => self.clients.claim());
self.addEventListener('fetch', (event) => {
  // Basic offline placeholder — extend per app caching needs
});
