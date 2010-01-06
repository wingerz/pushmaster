$('a.toggle').live('click', function(e) {
    e.preventDefault();
    $(this)
        .closest('form')
        .find('div.content')
        .slideToggle('fast');
});
