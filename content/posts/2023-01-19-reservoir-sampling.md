---
slug: reservoir-sampling
title: 水塘抽样算法
date: 2023-01-19 23:34:44
tags:
- leetcode
categories:
- Algorithm
---

下面是[维基百科水塘抽样](https://zh.wikipedia.org/zh-mo/%E6%B0%B4%E5%A1%98%E6%8A%BD%E6%A8%A3)的说明。

>  水塘抽样是一系列的随机算法，其目的在于从包含 $n$个项目的集合  中选取$k$ 个样本，其中 $n$为一很大或未知的数量，尤其适用于不能把所有 $n$ 个项目都存放到内存的情况。

本文分享在随机数据流中等概率抽取target的水塘抽样算法。

## 算法

1. 定义$count$计数变量
2. 遍历给定的数据流，如果当前数字等于$target$, $count$+1
3. 在$[0, count]$产生随机数，如果等于$count$，则抽样成功

## 示例

Leetcode [398. 随机数索引](https://leetcode.cn/problems/random-pick-index/)

**代码**

```java
class Solution {


        // 哈希表保存<值,List<下标>>
        private final int[] nums;
        private final Random random;

        public Solution(int[] nums) {
            this.nums = nums;
            this.random = new Random(System.currentTimeMillis());
        }

        // 水塘抽样
        // 统计target count,随机数%count 为0时重置index
        public int pick(int target) {
            var count = 0;
            var index = 0;
            for (var i = 0; i < nums.length; i++) {
                if (nums[i] == target) {
                    count++;
                    if (random.nextInt() % count == 0) {
                        index = i;
                    }
                }
            }
            return index;
        }
}
```

**复杂度分析**

时间复杂度：$O(n)$,$n$是$nums$长度，需要遍历一次$nums$

空间复杂度：$O(1)$,严格来说，java默认使用浅拷贝，因此$nums$不会有额外空间占用。
