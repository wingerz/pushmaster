$('a.toggle').live('click', function(e) {
    e.preventDefault();
    $(this)
        .closest('form')
        .find('div.content')
        .slideToggle('fast');
});

$('#new-request').live('click', function(e) {
    var form = $('#new-request-form');
    if (!form.data('newFormDialog')) {
        form.dialog({
            'title': 'Make Request',
            'width': 700,
            'height': 450
        });
        form.data('newFormDialog', true);
    } else {
        if (form.dialog('isOpen')) {
            form.dialog('close');
        } else {
            form.dialog('open');
        }
    }
});

$(function() {
    // for CSS
    if ($.browser.webkit) {
        $('body').addClass('webkit');
    }
});

$(function() {
    $('input.date').datepicker({ 
        'showAnim': 'fadeIn',
        'dateFormat': 'yy-mm-dd',
        'minDate': new Date()
    });
});
