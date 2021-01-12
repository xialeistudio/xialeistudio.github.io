---
layout: post
title: php利用百度地图API进行IP定位和GPS定位
date: 2015-01-12 01:12:57.000000000 +08:00
type: post
published: true
status: publish
categories:
- backend
- php
---
最近在做一个手机端的webapp地图应用，而核心内容当然是定位了，但是定位的话有几种方式，IP定位,GPS定位，基站定位（这个貌似webapp用不了），

那么剩下核心的gps定位和ip定位了，我们知道，html5有定位API，但是该API拿到的GPS数据是硬件坐标，无法直接显示在地图上。

后来上百度LBS云看到有地图IP定位API和GPS坐标转换API，地址：http://developer.baidu.com/map/

百度地图API的调用需要申请KEY，这里就不具体介绍了，直接贴上本人写了两个关键方法，为了方便前台调用，返回数据采用以下格式：

```javascript
{
    address: "北京市海淀区西二旗北路",
    province: "北京市",
    city: "北京市",
    street: "西二旗北路",
    street_number: "",
    city_code: 131,
    lng: 116.3207676804,
    lat: 40.064084055578
}
```

## PHP代码

```php
<?php

/**
 * @author xialei <xialeistudio@gmail.com>
 */
class map
{
 private static $_instance;

 const REQ_GET = 1;
 const REQ_POST = 2;

 /**
  * 单例模式
  * @return map
  */
 public static function instance()
 {
  if (!self::$_instance instanceof self)
  {
   self::$_instance = new self;
  }
  return self::$_instance;
 }

 /**
  * 执行CURL请求
  */
  protected function async($api,array $params)
  {
    $ch = curl_init($api.'?'.http_build_query($params));
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
    $resp = curl_exec($ch);
    curl_close($ch);
    return $resp;
 }

 /**
  * ip定位
  * @param string $ip
  * @return array
  * @throws Exception
  */
 public function locationByIP($ip)
 {
  //检查是否合法IP
  if (!filter_var($ip, FILTER_VALIDATE_IP))
  {
   throw new Exception('ip地址不合法');
  }
  $params = array(
    'ak' => '百度地图API KEY',
    'ip' => $ip,
    'coor' => 'bd09ll'//百度地图GPS坐标
  );
  $api = 'http://api.map.baidu.com/location/ip';
  $resp = $this->async($api, $params);
  $data = json_decode($resp, true);
  //有错误
  if ($data['status'] != 0)
  {
   throw new Exception($data['message']);
  }
  //返回地址信息
  return array(
    'address' => $data['content']['address'],
    'province' => $data['content']['address_detail']['province'],
    'city' => $data['content']['address_detail']['city'],
    'district' => $data['content']['address_detail']['district'],
    'street' => $data['content']['address_detail']['street'],
    'street_number' => $data['content']['address_detail']['street_number'],
    'city_code' => $data['content']['address_detail']['city_code'],
    'lng' => $data['content']['point']['x'],
    'lat' => $data['content']['point']['y']
  );
 }


 /**
  * GPS定位
  * @param $lng
  * @param $lat
  * @return array
  * @throws Exception
  */
 public function locationByGPS($lng, $lat)
 {
  $params = array(
    'coordtype' => 'wgs84ll',
    'location' => $lat . ',' . $lng,
    'ak' => '百度地图API KEY',
    'output' => 'json',
    'pois' => 0
  );
  $resp = $this->async('http://api.map.baidu.com/geocoder/v2/', $params, false);
  $data = json_decode($resp, true);
  if ($data['status'] != 0)
  {
   throw new Exception($data['message']);
  }
  return array(
    'address' => $data['result']['formatted_address'],
    'province' => $data['result']['addressComponent']['province'],
    'city' => $data['result']['addressComponent']['city'],
    'street' => $data['result']['addressComponent']['street'],
    'street_number' => $data['result']['addressComponent']['street_number'],
    'city_code'=>$data['result']['cityCode'],
    'lng'=>$data['result']['location']['lng'],
    'lat'=>$data['result']['location']['lat']
  );
 }
}
```