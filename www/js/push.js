var PAGE_RELOAD_DELAY = 60000; // ms

if (push.state != 'live') {
    setTimeout(function() {
        location.reload();
    }, PAGE_RELOAD_DELAY);
}