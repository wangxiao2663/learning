<?php

	$redis = new Redis();  
	$redis->connect('127.0.0.1',6379);  
	echo $redis->auth('panyongzhi');
	$redis->set('test','123456');  
	echo $redis->get('test');  

	print 'error'


?>

