<html>
	<head>
		<title><?= $layout->title ?></title>
		<script type="text/javascript" src="/js/jquery.js"></script>
		<script type="text/javascript" src="/js/mustache.js"></script>
		<script type="text/javascript" src="/js/ic.js"></script>
		<link rel="stylesheet" type="text/css" href="/css/ic.css" />
	</head>
	
	<body>
		<ul id="navigation">
			<li><a href="/sources/">Sources</a></li>
			<li><a href="/submissions/">Submissions</a></li>
			<li><a href="http://ec2-54-235-36-217.compute-1.amazonaws.com:8080">Documentation</a></li>
		</ul>
		
		<div id="container">
		
			<div id="response_dump">
				<p>API Output: <a id="rd_control" onclick="expandOutput();">[expand]</a></p>
				<textarea></textarea>
			</div>
			<?= $layout->dump ?>
		
			<div id="response_visualizer"></div>
			<?= $layout->viz ?>
		
		</div>
	</body>
</html>