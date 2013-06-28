<?php

error_reporting(E_ALL);

require 'slim/Slim/Slim.php';
\Slim\Slim::registerAutoloader();

require 'funcs.php';

$app = new \Slim\Slim(array(
	'debug' => true,
));

$app->get('/', function() {
	$layout = new SimpleLayout(null);
	$layout->title = "InformaCam API Browser";
	
	$layout->viz = <<<EOH
	<script>
		$("#response_dump").css('display','none');
	</script>
EOH;
	
	include "layouts/container.php";
});

$app->get('/sources/', function() {
	$i_get = new IGet();
	$i_get->setUrl("http://localhost:6666/sources/");

	$dump = $i_get->perform();
	
	$layout = new SimpleLayout($dump);
	$layout->title = "All Sources";

	$layout->viz = <<<EOH
	<table id="sourceList">
		<tr>
			<td><b>ID</b></td>
			<td><b>PGP Fingerprint</b></td>
			<td colspan="2"><b>Date Admitted</b></td>
		</tr>
	</table>
	<script>
		render('{$dump}', 'sources', 'sourceList');
	</script>
EOH;
	
	include "layouts/container.php";
});

$app->get('/submissions/', function() {
	$i_get = new IGet();
	$i_get->setUrl("http://localhost:6666/submissions/");
	$dump = $i_get->perform();
	
	$layout = new SimpleLayout($dump);
	$layout->title = "All Submissions";
	
	$layout->viz = <<<EOH
	<table id="submissionList">
		<tr>
			<td><b>ID</b></td>
			<td><b>File Name</b></td>
			<td colspan="2"><b>Date Admitted</b></td>
		</tr>
	</table>
	<script>
		render('{$dump}', 'submissions', 'submissionList');
	</script>
EOH;
	
	include "layouts/container.php";
});

$app->get('/source/:source_id/', function($source_id) {
	$i_get = new IGet();
	$i_get->setUrl("http://localhost:6666/source/" . $source_id . "/");
	$dump = $i_get->perform();
	
	$layout = new SimpleLayout($dump);
	$layout->title = "Viewing Source: " . $source_id;
	$layout->viz = <<<EOH
	<div id="sourceList"></div>
	<script>
		render('{$dump}', 'source', 'sourceList');
	</script>
EOH;
	
	include "layouts/container.php";
});

$app->get('/submission/:submission_id/', function($submission_id) {
	$i_get = new IGet();
	$i_get->setUrl("http://localhost:6666/submission/" . $submission_id . "/");
	$dump = $i_get->perform();
	
	$layout = new SimpleLayout($dump);
	$layout->title = "Viewing Submission: " . $submission_id;
	$layout->viz = <<<EOH
	<div id="submissionList"></div>
	<script>
		render('{$dump}', 'submission', 'submissionList');
	</script>
EOH;
	
	include "layouts/container.php";
});

// THIS IS HORRIBLE!!!
$app->get('/js/:file', function($file) {
	echo file_get_contents('js/' . $file);
});

$app->get('/css/:file', function($file) {
	echo file_get_contents('css/' . $file);
});

$app->get('/layouts/:file', function($file) {
	echo file_get_contents('layouts/' . $file);
});

$app->get('/media/:path/:file/', function($path, $file) {
	echo file_get_contents('/home/ubuntu/assets/submissions/' . $path . '/' . $file);
});

$app->run();

?>