---
title: MySQL、Redis、Aurora读书笔记
date: 2023-05-03 15:07:05
categories:
- engineering
---
本文分享一下五一期间的读书感悟，包括MySQL、Redis、Aurora。

<!--more-->

## 优化Redis主线程负载

1. 网络IO可以多线程处理，将请求包体和文件描述符投递到一个**request**队列，参考结构如下

   ```java
   class Request {
     byte[] req;
     int fd;
   }
   ```

2. 主线程轮询**request**队列，取出**req**数据并按照以往方式准备响应**resp**，再次投递到一个**response**队列，参考结构如下

   ```java
   class Response {
     byte[] req;
     int fd;
   }
   ```

3. 网络IO线程轮询**response**队列，将数据发往指定**fd**

优点：

+ 解耦业务线程和IO线程，充分利用多线程能力
+ 基于单线程+队列保证Redis业务线程仍然是单线程，无需同步/互斥逻辑

缺点：

+ 需要维护两个额外队列，当请求激增，主线程处理不过来会造成数据积压

## MySQL事务过程

1. 从磁盘加载数据到bufferpool
2. 写入并Flush undo日志 (顺序磁盘IO)
3. 修改bufferpool中的数据
4. 写入redo日志，不flush(无磁盘IO)
5. 如果有其他数据参与，重复步骤1...4
6. 设置所有redo日志为prepare状态
7. 写入并Flush binlog(顺序磁盘IO)
8. Flush redo日志（顺序磁盘IO）
9. 提交事务

## MySQL double-write

