<?php

define("_DOC_ROOT", dirname(__FILE__));
require_once(_DOC_ROOT."/config.php");
$jf_arr = array();
$index = 0;

foreach ($master as $ip => $jf) 
{
	if (in_array($jf, $jf_arr))
	{
		continue;
	}
	else
	{
		$jf_arr[$index] = $jf;
		$index++;
	}
}


print_r($jf_arr);

?>