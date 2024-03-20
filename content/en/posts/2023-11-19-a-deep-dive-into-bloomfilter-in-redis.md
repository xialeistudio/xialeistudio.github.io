---
title: A deep dive into Bloomfilter in Redis
slug: a-deep-dive-into-bloomfilter-in-redis
date: 2023-11-19
keywords:
  - redis
  - bloomfilter
series:
  - Redis
categories:
  - Engineering  
tags: 
  - redis
featured: true
---
In this article, I'll deep dive into an annother powerful data structure in Redis: Bloom Filter.
Bloom Filter can help you check whether elements exist, reduce unnecessary quering costs, improve system response speed and throughput. By properly utilizing Bloom Filter, you can optimize application performance effectively, meet the requirement of high-performance and large-scale data processing.

<!--more-->

## Working Principle
Bloom Filter is a probabilistic data structure that is highly space-efficient and can quickly determine the membership of elements. Here is the working principle of Bloom Filter.

1. Initialize: Bloom Filter consists of a bit array(usually a binary vector) and multiple independent hash functions. The initial state of the bit array is all 0s.
2. Add element: When adding an element to Bloom Filter, this element is passed  into multiple hash functions, each of which produces a hash value. Based on these hash values, the corresponding bit in the bit array is set to 1.
3. Query element: When quering whether an element exists in the Bloom Filter, similarly, the element is passed into multiple hash functions to get multiple hash values, then check the corresponding bit in the bit array. **If all bits are 1, it means that the element may exist in the Bloom Filter, if any position is 0, it means that the element definitely doest not exist in the Bloom Filter.**

## Use Case

Bloom Filter is not a built-in module in Redis, there are 2 solutions to solve this problem:

1. You can use your custom hash function and bitmap feature in Redis to implement a Bloom Filter by yourself.
2. Using the [RedisBloom](https://github.com/RedisBloom/RedisBloom) module (Recommended)

Here is an example of using Bloom Filter in redis-cli:

```bash
> BF.RESERVE bikes:models 0.001 1000000
OK
> BF.ADD bikes:models "Smoky Mountain Striker"
(integer) 1
> BF.EXISTS bikes:models "Smoky Mountain Striker"
(integer) 1
> BF.MADD bikes:models "Rocky Mountain Racer" "Cloudy City Cruiser" "Windy City Wippet"
1) (integer) 1
2) (integer) 1
3) (integer) 1
> BF.MEXISTS bikes:models "Rocky Mountain Racer" "Cloudy City Cruiser" "Windy City Wippet"
1) (integer) 1
2) (integer) 1
3) (integer) 1
```

## False positives

It is important to note that a Bloom filter has one possibility of error in its query results: **false positives**. A false positive occurs when the filter incorrectly indicates that an element is present, even though it hasn't been added. However, a Bloom filter **does not have false negatives**, meaning it will never incorrectly indicate that an element is not present if it has been added.

Why there are false positives in Bloom Filter? Here are the reasons:

1. Hash conflict: Bloom Filter uses multiple hash function to map an element to different positions in the bit array. However, different element may map to same positions, which is called hash confict. When hash conflict occur on multiple elements, they may cause the same bit to be set to 1, causing a false positive.
2. The limit on bit array: Bloom Filter uses a bit array to represent the presence of elements. Because the size of the bit array is limited, as the number of elements in the Bloom Filter increases, the degree of filling in the bit array also increases, which increases the probability of misjudgment.

It is important to note that false positives are an inherent characteristic of Bloom Filter, **this is not a bug! this is a trade-off between space occupation and the probability of misjudgment**. For specific application scenarios, we can adjust the probability of misjudgment to balance the trace-off between false positives and space efficiency.

## Conclusion

In conclusion, Bloom filters are a powerful probabilistic data structure that provides an efficient solution for membership queries. They offer constant-time lookup with minimal memory requirements, making them suitable for applications where space efficiency is crucial. **However, it's important to consider the trade-offs associated with Bloom filters, such as the possibility of false positives and the inability to delete elements**. Bloom filters are most effective when used in scenarios where the cost of false positives is acceptable and where the benefits of reduced memory usage outweigh the potential errors. With careful parameter selection and understanding of the specific requirements of the application, Bloom filters can be a valuable tool for improving performance and reducing resource consumption in various domains, including network protocols, caching systems, and large-scale data processing.

## References

+ https://redis.io/docs/data-types/probabilistic/bloom-filter/
+ https://en.wikipedia.org/wiki/Bloom_filter
+ https://github.com/RedisBloom/RedisBloom