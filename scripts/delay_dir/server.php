<?php

define("_DOC_ROOT", dirname(__FILE__));
require_once(_DOC_ROOT."/config.php");
require_once(_DOC_ROOT."/common.php");

$recv_msg_arr = array();

$redis = new Redis();
connect($redis);

$serv = new swoole_server("127.0.0.1", 9501); 
$serv->on('connect', function ($serv, $fd) {  
    echo "Client: Connect.\n";
});

$serv->on('receive', function ($serv, $fd, $from_id, $data) {
    $serv->send($fd, "ok");
    global $recv_msg_arr;
    print 'recv len = '.strlen($data)."\n";
    if(strlen($data) < 20)
    {
      if(strcmp($data, "hello") == 0)
      {
        print 'hello\n';
        $recv_msg_arr[$fd] = "";
      }
      if(strcmp($data, "donedonedone!") == 0)
      {
        print 'donedonedone\n';
        Analysis($data);
      }
    }
    else
    {
      $recv_msg_arr[$fd] = $recv_msg_arr[$fd].$data;
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
    	$Now = date("Y-m-d_H:i");
    	$redis->set($from_ip, $message);

      echo "\n";
      echo "msg:".strlen($message)."\n";

    	$msg = $redis->get($from_ip);
      echo "\n";
    	print("get:".strlen($msg)."\n");
    	
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