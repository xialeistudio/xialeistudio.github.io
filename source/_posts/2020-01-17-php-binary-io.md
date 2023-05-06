---
title: kafka二进制协议简要分析
date: 2020-01-17 12:00:00
categories:
- Engineering
---



最近分享了《应用层私有协议的设计和实战》，对应用层私有协议设计做了一些介绍，同时也对协议设计中常用的数据类型做了比较形象的讲解，今天我们来研究一下kafka的二进制协议。

## 数据类型

kafka二进制协议定义了许多的数据类型，包含常用的数字、字符串，也包含了数组等类型。

本文主要讨论不可变长数据类型，可变长度（如Google Protocol Buffers）不在讨论范围内。

| 数据类型        | 字节长度 | 说明                                                         |
| --------------- | -------- | ------------------------------------------------------------ |
| BOOLEAN         | 1        | 布尔值                                                       |
| INT8            | 1        | 单字节整型，-2^7 ~ 2^7-1                                     |
| INT16           | 2        | 双字节整型，大端序，范围 -2^15 ~ 2^15 - 1                    |
| INT32           | 4        | 四字节整型、大端序，范围 -2^31 ~ 2^31 - 1                    |
| INT64           | 8        | 八字节整型、大端序，范围 -2^63 ~ 2^63 -1                     |
| UINT32          | 4        | 十字街                                                       |
| UUID            | 16       | 16字节，Java UUID类型                                        |
| STRING          | 2+N      | 头部由2字节标识字符串长度N，后续N字节为字符串内容            |
| NULLABLE_STRING | 2+N      | 头部由2字节标识字符串长度N，后续N字节为字符串内容，N为-1时无后续内容 |
| BYTES           | 4+N      | 头部4字节标识字节数组长度，后续N字节为字节数组内容           |
| NULLABLE_BYTES  | 4+N      | 头部4字节标识字节数组长度，后续N字节为字节数组内容，N为-1时无后续内容 |
| ARRAY           | 4+N*M    | 头部4字节标识数组长度N，M为单个数组元素的长度，N为-1时为空数组 |

## 错误码

+ -1 未知错误
+ 0 未出错
+ 大于0， 具体错误

