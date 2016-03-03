<?php

define("_DOC_ROOT", dirname(__FILE__));
require_once(_DOC_ROOT."/config.php");
require_once(_DOC_ROOT."/common.php");

$jf_arr = array();
$jf_num = array();
$ip_msg = array();

$redis = new Redis();
connect($redis);

$nTime = _POST["time"];
$nTime = 2016030216;


foreach ($master as $ip => $jf) 
{
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
	if (array_key_exists($jf,$jf_arr) == false)
	{
		$jf_num[$jf] = 0;
	}
	$jf_arr[$jf][$jf_num[$jf]] = $ip;
	$jf_num[$jf] += 1;
}

$result_arr = array();

foreach ($jf_arr as $jf => $arr) 
{

	if (array_key_exists($jf, $result_arr) == false)
	{
		$result_arr[$jf] = array();
	}
	foreach ($arr as $index => $ip) 
	{
		if (array_key_exists($ip, $ip_msg) == false)
		{
			$result_arr[$jf][$ip] = "";
		}
		else
		{
			$result_arr[$jf][$ip] = $ip_msg[$ip];
		}
	}

}

//print_r($result_arr);


$avg_arr = array();

foreach ($result_arr as $jf => $ip_arr) 
{
	$ip_count = 0;
	$avg_arr[$jf] = array();
	foreach ($ip_arr as $ip => $isp_arr) 
	{
		if (empty($isp_arr))
		{
			continue;
		}
		else
		{
			$ip_count++;
		}
		foreach ($isp_arr as $isp => $provice_arr) 
		{
			$avg_arr[$jf][$isp] = array();
			foreach ($provice_arr as $provice => $value) 
			{
				if (array_key_exists($provice, $avg_arr[$jf][$isp]))
				{
					$avg_arr[$jf][$isp][$provice] += $value;
				}
				else
				{
					$avg_arr[$jf][$isp][$provice] = $value;
				}
			}
		}
	}

	if ($ip_count == 0)
	{
		continue;
	}

	foreach ($avg_arr as $jf => $isp_arr) 
	{
		# code...
		foreach ($isp_arr as $isp => $provice_arr) 
		{
			# code...
			foreach ($provice_arr as $provice => $value) 
			{
				# code...
				$avg_arr[$jf][$isp][$provice] = $value / $ip_count;
			}
		}
	}
}

print_r($avg_arr);


function Analysis($xmlMsg)
{
	$arr = array();
	$delayMessage = $xmlMsg->delayMessage;
	foreach ($delayMessage->children() as $isp => $detailMsg) {
		# code...
		foreach ($detailMsg->children() as $item => $value) {
			# code...
			$provice = "".$value->provice;
			$OvertimeRate = "".$value->OvertimeRate;
			$arr[$isp][$provice] = $OvertimeRate;
		}
	}
	return $arr;
}





?>
