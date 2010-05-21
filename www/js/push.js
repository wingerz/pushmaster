var PAGE_RELOAD_DELAY = 30 * 1000; // ms

pushmaster.provide('push');

pushmaster.push.retrievePushData = function() {
    if (push.state !== 'live') {
        $.ajax({'url': '/push/' + push.key, 'contentType': 'application/json', 'success': pushmaster.push.loadAsyncPushData});
    }
};

pushmaster.push.loadPushData = function(pushData) {
    push.state = pushData.push.state;
    $('.push').html(pushData.html);
    pushmaster.push.retrieveTimeout = setTimeout(pushmaster.push.retrievePushData, PAGE_RELOAD_DELAY);
};

pushmaster.push.load = function() {
    pushmaster.push.retrieveTimeout = setTimeout(pushmaster.push.retrievePushData, PAGE_RELOAD_DELAY);
};

$(pushmaster.push.load);