kafka内置的操作类型有点多，有兴趣的可以参阅[kafka错误码](https://kafka.apache.org/protocol#protocol_error_codes)

## Api Keys

可以理解为操作码，服务端根据该字段区分当前请求操作。

这里不做展开，有兴趣的可以参阅[kafka Api Keys](https://kafka.apache.org/protocol#protocol_api_keys)

## 报文结构

接下来我们重点分析一下kafka的报文结构。

> 本文基于kafka V1版本协议写作，其他版本的研究原理时一致的。

### 整体结构

kafka的协议结构比较简单，请求和响应使用同样的整体结构。

```
RequestOrResponse => Size (RequestMessage | ResponseMessage)
  Size => int32
```

我们转化为表格来看看

![image-20200117172959642](https://static.ddhigh.com/blog/2020-01-17-093002.png)

+ Size为INT32类型，正文长度
+ Message 为请求或响应正文的内容，变长字段，长度由Size给出

### 请求格式

请求数据包有固定的请求包头，我们来看看。

```
Request Header v1 => request_api_key request_api_version correlation_id client_id 
  request_api_key => INT16
  request_api_version => INT16
  correlation_id => INT32
  client_id => NULLABLE_STRING
```

上面给出的是请求头的内容，结合整体结构得出的协议表格如下：

![image-20200117173117965](https://static.ddhigh.com/blog/2020-01-17-093119.png)

+ Size 4字节正文长度（包含请求头）
+ request_api_key 2字节 api key，用来区分操作
+ request_api_version 2字节api 版本号
+ correlation_id 4字节请求ID，服务端会原样响应该请求ID
+ client_id 可空字符串，根据kafka数据类型定义，需要2字节client_id length字段标识client_id长度，如果client_id length为-1，则不需要传具体的client_id，否则需要传递client_id
+ request message* 请求正文，不同的api key请求正文不同

### 响应格式

```
Response Header v1 => correlation_id TAG_BUFFER 
  correlation_id => INT32
```

响应头的结构比较简单，返回了请求ID

![image-20200117173658934](https://static.ddhigh.com/blog/2020-01-17-093701.png)

+ Size 4字节响应正文长度（包含请求ID）
+ correlation_id 4字节请求ID
+ response message* 响应正文

### Metadata 示例

#### 请求数据

Kafka Metadata对应的协议格式如下

```
Metadata Request (Version: 1) => [topics] 
  topics => name 
    name => STRING
```

我们转化为表格看看

![image-20200117173855988](https://static.ddhigh.com/blog/2020-01-17-093858.png)

+ Size 4字节请求正文长度
+ Request_api_key，根据协议文档， 此处为3
+ Request_api_version，本文基于v1版本写作，因此版本号为1
+ correlation_id 请求ID
+ client_id length 2字节客户端长度，我们使用test作为客户端标识，此处传入4
+ client_id 客户端名称，传入test字符串
+ topic name length 需要查询的topic数组，我们查询test1这个topic，此处传入1
+ topic name 字符串类型，因此先写入字符串长度5(test1字符串长度为5)，再写入test1字符串（总共写入2+5 = 7个字节）

#### 响应数据

```
Metadata Response (Version: 1) => [brokers] controller_id [topics] 
  brokers => node_id host port rack 
    node_id => INT32
    host => STRING
    port => INT32
    rack => NULLABLE_STRING
  controller_id => INT32
  topics => error_code name is_internal [partitions] 
    error_code => INT16
    name => STRING
    is_internal => BOOLEAN
    partitions => error_code partition_index leader_id [replica_nodes] [isr_nodes] 
      error_code => INT16
      partition_index => INT32
      leader_id => INT32
      replica_nodes => INT32
      isr_nodes => INT32
```

![image-20200117174211271](https://static.ddhigh.com/blog/2020-01-17-094212.png)

+ Size 4字节响应长度
+ Correlation_id 4字节请求ID
+ Broker Count，数组类型，4字节整型标识数组长度
  + node_id 4字节整型，broker的节点ID
  + host 字符串类型，主机名称
  + port 4字节整型，端口号
  + rack 可空字符串，如果broker是rack，则需要2+N字节，否则只需要2字节
+ Controller_id 4字节整型
+ Topics 数组类型，topic数组
  + error_code 2字节整型，错误码
  + name 字符串类型，topic名称
  + is_internal 布尔类型，是否内部topic
  + partions 数组类型，topic所在partition
    + error_code 2字节整型，错误码
    + partition_index 4字节整型，partition index
    + leader_id 4字节整型，leader id
    + Replica_nodes 数组类型
      + Replica_node 4字节整型
    + isr_nodes 数组类型
      + Isr_node 4字节整型



> 其他类型的请求也可以使用同样的方式去分析

## PHP客户端实现

PHP自带了pack/unpack函数帮助我们操作二进制数据，不过pack/unpack易用性比较低。

> 对于二进制数据，java有byte[]，golang有[]byte，PHP没有专门的类型，而是使用字符串存储的，不过PHP字符串是二进制安全的。

针对pack/unpack函数易用性问题，这两天参考Java的IO系统开发了一个简单版本的io库来简化二进制数据流的操作（文末有仓库地址）。

接下来使用该库来编写一个kafka的客户端。

```php
<?php
/**
 * 读取kafka broker列表
 */
require __DIR__ . '/../vendor/autoload.php';

use io\BinaryStringInputStream;
use io\BinaryStringOutputStream;
use io\DataInputStream;
use io\DataOutputStream;
use io\FileInputStream;
use io\FileOutputStream;

$client = stream_socket_client('tcp://127.0.0.1:9092', $errno, $errstr, 5);
if ($errno) {
    die($errstr);
}


$binaryOutputStream = new BinaryStringOutputStream();
$binaryPacketOutput = new DataOutputStream($binaryOutputStream);
$binaryPacketOutput->writeUnSignedShortBE(0x03); // METADATA_REQUEST
$binaryPacketOutput->writeUnSignedShortBE(1); // API_VERSION
$binaryPacketOutput->writeUnSignedIntBE(0x01); // 请求ID
$binaryPacketOutput->writeUnSignedShortBE(strlen('test')); // 客户端标识长度
$binaryPacketOutput->writeString('test'); // 客户端标识
$binaryPacketOutput->writeUnSignedIntBE(1); // topic列表数组长度
// topic数组元素
$binaryPacketOutput->writeUnSignedShortBE(strlen('test1')); // 写入2字节topic名称长度
$binaryPacketOutput->writeString('test1'); // topic名称
$binaryPacketOutput->flush(); // 输出缓冲
$packet = $binaryOutputStream->toBinaryString(); // 获得构造好的正文数据包

// 包装socket链接，获得多数据类型操作能力
$out = new DataOutputStream(new FileOutputStream($client));
$out->writeUnSignedIntBE(strlen($packet)); // 4字节包长度
$out->write($packet); // 包体
$out->flush(); // 输出到Socket

// 实例化输入流，从socket读取数据
$in = new DataInputStream(new FileInputStream($client));
$size = $in->readUnSignedIntBE(); // 4字节包长度
// 一次性读取完socket数据后关闭，然后将读取到的响应数据填充到二进制字符串输入流中，释放socket
$in = new DataInputStream(new BinaryStringInputStream(fread($client, $size)));
fclose($client);

$requestId = $in->readUnSignedIntBE(); // 4字节请求ID
printf("packet length: %d requestId: %d\n", $size, $requestId);

$brokerCount = $in->readUnSignedIntBE(); // broker数量
for ($i = 0; $i < $brokerCount; $i++) { // 循环读取broker
    $nodeId = $in->readUnSignedIntBE(); // nodeId
    $hostLength = $in->readUnSignedShortBE(); // host长度
    $host = $in->readString($hostLength); // 主机名
    $port = $in->readUnSignedIntBE(); // port
    $rackLength = $in->readShortBE(); // rack
    $rack = null;
    if ($rackLength != -1) {
        $rack = $in->readString($rackLength);
    }
    printf("nodeId:%d host:%s port:%d rack: %s\n", $nodeId, $host, $port, $rack);
}
$controllerId = $in->readUnSignedIntBE();
printf("controllerId: %d\n", $controllerId);
$topicCount = $in->readUnSignedIntBE();
printf("topic count %d\n", $topicCount);


for ($i = 0; $i < $topicCount; $i++) {
    printf("----topic list----\n");
    $errCode = $in->readUnSignedShortBE();
    $nameLength = $in->readUnSignedShortBE();
    $name = $in->readString($nameLength);
    $isInternal = $in->readUnSignedChar();
    printf("errcode: %d name: %s interval: %d\n", $errCode, $name, $isInternal);

    $partitionCount = $in->readUnSignedIntBE();
    printf("----topic [%s] partition list count %d---\n", $name, $partitionCount);
    for ($j = 0; $j < $partitionCount; $j++) {
        $errCode = $in->readUnSignedShortBE();
        $partitionIndex = $in->readUnSignedIntBE();
        $leaderId = $in->readUnSignedIntBE();
        $replicaNodesCount = $in->readUnSignedIntBE();
        $replicaNodes = [];
        for ($k = 0; $k < $replicaNodesCount; $k++) {
            $replicaNodes[] = $in->readUnSignedIntBE();
        }
        $isrNodeCount = $in->readUnSignedIntBE();
        $isrNodes = [];
        for ($k = 0; $k < $isrNodeCount; $k++) {
            $isrNodes[] = $in->readUnSignedIntBE();
        }
        printf(
            "errcode: %d partitionIndex: %d leaderId: %d replicaNodes: [%s] isrNodes: [%s]\n",
            $errCode,
            $partitionIndex,
            $leaderId,
            join(',', $replicaNodes),
            join(',', $isrNodes)
        );
    }
}
```

输出如下：

```
packet length: 73 requestId: 1
nodeId:0 host:bogon port:9092 rack: 
controllerId: 0
topic count 1
----topic list----
errcode: 0 name: test1 interval: 0
----topic [test1] partition list count 1---
errcode: 0 partitionIndex: 0 leaderId: 0 replicaNodes: [0] isrNodes: [0]
```

## 项目地址

 [php-io](https://github.com/xialeistudio/php-io)

(完)