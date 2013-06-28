var response_dump;

$(document).ready(function() {
	
});

function setResponseDump(data) {
	response_dump = $($("#response_dump").find('textarea')[0]);
	response_dump.val(data);
}

function expandOutput() {
	if(response_dump.css('display') == 'none') {
		response_dump.css('display','block');
		$("#rd_control").html('[hide]');
	} else {
		response_dump.css('display', 'none');
		$("#rd_control").html('[expand]');
	}
}

function render(data, layout, root) {
	data = $.parseJSON(data);
	if(data.result == 200) {
		if(!(data.data instanceof Array)) {
			var d = [];
			d.push(data.data);
			data.data = d;
		}
		
		$.ajax({
			url: "/layouts/" + layout + ".html",
			dataType: "html",
			success: function(html) {
				$.each(data.data, function() {
					var d = this;
					$("#" + root).append(Mustache.to_html(html, d));
				})
			}
		});
	}
}