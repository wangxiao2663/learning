<?php

define("_DOC_ROOT", dirname(__FILE__));
require_once(_DOC_ROOT."/config.php");
require_once(_DOC_ROOT."/common.php");

$jf_arr = array();
$ip_msg = array();

$redis = new Redis();
connect($redis);

$nTime = $_POST["time"];
$nQsid = $_POST["qsid"];
$g_nqsid = $nQsid;


$g_arrData = array();
foreach ($master as $ip => $jf) 
{
	if (!array_key_exists($jf, $g_arrData))
	{
		$g_arrData[$jf] = array();
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
		$ip_arr = analysis($xmlMsg);
		if (sizeof($ip_arr) > 0)
		{
			$g_arrData[$jf][$ip] = $ip_arr;
		}
	}
}

//print_r($g_arrData);
print_r('('.json_encode($g_arrData).')');
function analysis($xmlMsg)
{
	global $g_nqsid;

	$arr = array();
	$delayMessage = $xmlMsg->delayMessage;
	foreach ($delayMessage->children() as $isp => $SummaryMsg) 
	{			
		$nIndex = 0;
		foreach ($SummaryMsg->children() as $item => $value) 
		{
			$detailMsg = $value->detailMsg;
			foreach ($detailMsg->children() as $item2 => $detail) 
			{
				# code...
				$bQsId = 0;
				
				$qsList = $detail->QsList;
				$qsinfo = array();
				$i = 0;
				foreach ($qsList->children() as $qsInfo => $Property) 
				{
					if ($Property->qsid != $g_nqsid)
					{
						continue;
					}
					# code...
					$bQsId = 1;
					$qsinfo["qsid"] = "".$Property->qsid;
					$qsinfo["yybname"] = "".$Property->yybname;
					$qsinfo["qsname"] = "".$Property->qsname;
					$i = $i + 1;
					break;
				}
				if ($bQsId == 1)
				{
					$detail_arr = array();
					$detail_arr["ip"] = "".$detail->ip;
					$detail_arr["port"] = "".$detail->port;
					$detail_arr["result"] = "".$detail->result;
					$detail_arr["qsid"] = $qsinfo["qsid"];
					$detail_arr["yybname"] = $qsinfo["yybname"];
					$detail_arr["qsname"] = $qsinfo["qsname"];
					$arr[$nIndex] = $detail_arr;
					$nIndex++;
				}

			}
			
		}
	}


	return $arr;
}





?>
