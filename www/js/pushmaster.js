this.provide = function() {
    var namespace = this;
    Array.forEach(arguments, function(name) {
        if (!namespace[name]) {
            namespace[name] = {};
        }
        namespace = namespace[name];
        namespace.provide = this.provide;
    }, this);
};

provide('pushmaster', 'location');

pushmaster.location.queryToObject = function(query) {
    var object = {};
    if (query) {
        if (query.charAt(0) == '?') {
            query = query.substring(1);
        }
        query.split('&').forEach(function(pair) {
            var parts = pair.split('=').map(function(part) {
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
