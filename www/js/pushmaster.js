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
