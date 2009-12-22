$.extend(push, {
    'requestsInState': function(state) {
        return filter(this.requests, function(request) {
            return request.state === state;
        });
    }
});

var view = {
    'states': {
        'tested': 'Tested on Stage',
        'onstage': 'On Stage',
        'checkedin': 'Checked In',
        'accepted': 'Accepted'
    },

    'requestList': function(push) {
        return $('<div><h2>Requests</h2></div>')
            .append($(
                flat(map.call(this, keys(this.states), function(state) {
                    return [
                        $('<h3/>')
                            .text(this.states[state])
                            .get(0),
                        $('<ol/>')
                            .addClass('accepted requests')
                            .append($(map.call(this, push.requestsInState(state), this.requestItem)))
                            .get(0)
                    ];
                }))
            ))
            .children();
    },

    'datetime': function(dt) {
        return $(['<span class="datetime">', dt, '</span>'].join(''));
    },

    'emailLink': function(email, display) {
        return $(['<span class="email"><a href="mailto:', email, '">', email || display, '</a></span>'].join(''));
    },

    'requestItem': function(request) {
        return $('<li/>')
            .addClass('accepted request')
            .append(
                $('<a/>')
                    .attr('href', request.uri)
                    .text(request.subject)
            )
            .append(this.emailLink(request.owner.email, request.owner.nickname))
            .get(0);
    },

    'acceptForm': function(push, request) {
        return $('<form/>')
            .addClass('small')
            .attr({
                'method': 'post',
                'action': request.uri
            })
            .append(
                $('<button/>')
                    .attr({
                        'type': 'submit',
                        'name': 'action',
                        'value': 'accept'
                    })
                    .text('Accept')
                    .get(0),
                $('<input/>')
                    .attr({
                        'type': 'hidden',
                        'name': 'push',
                        'value': push.key
                    })
                    .get(0)
            );
    },

    'pendingList': function(requests) {
        return $('<div/>')
            .append($(map.call(this, requests, function(request) {
                var item = $(this.requestItem(request));
                item.prepend(this.acceptForm(push, request));
                return item.get(0);
            })))
            .children();
    }
};

pushmaster.push = {
    'method': method,

    'display': function() {
        $('#push-title span.owner')
            .empty()
            .append(view.emailLink(push.owner.email, push.owner.nickname));

        $('#push-title span.state')
            .text(push.state);

        $('#requests')
            .empty()
            .append(view.requestList(push));

        $('#pending-requests')
            .empty()
            .append(view.pendingList(pending));
    },

    'PAGE_RELOAD_DELAY': 30000, // ms

    'reload': function() {
        setTimeout(this.method(function() {
            $.getJSON(push.uri, this.method(function(data) {
                $.extend(push, data.push);
                $.extend(pending, data.pending);

                this.display();

                if (push.state != 'live') {
                    this.reload();
                }
            }));
        }), this.PAGE_RELOAD_DELAY);
    }
};

$(pushmaster.push.display);
if (push.state != 'live') {
    pushmaster.push.reload();
}
