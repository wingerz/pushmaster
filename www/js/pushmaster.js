this.provide = function() {
    var namespace = this;
    var provide = this.provide;
    $.each(arguments, function(i, name) {
        if (!namespace[name]) {
            namespace[name] = {};
        }
        namespace = namespace[name];
        namespace.provide = provide;
    });
};

provide('pushmaster', 'location');

pushmaster.location.queryToObject = function(query) {
    var object = {};
    if (query) {
        if (query.charAt(0) == '?') {
            query = query.substring(1);
        }
        $.each(query.split('&'), function(i, pair) {
            var parts = $.map(pair.split('='), function(part) {
                return decodeURIComponent(part.replace(/\+/g, '%20'));
            });
            object[parts[0]] = parts[1];
        });
    }
    return object;
};

provide('pushmaster', 'dialog');

pushmaster.dialog.MakeRequest = function() {
    this.form = $('#new-request-form');

    if (location.search) {
        var query = pushmaster.location.queryToObject(location.search);

        if (query.subject) {
            this.form.find('[name=subject]').val(query.subject);
        }

        if (query.message) {
            this.form.find('[name=message]').val(query.message);
        }

        if (query.message || query.subject) {
            this.open();
        }
    }
};
pushmaster.dialog.MakeRequest.prototype = {
    initialized: false,

    dialogOptions: {
        'title': 'Make Request',
        'width': 700,
        'height': 450
    },

    ensureDialog: function() {
        if (!this.initialized) {
            this.form.dialog(this.dialogOptions);
            this.initialized = true;
        }
    },

    isOpen: function() {
        return this.initialized && this.form.dialog('isOpen');
    },

    open: function() {
        this.ensureDialog();
        if (!this.form.dialog('isOpen')) {
            this.form.dialog('open');
        }
    },

    close: function() {
        if (this.initialized && this.form.dialog('isOpen')) {
            this.form.dialog('close');
        }
    },

    toggle: function() {
        if (this.initialized && this.form.dialog('isOpen')) {
            this.close();
        } else {
            this.open();
        }
    }
};

pushmaster.provide('event');

pushmaster.event.preventDefaultEmptyHref = function(e) {
    var href = $(e.target).closest('a').attr('href');
    if (href.charAt(href.length - 1) === '#') {
        e.preventDefault();
    }
};

pushmaster.event.toggleFormContent = function(e) {
    $(e.target)
        .closest('form')
        .find('div.content')
        .toggle();
};

$('a').live('click', pushmaster.event.preventDefaultEmptyHref);
$('a.toggle').live('click', pushmaster.event.toggleFormContent);

pushmaster.provide('page');

$(function() {
    pushmaster.page.makeRequest = new pushmaster.dialog.MakeRequest();

    $('#new-request').click(function(e) {
        pushmaster.page.makeRequest.toggle();
    });
});

// initialize all datepickers
$(function() {
    $('input.date').datepicker({ 
        'showAnim': 'fadeIn',
        'dateFormat': 'yy-mm-dd',
        'minDate': new Date()
    });
});

pushmaster.provide('shortcuts');

pushmaster.shortcuts.lastKeys = [];

pushmaster.shortcuts.keyup = function(e) {
    console.debug('pushmaster.shortcuts.keyup', e.which);

    var lastKeys = pushmaster.shortcuts.lastKeys;
    lastKeys.push(e.which);
    while (lastKeys.length > 3) {
        lastKeys.shift();
    }
    $.each(pushmaster.shortcuts.actions, function(i, action) {
        if (action.keys.length === lastKeys.length) {
            var same = $.grep(action.keys, function(i, key) {
                return lastKeys[i] === key;
            });
            if (same.length === lastKeys.length) {
                action.callback.call();
            }
        }
    });
};

pushmaster.shortcuts.actions = [{
    'keys': [24, 52, 48], // ^C+x 4 0
    'callback': function() {
        pushmaster.page.makeRequest.open();
    }
}];

//$('body').live('keyup', pushmaster.shortcuts.keyup);
