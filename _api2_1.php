<?php
$callback = (string)$_GET['callback'];
if (!$callback) $callback = 'callback';

//CallAPI('GET', 'http://localhost:5000/bcx-web/api/v1.0/btc/series/price');
$url = "http://localhost:5000/bcx-web/api/v1.0/btc/series/price";

//function CallAPI($method, $url, $data = false)
//{
	
	$json1 = file_get_contents($url);
	$json2 = json_encode($json1);

	$array = array(7,4,2,8,4,1,9,3,2,16,7,12);
	//echo $_GET['callback']. '('. json_encode($json1, JSON_PRETTY_PRINT) . ')'; 
	
	header('Content-Type: text/javascript');
	echo "$callback($json1);";
	
	//echo json_decode($result, true);
//}

?>