<?php

$GLOBALS = array(
	'res' => array(
		'fail' => 503,
		'ok' => 200
	)
);

class SimpleLayout {
	public $title;
	public $body;
	public $dump;
	public $viz;
	
	public function __construct($dump) {
		if($dump != null) {
			$this->dump = <<<EOH
		<script>
			setResponseDump('{$dump}');
		</script>
EOH;
		}
	}	
}

class IGet {
	public $res;
	public $c;
	private $parameters;
	private $url;
	
	public function __construct() {
		$this->c = curl_init();
		
		curl_setopt($this->c, CURLOPT_HEADER, 0);
		curl_setopt($this->c, CURLOPT_VERBOSE, true);
		curl_setopt($this->c, CURLOPT_RETURNTRANSFER, 1);
		curl_setopt($this->c, CURLOPT_HTTPHEADER,array('Content-Type: application/json'));
		
		$this->parameters = array();
	}
	
	public function setUrl($url) {
		$this->url = $url;
	}
	
	public function setParam($param) {
		foreach($param as $k=>$v) {
			array_push($this->parameters, ($k . "=" . $v));
		}
	}
	
	public function perform() {
		if(count($this->parameters) > 0) {
			$this->url .= ("?" . join($this->parameters, "&"));
		}
	
		curl_setopt($this->c, CURLOPT_URL, $this->url);
		$this->res = curl_exec($this->c);
		curl_close($this->c);
		return $this->res;
	}
}

class IPost {
	public $res;
	public $c;
	private $post_data;
	private $post_files;
	
	public function __construct() {
		$this->c = curl_init();
		
		curl_setopt($this->c, CURLOPT_HEADER, 0);
		curl_setopt($this->c, CURLOPT_VERBOSE, true);
		curl_setopt($this->c, CURLOPT_RETURNTRANSFER, 1);
		curl_setopt($this->c, CURLOPT_HTTPHEADER,array('Content-Type: application/json'));
		
		$this->post_data = new stdclass;
	}
	
	public function setUrl($url) {
		curl_setopt($this->c, CURLOPT_URL, $url);
	}
	
	public function setParams($params) {
		foreach($params as $k=>$p) {
			$this->post_data->$k = $p;
		}
	}
	
	public function perform() {
		if(count($this->post_data) > 0) {
			curl_setopt($this->c, CURLOPT_POSTFIELDS, json_encode($this->post_data));
		}
	
		$this->res = curl_exec($this->c);
		curl_close($this->c);
		return $this->res;
	}
}

?>