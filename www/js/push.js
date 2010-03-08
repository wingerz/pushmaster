var PAGE_RELOAD_DELAY = 60000; // ms

var canReload = function() {
    return $('form.request div.content:visible').length == 0;
};

var maybeReloadAfterDelay = function() {
    setTimeout(function() {
        if (canReload()) {
            location.href = location.href;
        } else {
            maybeReloadAfterDelay();
        }
    }, PAGE_RELOAD_DELAY);
};

$(function() {
    if (push.state != 'live') {
        maybeReloadAfterDelay();
    }
});
