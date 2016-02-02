<?php

#version 1.0 

    define('YYBTB_XML', dirname(__FILE__)."/yybtb.xml"); 

    $req_list = array();
	$count = ParseConfigFile($req_list);
#    $i = 0;
  
    $workers = [];
#	$worker_num = $count;//创建的进程数

 

	function shutdown() {
  	  posix_kill(posix_getpid(), SIGHUP);
	}
	


echo my_ping('www.baidu.com', 80, 1);
	$ip = 0;
	$port = 0;
	$index = 0;

    for($i = 0; $i < sizeof($req_list); $i++)
    {
    	$ip = $req_list[$i]['mobileip'];
    	for($j = 0; $j < sizeof($req_list[$i]['port']); $j++)
    	{
    		$port = $req_list[$i]['port'][$j];
    	}
//	  	echo my_ping($ip, $port, 1);
	}


function ParseConfigFile(&$req_list)
{
    $xml = simplexml_load_file(YYBTB_XML);
  
    $i = 0;
    $count = 0;
//    $req_list = array();
    foreach($xml->children() as $child)
    {
        foreach ($child->attributes() as $key => $value) 
        {
            if (strcmp((string)$key, 'mobileip') == 0)
            {
              $req_list[$i]['mobileip'] = (string)$value;
            }
            else if (strcmp((string)$key, 'portlist') == 0)
            {
                if ($value != NULL && strlen($value) > 0) 
                {
                  	# code...
                	$str_array = explode("|", $value);
                	//print_r($str_array);
                	$index = 0;
                   	for($j = 0; $j < sizeof($str_array); $j++)
                	{
                		$str = strstr($str_array[$j], ",");
                		$str = substr($str, 1, strlen($str) - 1);
                		if ($str != NULL)
                		{
                			$req_list[$i]['port'][$index] = (int)$str;
                			$index++;
                			$count++;
                		}
                	}
                }
            }
#           $req_list[$i][(string)$key] = iconv('utf-8', 'gbk', (string)$b);
        }
        $i++;
    }
    return $count;
}

function GetProt($str)
{
	$str_array = explode($str);
}

function StartPing($ip, $port, $result)
{
  	$result_arr = array();
  	$ret_arr = array();
  	for($i = 0; $i <sizeof($req_list); $i++)
  	{
  			$command = sprintf("python tcping.py %s %s", $req_list[$i]['mobileip'], '8002');
  			exec($command, $result_arr[$i], $ret_arr[$i]);
  			echo $i."\n";
  	}
  	sleep(1);
  	print_r($result_arr[$i]);
}


function my_ping($host, $port, $timeout) 
{ 
  	$tB = microtime(true); 
  	if($fp = fsockopen($host,$port,$errCode,$errStr,$waitTimeoutInSeconds))
  	{   
   	// It worked   
  		$tA = microtime(true); 
  		return round((($tA - $tB) * 1000), 0)." ms"; 
	} 
	else 
	{
	   // It didn't work 
		 return "down";
	} 



}
?>