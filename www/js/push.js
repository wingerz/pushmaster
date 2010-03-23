var PAGE_RELOAD_DELAY = 60000; // ms

var canReload = function() {
    var form = $('#new-request-form');
    return !(form.data('newFormDialog') && form.dialog('isOpen'));
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
