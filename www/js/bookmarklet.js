(function() {
    var summary = $('#summary').text();

    var codeReview = location.href;
    var reviewers = $.makeArray(
        $('#target_people a')
            .map(function(i, a) {
                return $(a).text();
            }))
        .join(', ');

    var tickets = $('#bugs_closed')
        .text()
        .split(',')
        .filter(Boolean)
        .map(function(bug) { return 'https://trac.yelpcorp.com/ticket/' + bug.match(/\d+/)[0]; })
        .join(', ');
    
    var message = [
        codeReview, ' by ', reviewers, '\n\n',
        'Tickets: ', tickets
    ].join('');

    location.href = 'http://yelp-pushmaster.appspot.com/requests?' + $.param({
        'subject': summary,
        'message': message
    });
})();