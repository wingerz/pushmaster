var PAGE_RELOAD_DELAY = 30000; // ms

var reloadPush = function() {
    setTimeout(function() {
        $.getJSON(location.href, function(data) {
            $('#requests')
                .empty()
                .append($(data.requests).children());
            $('#pending-requests')
                .empty()
                .append($(data.pending).children());
            reloadPush();
        });
    }, PAGE_RELOAD_DELAY);
};

if (push.state != 'live') {
    reloadPush();
}