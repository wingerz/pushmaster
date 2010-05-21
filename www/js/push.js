var PAGE_RELOAD_DELAY = 20 * 1000; // ms

pushmaster.provide('push');

pushmaster.push.retrievePushData = function() {
    if (push.state !== 'live') {
        pushmaster.push.retrieveTimeout = setTimeout(function() {
            pushmaster.push.retrieveTimeout = null;
            $.ajax({'url': '/push/' + push.key, 'contentType': 'application/json', 'success': pushmaster.push.loadPushData});
        }, PAGE_RELOAD_DELAY);
    }
};

pushmaster.push.loadPushData = function(pushData) {
    push.state = pushData.push.state;
    $('.push').html(pushData.html);
    pushmaster.push.retrievePushData();
};

$(pushmaster.push.retrievePushData);
