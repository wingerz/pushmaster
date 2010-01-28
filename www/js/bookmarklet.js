(function() {
    var summary = $('#summary').text();

    var codeReview = location.href;
    var reviewers = $.makeArray(
        $('#target_people a')
            .map(function(i, a) {
                return $(a).text();
            }))
        .join(', ');

    var tickets = $.makeArray(
        $('#bugs_closed a')
            .map(function(i, a) {
                return a.href;
            }))
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