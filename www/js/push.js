pushmaster.provide('xhr');

pushmaster.xhr.get = function(options) {
    options = $.extend({'dataType': 'json'}, options, {'type': 'get'});
    return $.ajax(options);
};

pushmaster.provide('push');

pushmaster.push.pageReloadDelay = 30 * 1000; // ms

pushmaster.push.retrievePushData = function() {
    if (push.state !== 'live') {
        pushmaster.push.retrieveTimeout = setTimeout(function() {
            pushmaster.push.retrieveTimeout = null;
            pushmaster.xhr.get({'success': pushmaster.push.loadPushData, 'error': pushmaster.push.retrievePushData});
        }, pushmaster.push.pageReloadDelay);
    }
};

pushmaster.push.loadPushData = function(pushData) {
    push.state = pushData.push.state;
    $('.push').html(pushData.html);
    pushmaster.push.retrievePushData();
};

$(pushmaster.push.retrievePushData);