> 关于IO的最小单位：
>
> 　　1. 数据库IO的最小单位是16K（MySQL默认，oracle是8K）
>
> 　　2. 文件系统IO的最小单位是4K（也有1K的）
>
> 　　3. 磁盘IO的最小单位是512字节
>
> 因此，存在IO写入导致page损坏的风险：
>
> ![img](https://static.ddhigh.com/blog/2023/05/03/1683100294373935000.png) 
>
> ***[GeaoZhang](https://home.cnblogs.com/u/geaozhang/)*** - [InnoDB关键特性之double write](https://www.cnblogs.com/geaozhang/p/7241744.html)

上述例子中，一个脏页只有前面一半落盘了，后面一半还是老数据，所以这一个16K脏页数据无效。

### redo日志无法恢复

redo日志记录对数据页的物理修改，但是现在出现的问题是页本身无效，redo日志也无法恢复。具体原因如下：

1. 数据文件上有一个老页面，加载到内存之后，内存也有一个老页面
2. 修改内存数据，比如把某脏页第2个字节改为1， redo日志记录把该页第2个字节改为1
3. 当InnoDB刷新脏页出现刷一半的问题时，数据文件上的老页面已经无效了（一半是新的，一半是旧的），跟内存修改时的老页面不一致，redo日志无法应用

### double-write流程

![img](https://static.ddhigh.com/blog/2023/05/03/1683100403081956000.png)

1. 脏页刷新时，拷贝到内存中的doublewrite buffer（大小2MB）
2. 将doublewrite buffer分两次写入共享表空间文件（每次1MB，顺序IO，速度快）
3. 将doublewrite buffer数据写入数据文件（随机磁盘IO）

本质上优点类似WAL(Write-Ahead-Log)，通过先顺序写入文件，再随机磁盘IO落盘。

### 数据恢复

回到最开始的问题，InnoDB恢复时可以通过校验和发现数据文件中的脏页数据无效（对比脏页计算出来的校验和和磁盘上的校验和），此时可以通过共享表空间文件找到该页最近的数据，复制到数据文件，再应用redo日志，完成恢复



## Aurora

Aurora是Amazon研发的分布式MySQL，随着数据库上云，传统数据库的磁盘IO瓶颈已经变为了数据计算层和存储曾之间的IO瓶颈。换句话说，由于SSD的广泛使用，磁盘IO本身基本不是瓶颈。

Aurora的主要优点如下：

+ 使用一个独立部署、能容忍错误并且能自动修改的分布式存储服务（跨数据中心），保证数据库不受存储层的可用性影响
+ 不同数据库计算节点之间以及数据库存储节点之间，网络IO只有redolog（没有binlog）
+ 将耗时的串行操作尽量拆解为异步操作，减少延迟

### 术语定义

+ 计算节点：安装数据库软件的节点
+ 存储节点：存储数据的节点

### 传统MySQL分布式架构

![原MySQL负载](https://static.ddhigh.com/blog/2023/05/03/1683099089289616000.PNG)

可以看到MySQL节点之间同步了非常多的数据，而由于MySQL的分层架构，数据库层和存储引擎层是分离的，导致binlog和redolog两份日志出现，实际上这两份日志的功能本质上是一样的，提供数据镜像和数据恢复。

### Aurora的网络IO

Aurora极大减少了网络IO，节点之间真正传输的只有redolog和表的元数据，下图是Aurora的网络IO

![Aurora优化负载](https://static.ddhigh.com/blog/2023/05/03/1683099365972619000.PNG)

一个数据写入流程如下：

1. 存储节点接收到redo日志，写入本地内存队列（无磁盘IO）
2. 将redo日志持久化到磁盘，并返回响应给计算节点（顺序磁盘IO）
3. 整理记录，并检查是否有因为一些操作丢失导致的记录差异。
4. 基于gossip解析和其他节点对齐数据
5. 应用redo日志记录，将数据变更应用到数据页（随机磁盘IO）
6. 定期将日志和新页面备份到S3
7. 定期进行垃圾回收，清理掉无用的旧版本数据，释放存储空间
8. 定期进行CRC校验， 修复损坏数据

只有1/2步会影响计算节点，其他步骤全部是异步的，这是高性能的保证

### 数据同步

redo日志关联了（LSN，Log Sequence Number），LSN的概念和MySQL一致，当节点丢失数据时，可以通过gossip和其他节点对比LSN并补齐丢失的数据。

而当需要进行故障恢复时，Aurora首先会保证所有节点上的数据一致，通过使用LSN来实现，Aurora会选出一个保证可用的最高LSN，称为VCL（Volume Complete LSN），任何LSN高于VCL的日志记录会被截断。Aurora还规定只有某些特定的LSN可以作为截断点，称为CPL（Consistency Point LSNs），另外定义了VDL（Volume Durable LSN）为小于等于VCL的最大CPL。

简单例子：当前日志的LSN已经达到了1007，但数据库定义CPL为900，1000，1100这些特定值。那么>1000的LSN数据会被截断，所以，最终VCL是1000。实际流程如下：

1. 每个数据库层事务被切分成多个有序且可被原子操作的小事务（mini-transactions，MTRs）
2. 每个MTR由多个连续的log record组成。
3. 一个MTR的最后一个log record被认为是一个CPL。

### 数据操作

> - Writes：当数据库收到一批log日志的write quorum的确认后，就会向前推进当前的VDL。在每一时刻，会有很多事务在同时进行，数据库会为每个日志分配一个唯一有序的LSN，同时LSN要小于当前VDL和LAL（LSN Allocation Lmit）的和。这段话翻译有些生硬，其实就是为了防止前台操作太快，后台存储系统处理不过来，LSN不能超前VDL太多，其差值最大为LAL，目前设置为10M。同时，为了解决每个分片可能存在的日志丢失问题，每个日志都有一个向前的回链（像是一个反向链表），通过向前回溯，以及Gossip交互，可以为各个节点构建一个完整的日志记录，称之为SCL（Segement Complete LSN），也即所有日志到达了所有节点的最大LSN。
>- Commits：Aurora的事务提交是完全异步的。工作线程收到commit请求，在一个等待commit的事务列表中记录它的commit LSN，然后就继续处理其它请求。有一个专门的线程在VDL推进时，判断列表中有哪些LSN小于等于VDL，然后将这些事务的应答推回给还在等待的客户端。
> - Reads：Aurora和很多其它数据库一样，数据页会放在缓存中，命中丢失时才会做一次IO请求，当缓存满时，系统会根据特定的算法汰换数据页。Aurora不一样的是，它要求在缓存中的page LSN一定要大于等于VDL。从而保证在这个数据页中所有请求都已经写到log，且可以通过VDL始终获取到最新的持久化数据。也因此，正常的读取只需要读一个满足条件的分片就足够了。
> - Replicas：在Aurora中，一个存储磁盘可以挂载一个writer和最多15个read副本。增加一个read副本不会对性能有什么影响。为了加快响应，写请求生成的日志流也会被发送到所有读副本中去。如果这个写请求涉及到当前缓存中的某个数据页，那就把这个请求更新到数据页中，否则就直接丢弃了。这里读副本消费请求是异步的，需要遵循两条规则：一是会更新到数据页的请求，其LSN需要小于等于VDL。二是mini-transaction的修改需要原子性的写入缓存，以保障数据一致性。
> 
> ***Hotlink Qiu*** - [分布式存储研究——Aurora](https://hotlinkqiu.github.io/2019/08/15/%E5%88%86%E5%B8%83%E5%BC%8F%E5%AD%98%E5%82%A8%E7%A0%94%E7%A9%B6%E2%80%94%E2%80%94Aurora/)

### 数据恢复

和MySQL不同，Aurora的数据恢复是后台化的，在存储层即可完成，无需停机。恢复完成后，需要进行quorum读(从其他副本取出保证可用的数据)，同时进行VDL计算，截断>VDL的数据，这些操作都可以在后台进行，不影响前台响应延迟。

## 参考

+ [分布式存储研究——Aurora](https://hotlinkqiu.github.io/2019/08/15/%E5%88%86%E5%B8%83%E5%BC%8F%E5%AD%98%E5%82%A8%E7%A0%94%E7%A9%B6%E2%80%94%E2%80%94Aurora/)
+ [InnoDB关键特性之double write](https://www.cnblogs.com/geaozhang/p/7241744.html)

