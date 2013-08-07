var response_dump, j3m_dump;
var registration;

$(document).ready(function() {
	registration = $("#registration");
	$("#qr_code").qrcode("http://ec2-54-235-36-217.compute-1.amazonaws.com/informacam/");
});

function showRegistration() {
	if(registration.css('display') == 'none') {
		registration.css('display', 'block');
	} else {
		registration.css('display', 'none');
	}
}

function getRegistration() {
	$("#load_registration").prop('src','/informacam/');
}

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

function setJ3MDump(data) {
	j3m_dump = data;
}

function expandJ3M() {
	var j3m_display = $("#j3m_dump");
	if(j3m_display.css('display') == 'none') {
		var j3m = $(j3m_display.find('textarea')[0]);
		if(j3m.val().length == 0 && j3m_dump != undefined) {
			$.ajax({
				url: "/media/" + j3m_dump,
				dataType: "html",
				success: function(html) {
					j3m.val(html);
				}
			});
		}
		
		j3m_display.css('display','block');
	} else {
		j3m_display.css('display','none');
	}
}

function renderMedia(root) {
	
	$.each(root.find(".render_thumb"), function() {
		var thumb = $(this).prop('src');
		if(thumb.indexOf(".mkv") >= 0) {
			$(this).prop('src',thumb.replace('.mkv','.jpg'));
		}
	});
	
	$.each(root.find(".render_media"), function() {
		var asset = $(this).attr('asset');
		var media;
		
		if(asset.indexOf(".mkv") >= 0) {
			media = $(document.createElement('video'))
				.attr('controls','true')
				.addClass('render_fit');
			media.append(
				$(document.createElement('source'))
					.attr('src', asset.replace('.mkv','.ogv'))
					.prop('type', 'video/ogg')
			);
		} else if(asset.indexOf(".jpg") >= 0) {
			media = $(document.createElement('img'))
				.prop('src', asset)
				.addClass('render_fit');
		}
		
		if(media != undefined) {
			$(this).append(media);
		}
	});
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
				});
				
				renderMedia($("#" + root));
			}
		});
	}
}
