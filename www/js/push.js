var PAGE_RELOAD_DELAY = 60000; // ms

if (push.state != 'live') {
    setTimeout(function() {
        location.href = location.href;
    }, PAGE_RELOAD_DELAY);
}