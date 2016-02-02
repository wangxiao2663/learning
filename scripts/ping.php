<?php
/*
 * @author     xujiajay
 * @date       2010-10-7
 * @function   可以ping端口的php函数
 *
 */
    error_reporting(E_ERROR);
    header("content-Type: text/html; charset=utf-8");
    set_time_limit(120);
    $host = isset($_POST['url']) ? chop(str_replace('http://','',$_POST['url'])) : 'www.baidu.com';
    $port = isset($_POST['duankou']) ? chop($_POST['duankou']) : '80';
    $num  = 10;

    echo ping('www.baidu.com','80');
    function microtime_float()
    {
            list($usec, $sec) = explode(" ", microtime());
            return ((float)$usec + (float)$sec);
    }
    function getsoft($host,$port)
    {
    	$errno;
    	$errstr;
            $fp = fsockopen($host,$port,$errno,$errstr,3);
            if(!$fp) return 'unknown';
            $get = "GET / HTTP/1.1\r\nHost:".$host."\r\nConnection: Close\r\n\r\n";
            @fputs($fp,$get);
            $data = '';
            while ($fp && !feof($fp))
            $data .= fread($fp, 1024);
            @fclose($fp);
            $array = explode("\n",$data);
            $k = 2;
            for($i = 0;$i < 20;$i++)
            {
                    if(stristr($array[$i],'Server')){$k = $i; break;}
            }
            if(!stristr($array[$k],'Server')) return 'unknown';
            else return str_replace('Server','服务器软件',$array[$k]);
    }
    function ping($host,$port)
    {
    		$errno;
    	$errstr;
            $time_start = microtime_float();
            $ip = gethostbyname($host);
            $fp = fsockopen($host,$port,$errno,$errstr,1);
            if(!$fp) return 'Request timed out.'."\r\n";
            $get = "GET / HTTP/1.1\r\nHost:".$host."\r\nConnection: Close\r\n\r\n";
            @fputs($fp,$get);
            @fclose($fp);
            $time_end = microtime_float();
            $time = $time_end - $time_start;
            $time = ceil($time * 1000);
            return 'Reply from '.$ip.': time='.$time.'ms';
    }
    if(isset($_POST['url']) && isset($_POST['duankou']))
    {
            echo '<font color="#FF0000">'.getsoft($host,$port).'</font>';
            echo 'Pinging '.$host.' ['.gethostbyname($host).'] with Port:'.$port.' of data:'."\r\n";
            ob_flush();
            flush();
            for($i = 0;$i < $num;$i++)
            {
                    echo ping($host,$port);
                    ob_flush();
                    flush();
                    sleep(1);
            }
    }
?>