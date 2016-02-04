<?php

define ('REDIS_IP','127.0.0.1');
define ('REDIS_PORT', 6379);
define ('PASSPORT', 'panyongzhi');
define ('DB',0);

$redis = new Redis();  
$redis->connect(REDIS_IP,REDIS_PORT);
$redis->auth(PASSPORT);
$redis->select(DB);


$serv = new swoole_server("127.0.0.1", 9501); 

$serv->on('connect', function ($serv, $fd) {  
    echo "Client: Connect.\n";
});

$serv->on('receive', function ($serv, $fd, $from_id, $data) {
    $serv->send($fd, "ok");
    $key = strchr($data,":",true);
    $value = substr($data, strlen($key) + 1);
    global $redis;
    $redis->set($key, $value);
});

$serv->on('close', function ($serv, $fd) {
    echo "Client: Close.\n";
});

$serv->start(); 

?>