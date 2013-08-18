<html>
	<head>
		<title><?= $layout->title ?></title>
		<script type="text/javascript" src="/js/jquery.js"></script>
		<script type="text/javascript" src="/js/mustache.js"></script>
		<script type="text/javascript" src="/js/ic.js"></script>
		<script type="text/javascript" src="/js/qrcode.js"></script>
		<script type="text/javascript" src="/js/jquery.qrcode.js"></script>
		<link rel="stylesheet" type="text/css" href="/css/ic.css" />
	</head>
	
	<body>
		<ul id="navigation">
			<li>
				<a onclick="showRegistration();">Register</a>
				<div id="registration">
					<a onclick="showRegistration();">[x]</a><br />
					<a onclick="getRegistration();">Download (int-bar.ictd)</a>
					<div id="qr_code" style="width:200px;height:200px;margin-top:15px;" ></div><br />
					<iframe id="load_registration"></iframe>
					
				</div>
			
			</li>
			<li><a href="/sources/">Sources</a></li>
			<li><a href="/submissions/">Submissions</a></li>
			<li><a href="/documentation/">Documentation</a></li>
		</ul>
		
		<div id="container">
		
			<div id="response_dump">
				<p>API Output: <a id="rd_control" onclick="expandOutput();">[expand]</a></p>
				<textarea></textarea>
			</div>
			
			<?php
				$c = array_diff(explode("/", $_SERVER['REQUEST_URI']) ,array(""));
				if($_SERVER['QUERY_STRING'] == "" && count($c) == 1) { ?>
					<p>Filter: <a id="filter_control" onclick="expandFilter();">[expand]</a></p>
					<div id="filter_holder"></div>
					
					<script>
						setFilter('<?= str_replace("/","",$_SERVER['REQUEST_URI']) ?>');
					</script>
			<?php } ?>
			
			<?= $layout->dump ?>
		
			<div id="response_visualizer"></div>
			<?= $layout->viz ?>
		
		</div>
	</body>
</html>