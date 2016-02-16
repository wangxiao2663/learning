<?php

define("_DOC_ROOT", dirname(__FILE__));
require_once(_DOC_ROOT."/config.php");
require_once(_DOC_ROOT."/common.php");

define('_SERVER_IP', '192.168.200.132');
define('_SERVER_PORT', 9501);

define('_START_HEAD', 'fdfdfdfd');
define('_END_TAIL', 'DONEDONEDONE');

$recv_msg_arr = array();

$redis = new Redis();
connect($redis);

$serv = new swoole_server(_SERVER_IP, _SERVER_PORT); 
$serv->on('connect', function ($serv, $fd) {  
    echo "Client: Connect.\n";
});

$serv->on('receive', function ($serv, $fd, $from_id, $data) {
    $serv->send($fd, "ok");
    global $recv_msg_arr;
    if(strlen($data) < 20)
    {
        if(strcmp($data, _START_HEAD) == 0)
        {
            echo "hello.\n";
            $recv_msg_arr[$fd] = "";
        }
        if(strcmp($data, _END_TAIL) == 0)
        {
            echo "done!\n";
            Analysis($recv_msg_arr[$fd]);
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
    echo "Client: Close.\n";
});

$serv->start(); 




function Analysis($data)
{
	global $redis;
	try 
	{
		$from_ip = strchr($data,":",true);
    	$message = substr($data, strlen($from_ip) + 1);
        stripslashes($message);
    	$Now = date("YmdH");

        $redis->set($from_ip, $message);

        $hisKey = $from_ip."_".$Now;
        $redis->set($hisKey, $message);
        $redis->expire($hisKey, 3600 * 48);

    	$msg = $redis->get($from_ip);
    }
    catch (Exception $e)
    {
   		echo "error!";
    }
}



function Send($data_array)
{

}

?>