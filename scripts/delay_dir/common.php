<?php

define ('REDIS_IP','127.0.0.1');
define ('REDIS_PORT', 6379);
define ('PASSPORT', 'sjcg@hexin');
define ('DB',0);

function connect(Redis &$redis)
{
	try
	{
		$redis->connect(REDIS_IP,REDIS_PORT);
		$redis->auth(PASSPORT);
		$redis->select(DB);
	}
	catch (Exception $e)
	{
		echo "can't connect to redis-server".REDIS_IP.":".REDIS_PORT."\n";
		exit();
	}
}


?>
