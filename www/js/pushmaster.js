var $break = {};

var each = function(array, fun) {
    try {
        Array.prototype.forEach.call(array, fun, this);
    } catch (ex) {
        if (ex !== $break) {
            throw ex;
        }
    }
    return array;
};

var filter = function(array, fun) {
    return Array.prototype.filter.call(array, fun, this);
};

var map = function(array, fun) {
    return Array.prototype.map.call(array, fun, this);
};

var heir = function(ancestor) {
    var h = function() {};
    h.prototype = ancestor;
    return new h();
};

var keys = function(object) {
    var allkeys = []
    for (var key in object) {
        allkeys.push(key);
    }
    return allkeys;
};

var values = function(object) {
    var values = [];
    for (var key in object) {
        values.push(object[key]);
    }
    return values;
};

var flat = function(array) {
    var flattened = $.makeArray(array); // make a shallow copy
    for (var i = 0; i < flattened.length; /* */) {
        if ($.isArray(flattened[i])) {
            var args = $.makeArray(flattened[i]);
            args.unshift(i, 1);
            flattened.splice.apply(flattened, args);
        } else {
            i += 1;
        }
    }
    return flattened;
};

var method = function(fun) {
    var self = this;
    return function() {
        return fun.apply(self, arguments);
    };
};

//
//
//

var pushmaster = {};

$(function() {
    $('a.toggle')
		.attr('href', '#')
		.each(function(i, toggle) {
			toggle = $(toggle);
			toggle
				.click(function(event) {
					event.preventDefault();
					toggle
                        .closest('legend')
                        .next()
                        .slideToggle('fast');
				});
		});
});
