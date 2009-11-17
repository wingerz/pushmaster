$(function() {
    $('a.edit-request-toggle')
		.attr('href', '#')
		.each(function(i, toggle) {
			toggle = $(toggle);
			var content = toggle
				.closest('fieldset')
				.find('div.edit-request-content');
			
			toggle
				.click(function(event) {
					event.preventDefault();
					content.slideToggle('fast');
				});
		});
});
