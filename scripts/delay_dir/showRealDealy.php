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
$nTime = 2016021615;


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

print_r($result_arr);

/*
foreach ($jf_arr as $jf => $arr) 
{
	$count_arr = array();
	$count = count($arr);
	foreach ($arr as $index => $ip) 
	{
		print ("ip:".$ip."\n");
		$detail_arr = $ip_msg[$ip];
		print("detail:\n");
		print_r($detail_arr);
		foreach ($detail_arr as $isp => $provice_arr) 
		{
			if (array_key_exists($isp, $count_arr) == false)
			{
				$count_arr[$isp] = array();
			}
			foreach ($provice_arr as $provice => $OvertimeRate) 
			{
				if (array_key_exists($provice, $count_arr[$isp]) == false)
				{
					$count_arr[$isp][$provice] = 0.00;
				}
				$count_arr[$isp][$provice] += $OvertimeRate;
			}
		}
	}

	foreach ($count_arr as $isp => $provice_arr) {
		# code...
		foreach ($provice_arr as $provice => $OvertimeRate) {
			# code...
			$count_arr[$isp][$provice] = $count_arr[$isp][$provice] / $count;
		}
	}

	$result_arr[$jf] = $count_arr;

}

print_r($result_arr);
*/

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