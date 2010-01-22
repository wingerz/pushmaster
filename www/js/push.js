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

    var epic = $('h1.epic');
    if (epic.length > 0) {
        var highlight = {
            'on': function() {
                epic.animate({ 'backgroundColor': 'yellow' }, 1500, 'linear', highlight.off);
            },

            'off': function() {
                epic.animate({ 'backgroundColor': 'white' }, 1500, 'linear', highlight.on);
            }
        };

        highlight.on();
    }
});
