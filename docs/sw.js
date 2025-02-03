// Service Worker to handle CORS requests
self.addEventListener('fetch', event => {
    if (event.request.url.includes('cloudfront.net')) {
        event.respondWith(
            fetch(event.request.url, {
                mode: 'cors',
                credentials: 'omit',
                headers: {
                    'Origin': 'https://app.perusall.com',
                    'Referer': 'https://app.perusall.com/'
                }
            })
        );
    }
});
