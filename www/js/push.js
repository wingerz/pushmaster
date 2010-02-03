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

    var header = $('h1');
    var backgroundColor = null;
    if (header.is('.epic')) {
        backgroundColor = 'yellow';
    } else if (header.is('.gonzo')) {
        backgroundColor = '#7FFF00';
    }

    if (backgroundColor) {
        var highlight = {
            'on': function() {
                header.animate({ 'backgroundColor': backgroundColor }, 1500, 'linear', highlight.off);
            },

            'off': function() {
                header.animate({ 'backgroundColor': 'white' }, 1500, 'linear', highlight.on);
            }
        };

        highlight.on();
    }
});
