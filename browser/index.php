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
			<td colspan="2"><b>ID</b></td>
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
	
	$d = json_decode($dump);
	
	$layout = new SimpleLayout($dump);
	$layout->title = "Viewing Submission: " . $submission_id;
	$layout->viz = <<<EOH
	<div id="submissionList"></div>
	<script>
		render('{$dump}', 'submission', 'submissionList');
		setJ3MDump('{$submission_id}/{$d->data->j3m}');
	</script>
EOH;
	
	include "layouts/container.php";
});

$app->get('/informacam/', function() {
	$i_get = new IGet();
	$i_get->setUrl("http://localhost:6666/public/");
	$res = json_decode($i_get->perform());
		
	header('Content-disposition: attachment; filename=int-bar.ictd');
	header('Content-type: application/ictd');

	echo json_encode($res->data);
});

// THIS WON'T BE NECESSARY
$app->get('/documentation/', function() {
	$layout = new SimpleLayout(null);
	$layout->title = "InformaCam Documents";
	
	$doc_root = 'http://ec2-54-235-36-217.compute-1.amazonaws.com:8080';
	$layout->viz = <<<EOH
	<script>
		$("#response_dump").css('display','none');
	</script>
	<ul>
		<li><a href="{$doc_root}/api/html/index.html">Data API Docs</a></li>
		<li><a href="{$doc_root}/server/html/index.html">Server API Docs</a></li>
		<li><a href="https://github.com/harlo/InformaCam-Service" target="_blank">Codebase</a></li>
		<li><a href="https://dev.guardianproject.info/projects/informacam/wiki/">Wiki</a></li>
	</ul>
EOH;
	
	include "layouts/container.php";
});

// THIS IS HORRIBLE!!!
$app->get('/js/:file', function($file) {
	echo file_get_contents('js/' . $file);
});

// THIS IS ALSO HORRIBLE!!!
$app->get('/css/:file', function($file) {
	echo file_get_contents('css/' . $file);
});

// THIS IS ALSO HORRIBLE!!!
$app->get('/layouts/:file', function($file) {
	echo file_get_contents('layouts/' . $file);
});

// THIS IS ALSO HORRIBLE!!!
$app->get('/media/:path/:file/', function($path, $file) {
	if(preg_match('/.ogv/i', $file)) {
		header('Content-type: video/ogg');
	}
	
	if(preg_match('/.mp4/i', $file)) {
		header('Content-type: video/mp4');
	}
	
	echo file_get_contents('/home/ubuntu/assets/submissions/' . $path . '/' . $file);
});

$app->run();

?>
