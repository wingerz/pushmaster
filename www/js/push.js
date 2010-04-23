var PAGE_RELOAD_DELAY = 30 * 1000; // ms

pushmaster.provide('push');

pushmaster.push.canReload = function() {
    return pushmaster.page.makeRequest && !pushmaster.page.makeRequest.isOpen();
};

pushmaster.push.maybeReloadAfterDelay = function() {
    setTimeout(function() {
        if (pushmaster.push.canReload()) {
            pushmaster.location.reload();
        } else {
            pushmaster.push.maybeReloadAfterDelay();
        }
    }, PAGE_RELOAD_DELAY);
};

pushmaster.push.load = function() {
    if (push.state != 'live') {
        pushmaster.push.maybeReloadAfterDelay();
    }
};

$(pushmaster.push.load);
