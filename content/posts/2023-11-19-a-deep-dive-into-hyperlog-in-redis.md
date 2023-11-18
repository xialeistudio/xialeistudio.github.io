---
title: A deep dive into HyperLog in redis
slug: a-deep-dive-into-hyperlog-in-redis
date: 2023-11-18
tags: 
  - redis
featured: true
---
In this article, we'll deep dive into an interesting and powerful feature of Redis: HyperLog.
By understanding the working principles and application scenarios of these features, you'll be able to leverage Redis effectively to build high-performance and high-scalable applications.

<!--more-->

[Redis](https://redis.io) is an open-source, high-performance key-value storage system 
that is widely used in scenarios such as caching, message queues, counters, real-time leaderboards.
It is known for its fast read and write speeds, flexible data structures and rich features.

## Working Principle
HyperLog is a cardinality estimation algorithm used to approximate the number of distinct elements in a set. 
It achieves this by mapping elements to fixed-length binary sequences through hash functions and estimating the cardinality based on the count of leading zeros in these sequences. 
By observing the number of leading zeros, HyperLogLog can provide an efficient estimation of the number of unique elements in a large dataset while requiring a fixed amount of memory.

## Use Case

In Redis, HyperLog can be used to count the number of visitors 
and implement fast and memory-saving unique visitor counting.  
First, we can use Redis's HyperLog to create a structure that logs visitors, such as "visitors". 
Whenever a visitor visits a website, we use the `PFADD` command to add its unique identifier (such as an IP address or user ID) to the HyperLog.
Also, we can use `PFCOUNT` command to retrieve the amount of unique visitors.
Here is an example:

```bash
127.0.0.1:6379> PFADD visitors visitor1 visitor2 visitor3 visitor4 visitor1 visitor5
(integer) 1
127.0.0.1:6379> PFCOUNT visitors
(integer) 5
127.0.0.1:6379> 
```

## Margin of Error
When storing 100 million IP addresses using HyperLogLog, it's important to note that the algorithm introduces a small margin of error in estimating the cardinality (number of distinct IP addresses). The error rate of HyperLogLog is typically around **0.81%** (or 0.0081) of the estimated cardinality.

In the case of storing 100 million IP addresses, the estimated cardinality provided by HyperLogLog may have an error of approximately 0.81% of the actual number of distinct IP addresses. This means that the estimated count returned by HyperLogLog may deviate from the true count by around 810,000 IP addresses.

However, it's worth mentioning that HyperLogLog's error rate remains constant regardless of the total number of distinct IP addresses being tracked. This makes it a highly efficient and scalable solution for estimating the cardinality of large datasets while using minimal memory.

In summary, when using HyperLogLog to store 100 million IP addresses, the estimated cardinality may have an error rate of approximately 0.81%, which translates to around 810,000 IP addresses in this scenario.

## Memory Estimation
Let's talk about Memory usage of Using set and HyperLog.

When considering storing **100 million IP addresses**, the memory estimation for using a set and HyperLogLog would be as follows:

Using a Set:

+ Each IP address is stored as a separate entry in the set.
+ Assuming each IP address is a 32-bit integer, it would require 4 bytes (32 bits / 8 bits per byte) of memory per IP address.
+ Therefore, storing 100 million IP addresses in a set would require approximately **400 million bytes or 400 megabytes** of memory.

Using HyperLogLog:

+ HyperLogLog is a probabilistic algorithm that uses a fixed amount of memory regardless of the number of unique IP addresses.
+ Even with 100 million unique IP addresses, HyperLogLog can estimate the cardinality using just **a few kilobytes** of memory.

## Conclusion

Redis's HyperLog feature is a powerful tool for estimating the cardinality of distinct elements in a set. It offers fast and memory-efficient counting capabilities, making it ideal for scenarios such as visitor counting in web applications. Although HyperLog introduces a small margin of error in its cardinality estimation, its error rate remains constant regardless of the dataset size, making it a scalable solution. Compared to storing individual elements in a set, HyperLogLog requires significantly less memory, making it a preferred choice for large-scale applications. By leveraging HyperLog in Redis, developers can build high-performance and high-scalable applications that effectively handle counting and estimation tasks

## References

+ https://en.wikipedia.org/wiki/HyperLogLog
+ https://redis.io/docs/data-types/probabilistic/hyperloglogs/