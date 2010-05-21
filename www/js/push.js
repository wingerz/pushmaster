var PAGE_RELOAD_DELAY = 20 * 1000; // ms

pushmaster.provide('xhr');

pushmaster.xhr.acceptJSON = function(xhr) {
    xhr.setRequestHeader('Accept', 'application/json');
};

pushmaster.provide('push');

pushmaster.push.retrievePushData = function() {
    if (push.state !== 'live') {
        pushmaster.push.retrieveTimeout = setTimeout(function() {
            pushmaster.push.retrieveTimeout = null;
            $.ajax({'success': pushmaster.push.loadPushData, 'beforeSend': pushmaster.xhr.acceptJSON});
        }, PAGE_RELOAD_DELAY);
    }
};

pushmaster.push.loadPushData = function(pushData) {
    push.state = pushData.push.state;
    $('.push').html(pushData.html);
    pushmaster.push.retrievePushData();
};

$(pushmaster.push.retrievePushData);
