<?php

define("_DOC_ROOT", dirname(__FILE__));
require_once(_DOC_ROOT."/config.php");
require_once(_DOC_ROOT."/common.php");

$jf_arr = array();
$ip_msg = array();

$redis = new Redis();
connect($redis);

$nTime = _POST["time"];
$nTime = 2016031211;
$site = _POST["site"];
$isp = _POST["isp"];
$provice = _POST["provice"];
$g_site = "测试服务器";
$g_isp = "CU";
$g_provice = "12";




foreach ($master as $ip => $jf) 
{
	if (strcmp($g_site, $jf) != 0)
	{
		continue;
	}
	if ($nTime == 0)
	{
		$key = $ip;
	}
	else
	{
		$key = $ip."_".$nTime;
	}

	$msg = $redis->get($key);
	if ($msg != NULL)
	{
		$xmlMsg = simplexml_load_string($msg);
		$ip_msg[$ip] = Analysis($xmlMsg);
	}

}

print_r($ip_msg);


function Analysis($xmlMsg)
{
	global $g_sit;
	global $g_isp;
	global $g_provice;

	$arr = array();
	$delayMessage = $xmlMsg->delayMessage;
	foreach ($delayMessage->children() as $isp => $SummaryMsg) 
	{
		# code...
		if (strcmp($g_isp, $isp) != 0)
		{
			continue;
		}
		foreach ($SummaryMsg->children() as $item => $value) 
		{
			# code...
			$provice = "".$value->provice;
			if (strcmp($provice, $g_provice) != 0)
			{
				continue;
			}
			$detailMsg = $value->detailMsg;
			//$arr[$isp][$provice] = array();
			$index = 0;
			foreach ($detailMsg->children() as $item2 => $detail) 
			{
				# code...
				$detail_arr = array();
				$detail_arr["ip"] = "".$detail->ip;
				$detail_arr["port"] = "".$detail->port;
				$detail_arr["result"] = "".$detail->result;

				$qsList = $detail->QsList;
				$qs_arr = array();
				$i = 0;
				foreach ($qsList->children() as $qsInfo => $Property) 
				{
					# code...
					$qsinfo_arr = array();
					$qsinfo_arr["qsid"] = "".$Property->qsid;
					$qsinfo_arr["wtid"] = "".$Property->wtid;
					$qsinfo_arr["yybname"] = "".$Property->yybname;
					$qsinfo_arr["area"] = "".$Property->area;
					$qsinfo_arr["qsname"] = "".$Property->qsname;
					$qs_arr[$i] = $qsinfo_arr;
					$i = $i + 1;
				}

				$detail_arr["qsList"] = $qs_arr;
				$arr[$index] = $detail_arr;
				$index = $index + 1;
			}


			
		}
	}


	return $arr;
}





?>
