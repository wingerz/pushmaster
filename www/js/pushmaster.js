$('a.toggle').live('click', function(e) {
    e.preventDefault();
    $(this)
        .closest('form')
        .find('div.content')
        .slideToggle('fast');
});

$(function() {
    $('input.date').datepicker({ 
        'showAnim': 'fadeIn',
        'dateFormat': 'yy-mm-dd',
        'minDate': new Date()
    });
});