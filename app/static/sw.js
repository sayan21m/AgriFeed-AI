const SHELL = [
  "/",
  "/static/styles.css",
  "/static/app.js",
  "/static/icon-192.png",
  "/manifest.webmanifest",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open("smartfeed-shell").then((cache) => cache.addAll(SHELL)).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(self.clients.claim());
});

self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);
  if (event.request.method !== "GET") return;
  if (url.pathname.startsWith("/api/")) return;
  event.respondWith(
    caches.match(event.request).then((hit) => hit || fetch(event.request).then((res) => {
      const copy = res.clone();
      caches.open("smartfeed-shell").then((cache) => cache.put(event.request, copy)).catch(() => {});
      return res;
    }).catch(() => caches.match("/")))
  );
});
