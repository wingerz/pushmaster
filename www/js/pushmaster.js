$('a.toggle').live('click', function(e) {
    e.preventDefault();
    $(this)
        .closest('form')
        .find('div.content')
        .slideToggle('fast');
});

$(function() {
    $('input.date').datepicker({ 
        'dateFormat': 'yy-mm-dd' 
    });
});