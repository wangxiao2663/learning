<?php

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
    echo "Connect : ".$fd."\n";
});

$serv->on('receive', function ($serv, $fd, $from_id, $data) {
    $serv->send($fd, "ok");
    global $recv_msg_arr;
    if(strlen($data) < 20)
    {
        if(strcmp($data, _START_HEAD) == 0)
        {
        	echo "start receive from ".$fd."\n";
            $recv_msg_arr[$fd] = "";
        }
        if(strcmp($data, _END_TAIL) == 0)
        {
        	echo "end receive from ".$fd."\n";
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
        $redis->set($from_ip, $message);
        $hisKey = $from_ip."_".$Now;
        $redis->set($hisKey, $message);
		echo "set ".$hisKey."\n";
        $redis->expire($hisKey, 3600 * 48);
        echo "time : ".$Now.", ip : ".$from_ip."\n";
    }
    catch (Exception $e)
    {
        foreach ($recv_msg_arr as $key => $value) 
        {
            $recv_msg_arr[$key] = "";
        }
        echo "error!";
		$redis->close();
        connect($redis);
    }
}



?>
