<?php

ini_set('default_socket_timeout', -1);

define("_DOC_ROOT", dirname(__FILE__));
require_once(_DOC_ROOT."/config.php");
require_once(_DOC_ROOT."/common.php");

define('_SERVER_IP', '192.168.200.132');
define('_SERVER_PORT', 9501);

define('_START_HEAD', 'fdfdfdfd');
define('_END_TAIL', 'DONEDONEDONE');

$recv_msg_arr = array();

$serv = new swoole_server(_SERVER_IP, _SERVER_PORT); 
$serv->on('connect', function ($serv, $fd) {  
    echo "Connect : ".$fd."\n";
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

    $redis = new Redis();
    connect($redis);
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
        do
        {
    	   $Now = date("YmdH");
            $retCode = $redis->set($from_ip, $message);
            if ($retCode != true)
            {
            	break;
            }
            $hisKey = $from_ip."_".$Now;
            $retCode = $redis->set($hisKey, $message);
            if ($retCode != true)
            {
            	break;
            }
            $retCode = $redis->expire($hisKey, 3600 * 48);
            if ($retCode != true)
            {
            	break;
            }
        }
        while(0);
        unset($redis);
    }
    catch (Exception $e)
    {
        foreach ($recv_msg_arr as $key => $value) 
        {
            $recv_msg_arr[$key] = "";
        }
        echo "error!";
		unset($redis);
    }
}


?>
