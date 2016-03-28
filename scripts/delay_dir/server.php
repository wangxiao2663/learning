<?php

ini_set('default_socket_timeout', -1);

define("_DOC_ROOT", dirname(__FILE__));
require_once(_DOC_ROOT."/config.php");
require_once(_DOC_ROOT."/common.php");

define('_SERVER_IP', '172.31.60.33');
define('_SERVER_PORT', 9888);

define('_START_HEAD', 'fdfdfdfd');
define('_END_TAIL', 'DONEDONEDONE');

$recv_msg_arr = array();

$redis = new Redis();
connect($redis);

$serv = new swoole_server(_SERVER_IP, _SERVER_PORT); 
$serv->on('connect', function ($serv, $fd) {  
    #echo "Connect : ".$fd."\n";
    $recv_msg_arr[$fd] = "";
});

$serv->on('receive', function ($serv, $fd, $from_id, $data) {
    $serv->send($fd, "ok");
    global $recv_msg_arr;
    if(strlen($data) < 20)
    {
        if(strcmp($data, _START_HEAD) == 0)
        {
            $recv_msg_arr[$fd] = "";
        }
        if(strcmp($data, _END_TAIL) == 0)
        {
            Analysis($recv_msg_arr[$fd]);
            $recv_msg_arr[$fd] = "";
        }
    }
    else
    {
        if (array_key_exists($fd, $recv_msg_arr) == true)
        {
            $recv_msg_arr[$fd] = $recv_msg_arr[$fd].$data;
        }
    }
    
});

$serv->on('close', function ($serv, $fd) {
    echo "Client ".$fd." : Close.\n";
    $recv_msg_arr[$fd] = "";
    unset($recv_msg_arr[$fd]);
});

$serv->start();




function Analysis($data)
{
	global $redis;
	$from_ip = "";
	$message = "";

	try 
	{
		$from_ip = strchr($data,":",true);
    	$message = substr($data, strlen($from_ip) + 1);
    }
    catch (Exception $e)
    {
    	echo "mem error!\n";
		return;
    }
	if (empty($from_ip) || $from_ip == "" || strlen($from_ip) == 0)
	{
		echo "empty !!!\n";
		return;
	}
	
	
    try
    {
    	$Now = date("YmdH");
        $retCode = $redis->set($from_ip, $message);
        if ($retCode != 1)
        {
        	print('1.set error, retcode = '.$retCode."\n");
        	#resetRedis();
        	return;
        }
        $hisKey = $from_ip."_".$Now;
        $retCode = $redis->set($hisKey, $message);
        if ($retCode != 1)
        {
        	print('2.set error, retcode = '.$retCode."\n");
        	#resetRedis();
        	return;
        }
        $retCode = $redis->expire($hisKey, 3600 * 48);
        if ($retCode != 1)
        {
        	print('3.expire error, retcode = '.$retCode."\n");
        	#resetRedis();
        	return;
        }
    }
    catch (Exception $e)
    {
        foreach ($recv_msg_arr as $key => $value) 
        {
            $recv_msg_arr[$key] = "";
        }
        echo "error!";
		resetRedis();
    }
}


function resetRedis()
{
	global $redis;
	$redis->close();
	unset($GLOBALS['redis']);
	global $redis;
	$redis = new Redis();
	connect($redis);
}

?>
